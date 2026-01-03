from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnSslClientCreateRequest(CtyunOpenAPIRequest):
    vpnServiceID: str  # VPN实例ID
    regionID: str  # 资源池ID
    sslClientName: str  # SSL客户端名称
    sslServerID: str  # vpn服务端uuid
    sslServerName: str  # SSL服务端名称
    upBandwidth: Optional[int] = None  # 上行带宽,单位为Kbps或Mbps
    downBandwidth: Optional[int] = None  # 下行带宽,单位为Kbps或Mbps
    isOnline: Optional[bool] = None  # 是否在线<br/>取值范围:<br/>false:不在线<br/>true:在线
    isLimitSpeed: Optional[bool] = None  # 是否限速<br/>取值范围:<br/>false:不限速<br/>true:限速
    vpnGatewayID: Optional[str] = None  # vpn网关ID
    projectID: Optional[str] = None  # 企业项目ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnSslClientCreateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


