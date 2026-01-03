from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnGatewayQueryPriceRenewRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID, 例:100054c0416811e9a6690242ac110002
    resourceID: str  # VPN网关资源ID
    cycleType: str  # 本参数表示包周期类型。<br/>取值范围：<br/>YEAR<br/>MONTH
    cycleCount: int  # 包周期数，周期最大长度不能超过36个月

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnGatewayQueryPriceRenewResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


