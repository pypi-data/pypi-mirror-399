from collections.abc import Mapping
from typing import List, Type


class ProviderBase:
    # 类属性（不可变字段）
    name: str = "base"
    version: str = "0.0.1"

    def __init__(self):
        # 实例属性（可变字段）
        self.capabilities: List[str] = []
        self.recipes: List[str] = []

    def info(self) -> dict:
        """返回 provider 信息字典"""
        return {"name": self.name, "version": self.version, "capabilities": self.capabilities, "recipes": self.recipes}


class ProviderRegister(Mapping):
    """只读 Provider 注册表"""

    def __init__(self):
        self._registry: dict[str, Type[ProviderBase]] = {}
        self._registry2: dict[str, ProviderBase] = {}

    def register(self, provider_cls: Type[ProviderBase]):
        """注册 Provider 类"""
        self._registry[provider_cls.name] = provider_cls

    # Mapping 接口
    def __getitem__(self, key):
        return self._registry[key]

    def __iter__(self):
        return iter(self._registry)

    def __len__(self):
        return len(self._registry)

    # 便捷方法
    def list_all(self) -> list[str]:
        return list(self._registry.keys())

    def info(self, name: str) -> dict:
        cls = self._registry[name]
        return cls().info()
