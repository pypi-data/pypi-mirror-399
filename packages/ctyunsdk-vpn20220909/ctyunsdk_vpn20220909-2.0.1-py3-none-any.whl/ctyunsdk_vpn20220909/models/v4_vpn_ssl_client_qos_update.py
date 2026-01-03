from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnSslClientQosUpdateRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    sslClientID: str  # SSL客户端ID
    upBandwidth: int  # 上行带宽,单位为Kbps或Mbps
    downBandwidth: int  # 下行带宽,单位为Kbps或Mbps
    isLimitSpeed: Optional[bool] = None  # 是否限速<br/>取值范围:<br/>false:不限速<br/>true:限速

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnSslClientQosUpdateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


