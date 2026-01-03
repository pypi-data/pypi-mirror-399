"""
单文件示例：模拟 applab 的索引 + 按需安装 provider/app
- applab_registry：存放所有可安装的 provider 信息
- install_app()：模拟安装
- get_provider()：动态注册和加载
- QueryChoices：动态生成 UI 下拉
"""

from abc import ABC, abstractmethod
from typing import Annotated

from pydantic import BaseModel
from pydantic.dataclasses import dataclass

from applab.provider.base import ProviderRegister

# 全局注册表实例
providers = ProviderRegister()

# ============================================================
# Extension Point：Provider 抽象基类
# ============================================================


class Provider(ABC):
    """Extension Point: 所有 Provider 必须实现 login"""

    PROVIDER_NAME: str

    @abstractmethod
    def ping(self) -> None: ...


# ============================================================
# 模拟 applab_apps 包（provider 实现）
# ============================================================
class UIField:
    pass


@dataclass
class TextField(UIField):
    label: str
    help: str | None = None


class QCloudCredential(BaseModel):
    secret_id: Annotated[
        str,
        TextField(
            label="SecretId",
            help="Tencent Cloud API SecretId",
        ),
    ]

    secret_key: Annotated[str, UIField(label="SecretKey", widget="password", help="Tencent Cloud API SecretKey")]


# 模拟 qcloud.py
class QCloudProvider(Provider):
    PROVIDER_NAME = "Tencent Cloud"

    def ping(self):
        print("Login to QCloud")


# 模拟 aliyun.py
class AliyunProvider(Provider):
    PROVIDER_NAME = "Alibaba Cloud"

    def ping(self):
        print("Login to Aliyun")


# ============================================================
# 全局 Provider Registry（已安装的 provider）
# ============================================================

_PROVIDER_REGISTRY2: dict[str, Provider] = {
    "qcloud": QCloudProvider(),
    "aliyun": AliyunProvider(),
}  # 已安装的 provider


# ============================================================
# 使用示例
# ============================================================

if __name__ == "__main__":
    print("\n=== 使用 provider ===")
    provider = _PROVIDER_REGISTRY2["qcloud"]
    provider.ping()

    provider = _PROVIDER_REGISTRY2["aliyun"]
    provider.ping()
