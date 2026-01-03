from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnSslClientListRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    queryContent: Optional[str] = None  # Query Content模糊查询
    vpnServiceID: Optional[str] = None  # VPN实例ID
    isOnline: Optional[str] = None  # 是否在线<br/>取值范围:<br/>false:不在线<br/>true:在线
    pageSize: Optional[int] = None  # 每页行数(不填默认为10)
    pageNo: Optional[int] = None  # 页码(不填默认为1)
    projectID: Optional[str] = None  # 企业项目ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnSslClientListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


