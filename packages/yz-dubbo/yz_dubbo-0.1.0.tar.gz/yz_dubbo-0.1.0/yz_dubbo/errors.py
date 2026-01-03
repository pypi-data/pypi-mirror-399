"""
错误定义与错误码映射
"""

from enum import Enum
from typing import Any, Dict, Optional


class ErrorCode(str, Enum):
    """Dubbo 错误码枚举 (与 JS 版本保持一致)"""

    ERR_TIMEOUT = "ERR_TIMEOUT"
    ERR_NETWORK_ERROR = "ERR_NETWORK_ERROR"


class ErrorLevel(str, Enum):
    """错误级别"""

    FATAL = "fatal"
    ERROR = "error"
    WARN = "warn"


class DubboError(Exception):
    """Dubbo 调用异常基类"""

    def __init__(
        self,
        code: ErrorCode,
        message: str,
        level: ErrorLevel = ErrorLevel.ERROR,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        初始化 Dubbo 异常

        Args:
            code: 错误码
            message: 错误信息
            level: 错误级别
            context: 上下文信息 (service, method 等)
        """
        self.code = code
        self.message = message
        self.level = level
        self.context = context or {}
        super().__init__(f"[{code}] {message}")

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "code": self.code,
            "message": self.message,
            "level": self.level,
            "context": self.context,
        }


class ErrorMapper:
    """错误码映射器"""

    # Dubbo 状态码映射 (参考 JS 实现)
    STATUS_TO_ERROR_CODE = {
        30: ErrorCode.ERR_TIMEOUT,  # CLIENT_TIMEOUT
        31: ErrorCode.ERR_TIMEOUT,  # SERVER_TIMEOUT
    }

    @classmethod
    def map_from_status(cls, status_code: int) -> ErrorCode:
        """
        从 Dubbo 状态码映射错误码

        Args:
            status_code: Dubbo 响应状态码

        Returns:
            对应的错误码
        """
        return cls.STATUS_TO_ERROR_CODE.get(status_code, ErrorCode.ERR_INTERNAL_SERVER_ERROR)

    @classmethod
    def map_from_exception(cls, exc: Exception) -> ErrorCode:
        """
        从异常文本推断错误码

        Args:
            exc: 捕获的异常

        Returns:
            推断的错误码
        """
        error_msg = str(exc).lower()

        # 超时错误
        if "timeout" in error_msg or "timed out" in error_msg:
            return ErrorCode.ERR_TIMEOUT

        # 参数类型错误
        if "numberformatexception" in error_msg or "type error" in error_msg:
            return ErrorCode.ERR_PARAMS_TYPE_ERROR

        # 连接错误
        if "connection" in error_msg or "network" in error_msg:
            return ErrorCode.ERR_NETWORK_ERROR

        # 默认内部错误
        return ErrorCode.ERR_INTERNAL_SERVER_ERROR
