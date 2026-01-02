import sys
import pytest
from dataclasses import field
from pydrafig import pydraclass, apply_overrides, main, run

@pydraclass
class Config:
    x: int = 1
    y: float = 1.0
    name: str = "default"
    items: list[int] = field(default_factory=list)

def test_apply_overrides_basic():
    config = Config()
    args = ["x=10", "y=2.5", "name='updated'"]
    apply_overrides(config, args)
    
    assert config.x == 10
    assert config.y == 2.5
    assert config.name == "updated"

def test_apply_overrides_expressions():
    config = Config()
    # Test math and list operations
    args = ["x=2+2", "items=[1, 2, 3]"]
    apply_overrides(config, args)
    
    assert config.x == 4
    assert config.items == [1, 2, 3]

def test_apply_overrides_nested():
    from dataclasses import field
    
    @pydraclass
    class Inner:
        val: int = 0
        
    @pydraclass
    class Outer:
        inner: Inner = field(default_factory=Inner)
        
    config = Outer()
    apply_overrides(config, ["inner.val=42"])
    assert config.inner.val == 42

def test_main_decorator(capsys):
    @pydraclass
    class MyConfig:
        val: int = 0

    @main(MyConfig)
    def app(cfg):
        print(f"Value: {cfg.val}")
        return cfg.val

    # Test execution
    result = app(["val=100"])
    assert result == 100
    
    out, _ = capsys.readouterr()
    assert "Value: 100" in out

def test_show_flag(capsys):
    @pydraclass
    class MyConfig:
        val: int = 0

    @main(MyConfig)
    def app(cfg):
        return "Executed"

    # --show should print config and NOT run function
    result = app(["val=99", "--show"])
    
    assert result is None
    out, _ = capsys.readouterr()
    assert "val: 99" in out

def test_run_function():
    @pydraclass
    class MyConfig:
        a: int = 1

    def task(cfg: MyConfig):
        return cfg.a * 2

    res = run(task, args=["a=21"])
    assert res == 42

def test_invalid_syntax():
    config = Config()
    with pytest.raises(SyntaxError):
        apply_overrides(config, ["invalid syntax here"])

def test_unknown_attribute():
    config = Config()
    # Should raise error because attribute validation happens during assignment
    # The exec() will try to set config.unknown = 1, which triggers __setattr__
    from pydrafig.base_config import InvalidConfigurationError
    with pytest.raises(InvalidConfigurationError):
        apply_overrides(config, ["unknown=1"])

