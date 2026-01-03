from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnIpsecVpnConnectionListRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    vpnConnectionName: Optional[str] = None  # IPsec VPN连接名称
    vpnConnectionID: Optional[str] = None  # IPsec VPN连接ID
    vpnServiceID: Optional[str] = None  # vpn网关实例ID
    queryContent: Optional[str] = None  # 模糊查询
    pageNo: Optional[int] = None  # 页码
    pageSize: Optional[int] = None  # 页面大小
    projectID: Optional[str] = None  # 企业项目ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnIpsecVpnConnectionListResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


