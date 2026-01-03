from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnSslServerUpdateRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    vpnServiceID: str  # VPN实例ID
    sslServerID: str  # vpn服务端uuid
    localSubnets: str  # 本端子网，如有多个子网由逗号分隔
    ipPoolSubnet: str  # 客户端地址池
    ipPoolMask: str  # 客户端地址池掩码长度
    sslServerName: str  # SSL服务端名称
    enableDNS: Optional[bool] = None  # 是否开启DNS<br/>取值范围:<br/>false:不开启<br/>true:开启
    enableUDP: Optional[bool] = None  # 是否开启UDP<br/>取值范围:<br/>false:不开启<br/>true:开启<br/>默认为false
    dns: Optional[str] = None  # DNS地址

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnSslServerUpdateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


