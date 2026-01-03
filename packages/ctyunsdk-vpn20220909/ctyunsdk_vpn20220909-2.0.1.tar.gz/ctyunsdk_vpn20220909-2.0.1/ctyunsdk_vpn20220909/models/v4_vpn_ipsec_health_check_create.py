from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnIpsecHealthCheckCreateRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    vpnConnectionID: str  # vpn connection id
    sourceIP: str  # 源IP
    targetIP: str  # 目的IP
    enableHealth: bool  # 是否启用健康检查
    detectTime: int  # 探测时间，单位S，取值范围:[1~120]
    detectNumber: int  # 探测次数，取值范围:[1~50]
    dropThreshold: int  # 异常阈值，单位百分比，取值范围:[1~100]
    routeNotify: bool  # 是否关联路由

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnIpsecHealthCheckCreateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


