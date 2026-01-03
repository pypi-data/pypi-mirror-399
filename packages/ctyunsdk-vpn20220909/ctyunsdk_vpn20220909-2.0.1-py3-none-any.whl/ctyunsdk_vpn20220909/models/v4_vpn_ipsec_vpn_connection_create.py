from typing import Optional, List

from ctyun_python_sdk_core.ctyun_openapi_request import CtyunOpenAPIRequest
from ctyun_python_sdk_core.ctyun_openapi_response import CtyunOpenAPIResponse
from dataclasses_json import dataclass_json
from dataclasses import dataclass


@dataclass_json
@dataclass
class V4VpnIpsecVpnConnectionCreateRequest(CtyunOpenAPIRequest):
    regionID: str  # 资源池ID
    vpnConnectionName: str  # VPN连接名称
    vpnServiceID: str  # VPN实例ID
    ipsecServiceID: str  # VPN用户服务ID
    srcSubnet: List[str]  # 本端子网
    dstCidr: List[str]  # 对端网络
    psk: str  # 预共享密钥
    ikeAuthAlgorithm: str  # IKE策略:IKE认证算法，取值范围为：["sha1","sha256","sha384","sha512"]
    ikeVersion: str  # IKE策略:IKE版本，取值范围为：["v1","v2"]
    ikeEncryptionAlgorithm: str  # IKE策略:IKE加密算法，取值范围为：["aes-128","aes-192","aes-256","3des"]
    ikeLifeTime: int  # IKE策略:IKE生命周期，单位为秒
    ikePfs: str  # IKE策略:DH算法，取值范围为：["group2","group5","group14"]
    phaseNegotiationMode: str  # IPsec策略:协商模式，取值范围为：["main","aggressive"]
    ipsecAuthAlgorithm: str  # IPsec策略:IPsec认证算法，取值范围为：["sha1","sha256","sha384","sha512"]
    transformProtocol: str  # IPsec策略:传输协议，其取值为"esp"
    ipsecEncryptionAlgorithm: str  # IPsec策略:IPsec策略算法，取值范围为：["aes-128","aes-192","aes-256","3des"]
    ipsecLifeTime: int  # IPsec策略:IPsec生命周期，单位为秒
    ipsecPfs: str  # IPsec策略:PFS，取值范围为：["group2","group5","group14"]
    selfSign: bool  # 是否自签
    localID: str  # 本地识别ID
    remoteID: str  # 远端识别ID
    policyMode: Optional[bool] = None  # 路由模式，默认值:true
    triggerMode: Optional[bool] = None  # 协商生效模式，默认值为false
    authType: Optional[str] = None  # 认证方式
    dpdSwitch: Optional[bool] = None  # dpd开关，默认值:true
    vpnGatewayID: Optional[str] = None  # VPN网关ID
    certID: Optional[str] = None  # 证书ID
    selfSigncertID: Optional[str] = None  # 自签证书ID
    srcSubnetType: Optional[str] = None  # 本端子网输入类型
    projectID: Optional[str] = None  # 企业项目ID

    def __post_init__(self):
        super().__init__()


@dataclass_json
@dataclass
class V4VpnIpsecVpnConnectionCreateResponse(CtyunOpenAPIResponse):
    statusCode: Optional[int] = None  # 返回状态码（800为成功，900为失败）
    errorCode: Optional[str] = None  # 错误码，为product.module.code三段式码
    error: Optional[str] = None  # 错误码，为product.module.code三段式码
    message: Optional[str] = None  # 失败时的错误描述，一般为英文描述
    description: Optional[str] = None  # 失败时的错误描述，一般为中文描述
    returnObj: Optional[object] = None  # 成功时返回的数据

    def __post_init__(self):
        super().__init__()


