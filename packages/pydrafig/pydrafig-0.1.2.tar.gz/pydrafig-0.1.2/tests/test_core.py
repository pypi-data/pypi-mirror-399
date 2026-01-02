import pytest
from dataclasses import field
from pydrafig import pydraclass, REQUIRED
from pydrafig.base_config import InvalidConfigurationError

@pydraclass
class SimpleConfig:
    lr: float = 0.01
    batch_size: int = 32
    name: str = "test"

@pydraclass
class NestedConfig:
    simple: SimpleConfig = field(default_factory=SimpleConfig)
    epochs: int = 10

def test_basic_config():
    config = SimpleConfig()
    assert config.lr == 0.01
    assert config.batch_size == 32
    assert config.name == "test"
    
    # Test valid update
    config.lr = 0.001
    assert config.lr == 0.001

def test_typo_detection():
    config = SimpleConfig()
    
    with pytest.raises(InvalidConfigurationError) as excinfo:
        config.learning_rate = 0.02
    
    msg = str(excinfo.value)
    assert "Invalid parameter 'learning_rate'" in msg
    # Should not suggest anything for 'learning_rate' vs 'lr' as distance is large, 
    # but let's test a closer typo
    
    with pytest.raises(InvalidConfigurationError) as excinfo:
        config.bacth_size = 64
    
    msg = str(excinfo.value)
    assert "Did you mean: 'batch_size'?" in msg

def test_nested_config():
    config = NestedConfig()
    assert config.simple.lr == 0.01
    
    config.simple.lr = 0.05
    assert config.simple.lr == 0.05

def test_required_field():
    @pydraclass
    class RequiredConfig:
        x: int = REQUIRED
        
    # Should probably raise error if accessed before set, or just allow it as sentinel?
    # The current implementation uses REQUIRED as a sentinel value.
    config = RequiredConfig()
    assert config.x == REQUIRED
    
    config.x = 10
    assert config.x == 10

def test_custom_finalize():
    @pydraclass
    class ValidatedConfig:
        x: int = 10
        y: int = 0
        sum: int = 0
        
        def custom_finalize(self):
            if self.x < 0:
                raise ValueError("x must be positive")
            self.sum = self.x + self.y

    config = ValidatedConfig(x=5, y=5)
    config.finalize()
    assert config.sum == 10
    
    bad_config = ValidatedConfig(x=-1)
    with pytest.raises(ValueError, match="x must be positive"):
        bad_config.finalize()

def test_recursive_finalize():
    @pydraclass
    class Leaf:
        val: int = 1
        doubled: int = 0
        def custom_finalize(self):
            self.doubled = self.val * 2

    @pydraclass
    class Node:
        leaf: Leaf = field(default_factory=Leaf)
        total: int = 0
        def custom_finalize(self):
            # Should have been finalized already
            self.total = self.leaf.doubled + 1

    config = Node()
    config.leaf.val = 5
    config.finalize()
    
    assert config.leaf.doubled == 10
    assert config.total == 11

def test_circular_dependency():
    @pydraclass
    class Node:
        child: 'Node' = None

    n1 = Node()
    n2 = Node()
    n1.child = n2
    n2.child = n1
    
    # Finalization should detect cycle
    with pytest.raises(ValueError, match="Circular reference detected"):
        n1.finalize()

def test_container_finalization():
    @pydraclass
    class Item:
        v: int = 1
        finalized: bool = False
        def custom_finalize(self):
            self.finalized = True

    @pydraclass
    class Container:
        items_list: list[Item] = field(default_factory=list)
        items_dict: dict[str, Item] = field(default_factory=dict)
    
    c = Container()
    c.items_list.append(Item())
    c.items_dict["k"] = Item()
    
    c.finalize()
    assert c.items_list[0].finalized
    assert c.items_dict["k"].finalized


def test_replace_basic():
    """Test basic replace functionality."""
    @pydraclass
    class OptimizerConfig:
        lr: float = 0.001
        name: str = "adam"

    @pydraclass
    class SGDConfig:
        lr: float = 0.01
        momentum: float = 0.9

    @pydraclass
    class TrainConfig:
        optimizer: OptimizerConfig | SGDConfig = field(default_factory=OptimizerConfig)
        epochs: int = 10

    config = TrainConfig()
    assert isinstance(config.optimizer, OptimizerConfig)
    
    # Replace with valid type by name and kwargs
    config.replace("optimizer", "SGDConfig", lr=0.05, momentum=0.95)
    assert config.optimizer.__class__.__name__ == "SGDConfig"
    assert config.optimizer.lr == 0.05
    assert config.optimizer.momentum == 0.95


def test_replace_invalid_type():
    """Test that replace rejects invalid class names."""
    @pydraclass
    class OptimizerConfig:
        lr: float = 0.001

    @pydraclass
    class SGDConfig:
        lr: float = 0.01

    @pydraclass
    class TrainConfig:
        optimizer: OptimizerConfig | SGDConfig = field(default_factory=OptimizerConfig)

    config = TrainConfig()
    
    # Try to replace with invalid class name
    with pytest.raises(ValueError) as excinfo:
        config.replace("optimizer", "InvalidClass")
    
    assert "not an allowed type" in str(excinfo.value)
    assert "OptimizerConfig" in str(excinfo.value) or "SGDConfig" in str(excinfo.value)


def test_replace_invalid_param_name():
    """Test that replace catches invalid parameter names."""
    config = SimpleConfig()
    
    with pytest.raises(InvalidConfigurationError) as excinfo:
        config.replace("unknown_param", "SomeClass")
    
    assert "Invalid parameter 'unknown_param'" in str(excinfo.value)


def test_replace_with_typo_suggestion():
    """Test that replace suggests correct parameter names for typos."""
    @pydraclass
    class ConfigWithField:
        batch_size: int = 32

    config = ConfigWithField()
    
    with pytest.raises(InvalidConfigurationError) as excinfo:
        config.replace("bacth_size", "int")
    
    assert "Did you mean: 'batch_size'?" in str(excinfo.value)


def test_replace_with_kwargs():
    """Test replace passes kwargs to constructor."""
    @pydraclass
    class ConfigA:
        x: int = 1
        y: str = "default"

    @pydraclass
    class ConfigB:
        x: int = 2
        y: str = "other"

    @pydraclass
    class Parent:
        child: ConfigA | ConfigB = field(default_factory=ConfigA)

    config = Parent()
    
    # Replace with specific kwargs
    config.replace("child", "ConfigB", x=100, y="custom")
    assert config.child.__class__.__name__ == "ConfigB"
    assert config.child.x == 100
    assert config.child.y == "custom"


def test_replace_invalid_kwargs():
    """Test replace with invalid kwargs raises TypeError."""
    @pydraclass
    class ConfigA:
        x: int = 1

    @pydraclass
    class Parent:
        child: ConfigA = field(default_factory=ConfigA)

    config = Parent()
    
    # Try to replace with invalid kwarg
    with pytest.raises(TypeError) as excinfo:
        config.replace("child", "ConfigA", nonexistent_param=42)
    
    assert "Failed to instantiate" in str(excinfo.value)

