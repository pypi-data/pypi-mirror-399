import importlib
import os
from types import SimpleNamespace


_settings = None


DEFAULTS = {
    "DATABASE_NAME": ":memory:",
    "DATABASE_ENGINE": "sqlite",
}


def get_settings():
    """
    加载外部 settings 模块，参考 Django：
    - 优先读取环境变量 ASYNC_DRF_API_SETTINGS_MODULE
    - 否则默认使用 'settings'（即项目根目录下的 settings.py）
    """
    global _settings
    if _settings is not None:
        return _settings

    module_path = os.getenv("ASYNC_DRF_API_SETTINGS_MODULE", "settings")
    print(module_path,3333)
    try:
        mod = importlib.import_module(module_path)
    except ImportError:
        # 没有提供外部 settings 时，使用默认配置
        mod = SimpleNamespace()

    data = {**DEFAULTS}

    for key in DEFAULTS.keys():
        if hasattr(mod, key):
            data[key] = getattr(mod, key)

    _settings = SimpleNamespace(**data)
    return _settings


