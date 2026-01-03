from ctyun_python_sdk_core import CtyunClient, Credential, ClientConfig, CtyunRequestException

from .models import *


class VpnClient:
    def __init__(self, client_config: ClientConfig):
        self.endpoint = client_config.endpoint
        self.credential = Credential(client_config.access_key_id, client_config.access_key_secret)
        self.ctyun_client = CtyunClient(client_config.verify_tls)

    def ipsec_vpn_static_route_create(self, request: IpsecVpnStaticRouteCreateRequest) -> IpsecVpnStaticRouteCreateResponse:
        """ipsec vpn目的路由创建"""
        url = f"{self.endpoint}/v4/vpn/ipsec-static-route/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, IpsecVpnStaticRouteCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_static_route_list(self, request: V4VpnIpsecStaticRouteListRequest) -> V4VpnIpsecStaticRouteListResponse:
        """ipsec vpn目的路由连接查询"""
        url = f"{self.endpoint}/v4/vpn/ipsec-static-route/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecStaticRouteListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_policy_route_list(self, request: V4VpnIpsecPolicyRouteListRequest) -> V4VpnIpsecPolicyRouteListResponse:
        """ipsec vpn策略路由连接查询"""
        url = f"{self.endpoint}/v4/vpn/ipsec-policy-route/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecPolicyRouteListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_gateway_vpc_update(self, request: V4VpnVpnGatewayVpcUpdateRequest) -> V4VpnVpnGatewayVpcUpdateResponse:
        """vpn网关VPC修改"""
        url = f"{self.endpoint}/v4/vpn/vpn-gateway-vpc/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnGatewayVpcUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_gateway_update(self, request: V4VpnVpnGatewayUpdateRequest) -> V4VpnVpnGatewayUpdateResponse:
        """vpn网关信息修改"""
        url = f"{self.endpoint}/v4/vpn/vpn-gateway/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnGatewayUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_subnet_update(self, request: V4VpnVpnSubnetUpdateRequest) -> V4VpnVpnSubnetUpdateResponse:
        """vpn网关修改子网"""
        url = f"{self.endpoint}/v4/vpn/vpn-subnet/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnSubnetUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_service_update(self, request: V4VpnVpnServiceUpdateRequest) -> V4VpnVpnServiceUpdateResponse:
        """vpn网关实例修改"""
        url = f"{self.endpoint}/v4/vpn/vpn-service/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnServiceUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_client_update(self, request: V4VpnSslClientUpdateRequest) -> V4VpnSslClientUpdateResponse:
        """修改SSL客户端"""
        url = f"{self.endpoint}/v4/vpn/ssl-client/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslClientUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_server_update(self, request: V4VpnSslServerUpdateRequest) -> V4VpnSslServerUpdateResponse:
        """修改SSL服务端"""
        url = f"{self.endpoint}/v4/vpn/ssl-server/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslServerUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_client_create(self, request: V4VpnSslClientCreateRequest) -> V4VpnSslClientCreateResponse:
        """创建SSL客户端"""
        url = f"{self.endpoint}/v4/vpn/ssl-client/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslClientCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_server_create(self, request: V4VpnSslServerCreateRequest) -> V4VpnSslServerCreateResponse:
        """创建SSL服务端"""
        url = f"{self.endpoint}/v4/vpn/ssl-server/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslServerCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_client_delete(self, request: V4VpnSslClientDeleteRequest) -> V4VpnSslClientDeleteResponse:
        """删除SSL客户端"""
        url = f"{self.endpoint}/v4/vpn/ssl-client/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslClientDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_server_delete(self, request: V4VpnSslServerDeleteRequest) -> V4VpnSslServerDeleteResponse:
        """删除SSL服务端"""
        url = f"{self.endpoint}/v4/vpn/ssl-server/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslServerDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_client_get_secret(self, request: V4VpnSslClientGetSecretRequest) -> V4VpnSslClientGetSecretResponse:
        """客户端认证信息获取"""
        url = f"{self.endpoint}/v4/vpn/ssl-client/get-secret"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslClientGetSecretResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_client_qos_update(self, request: V4VpnSslClientQosUpdateRequest) -> V4VpnSslClientQosUpdateResponse:
        """客户端限速修改"""
        url = f"{self.endpoint}/v4/vpn/ssl-client-qos/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslClientQosUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_client_list(self, request: V4VpnSslClientListRequest) -> V4VpnSslClientListResponse:
        """查询SSL客户端"""
        url = f"{self.endpoint}/v4/vpn/ssl-client/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslClientListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_server_list(self, request: V4VpnSslServerListRequest) -> V4VpnSslServerListResponse:
        """查询SSL服务端"""
        url = f"{self.endpoint}/v4/vpn/ssl-server/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslServerListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_gateway_list(self, request: V4VpnVpnGatewayListRequest) -> V4VpnVpnGatewayListResponse:
        """获取VPN网关详情"""
        url = f"{self.endpoint}/v4/vpn/vpn-gateway/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnGatewayListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_region_list(self, request: V4VpnVpnRegionListRequest) -> V4VpnVpnRegionListResponse:
        """获取VPN网关资源池详情"""
        url = f"{self.endpoint}/v4/vpn/vpn-region/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnRegionListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_gateway_quato_list(self, request: V4VpnVpnGatewayQuatoListRequest) -> V4VpnVpnGatewayQuatoListResponse:
        """获取VPN网关配额详情"""
        url = f"{self.endpoint}/v4/vpn/vpn-gateway-quato/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnGatewayQuatoListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_vpn_connection_update(self, request: V4VpnIpsecVpnConnectionUpdateRequest) -> V4VpnIpsecVpnConnectionUpdateResponse:
        """ipsec vpn连接修改"""
        url = f"{self.endpoint}/v4/vpn/ipsec-vpn-connection/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecVpnConnectionUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_health_check_list(self, request: V4VpnIpsecHealthCheckListRequest) -> V4VpnIpsecHealthCheckListResponse:
        """ipsec vpn连接健康检查查询"""
        url = f"{self.endpoint}/v4/vpn/ipsec-health-check/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecHealthCheckListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_health_check_create(self, request: V4VpnIpsecHealthCheckCreateRequest) -> V4VpnIpsecHealthCheckCreateResponse:
        """ipsec vpn连接健康检查配置"""
        url = f"{self.endpoint}/v4/vpn/ipsec-health-check/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecHealthCheckCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_vpn_connection_create(self, request: V4VpnIpsecVpnConnectionCreateRequest) -> V4VpnIpsecVpnConnectionCreateResponse:
        """ipsec vpn连接创建"""
        url = f"{self.endpoint}/v4/vpn/ipsec-vpn-connection/create"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecVpnConnectionCreateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_vpn_connection_delete(self, request: V4VpnIpsecVpnConnectionDeleteRequest) -> V4VpnIpsecVpnConnectionDeleteResponse:
        """ipsec vpn连接删除"""
        url = f"{self.endpoint}/v4/vpn/ipsec-vpn-connection/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecVpnConnectionDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_vpn_connection_log_list(self, request: V4VpnIpsecVpnConnectionLogListRequest) -> V4VpnIpsecVpnConnectionLogListResponse:
        """ipsec vpn连接日志详情查询"""
        url = f"{self.endpoint}/v4/vpn/ipsec-vpn-connection-log/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecVpnConnectionLogListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_vpn_connection_list(self, request: V4VpnIpsecVpnConnectionListRequest) -> V4VpnIpsecVpnConnectionListResponse:
        """ipsec vpn连接查询"""
        url = f"{self.endpoint}/v4/vpn/ipsec-vpn-connection/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecVpnConnectionListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_vpn_connection_policy_detail_list(self, request: V4VpnIpsecVpnConnectionPolicyDetailListRequest) -> V4VpnIpsecVpnConnectionPolicyDetailListResponse:
        """ipsec vpn连接策略详情查询"""
        url = f"{self.endpoint}/v4/vpn/ipsec-vpn-connection-policy-detail/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecVpnConnectionPolicyDetailListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_qos_limit_update(self, request: V4VpnIpsecQosLimitUpdateRequest) -> V4VpnIpsecQosLimitUpdateResponse:
        """ipsec vpn连接限速修改"""
        url = f"{self.endpoint}/v4/vpn/ipsec-qos-limit/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecQosLimitUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_qos_limit_delete(self, request: V4VpnIpsecQosLimitDeleteRequest) -> V4VpnIpsecQosLimitDeleteResponse:
        """ipsec vpn连接限速删除"""
        url = f"{self.endpoint}/v4/vpn/ipsec-qos-limit/delete"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecQosLimitDeleteResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_qos_limit_list(self, request: V4VpnIpsecQosLimitListRequest) -> V4VpnIpsecQosLimitListResponse:
        """ipsec vpn连接限速查询"""
        url = f"{self.endpoint}/v4/vpn/ipsec-qos-limit/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecQosLimitListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_client_keyword_update(self, request: V4VpnSslClientKeywordUpdateRequest) -> V4VpnSslClientKeywordUpdateResponse:
        """SSLVPN客户端密码修改"""
        url = f"{self.endpoint}/v4/vpn/ssl-client-keyword/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslClientKeywordUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_client_reset_keyword(self, request: V4VpnSslClientResetKeywordRequest) -> V4VpnSslClientResetKeywordResponse:
        """SSL VPN客户端密码重置"""
        url = f"{self.endpoint}/v4/vpn/ssl-client/reset-keyword"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslClientResetKeywordResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ssl_client_disconnect(self, request: V4VpnSslClientDisconnectRequest) -> V4VpnSslClientDisconnectResponse:
        """SSL客户端断开连接"""
        url = f"{self.endpoint}/v4/vpn/ssl-client/disconnect"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnSslClientDisconnectResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_used_count_list(self, request: V4VpnUsedCountListRequest) -> V4VpnUsedCountListResponse:
        """VPN相关资源用量获取"""
        url = f"{self.endpoint}/v4/vpn/used-count/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnUsedCountListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_usage_list(self, request: V4VpnUsageListRequest) -> V4VpnUsageListResponse:
        """VPN相关资源用量获取"""
        url = f"{self.endpoint}/v4/vpn/usage/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnUsageListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_gateway_upgrade(self, request: V4VpnVpnGatewayUpgradeRequest) -> V4VpnVpnGatewayUpgradeResponse:
        """VPN网关升配，目前只支持升配:增加带宽和连接数。"""
        url = f"{self.endpoint}/v4/vpn/vpn-gateway/upgrade"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnGatewayUpgradeResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_gateway_query_price_upgrade(self, request: V4VpnGatewayQueryPriceUpgradeRequest) -> V4VpnGatewayQueryPriceUpgradeResponse:
        """VPN网关升配询价，目前只支持升配询价:增加带宽和连接数。"""
        url = f"{self.endpoint}/v4/vpn/gateway/query-price-upgrade"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnGatewayQueryPriceUpgradeResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_service_list(self, request: V4VpnVpnServiceListRequest) -> V4VpnVpnServiceListResponse:
        """VPN网关实例查看"""
        url = f"{self.endpoint}/v4/vpn/vpn-service/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnServiceListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_gateway_renew(self, request: V4VpnVpnGatewayRenewRequest) -> V4VpnVpnGatewayRenewResponse:
        """支持VPN网关包周期计费的续订。"""
        url = f"{self.endpoint}/v4/vpn/vpn-gateway/renew"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnGatewayRenewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_gateway_query_price_renew(self, request: V4VpnGatewayQueryPriceRenewRequest) -> V4VpnGatewayQueryPriceRenewResponse:
        """支持VPN网关包周期计费的续订询价。"""
        url = f"{self.endpoint}/v4/vpn/gateway/query-price-renew"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnGatewayQueryPriceRenewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_gateway_new(self, request: V4VpnVpnGatewayNewRequest) -> V4VpnVpnGatewayNewResponse:
        """多AZ资源池VPN网关订购"""
        url = f"{self.endpoint}/v4/vpn/vpn-gateway/new"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnGatewayNewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_gateway_query_price_new(self, request: V4VpnGatewayQueryPriceNewRequest) -> V4VpnGatewayQueryPriceNewResponse:
        """支持按需/包年包月VPN网关订购询价。"""
        url = f"{self.endpoint}/v4/vpn/gateway/query-price-new"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnGatewayQueryPriceNewResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_vpn_gateway_refund(self, request: V4VpnVpnGatewayRefundRequest) -> V4VpnVpnGatewayRefundResponse:
        """支持退订一个包周期计费/按需的VPN网关。退订后，将退还对应部分VPN网关费用。"""
        url = f"{self.endpoint}/v4/vpn/vpn-gateway/refund"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnVpnGatewayRefundResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_user_service_update(self, request: V4VpnIpsecUserServiceUpdateRequest) -> V4VpnIpsecUserServiceUpdateResponse:
        """vpn用户服务修改"""
        url = f"{self.endpoint}/v4/vpn/ipsec-user-service/update"
        method = 'POST'
        try:
            headers = request.get_headers() or {} 
            body = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                body=body
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecUserServiceUpdateResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))

    def v4_vpn_ipsec_user_service_list(self, request: V4VpnIpsecUserServiceListRequest) -> V4VpnIpsecUserServiceListResponse:
        """vpn用户服务查看"""
        url = f"{self.endpoint}/v4/vpn/ipsec-user-service/list"
        method = 'GET'
        try:
            headers = request.get_headers() or {} 
            params = request.to_dict()
            response = self.ctyun_client.request(
                url=url,
                method=method,
                credential=self.credential,
                headers=headers,
                params=params
            ) 
            return self.ctyun_client.handle_response(response, V4VpnIpsecUserServiceListResponse)
        except Exception as e:
            raise CtyunRequestException(str(e))



