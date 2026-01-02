import os
import pytest
import yaml
import pickle
import dill
from dataclasses import field
from pydrafig import pydraclass

@pydraclass
class SubConfig:
    s: str = "sub"

@pydraclass
class MainConfig:
    i: int = 1
    f: float = 2.0
    sub: SubConfig = field(default_factory=SubConfig)
    lst: list[int] = field(default_factory=lambda: [1, 2])
    dct: dict[str, int] = field(default_factory=lambda: {"a": 1})

def test_to_dict():
    cfg = MainConfig()
    d = cfg.to_dict()
    
    assert d['i'] == 1
    assert d['sub']['s'] == "sub"
    assert d['lst'] == [1, 2]
    
def test_yaml_compatible():
    # Helper to check if type is simple
    cfg = MainConfig()
    d = cfg.to_dict(yaml_compatible=True)
    
    # Should be pure python types
    assert isinstance(d['sub'], dict)
    
def test_save_load_yaml(tmp_path):
    cfg = MainConfig()
    cfg.i = 99
    cfg.sub.s = "changed"
    
    p = tmp_path / "config.yaml"
    cfg.save_yaml(p)
    
    assert p.exists()
    
    with open(p, 'r') as f:
        data = yaml.safe_load(f)
        
    assert data['i'] == 99
    assert data['sub']['s'] == "changed"

def test_save_load_pickle(tmp_path):
    cfg = MainConfig()
    cfg.i = 123
    
    p = tmp_path / "config.pkl"
    cfg.save_pickle(p)
    
    with open(p, 'rb') as f:
        loaded = pickle.load(f)
        
    assert loaded.i == 123
    assert isinstance(loaded, MainConfig)

def test_save_load_dill(tmp_path):
    cfg = MainConfig()
    cfg.i = 456
    
    p = tmp_path / "config.dill"
    cfg.save_dill(p)
    
    with open(p, 'rb') as f:
        loaded = dill.load(f)
        
    assert loaded.i == 456
    assert isinstance(loaded, MainConfig)

