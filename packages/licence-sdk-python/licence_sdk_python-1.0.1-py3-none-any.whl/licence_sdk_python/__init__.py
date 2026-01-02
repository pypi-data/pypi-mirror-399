"""
Licence SDK Python

授权验证 SDK，用于验证应用授权状态

使用 RSA-SHA256 非对称加密进行签名验证：
- 私钥：仅存在于授权服务中，用于签名
- 公钥：硬编码在此 SDK 中，用于验证签名

即使公钥被公开，也无法伪造有效的授权签名。
"""

__version__ = "1.0.0"

# ============================================================================
# 核心功能
# ============================================================================

from .check import (
    check_licence,
    check_licence_sync,
    is_licenced,
    get_licence_state,
    clear_licence_cache,
    set_licence_state,
)

from .verify import verify_signature

# ============================================================================
# 机器码/设备指纹
# ============================================================================

from .fingerprint import (
    get_fingerprint,
    get_fingerprint_sync,
    check_service_health,
    check_service_health_sync,
    get_service_version,
    get_service_version_sync,
)

# ============================================================================
# 数据过滤
# ============================================================================

from .filter import (
    filter_data,
    is_feature_enabled,
    get_data_limit_info,
    set_free_features,
    set_default_data_limit,
)

# ============================================================================
# API 保护装饰器
# ============================================================================

from .decorators import (
    licence_required,
    licence_required_async,
)

# ============================================================================
# 类型定义
# ============================================================================

from .types import (
    LicenceResult,
    LicenceState,
    LicenceServiceResponse,
    LicenceServiceData,
    FingerprintResult,
    DataLimitInfo,
    LicenceStatus,
)

from .public_key import (
    LICENCE_PUBLIC_KEY,
    is_public_key_configured,
)


# 公开的 API
__all__ = [
    # 版本
    "__version__",
    # 核心功能
    "check_licence",
    "check_licence_sync",
    "is_licenced",
    "get_licence_state",
    "clear_licence_cache",
    "set_licence_state",
    "verify_signature",
    # 机器码/设备指纹
    "get_fingerprint",
    "get_fingerprint_sync",
    "check_service_health",
    "check_service_health_sync",
    "get_service_version",
    "get_service_version_sync",
    # 数据过滤
    "filter_data",
    "is_feature_enabled",
    "get_data_limit_info",
    "set_free_features",
    "set_default_data_limit",
    # API 保护装饰器
    "licence_required",
    "licence_required_async",
    # 类型定义
    "LicenceResult",
    "LicenceState",
    "LicenceServiceResponse",
    "LicenceServiceData",
    "FingerprintResult",
    "DataLimitInfo",
    "LicenceStatus",
    # 公钥
    "LICENCE_PUBLIC_KEY",
    "is_public_key_configured",
]
