from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnVpnGatewayUpgradeRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    vpnType: str  # VPN网关类型，取值范围:<br/>[1,2]<br/>1为IPSEC类型VPN，2为SSL类型VPN
    bandwidth: str  # 带宽，单位为Mbps，取值为：["5","10","20","50","100","200","500","1000"]
    connectionLimit: str  # VPN网关连接数限制<br/>当vpnType为1时，取值为：["10","20","30","40","50","100"]<br/>当vpnType为2时，取值为：["5","10","20","50","100","200","500","1000"]
    resourceID: str  # VPN网关资源ID
    linkResourceID: str  # VPN连接资源ID
    clientToken: Optional[str] = None  # 客户端存根，用于保证订单幂等性。要求单个云平台账户内唯一。

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnVpnGatewayUpgradeResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


