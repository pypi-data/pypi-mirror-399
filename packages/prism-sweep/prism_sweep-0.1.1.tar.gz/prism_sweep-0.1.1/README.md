# 🔬 PRISM - Parameter Research & Investigation Sweep Manager

[![PyPI version](https://badge.fury.io/py/prism-sweep.svg)](https://badge.fury.io/py/prism-sweep)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

PRISM is a simple tool to run **parameter sweeps** for ML experiments. Give it a base config and a sweep definition, and it will generate, validate, and execute all experiment variations.

## What is PRISM?

PRISM takes your base experiment configuration and creates multiple variations by changing specific parameters. It then:
1. Validates each configuration using your custom Python validator
2. Runs your training script with each validated config
3. Tracks progress and captures metrics
4. Provides an interactive TUI to monitor experiments

## Installation

### From pip

```bash
pip install prism-sweep
```

### From Source

```bash
git clone https://github.com/FrancescoCorrenti/prism-sweep.git
cd prism-sweep
pip install -e .
```

After installation, you can use `prism_tui` or `prism` commands from anywhere.

---

## Quick Start Guide

### Using the Interactive TUI (Recommended)

The easiest way to use PRISM is through the interactive terminal interface:

<!-- liv gif : -->
![prism_tui_demo](docs\live-tutorial.gif)

This example uses this directory structure:

```
iris-project/
├── configs/
│   ├── prism/
│   │   └── kernels.prism.yaml
│   └── base-config.yaml
├── iris/
│   └── Iris.csv
└── train.py
```

Prism will then generate:
```
iris-project/
├── outputs/
│   ├── kernels/
│   │   ├── kern_linear/
│   │   │   └── config.yaml
│   │   ├── kern_poly/
│   │   │   └── config.yaml
│   │   └── kern_rbf/
│   │   │   └── config.yaml
│   └── kernels.study.json
└── prism.project.yaml

### Using the Command Line

For automation and scripting, use the CLI:

```bash
# Create a study from base config and sweep definition
prism create --base configs/base.yaml \
             --prism configs/prism/lr_sweep.prism.yaml \
             --name lr_experiment

# Run all experiments in the study
prism run lr_experiment --all

# Run specific experiments
prism run lr_experiment lr_low lr_mid

# Check study status
prism status lr_experiment

# List all studies
prism list

# Retry failed experiments
prism retry lr_experiment
```

---

## What Files Do I Need?

PRISM needs 4-5 files in your project:

### 1. **prism.project.yaml** (Project Configuration)

This tells PRISM where everything is. The TUI can create this for you, or create it manually:

```yaml
# PRISM Project Configuration
project:
  name: "iris"
  version: "1.0.0"

paths:
  train_script: "train.py"
  configs_dir: "configs"
  prism_configs_dir: "configs/prism"
  output_dir: "outputs"

metrics:
  output_mode: "stdout_json"
  output_file: "metrics.json"
```

### 2. **Configuration File** (e.g., `configs/*.yaml`)

Your experiment's default configuration:

```yaml
C: 1
sigma: 0.5
kernel: "rbf"
# Other parameters... 
# You can use nested structures too, prism supports full YAML syntax.
```

You can have multiple base configs. Each time you create a study, you will have to specify which base config to use.

### 3. **Sweep Definition** (e.g., `configs/prism/*.prism.yaml`)

This is the core of PRISM. It defines which parameters to vary and how:

```yaml
kernel: 
  $kern_rbf: "rbf"
  $kern_linear: "linear"
  $kern_poly: "poly"
```

More examples of sweep definitions are provided at the end of this README.

### 4. **Custom Validator** (Optional: `configs/validator.py`)

Validates configs before training.

PRISM will call a `validate(config_dict)` function (or a `ConfigValidator` class) **right before launching** your training script. The input is the fully-expanded YAML config as a plain Python `dict`.

Configure it in `prism.project.yaml` (path is relative to project root):

```yaml
validator:
  module: "configs/validator.py"
```
You can use this to catch invalid configurations early, before wasting time and resources on training.
- Cross-field validation
- Set default values
- Convert enums, paths, etc.
```python
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class ExperimentConfig:
    learning_rate: float
    batch_size: int
    epochs: int
    
    def validate(self):
        if self.learning_rate <= 0:
            raise ValueError("Learning rate must be > 0")
        if self.batch_size < 1:
            raise ValueError("Batch size must be >= 1")

def validate(config_dict: Dict[str, Any]) -> ExperimentConfig:
    """Called by PRISM to validate each config."""
    config = ExperimentConfig(
        learning_rate=config_dict.get('learning_rate', 0.001),
        batch_size=config_dict.get('batch_size', 32),
        epochs=config_dict.get('epochs', 100)
    )
    config.validate()
    return config
```
  Return value:
  - Recommended: return a `dict` (it will be written to `config.yaml` for the experiment).
  - Also supported: return a `dataclass` instance (PRISM will convert it to a `dict`), or an object with `to_dict()` / `__dict__`.

  Failure behavior:
  - If `validate(...)` raises an exception (e.g. `ValueError`), the experiment is marked as failed with `Config validation failed: ...`.

### 5. **Training Script** (e.g., `train.py`)

Make sure it accepts a `--config` argument:

```python
# scripts/train.py
import argparse
import yaml
import json

parser = argparse.ArgumentParser()
parser.add_argument('--config', required=True)
args = parser.parse_args()

with open(args.config) as f:
    config = yaml.safe_load(f)

# Train your model...
learning_rate = config['learning_rate']
# ...

# Print metrics for PRISM
print(json.dumps({"loss": 0.123, "accuracy": 0.95}))
```

---

## Sweep Definition Syntax

Notes:
- PRISM only treats these as sweep syntax:
 - `$`-named experiments 
 - lists of values
 - `_type`/`_*` sweep definitions.
- Do not mix `$`-named experiments with positional sweeps (lists / `_type`) in the same `.prism.yaml`. If you need both, split them into multiple prism files.
- All overridden parameter paths must already exist in the base config (helps catch typos early).

### Named Experiments (`$` notation)

```yaml
# Creates experiments with custom names.
# Same $name across multiple parameters belongs to the same experiment.
model:
  size:
    $small_model: small
    $large_model: large
  layers:
    $small_model: 12
    $large_model: 24
```

Creates experiments: `small_model`, `large_model`

### Positional Parameters (Lists)

```yaml
# Creates experiments run_0, run_1, run_2
batch_size: [16, 32, 64]
learning_rate: [0.01, 0.001, 0.0001]
```
- `run_0`: batch_size=16, lr=0.01
- `run_1`: batch_size=32, lr=0.001  
- `run_2`: batch_size=64, lr=0.0001

### Sweep Definitions (Advanced)

```yaml
# Choice sweep
optimizer:
  lr:
    _type: choice
    _values: [0.001, 0.01, 0.1]

# Range sweep
epochs:
  _type: range
  _min: 10
  _max: 100
  _step: 10

# Linspace sweep
momentum:
  _type: linspace
  _min: 0.0
  _max: 0.99
  _num: 5
```

### Multiple Files (Cartesian Product)

```bash
prism create --base base.yaml \
             --prism models.yaml \
             --prism optimizers.yaml \
             --name model_opt_sweep
```
If `models.yaml` has 3 variations and `optimizers.yaml` has 2, you get 3×2=6 experiments.

### Complete Example

Base config (`configs/base.yaml`):
```yaml
optimizer:
  type: adam
  lr: 0.001
  weight_decay: 0.0001
model:
  backbone: resnet50
  hidden_dim: 512
```

Sweep config (`configs/prism/lr_sweep.prism.yaml`):
```yaml
optimizer:
  lr:
    $lr_low: 0.0001
    $lr_mid: 0.001
    $lr_high: 0.01
```

This creates 3 experiments:
- `lr_low`: with optimizer.lr = 0.0001
- `lr_mid`: with optimizer.lr = 0.001  
- `lr_high`: with optimizer.lr = 0.01

All other parameters stay the same from base config.

---

## Metrics Capture

PRISM can capture metrics in three ways:

### 1. JSON stdout (default)

Your training script prints JSON:
```python
import json
print(json.dumps({"loss": 0.5, "accuracy": 0.92}))
```

### 2. File output

```yaml
# In prism.project.yaml
metrics:
  output_mode: file
  output_file: metrics.json
```

Your script writes `metrics.json` in the output directory.

### 3. Exit code only

```yaml
metrics:
  output_mode: exit_code
```
PRISM only checks if the script succeeded (exit code 0).

---

## Advanced Features

### Custom Train Arguments

You can customize how PRISM calls your training script:

```yaml
# In prism.project.yaml  
paths:
  train_script: scripts/train.py
  train_args:
    - --config
    - "{config_path}"
    - --gpu
    - "0"
```

### Resume Failed Experiments

```bash
prism retry study_name
```
Or in TUI: Study Menu → Retry Failed

---

## Tips

1. **Start small**: Test with 2-3 experiments before scaling up
2. **Use the TUI**: It's much easier than CLI for exploration  
3. **Validate early**: Run one experiment manually before creating a big sweep
5. **Check metrics**: Make sure your training script prints/writes them correctly

---

## Troubleshooting

**"No train_script defined"**
→ Add `paths.train_script: scripts/train.py` to `prism.project.yaml`

**"Validator module not found"**  
→ Check the path in `validator.module` is correct relative to project root

**"Config validation failed"**
→ Check your `validate()` function - it's rejecting the config

**Experiments hang at "Testing data loading"**
→ Fixed! Make sure you have latest version with `PYTHONUNBUFFERED=1`

→ Fixed! Latest version forces colors with `FORCE_COLOR=1`

---
- Python 3.8+
- `pyyaml`
- `rich` (for TUI)
That's it! No other dependencies.

---
- **Organized**: Never lose track of which experiment used which parameters
- **Validated**: Catch config errors before training starts
- **Interactive**: TUI makes it easy to monitor and manage experiments

Ready to start? Run `prism_tui` and follow the prompts!  
