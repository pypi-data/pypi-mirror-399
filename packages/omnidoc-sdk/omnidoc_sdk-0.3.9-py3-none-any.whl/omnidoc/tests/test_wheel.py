import omnidoc
import pkgutil

def test_all_submodules_present():
    modules = [m.name for m in pkgutil.iter_modules(omnidoc.__path__)]
    assert "pdf" in modules
    assert "cli" in modules
    assert "adapters" in modules
