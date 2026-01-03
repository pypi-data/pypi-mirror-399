from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnIpsecQosLimitUpdateRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    limitType: str  # 限速类型，取值范围:<br/>cidr:子网类型,<br/>ipsec:ipsec连接型,<br/>不能修改之前的限速类型
    vpnConnectionID: str  # 连接ID
    qosID: str  # 限速qos id
    value: Optional[int] = None  # IPSec类型限速值,当limitType为ipsec必填，否则不填,范围不超过购买带宽上限
    unit: Optional[str] = None  # IPSec限速单位，取值范围:<br/>Mbps:Mbps,<br/>Kbps:Kbps,<br/>当limitType为ipsec必填，否则不填
    ruleList: Optional[List['V4VpnIpsecQosLimitUpdateRequestRuleList']] = None  # cidr限速规则, 当limitType为cidr必填，否则不填

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnIpsecQosLimitUpdateRequestRuleList:
    srcCidr: Optional[str] = None
    dstCidr: Optional[str] = None
    ruleValue: Optional[str] = None
    ruleUnit: Optional[str] = None


@dataclass_json
@dataclass
class V4VpnIpsecQosLimitUpdateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


