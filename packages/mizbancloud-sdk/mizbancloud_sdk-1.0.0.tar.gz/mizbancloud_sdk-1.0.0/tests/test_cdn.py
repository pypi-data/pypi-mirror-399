"""Tests for CDN module."""

import pytest
from mizbancloud import MizbanCloudClient
from mizbancloud.modules.cdn import Cdn


class TestCdnModule:
    """Tests for the CDN module."""

    def test_cdn_module_exists(self):
        """Test CDN module exists on client."""
        with MizbanCloudClient() as client:
            assert client.cdn is not None
            assert isinstance(client.cdn, Cdn)

    def test_cdn_has_at_least_90_methods(self):
        """Test CDN has at least 90 public methods."""
        methods = [m for m in dir(Cdn) if not m.startswith("_")]
        assert len(methods) >= 90, f"Expected at least 90 methods, found {len(methods)}"

    # Domain Methods
    def test_list_domains_exists(self):
        assert hasattr(Cdn, "list_domains")

    def test_get_domain_exists(self):
        assert hasattr(Cdn, "get_domain")

    def test_add_domain_exists(self):
        assert hasattr(Cdn, "add_domain")

    def test_delete_domain_exists(self):
        assert hasattr(Cdn, "delete_domain")

    def test_send_delete_confirm_code_exists(self):
        assert hasattr(Cdn, "send_delete_confirm_code")

    def test_get_usage_exists(self):
        assert hasattr(Cdn, "get_usage")

    def test_get_whois_exists(self):
        assert hasattr(Cdn, "get_whois")

    def test_get_reports_exists(self):
        assert hasattr(Cdn, "get_reports")

    def test_set_redirect_mode_exists(self):
        assert hasattr(Cdn, "set_redirect_mode")

    # DNS Methods
    def test_list_dns_records_exists(self):
        assert hasattr(Cdn, "list_dns_records")

    def test_get_dns_record_exists(self):
        assert hasattr(Cdn, "get_dns_record")

    def test_add_dns_record_exists(self):
        assert hasattr(Cdn, "add_dns_record")

    def test_update_dns_record_exists(self):
        assert hasattr(Cdn, "update_dns_record")

    def test_delete_dns_record_exists(self):
        assert hasattr(Cdn, "delete_dns_record")

    def test_fetch_records_exists(self):
        assert hasattr(Cdn, "fetch_records")

    def test_export_dns_records_exists(self):
        assert hasattr(Cdn, "export_dns_records")

    def test_import_dns_records_exists(self):
        assert hasattr(Cdn, "import_dns_records")

    def test_get_proxiable_records_exists(self):
        assert hasattr(Cdn, "get_proxiable_records")

    def test_set_custom_nameservers_exists(self):
        assert hasattr(Cdn, "set_custom_nameservers")

    def test_set_dnssec_exists(self):
        assert hasattr(Cdn, "set_dnssec")

    # SSL Methods
    def test_list_ssl_exists(self):
        assert hasattr(Cdn, "list_ssl")

    def test_get_ssl_info_exists(self):
        assert hasattr(Cdn, "get_ssl_info")

    def test_get_ssl_configs_exists(self):
        assert hasattr(Cdn, "get_ssl_configs")

    def test_add_custom_ssl_exists(self):
        assert hasattr(Cdn, "add_custom_ssl")

    def test_request_free_ssl_exists(self):
        assert hasattr(Cdn, "request_free_ssl")

    def test_remove_ssl_exists(self):
        assert hasattr(Cdn, "remove_ssl")

    def test_attach_ssl_exists(self):
        assert hasattr(Cdn, "attach_ssl")

    def test_detach_ssl_exists(self):
        assert hasattr(Cdn, "detach_ssl")

    def test_attach_default_ssl_exists(self):
        assert hasattr(Cdn, "attach_default_ssl")

    def test_detach_default_ssl_exists(self):
        assert hasattr(Cdn, "detach_default_ssl")

    def test_set_tls_version_exists(self):
        assert hasattr(Cdn, "set_tls_version")

    def test_set_hsts_exists(self):
        assert hasattr(Cdn, "set_hsts")

    def test_set_https_redirect_exists(self):
        assert hasattr(Cdn, "set_https_redirect")

    def test_set_csp_override_exists(self):
        assert hasattr(Cdn, "set_csp_override")

    def test_set_backend_protocol_exists(self):
        assert hasattr(Cdn, "set_backend_protocol")

    def test_set_http3_exists(self):
        assert hasattr(Cdn, "set_http3")

    # Cache Methods
    def test_get_cache_settings_exists(self):
        assert hasattr(Cdn, "get_cache_settings")

    def test_set_cache_mode_exists(self):
        assert hasattr(Cdn, "set_cache_mode")

    def test_set_cache_ttl_exists(self):
        assert hasattr(Cdn, "set_cache_ttl")

    def test_set_developer_mode_exists(self):
        assert hasattr(Cdn, "set_developer_mode")

    def test_set_always_online_exists(self):
        assert hasattr(Cdn, "set_always_online")

    def test_set_cache_cookies_exists(self):
        assert hasattr(Cdn, "set_cache_cookies")

    def test_set_browser_cache_mode_exists(self):
        assert hasattr(Cdn, "set_browser_cache_mode")

    def test_set_browser_cache_ttl_exists(self):
        assert hasattr(Cdn, "set_browser_cache_ttl")

    def test_set_error_cache_ttl_exists(self):
        assert hasattr(Cdn, "set_error_cache_ttl")

    def test_purge_cache_exists(self):
        assert hasattr(Cdn, "purge_cache")

    # Acceleration Methods
    def test_set_minify_exists(self):
        assert hasattr(Cdn, "set_minify")

    def test_set_image_optimization_exists(self):
        assert hasattr(Cdn, "set_image_optimization")

    def test_set_image_resize_exists(self):
        assert hasattr(Cdn, "set_image_resize")

    # DDoS Methods
    def test_get_ddos_settings_exists(self):
        assert hasattr(Cdn, "get_ddos_settings")

    def test_set_ddos_settings_exists(self):
        assert hasattr(Cdn, "set_ddos_settings")

    def test_set_captcha_module_exists(self):
        assert hasattr(Cdn, "set_captcha_module")

    def test_set_captcha_ttl_exists(self):
        assert hasattr(Cdn, "set_captcha_ttl")

    def test_set_cookie_challenge_ttl_exists(self):
        assert hasattr(Cdn, "set_cookie_challenge_ttl")

    def test_set_js_challenge_ttl_exists(self):
        assert hasattr(Cdn, "set_js_challenge_ttl")

    # Firewall Methods
    def test_get_firewall_configs_exists(self):
        assert hasattr(Cdn, "get_firewall_configs")

    def test_set_firewall_configs_exists(self):
        assert hasattr(Cdn, "set_firewall_configs")

    # WAF Methods
    def test_get_waf_settings_exists(self):
        assert hasattr(Cdn, "get_waf_settings")

    def test_set_waf_settings_exists(self):
        assert hasattr(Cdn, "set_waf_settings")

    def test_get_waf_layers_exists(self):
        assert hasattr(Cdn, "get_waf_layers")

    def test_get_waf_rules_exists(self):
        assert hasattr(Cdn, "get_waf_rules")

    def test_get_disabled_waf_rules_exists(self):
        assert hasattr(Cdn, "get_disabled_waf_rules")

    def test_switch_waf_group_exists(self):
        assert hasattr(Cdn, "switch_waf_group")

    def test_switch_waf_rule_exists(self):
        assert hasattr(Cdn, "switch_waf_rule")

    # Page Rules Methods
    def test_get_page_rules_exists(self):
        assert hasattr(Cdn, "get_page_rules")

    def test_get_page_rules_waf_exists(self):
        assert hasattr(Cdn, "get_page_rules_waf")

    def test_get_page_rules_ratelimit_exists(self):
        assert hasattr(Cdn, "get_page_rules_ratelimit")

    def test_get_page_rules_ddos_exists(self):
        assert hasattr(Cdn, "get_page_rules_ddos")

    def test_get_page_rules_firewall_exists(self):
        assert hasattr(Cdn, "get_page_rules_firewall")

    def test_create_page_rule_path_exists(self):
        assert hasattr(Cdn, "create_page_rule_path")

    def test_set_page_rule_priority_exists(self):
        assert hasattr(Cdn, "set_page_rule_priority")

    def test_delete_page_rule_path_exists(self):
        assert hasattr(Cdn, "delete_page_rule_path")

    def test_create_rule_exists(self):
        assert hasattr(Cdn, "create_rule")

    def test_delete_rule_exists(self):
        assert hasattr(Cdn, "delete_rule")

    def test_set_direct_rule_exists(self):
        assert hasattr(Cdn, "set_direct_rule")

    # Cluster Methods
    def test_get_clusters_exists(self):
        assert hasattr(Cdn, "get_clusters")

    def test_get_cluster_assignments_exists(self):
        assert hasattr(Cdn, "get_cluster_assignments")

    def test_add_cluster_exists(self):
        assert hasattr(Cdn, "add_cluster")

    def test_update_cluster_exists(self):
        assert hasattr(Cdn, "update_cluster")

    def test_delete_cluster_exists(self):
        assert hasattr(Cdn, "delete_cluster")

    def test_add_server_to_cluster_exists(self):
        assert hasattr(Cdn, "add_server_to_cluster")

    def test_remove_server_from_cluster_exists(self):
        assert hasattr(Cdn, "remove_server_from_cluster")

    # Log Forwarder Methods
    def test_get_log_forwarders_exists(self):
        assert hasattr(Cdn, "get_log_forwarders")

    def test_add_log_forwarder_exists(self):
        assert hasattr(Cdn, "add_log_forwarder")

    def test_update_log_forwarder_exists(self):
        assert hasattr(Cdn, "update_log_forwarder")

    def test_delete_log_forwarder_exists(self):
        assert hasattr(Cdn, "delete_log_forwarder")

    # Custom Pages Methods
    def test_get_custom_pages_exists(self):
        assert hasattr(Cdn, "get_custom_pages")

    def test_set_custom_pages_exists(self):
        assert hasattr(Cdn, "set_custom_pages")

    def test_delete_custom_pages_exists(self):
        assert hasattr(Cdn, "delete_custom_pages")

    # Plan Methods
    def test_get_plans_exists(self):
        assert hasattr(Cdn, "get_plans")

    def test_change_plan_exists(self):
        assert hasattr(Cdn, "change_plan")
