from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnVpnGatewayNewRequest(CtyunOpenAPIRequest):
    vpnName: str  # VPN网关名字
    regionID: str  # 资源池ID
    vpnType: str  # VPN网关类型，取值范围:<br/>[1,2,3]<br/>1为订购IPSEC，2为订购SSL，3为同时订购IPSEC和SSL
    gatewayType: str  # 网关类型，取值范围：<br/>normal：为普通类型  <br/>secret：为国密类型<br/>
    billMode: str  # 网关付费类型，取值范围：<br/>1：为包周期  <br/>2：为按需<br/>
    clientToken: Optional[str] = None  # 客户端存根，用于保证订单幂等性。要求单个云平台账户内唯一。
    vpcID: Optional[str] = None  # vpc ID，  vpnServiceType为vpc时必填
    vpnServiceType: Optional[str] = None  # 网关服务类型，默认vpc,取值范围： <br/>vpc：vpc类型  <br/>cloud_high：云间高速<br/>
    projectID: Optional[str] = None  # 企业项目ID
    sslBandwidth: Optional[int] = None  # SSL带宽，单位为Mbps，当vpnType为2和3时,此项为必填
    sslConnectionLimit: Optional[str] = None  # SSLVPN网关连接数限制，当vpnType为2和3时,此项为必填，取值为：["5","10","20","50","100","200","500","1000"]
    sslCycleType: Optional[str] = None  # SSL定购类型，取值范围：<br/>MONTH：按月计费，最大支持36个月，当vpnType为2和3时,此项为必填
    sslCycleCount: Optional[int] = None  # 订购周期，最大支持36个月，当vpnType为2和3时,此项为必填
    sslDescription: Optional[str] = None  # SSL描述信息
    localSubnets: Optional[List['V4VpnVpnGatewayNewRequestLocalSubnets']] = None  # 子网信息，vpnServiceType为vpc时必填
    ipsecBandwidth: Optional[int] = None  # IPSEC带宽，单位为Mbps，当vpnType为1和3时,此项为必填
    ipsecConnectionLimit: Optional[str] = None  # IPSECVPN网关连接数限制，当vpnType为1和3时,此项为必填，取值为：["10","20","30","40","50","100"]
    ipsecCycleType: Optional[str] = None  # IPSEC定购类型，取值范围：<br/>MONTH：按月计费，最大支持36个月，当vpnType为1和3时,此项为必填
    ipsecCycleCount: Optional[int] = None  # IPSEC订购周期，当vpnType为1和3时,此项为必填
    ipsecDescription: Optional[str] = None  # IPSEC描述信息

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnVpnGatewayNewRequestLocalSubnets:
    subnetID: Optional[str] = None
    subnetName: Optional[str] = None
    cidr: Optional[str] = None
    cidrType: Optional[str] = None


@dataclass_json
@dataclass
class V4VpnVpnGatewayNewResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional['V4VpnVpnGatewayNewReturnObj'] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnVpnGatewayNewReturnObj:
    masterOrderNo: Optional[str] = None
    regionID: Optional[str] = None
    masterOrderID: Optional[str] = None
