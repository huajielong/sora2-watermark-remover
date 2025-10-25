# 为较旧版本的Python提供StrEnum的兼容性实现
try:
    from enum import StrEnum
except ImportError:
    from enum import Enum

    class StrEnum(str, Enum):
        """为Python 3.11之前版本提供的StrEnum兼容类"""
        pass

from pydantic import BaseModel


class Status(StrEnum):
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    FINISHED = "FINISHED"
    ERROR = "ERROR"


class WMRemoveResults(BaseModel):
    percentage: int
    status: Status
    download_url: str | None = None
