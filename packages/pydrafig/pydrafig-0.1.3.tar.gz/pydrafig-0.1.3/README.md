# pydrafig

A dataclass-based configuration system with strict validation, automatic finalization, and enhanced CLI parsing. It is heavily inspired by [pydra](https://github.com/jordan-benjamin/pydra).

## Features

- **Dataclass with perks**: `@pydraclass` is a wrapper around standard Python `@dataclass`, adding extra functionality while preserving standard behavior.
- **Strict attribute validation**: Catches typos with helpful error messages
- **Type-safe replacement**: Replace nested configs with type validation against annotations
- **Recursive finalization**: Automatically finalizes all nested configs (including those in lists/dicts/tuples)
- **Enhanced CLI parsing**: Full Python expression support (including `numpy`, `torch`, etc.)
- **Serialization**: Export to dict/YAML/pickle/dill
- **Type hints**: Full IDE support with autocomplete

## Quick Start

### Basic Config

```python
from pydrafig import pydraclass
from dataclasses import field

@pydraclass
class TrainConfig:
    learning_rate: float = 0.001
    batch_size: int = 32
    epochs: int = 10

config = TrainConfig()
config.learning_rate = 0.01  # ✅ Valid
config.learning_rat = 0.01   # ❌ Raises InvalidConfigurationError with suggestion
```

### Nested Configs

```python
@pydraclass
class OptimizerConfig:
    name: str = "adam"
    lr: float = 0.001

@pydraclass
class ModelConfig:
    hidden_size: int = 128
    optimizer: OptimizerConfig = field(default_factory=OptimizerConfig)

config = ModelConfig()
config.optimizer.lr = 0.01
```

**Important**: Use `field(default_factory=ConfigClass)` for nested configs to avoid shared instances!

### Replacing Nested Configs

When you have a parameter that accepts multiple config types (using Union types), you can use `replace()` to swap it with a different type:

```python
@pydraclass
class AdamConfig:
    lr: float = 0.001
    betas: tuple = (0.9, 0.999)

@pydraclass
class SGDConfig:
    lr: float = 0.01
    momentum: float = 0.9

@pydraclass
class TrainConfig:
    optimizer: AdamConfig | SGDConfig = field(default_factory=AdamConfig)
    epochs: int = 10

config = TrainConfig()
print(config.optimizer)  # AdamConfig(lr=0.001, betas=(0.9, 0.999))

# Replace with a different optimizer type
config.replace("optimizer", "SGDConfig", lr=0.05, momentum=0.95)
print(config.optimizer)  # SGDConfig(lr=0.05, momentum=0.95)
```

The `replace()` method:
1. Takes the parameter name and the class name (as a string)
2. Validates that the class is in the list of allowed types from the type annotation
3. Instantiates the class with any provided `**kwargs`
4. Assigns the new instance to the parameter

```python
# These work:
config.replace("optimizer", "AdamConfig")  # Use defaults
config.replace("optimizer", "SGDConfig", lr=0.1)  # With kwargs

# This raises ValueError - InvalidOptimizer is not in the type annotation:
config.replace("optimizer", "InvalidOptimizer")
```

### Finalization

Configs support a `custom_finalize()` hook for custom validation:

```python
@pydraclass
class Config:
    batch_size: int = 32
    max_batch_size: int = 128

    def custom_finalize(self):
        if self.batch_size > self.max_batch_size:
            raise ValueError("batch_size exceeds max_batch_size")

config = Config()
config.batch_size = 256
config.finalize()  # Raises ValueError
```

The `finalize()` method automatically:
1. Recursively finalizes all nested configs (even in lists/dicts/tuples)
2. Calls your custom `custom_finalize()` hook
3. Marks the config as finalized

### CLI Usage

```python
from pydrafig import main

@pydraclass
class TrainConfig:
    learning_rate: float = 0.001
    batch_size: int = 32

@main(TrainConfig)
def train(config: TrainConfig):
    print(f"Training with lr={config.learning_rate}, batch_size={config.batch_size}")

if __name__ == "__main__":
    train()  # Automatically parses CLI args
```

Run with:
```bash
# Use defaults
python train.py

# Override single values
python train.py learning_rate=0.01 batch_size=64

# Use complex Python literals (lists, dicts, tuples, etc.)
python train.py 'layers=[64,128,256]' 'params={"dropout":0.1}'

# Show config without running
python train.py --show learning_rate=0.01

# Nested configs
python train.py optimizer.lr=0.01 optimizer.weight_decay=1e-4
```

## CLI Expression Evaluation

The CLI parser supports full Python expression evaluation using `exec()`:

```bash
# Basic values work directly
python train.py learning_rate=0.01

# Complex expressions are evaluated
python train.py 'layers=[64, 128, 256]' \
                'params={"dropout": 0.1}' \
                'hidden_size=2**8' \
                'threshold=math.sqrt(2)'
```

The execution environment includes standard Python types (`list`, `dict`, `int`, `float`, etc.) and common math libraries (`math`, `numpy` (as `np`), `torch`) if installed.

> **Note**: Because this uses `exec()`, only run configs from trusted sources.

## API Reference

### @pydraclass

Decorator that creates a strict, auto-finalizing config class.

```python
@pydraclass
class MyConfig:
    param: type = default_value
```

### ConfigMeta Methods

All `@pydraclass` decorated classes have these methods:

- `finalize()`: Recursively finalize all nested configs, then call `custom_finalize()`
- `custom_finalize()`: User-defined hook for custom validation (override this)
- `replace(param_name, class_name, **kwargs)`: Replace a parameter with a new instance of an allowed type
- `to_dict()`: Convert config to dictionary
- `save_yaml(path)`: Save config to YAML file
- `save_pickle(path)`: Save config to pickle file
- `save_dill(path)`: Save config to dill file

### CLI Functions

- `main(ConfigClass)`: Decorator for main functions that take a config argument
- `run(fn)`: Run a function with config parsed from CLI (infers config type from annotation)
- `apply_overrides(config, args)`: Manually apply CLI overrides to a config

## Examples

See the `examples/` directory for full usage examples.

## Files

- `base_config.py` - Core `@pydraclass` decorator and `ConfigMeta` class
- `cli.py` - CLI parsing logic using `exec()`

