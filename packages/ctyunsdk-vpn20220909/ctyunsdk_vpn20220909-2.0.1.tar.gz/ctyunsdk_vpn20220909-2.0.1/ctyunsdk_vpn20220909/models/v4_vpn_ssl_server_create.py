from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnSslServerCreateRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    vpnServiceID: str  # VPN实例ID
    localSubnets: str  # 本端子网，如有多个子网由逗号分隔
    ipPoolSubnet: str  # 客户端地址池
    ipPoolMask: str  # 客户端地址池掩码长度，取值范围为16-29
    sslServerName: str  # SSL服务端名称
    sslPort: str  # 端口号,取值范围为:1024-4499,4501-49151
    enableDNS: Optional[bool] = None  # 是否开启DNS<br/>取值范围:<br/>false:不开启<br/>true:开启
    sslProtocol: Optional[str] = None  # SSL协议，只能填入tcp
    enableUDP: Optional[bool] = None  # 是否开启UDP,<br/>取值范围:<br/>false:不开启<br/>true:开启<br/>默认为false
    vpnGatewayID: Optional[str] = None  # vpn网关ID
    dns: Optional[str] = None  # DNS地址,当enableDNS取值为false时,不传入dns参数
    twoFactorVerify: Optional[bool] = None  # 是否开启双因子认证<br/>取值范围:<br/>false:不开启<br/>true:开启
    projectID: Optional[str] = None  # 企业项目ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnSslServerCreateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


