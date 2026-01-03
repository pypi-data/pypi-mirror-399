"""
Prism Manager - Core Logic for Parameter Sweep Management

This module provides the PrismManager class that handles:
- Configuration expansion from base + prism configs
- State file (.prism) management
- Nominal (dictionary) and Positional (list) parameter linking
- Experiment naming and tracking
"""

import json
import yaml
import copy
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Callable, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import itertools

from .utils import (
    print_info, print_success, print_warning, print_error, 
    print_progress, print_file, deep_merge, deep_get, deep_set
)

if TYPE_CHECKING:
    from .project import Project
    from .executor import Executor


class ExperimentStatus(str, Enum):
    """Status of an experiment run."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    DONE = "DONE"
    FAILED = "FAILED"


@dataclass
class ExperimentRecord:
    """Record of a single experiment configuration and its state."""
    status: ExperimentStatus = ExperimentStatus.PENDING
    config: Dict[str, Any] = field(default_factory=dict)
    metrics: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    duration_seconds: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "status": self.status.value if isinstance(self.status, ExperimentStatus) else self.status,
            "config": self.config,
            "metrics": self.metrics,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "error_message": self.error_message,
            "duration_seconds": self.duration_seconds,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentRecord":
        """Create from dictionary."""
        status = data.get("status", "PENDING")
        if isinstance(status, str):
            status = ExperimentStatus(status)
        return cls(
            status=status,
            config=data.get("config", {}),
            metrics=data.get("metrics", {}),
            started_at=data.get("started_at"),
            completed_at=data.get("completed_at"),
            error_message=data.get("error_message"),
            duration_seconds=data.get("duration_seconds"),
        )


@dataclass 
class PrismState:
    """State file content for a Prism study."""
    study_name: str
    base_config_path: str
    prism_config_paths: List[str]
    base_config_content: Dict[str, Any] = field(default_factory=dict)
    prism_configs_content: List[Dict[str, Any]] = field(default_factory=list)
    experiments: Dict[str, ExperimentRecord] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    @property
    def prism_config_path(self) -> str:
        """For backward compatibility."""
        return self.prism_config_paths[0] if self.prism_config_paths else ""
    
    @property
    def prism_config_content(self) -> Dict[str, Any]:
        """For backward compatibility, return merged prism config."""
        if not self.prism_configs_content:
            return {}
        if len(self.prism_configs_content) == 1:
            return self.prism_configs_content[0]
        merged = {}
        for cfg in self.prism_configs_content:
            merged = deep_merge(merged, cfg)
        return merged
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "study_name": self.study_name,
            "base_config_path": self.base_config_path,
            "prism_config_paths": self.prism_config_paths,
            "prism_configs_content": self.prism_configs_content,
            "base_config_content": self.base_config_content,
            "experiments": {k: v.to_dict() for k, v in self.experiments.items()},
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PrismState":
        """Create from dictionary."""
        experiments = {}
        for k, v in data.get("experiments", {}).items():
            experiments[k] = ExperimentRecord.from_dict(v)
        
        # Handle backward compatibility
        prism_config_paths = data.get("prism_config_paths")
        if prism_config_paths is None:
            legacy_path = data.get("prism_config_path", "")
            prism_config_paths = [legacy_path] if legacy_path else []
        
        prism_configs_content = data.get("prism_configs_content")
        if prism_configs_content is None:
            legacy_content = data.get("prism_config_content", {})
            prism_configs_content = [legacy_content] if legacy_content else []
        
        return cls(
            study_name=data["study_name"],
            base_config_path=data["base_config_path"],
            prism_config_paths=prism_config_paths,
            base_config_content=data.get("base_config_content", {}),
            prism_configs_content=prism_configs_content,
            experiments=experiments,
            created_at=data.get("created_at", datetime.now().isoformat()),
            updated_at=data.get("updated_at", datetime.now().isoformat())
        )


class PrismManager:
    """
    Manager for parameter sweep experiments.
    
    Handles the combination of a base config and prism configs to generate,
    manage, and execute multiple experiment configurations.
    
    Prism Config Format:
    --------------------
    Prism configs can contain two types of parameter specifications:
    
    1. Nominal Linking (Dictionary): Named configurations
       ```yaml
       training:
         optimizer:
           lr: {"low_lr": 0.0001, "high_lr": 0.01}
       ```
       Creates experiments named by their keys (low_lr, high_lr).
       
    2. Positional Linking (List): Sequential configurations  
       ```yaml
       data:
         seed: [42, 123, 456]
       ```
       Creates experiments run_0, run_1, run_2, etc.
    
    Usage:
    ------
    ```python
    manager = PrismManager(
        base_config_path="configs/base.yaml",
        prism_config_path="configs/sweep.prism.yaml", 
        study_name="my_sweep",
        output_dir="outputs"
    )
    
    # Generate experiment configurations
    manager.expand_configs()
    
    # Execute with custom executor
    from prism.executor import Executor
    executor = Executor(project)
    manager.execute_all(executor)
    ```
    """
    
    def __init__(
        self,
        base_config_path: Union[str, Path],
        prism_config_path: Union[str, Path, List[Union[str, Path]], None] = None,
        study_name: str = "study",
        output_dir: Union[str, Path] = "outputs",
    ):
        """
        Initialize PrismManager.
        
        Args:
            base_config_path: Path to the base configuration YAML file
            prism_config_path: Path(s) to prism config file(s). Can be:
                              - Single path
                              - List of paths (cartesian product)
                              - None (single experiment = base config only)
            study_name: Name of the study (used for .prism state file)
            output_dir: Directory for outputs and state file
        """
        self.base_config_path = Path(base_config_path)
        
        # Handle prism config paths
        if prism_config_path is None:
            self.prism_config_paths = []
        elif isinstance(prism_config_path, (str, Path)):
            self.prism_config_paths = [Path(prism_config_path)]
        else:
            self.prism_config_paths = [Path(p) for p in prism_config_path]
        
        self.study_name = study_name
        self.output_dir = Path(output_dir)
        
        # State file path
        self.state_file_path = self.output_dir / f"{study_name}.prism"
        
        # Load or create state
        self.state: PrismState = self._load_or_create_state()
    
    # =========================================================================
    # File I/O
    # =========================================================================
    
    def _load_yaml(self, path: Path) -> Dict[str, Any]:
        """Load a YAML file with inheritance support."""
        with open(path, 'r') as f:
            config = yaml.safe_load(f) or {}
        
        # Handle inheritance
        if 'inherit_from' in config:
            base_path = path.parent / config['inherit_from']
            if base_path.exists():
                base_config = self._load_yaml(base_path)
                config = deep_merge(base_config, config)
                config.pop('inherit_from', None)
        
        return config
    
    def _save_yaml(self, path: Path, data: Dict[str, Any]):
        """Save data to a YAML file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    
    def _load_json(self, path: Path) -> Dict[str, Any]:
        """Load a JSON file."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def _save_json(self, path: Path, data: Dict[str, Any]):
        """Save data to a JSON file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    
    # =========================================================================
    # State Management
    # =========================================================================
    
    def _load_or_create_state(self) -> PrismState:
        """Load existing state file or create a new one."""
        if self.state_file_path.exists():
            print_file(str(self.state_file_path), "Loading state")
            data = self._load_json(self.state_file_path)
            state = PrismState.from_dict(data)
            
            # Reset any RUNNING experiments to PENDING
            # (they were interrupted if we're loading from disk)
            running_count = 0
            for exp in state.experiments.values():
                if exp.status == ExperimentStatus.RUNNING:
                    exp.status = ExperimentStatus.PENDING
                    exp.started_at = None
                    running_count += 1
            
            if running_count > 0:
                print_warning(f"Reset {running_count} interrupted experiments from RUNNING to PENDING")
                # Save the corrected state
                self._save_state(state)
            
            return state
        
        # Create new state
        print_progress(f"Creating new study: {self.study_name}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load base config
        if not self.base_config_path.exists():
            raise FileNotFoundError(f"Base config not found: {self.base_config_path}")
        base_config = self._load_yaml(self.base_config_path)
        
        # Load all prism configs
        prism_configs = []
        for prism_path in self.prism_config_paths:
            if not prism_path.exists():
                raise FileNotFoundError(f"Prism config not found: {prism_path}")
            prism_configs.append(self._load_yaml(prism_path))
            print_file(str(prism_path), "Loaded prism config")
        
        state = PrismState(
            study_name=self.study_name,
            base_config_path=str(self.base_config_path),
            prism_config_paths=[str(p) for p in self.prism_config_paths],
            base_config_content=base_config,
            prism_configs_content=prism_configs
        )
        
        self._save_state(state)
        return state
    
    def _save_state(self, state: Optional[PrismState] = None):
        """Save current state to the .prism file."""
        if state is None:
            state = self.state
        state.updated_at = datetime.now().isoformat()
        self._save_json(self.state_file_path, state.to_dict())
    
    def reload_configs(self):
        """Reload base and prism configs from disk."""
        self.state.base_config_content = self._load_yaml(self.base_config_path)
        self.state.prism_configs_content = [
            self._load_yaml(Path(p)) for p in self.state.prism_config_paths
        ]
        self._save_state()
        print_success("Reloaded configurations from disk")
    
    # =========================================================================
    # Parameter Analysis
    # =========================================================================
    
    def _set_nested_value(self, config: Dict, key_path: str, value: Any):
        """Set a value in a nested dictionary using dot notation."""
        keys = key_path.split(".")
        current = config
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def _get_nested_value(self, config: Dict, key_path: str, default: Any = None) -> Any:
        """Get a value from a nested dictionary using dot notation."""
        return deep_get(config, key_path, default)
    
    def _is_sweep_definition(self, value: Any) -> bool:
        """
        Check if a value is a sweep definition (e.g., _type: choice, _values: [...]).
        
        Supported formats:
        - {_type: "choice", _values: [...]}
        - {_type: "range", _min: ..., _max: ..., _step: ...}
        - {_type: "linspace", _min: ..., _max: ..., _num: ...}
        """
        if not isinstance(value, dict):
            return False
        return "_type" in value and ("_values" in value or "_min" in value)
    
    def _expand_sweep_definition(self, sweep_def: Dict[str, Any]) -> List[Any]:
        """
        Expand a sweep definition into a list of values.
        
        Args:
            sweep_def: Dict with _type and _values or _min/_max/_step
        
        Returns:
            List of expanded values
        """
        sweep_type = sweep_def.get("_type", "choice")
        
        if sweep_type == "choice":
            return sweep_def.get("_values", [])
        
        elif sweep_type == "range":
            import numpy as np
            start = sweep_def.get("_min", 0)
            stop = sweep_def.get("_max", 1)
            step = sweep_def.get("_step", 1)
            return list(np.arange(start, stop + step/2, step))
        
        elif sweep_type == "linspace":
            import numpy as np
            start = sweep_def.get("_min", 0)
            stop = sweep_def.get("_max", 1)
            num = sweep_def.get("_num", 10)
            return list(np.linspace(start, stop, num))
        
        else:
            # Unknown type, return values if present
            return sweep_def.get("_values", [sweep_def])
    
    def _is_nominal_parameter(self, value: Dict[str, Any]) -> bool:
        """
        Determine if a dictionary represents a nominal parameter (sweep config)
        rather than a nested configuration section.
        """
        if not isinstance(value, dict) or not value:
            return False
        
        # Sweep definitions are NOT nominal parameters, they're positional
        if self._is_sweep_definition(value):
            return False
        
        # Check if all values are terminal (non-dict)
        for v in value.values():
            if isinstance(v, dict):
                return False
        
        # Common config section keys that are NOT nominal
        config_section_keys = {
            'type', 'enabled', 'mode', 'path', 'dir', 'root', 'name',
            'lr', 'weight_decay', 'momentum', 'batch_size', 'num_workers',
            'patience', 'factor', 'min_lr', 'delta',
            'train', 'val', 'test', 'prob', 'mean', 'std'
        }
        
        if all(k.lower() in config_section_keys for k in value.keys()):
            return False
        
        # If keys have underscores or look like identifiers, likely nominal
        identifier_patterns = ['conf', 'exp', 'run', 'model', 'setting']
        for k in value.keys():
            if '_' in k and not k.startswith('_'):
                return True
            if any(k.lower().startswith(p) for p in identifier_patterns):
                return True
        
        return False
    
    def _extract_parameter_types(self, prism_config: Dict[str, Any]) -> tuple:
        """
        Extract nominal (dict), positional (list), and scalar parameters.
        
        Returns:
            Tuple of (nominal_params, positional_params, scalar_params)
        """
        nominal_params = {}
        positional_params = {}
        scalar_params = {}
        
        def extract_recursive(config: Dict, prefix: str = ""):
            for key, value in config.items():
                full_key = f"{prefix}.{key}" if prefix else key
                
                if isinstance(value, dict):
                    # Check for sweep definition first (_type/_values syntax)
                    if self._is_sweep_definition(value):
                        expanded = self._expand_sweep_definition(value)
                        if len(expanded) > 1:
                            positional_params[full_key] = expanded
                        elif len(expanded) == 1:
                            scalar_params[full_key] = expanded[0]
                    elif self._is_nominal_parameter(value):
                        nominal_params[full_key] = value
                    else:
                        extract_recursive(value, full_key)
                elif isinstance(value, list):
                    if all(not isinstance(item, (dict, list)) for item in value):
                        if len(value) > 1 and isinstance(value[0], (int, float)):
                            positional_params[full_key] = value
                        else:
                            scalar_params[full_key] = value
                    else:
                        scalar_params[full_key] = value
                else:
                    scalar_params[full_key] = value
        
        extract_recursive(prism_config)
        return nominal_params, positional_params, scalar_params
    
    def _get_nominal_keys(self, nominal_params: Dict[str, Dict]) -> List[str]:
        """Extract all unique nominal keys from nominal parameters."""
        all_keys = set()
        for param_values in nominal_params.values():
            all_keys.update(param_values.keys())
        return sorted(list(all_keys))
    
    def _get_keys_per_file(self) -> List[List[str]]:
        """Get the list of keys for each prism file separately."""
        prism_configs = self.state.prism_configs_content
        keys_per_file = []
        
        for prism_config in prism_configs:
            nominal_params, positional_params, _ = self._extract_parameter_types(prism_config)
            
            file_keys = []
            if nominal_params:
                file_keys = self._get_nominal_keys(nominal_params)
            elif positional_params:
                first_list = list(positional_params.values())[0]
                file_keys = [f"run_{j}" for j in range(len(first_list))]
            
            if file_keys:
                keys_per_file.append(file_keys)
        
        return keys_per_file
    
    def get_available_keys(self) -> List[str]:
        """
        Get all available experiment keys.
        
        When multiple prism files are provided, returns cartesian product.
        """
        if not self.state.prism_configs_content:
            return ["default"]
        
        keys_per_file = self._get_keys_per_file()
        
        if not keys_per_file:
            return ["default"]
        
        if len(keys_per_file) == 1:
            return keys_per_file[0]
        
        # Cartesian product
        product_keys = []
        for combo in itertools.product(*keys_per_file):
            product_keys.append("_".join(combo))
        
        return product_keys
    
    # =========================================================================
    # Config Expansion
    # =========================================================================
    
    def expand_configs(
        self,
        prism_keys: Optional[List[str]] = None,
        linking_mode: str = "zip"
    ) -> Dict[str, Dict[str, Any]]:
        """
        Expand the base config with prism overrides to generate experiment configs.
        
        Args:
            prism_keys: Optional list of specific keys to generate
            linking_mode: "zip" (strict) or "product" (cartesian)
        
        Returns:
            Dict of {experiment_key: merged_config}
        """
        prism_configs = self.state.prism_configs_content
        base_config = self.state.base_config_content

        # No prism configs -> single experiment
        if not prism_configs:
            experiments = {"default": copy.deepcopy(base_config)}
            self._update_state_experiments(experiments)
            print_success("Generated 1 experiment configuration (no prism sweep)")
            return experiments
        
        # Check for multiple prism files
        keys_per_file = self._get_keys_per_file()
        if len(keys_per_file) > 1:
            return self._expand_configs_cartesian(prism_keys)
        
        # Single file mode
        prism_config = self.state.prism_config_content
        nominal_params, positional_params, scalar_params = self._extract_parameter_types(prism_config)
        
        print_info(f"Found {len(nominal_params)} nominal, {len(positional_params)} positional, {len(scalar_params)} scalar params")
        
        experiments = {}
        
        # Handle nominal parameters
        if nominal_params:
            all_nominal_keys = self._get_nominal_keys(nominal_params)
            keys_to_generate = all_nominal_keys if prism_keys is None else [k for k in prism_keys if k in all_nominal_keys]
            
            for config_key in keys_to_generate:
                merged = copy.deepcopy(base_config)
                
                for param_path, value in scalar_params.items():
                    self._set_nested_value(merged, param_path, value)
                
                for param_path, param_values in nominal_params.items():
                    if config_key in param_values:
                        self._set_nested_value(merged, param_path, param_values[config_key])
                
                experiments[config_key] = merged
        
        # Handle positional parameters
        elif positional_params:
            list_lengths = [len(v) for v in positional_params.values()]
            
            if linking_mode == "zip":
                if len(set(list_lengths)) > 1:
                    raise ValueError(f"Positional parameters have different lengths: {list_lengths}")
                
                num_runs = list_lengths[0] if list_lengths else 0
                
                for run_idx in range(num_runs):
                    run_key = f"run_{run_idx}"
                    merged = copy.deepcopy(base_config)
                    
                    for param_path, value in scalar_params.items():
                        self._set_nested_value(merged, param_path, value)
                    
                    for param_path, param_values in positional_params.items():
                        self._set_nested_value(merged, param_path, param_values[run_idx])
                    
                    experiments[run_key] = merged
            
            elif linking_mode == "product":
                param_paths = list(positional_params.keys())
                param_values = list(positional_params.values())
                
                for run_idx, combo in enumerate(itertools.product(*param_values)):
                    run_key = f"run_{run_idx}"
                    merged = copy.deepcopy(base_config)
                    
                    for param_path, value in scalar_params.items():
                        self._set_nested_value(merged, param_path, value)
                    
                    for param_path, value in zip(param_paths, combo):
                        self._set_nested_value(merged, param_path, value)
                    
                    experiments[run_key] = merged
        
        # Only scalar overrides
        elif scalar_params:
            merged = copy.deepcopy(base_config)
            for param_path, value in scalar_params.items():
                self._set_nested_value(merged, param_path, value)
            experiments["default"] = merged
        
        else:
            experiments["default"] = copy.deepcopy(base_config)
        
        self._update_state_experiments(experiments)
        print_success(f"Generated {len(experiments)} experiment configurations")
        
        return experiments
    
    def _expand_configs_cartesian(
        self,
        prism_keys: Optional[List[str]] = None
    ) -> Dict[str, Dict[str, Any]]:
        """Expand configs using cartesian product of keys from multiple prism files."""
        prism_configs = self.state.prism_configs_content
        base_config = self.state.base_config_content
        
        keys_per_file = self._get_keys_per_file()
        params_per_file = [self._extract_parameter_types(cfg) for cfg in prism_configs]
        
        print_info(f"Multi-file mode: {len(prism_configs)} files, cartesian product")
        
        all_combos = list(itertools.product(*keys_per_file))
        
        if prism_keys:
            all_combos = [c for c in all_combos if "_".join(c) in prism_keys]
        
        experiments = {}
        
        for combo in all_combos:
            compound_key = "_".join(combo)
            merged = copy.deepcopy(base_config)
            
            for file_idx, key_for_file in enumerate(combo):
                nominal_params, positional_params, scalar_params = params_per_file[file_idx]
                
                for param_path, value in scalar_params.items():
                    self._set_nested_value(merged, param_path, value)
                
                for param_path, param_values in nominal_params.items():
                    if key_for_file in param_values:
                        self._set_nested_value(merged, param_path, param_values[key_for_file])
            
            experiments[compound_key] = merged
        
        self._update_state_experiments(experiments)
        print_success(f"Generated {len(experiments)} experiment configurations (cartesian)")
        
        return experiments
    
    def _update_state_experiments(self, experiments: Dict[str, Dict[str, Any]]):
        """Update state with generated experiments."""
        for exp_key, exp_config in experiments.items():
            if exp_key not in self.state.experiments:
                self.state.experiments[exp_key] = ExperimentRecord(
                    status=ExperimentStatus.PENDING,
                    config=exp_config
                )
            else:
                self.state.experiments[exp_key].config = exp_config
        self._save_state()
    
    # =========================================================================
    # Experiment Access
    # =========================================================================
    
    def get_experiment(self, key: str) -> Optional[ExperimentRecord]:
        """Get an experiment record by key."""
        return self.state.experiments.get(key)
    
    def get_experiments_by_status(self, status: ExperimentStatus) -> List[str]:
        """Get experiment keys with a specific status."""
        return [k for k, v in self.state.experiments.items() if v.status == status]
    
    def get_pending_experiments(self) -> List[str]:
        """Get list of pending experiment keys."""
        return self.get_experiments_by_status(ExperimentStatus.PENDING)
    
    def get_failed_experiments(self) -> List[str]:
        """Get list of failed experiment keys."""
        return self.get_experiments_by_status(ExperimentStatus.FAILED)
    
    def get_completed_experiments(self) -> List[str]:
        """Get list of completed experiment keys."""
        return self.get_experiments_by_status(ExperimentStatus.DONE)
    
    def get_next_pending(self) -> Optional[str]:
        """Get the first pending experiment key."""
        pending = self.get_pending_experiments()
        return pending[0] if pending else None
    
    # =========================================================================
    # Status Management
    # =========================================================================
    
    def reset_experiment(self, key: str):
        """Reset an experiment to PENDING status."""
        if key in self.state.experiments:
            exp = self.state.experiments[key]
            exp.status = ExperimentStatus.PENDING
            exp.metrics = {}
            exp.started_at = None
            exp.completed_at = None
            exp.error_message = None
            exp.duration_seconds = None
            self._save_state()
            print_progress(f"Reset '{key}' to PENDING")
    
    def reset_all(self):
        """Reset all experiments to PENDING status."""
        for key in self.state.experiments.keys():
            self.reset_experiment(key)
    
    def reset_failed(self):
        """Reset only failed experiments to PENDING."""
        for key in self.get_failed_experiments():
            self.reset_experiment(key)
    
    def mark_done(self, key: str, metrics: Optional[Dict[str, Any]] = None):
        """Mark an experiment as done."""
        if key in self.state.experiments:
            exp = self.state.experiments[key]
            exp.status = ExperimentStatus.DONE
            exp.completed_at = datetime.now().isoformat()
            if metrics:
                exp.metrics = metrics
            self._save_state()
    
    def mark_failed(self, key: str, error_message: Optional[str] = None):
        """Mark an experiment as failed."""
        if key in self.state.experiments:
            exp = self.state.experiments[key]
            exp.status = ExperimentStatus.FAILED
            exp.completed_at = datetime.now().isoformat()
            if error_message:
                exp.error_message = error_message
            self._save_state()
    
    def mark_running(self, key: str):
        """Mark an experiment as running."""
        if key in self.state.experiments:
            exp = self.state.experiments[key]
            exp.status = ExperimentStatus.RUNNING
            exp.started_at = datetime.now().isoformat()
            self._save_state()
    
    # =========================================================================
    # Execution
    # =========================================================================
    
    def execute_key(
        self,
        key: str,
        executor: "Executor",
        restart: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a specific experiment.
        
        Args:
            key: The experiment key
            executor: Executor instance to run the training
            restart: If True, reset to PENDING before running
        
        Returns:
            Metrics dictionary if successful, None otherwise
        """
        if key not in self.state.experiments:
            print_error(f"Experiment '{key}' not found")
            return None
        
        if restart:
            self.reset_experiment(key)
        
        experiment = self.state.experiments[key]
        
        if experiment.status != ExperimentStatus.PENDING:
            print_warning(f"Experiment '{key}' is not PENDING (status: {experiment.status.value})")
            return None
        
        # Mark as running
        self.mark_running(key)
        
        print_progress(f"Starting experiment: {key}")
        
        # Execute
        exp_output_dir = self.output_dir / self.study_name / key
        result = executor.run(
            config=experiment.config,
            experiment_name=f"{self.study_name}_{key}",
            output_dir=exp_output_dir,
        )
        
        # Update state based on result
        experiment.duration_seconds = result.duration_seconds
        
        if result.success:
            experiment.status = ExperimentStatus.DONE
            experiment.metrics = result.metrics
            print_success(f"Experiment '{key}' completed")
        else:
            experiment.status = ExperimentStatus.FAILED
            experiment.error_message = result.error_message
            print_error(f"Experiment '{key}' failed: {result.error_message}")
        
        experiment.completed_at = datetime.now().isoformat()
        self._save_state()
        
        return result.metrics if result.success else None
    
    def execute_next(
        self,
        executor: "Executor",
    ) -> Optional[Dict[str, Any]]:
        """Execute the first pending experiment."""
        next_key = self.get_next_pending()
        if next_key is None:
            print_info("No pending experiments")
            return None
        return self.execute_key(next_key, executor)
    
    def execute_all(
        self,
        executor: "Executor",
        stop_on_failure: bool = False,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Execute all pending experiments.
        
        Args:
            executor: Executor instance
            stop_on_failure: If True, stop on first failure
        
        Returns:
            Dict of {key: metrics} for successful experiments
        """
        results = {}
        pending = self.get_pending_experiments()
        
        print_progress(f"Executing {len(pending)} pending experiments")
        
        for i, key in enumerate(pending):
            print_info(f"\n=== [{i+1}/{len(pending)}] {key} ===")
            
            metrics = self.execute_key(key, executor)
            
            if metrics is not None:
                results[key] = metrics
            elif stop_on_failure:
                print_warning("Stopping due to failure")
                break
        
        self.print_summary()
        return results
    
    # =========================================================================
    # Reporting
    # =========================================================================
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the study state."""
        status_counts = {s.value: 0 for s in ExperimentStatus}
        for exp in self.state.experiments.values():
            status_counts[exp.status.value] += 1
        
        return {
            "study_name": self.study_name,
            "state_file": str(self.state_file_path),
            "total_experiments": len(self.state.experiments),
            "status_counts": status_counts,
            "experiments": {k: v.status.value for k, v in self.state.experiments.items()}
        }
    
    def print_summary(self):
        """Print a formatted summary of the study."""
        summary = self.get_summary()
        
        print_info(f"\n{'='*60}")
        print_info(f"Study: {summary['study_name']}")
        print_info(f"{'='*60}")
        print_file(summary['state_file'], "State file")
        print_info(f"Total: {summary['total_experiments']} experiments")
        
        for status, count in summary['status_counts'].items():
            if count > 0:
                print_info(f"  {status}: {count}")
        
        print_info(f"{'='*60}\n")
    
    def export_config(self, key: str, output_path: Union[str, Path]):
        """Export a specific experiment config to a YAML file."""
        if key not in self.state.experiments:
            raise ValueError(f"Experiment '{key}' not found")
        
        config = self.state.experiments[key].config
        output_path = Path(output_path)
        self._save_yaml(output_path, config)
        print_file(str(output_path), f"Exported '{key}'")
    
    def get_config_diff(self, key1: str, key2: str) -> Dict[str, tuple]:
        """
        Get the differences between two experiment configs.
        
        Returns:
            Dict of {param_path: (value1, value2)} for differing values
        """
        if key1 not in self.state.experiments:
            raise ValueError(f"Experiment '{key1}' not found")
        if key2 not in self.state.experiments:
            raise ValueError(f"Experiment '{key2}' not found")
        
        config1 = self.state.experiments[key1].config
        config2 = self.state.experiments[key2].config
        
        diffs = {}
        
        def compare_recursive(c1: Any, c2: Any, path: str = ""):
            if isinstance(c1, dict) and isinstance(c2, dict):
                all_keys = set(c1.keys()) | set(c2.keys())
                for key in all_keys:
                    new_path = f"{path}.{key}" if path else key
                    v1 = c1.get(key)
                    v2 = c2.get(key)
                    compare_recursive(v1, v2, new_path)
            elif c1 != c2:
                diffs[path] = (c1, c2)
        
        compare_recursive(config1, config2)
        return diffs


# =========================================================================
# Convenience Functions
# =========================================================================

def load_study(state_file: Union[str, Path]) -> PrismManager:
    """
    Load an existing study from a .prism state file.
    
    Args:
        state_file: Path to the .prism state file
    
    Returns:
        PrismManager instance
    """
    state_file = Path(state_file)
    if not state_file.exists():
        raise FileNotFoundError(f"State file not found: {state_file}")
    
    with open(state_file, 'r') as f:
        data = json.load(f)
    
    state = PrismState.from_dict(data)
    
    manager = PrismManager(
        base_config_path=state.base_config_path,
        prism_config_path=state.prism_config_paths or None,
        study_name=state.study_name,
        output_dir=state_file.parent,
    )
    manager.state = state
    
    return manager


def list_studies(output_dir: Union[str, Path]) -> List[Dict[str, Any]]:
    """
    List all studies in an output directory.
    
    Args:
        output_dir: Directory to search for .prism files
    
    Returns:
        List of study info dictionaries
    """
    output_dir = Path(output_dir)
    studies = []
    
    if not output_dir.exists():
        return studies
    
    for prism_file in output_dir.glob("**/*.prism"):
        try:
            with open(prism_file) as f:
                data = json.load(f)
            
            experiments = data.get("experiments", {})
            status_counts = {"PENDING": 0, "RUNNING": 0, "DONE": 0, "FAILED": 0}
            for exp in experiments.values():
                status = exp.get("status", "PENDING")
                status_counts[status] = status_counts.get(status, 0) + 1
            
            studies.append({
                "name": data.get("study_name", prism_file.stem),
                "path": str(prism_file),
                "total": len(experiments),
                **status_counts,
                "updated_at": data.get("updated_at", ""),
            })
        except Exception:
            continue
    
    return studies
