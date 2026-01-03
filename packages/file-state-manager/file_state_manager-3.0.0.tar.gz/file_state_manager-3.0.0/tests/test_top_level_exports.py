import importlib
import pytest

# パッケージのトップレベル __all__
from file_state_manager import __all__ as top_level_all

@pytest.mark.parametrize("name", top_level_all)
def test_top_level_imports(name):
    """
    __init__.py で定義されたトップレベル __all__ に含まれる
    名前が実際に import できるか確認する
    """
    module = importlib.import_module("file_state_manager")
    assert hasattr(module, name), f"'{name}' is not accessible at top level"
