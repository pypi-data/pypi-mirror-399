from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class IntegrationErrorType(str, Enum):
    AUTHENTICATION_ERROR = "authentication_error"
    NETWORK_ERROR = "network_error"
    TIMEOUT_ERROR = "timeout_error"
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    NOT_CONFIGURED = "not_configured"
    PENDING = "pending"
    MISSING_DATA = "missing_data"
    UNKNOWN_ERROR = "unknown_error"


class IntegrationErrorDetail(BaseModel):
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of the last update attempt")
    message: Optional[str] = Field(None, description="Error message describing the issue")
    type: str = Field(default=IntegrationErrorType.UNKNOWN_ERROR.value, description="Type of error encountered")
    upstream_status_code: Optional[int] = Field(None, description="HTTP status code from the upstream service, if applicable")

    @classmethod
    def prepare_detail(
        cls,
        message: str,
        error_type: Optional[IntegrationErrorType] = None,
        upstream_status_code: Optional[int] = None,
    ) -> "IntegrationErrorDetail":
        kwargs = {"message": message, "upstream_status_code": upstream_status_code}
        if error_type:
            kwargs["type"] = error_type.value
        return cls(**kwargs)
