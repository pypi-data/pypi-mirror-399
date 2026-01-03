# EasySweeps

A CLI tool for automating Weights & Biases sweeps across multiple GPUs.

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/easysweeps)](https://badge.fury.io/py/easysweeps)
[![PyPI version](https://badge.fury.io/py/easysweeps.svg)](https://badge.fury.io/py/easysweeps)
[![Downloads](https://pepy.tech/badge/easysweeps)](https://pepy.tech/project/easysweeps)

## Why EasySweeps?

W&B is great for experiment tracking, but managing sweeps at scale has pain points:

- **Repetitive setup** – Launching sweeps across datasets requires manual duplication
- **Limited agent control** – No built-in way to stop agents by GPU or sweep
<!-- - **Code consistency** – Agents run the latest code, which can break ongoing sweeps -->
- **Manual management** – Multi-GPU sweep orchestration requires custom scripts

EasySweeps solves these by providing simple commands to create, launch, monitor, and manage sweep agents.

## Installation

```bash
pip install easysweeps
```

**Requirements:** Python 3.7+, W&B account, CUDA GPUs (optional)

## Quick Start

```bash
# Initialize project
ez init

# Edit ez_config.yaml with your W&B entity/project

# Create sweeps from template
ez sweep

# Launch agents
ez agent <SWEEP_ID> --gpu-list 0 1 2

# Monitor status
ez status

# Kill agents when done
ez kill --sweep <SWEEP_ID>
```

## Configuration

After running `ez init`, edit `ez_config.yaml`:

```yaml
sweep_dir: "sweeps"          # Directory for sweep configs
agent_log_dir: "agent_logs"  # Directory for agent logs
entity: "your_entity"        # W&B entity (null = default)
project: "your_project"      # W&B project name
```

## Commands

### `ez init`
Scaffolds project structure with config file and example templates.

### `ez sweep`
Creates W&B sweeps from a template and variants file.

**Template** (`sweeps/sweep_template.yaml`):
```yaml
name: "example_{dataset}"
method: "grid"
metric:
  name: "loss"
  goal: "minimize"
parameters:
  learning_rate:
    values: [0.001, 0.01]
  dataset:
    value: None  # Replaced by variants
program: "train.py"
```

**Variants** (`sweeps/sweep_variants.yaml`):
```yaml
dataset: ['mnist', 'cifar10']  # Creates one sweep per dataset
```

### `ez agent`
Launches sweep agents on specified GPUs as systemd scope units.

```bash
ez agent                                # List available sweeps
ez agent abc123 --gpu-list 0 1 2        # Launch on GPUs 0,1,2
ez agent abc123 --gpu-list 0 --agents-per-sweep 3  # 3 agents on GPU 0
```

### `ez status`
Shows all sweeps and running agents with GPU assignments and runtime.

### `ez kill`
Stops running agents with flexible targeting.

```bash
ez kill                         # List active sweeps
ez kill --force                 # Kill all agents
ez kill --gpu 0                 # Kill agents on GPU 0
ez kill --sweep abc123          # Kill agents for specific sweep
ez kill --sweep abc123 --gpu 0  # Target specific sweep + GPU
```

## Project Copying (Optional)

Enable in `ez_config.yaml` to run agents in isolated code copies:

```yaml
enable_project_copy: true
project_copy_base_dir: "~/wandb_projects"
```

This prevents code changes from affecting running experiments. Use `--force-recopy` to refresh copies.

## Authors

Created by [Yaniv Galron](https://github.com/YanivDorGalron)  
Contributors: [Hadar Sinai](https://github.com/hadarsi320), [Ron Tohar](https://github.com/rontohar1)

## License

MIT License - see [LICENSE](LICENSE) for details.

---

⭐ If you find this helpful, a star would be appreciated!
