"""MizbanCloud CDN Module."""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Cdn:
    """CDN management: domains, DNS, SSL, cache, security, WAF, page rules, and more."""

    def __init__(self, http_client: "HttpClient"):
        self._http = http_client

    # ==================== Domain Methods ====================

    def list_domains(self) -> Any:
        """List all CDN domains."""
        return self._http.get("/api/v1/cdn/domains")

    def get_domain(self, domain_id: int) -> Any:
        """Get domain details."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}")

    def add_domain(self, data: Dict[str, Any]) -> Any:
        """Add a new domain."""
        return self._http.post("/api/v1/cdn/domains", data)

    def delete_domain(self, domain_id: int, confirm_code: str) -> Any:
        """Delete a domain."""
        return self._http.delete(f"/api/v1/cdn/domains/{domain_id}", {"code": confirm_code})

    def send_delete_confirm_code(self, domain_id: int) -> Any:
        """Send SMS confirmation code for domain deletion."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/delete/confirm")

    def get_usage(self, domain_id: int) -> Any:
        """Get domain usage/analytics."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/usage")

    def get_whois(self, domain_id: int) -> Any:
        """Get domain WHOIS information."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/whois")

    def get_reports(self, domain_id: int) -> Any:
        """Get domain reports."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/reports")

    def set_redirect_mode(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set domain redirect mode."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/redirect-mode", data)

    # ==================== DNS Methods ====================

    def list_dns_records(self, domain_id: int) -> Any:
        """List DNS records for a domain."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/dns")

    def get_dns_record(self, domain_id: int, record_id: int) -> Any:
        """Get a specific DNS record."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/dns/{record_id}")

    def add_dns_record(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Add a DNS record."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/dns", data)

    def update_dns_record(self, domain_id: int, record_id: int, data: Dict[str, Any]) -> Any:
        """Update a DNS record."""
        return self._http.put(f"/api/v1/cdn/domains/{domain_id}/dns/{record_id}", data)

    def delete_dns_record(self, domain_id: int, record_id: int) -> Any:
        """Delete a DNS record."""
        return self._http.delete(f"/api/v1/cdn/domains/{domain_id}/dns/{record_id}")

    def fetch_records(self, domain_id: int) -> Any:
        """Fetch DNS records from origin."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/dns/fetch")

    def export_dns_records(self, domain_id: int) -> Any:
        """Export DNS records."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/dns/export")

    def import_dns_records(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Import DNS records."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/dns/import", data)

    def get_proxiable_records(self, domain_id: int) -> Any:
        """Get proxiable DNS records."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/dns/proxiable")

    def set_custom_nameservers(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set custom nameservers."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/dns/nameservers", data)

    def set_dnssec(self, domain_id: int, enabled: bool) -> Any:
        """Enable or disable DNSSEC."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/dns/dnssec", {"enabled": enabled})

    # ==================== SSL Methods ====================

    def list_ssl(self, domain_id: int) -> Any:
        """List SSL certificates."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/ssl")

    def get_ssl_info(self, domain_id: int) -> Any:
        """Get SSL information."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/ssl/info")

    def get_ssl_configs(self, domain_id: int) -> Any:
        """Get SSL configurations."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/ssl/configs")

    def add_custom_ssl(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Add custom SSL certificate."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/custom", data)

    def request_free_ssl(self, domain_id: int) -> Any:
        """Request free SSL certificate (Let's Encrypt)."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/free")

    def remove_ssl(self, domain_id: int, ssl_id: int) -> Any:
        """Remove SSL certificate."""
        return self._http.delete(f"/api/v1/cdn/domains/{domain_id}/ssl/{ssl_id}")

    def attach_ssl(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Attach SSL certificate to subdomain."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/attach", data)

    def detach_ssl(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Detach SSL certificate from subdomain."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/detach", data)

    def attach_default_ssl(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Attach default SSL certificate."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/default/attach", data)

    def detach_default_ssl(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Detach default SSL certificate."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/default/detach", data)

    def set_tls_version(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set minimum TLS version."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/tls-version", data)

    def set_hsts(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Configure HSTS settings."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/hsts", data)

    def set_https_redirect(self, domain_id: int, enabled: bool) -> Any:
        """Enable or disable HTTPS redirect."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/https-redirect", {"enabled": enabled})

    def set_csp_override(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set Content Security Policy override."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/csp-override", data)

    def set_backend_protocol(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set backend protocol (HTTP/HTTPS)."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/backend-protocol", data)

    def set_http3(self, domain_id: int, enabled: bool) -> Any:
        """Enable or disable HTTP/3."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ssl/http3", {"enabled": enabled})

    # ==================== Cache Methods ====================

    def get_cache_settings(self, domain_id: int) -> Any:
        """Get cache settings."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/cache")

    def set_cache_mode(self, domain_id: int, mode: str) -> Any:
        """Set cache mode."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/cache/mode", {"mode": mode})

    def set_cache_ttl(self, domain_id: int, ttl: int) -> Any:
        """Set cache TTL."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/cache/ttl", {"ttl": ttl})

    def set_developer_mode(self, domain_id: int, enabled: bool) -> Any:
        """Enable or disable developer mode."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/cache/developer-mode", {"enabled": enabled})

    def set_always_online(self, domain_id: int, enabled: bool) -> Any:
        """Enable or disable always online mode."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/cache/always-online", {"enabled": enabled})

    def set_cache_cookies(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set cache cookies settings."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/cache/cookies", data)

    def set_browser_cache_mode(self, domain_id: int, mode: str) -> Any:
        """Set browser cache mode."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/cache/browser-mode", {"mode": mode})

    def set_browser_cache_ttl(self, domain_id: int, ttl: int) -> Any:
        """Set browser cache TTL."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/cache/browser-ttl", {"ttl": ttl})

    def set_error_cache_ttl(self, domain_id: int, ttl: int) -> Any:
        """Set error page cache TTL."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/cache/error-ttl", {"ttl": ttl})

    def purge_cache(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Purge cache."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/cache/purge", data)

    # ==================== Acceleration Methods ====================

    def set_minify(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set minification settings."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/acceleration/minify", data)

    def set_image_optimization(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set image optimization settings."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/acceleration/image-optimization", data)

    def set_image_resize(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set image resize settings."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/acceleration/image-resize", data)

    # ==================== DDoS Methods ====================

    def get_ddos_settings(self, domain_id: int) -> Any:
        """Get DDoS protection settings."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/ddos")

    def set_ddos_settings(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set DDoS protection settings."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ddos", data)

    def set_captcha_module(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set captcha module settings."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ddos/captcha", data)

    def set_captcha_ttl(self, domain_id: int, ttl: int) -> Any:
        """Set captcha TTL."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ddos/captcha-ttl", {"ttl": ttl})

    def set_cookie_challenge_ttl(self, domain_id: int, ttl: int) -> Any:
        """Set cookie challenge TTL."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ddos/cookie-challenge-ttl", {"ttl": ttl})

    def set_js_challenge_ttl(self, domain_id: int, ttl: int) -> Any:
        """Set JavaScript challenge TTL."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/ddos/js-challenge-ttl", {"ttl": ttl})

    # ==================== Firewall Methods ====================

    def get_firewall_configs(self, domain_id: int) -> Any:
        """Get firewall configurations."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/firewall")

    def set_firewall_configs(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set firewall configurations."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/firewall", data)

    # ==================== WAF Methods ====================

    def get_waf_settings(self, domain_id: int) -> Any:
        """Get WAF settings."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/waf")

    def set_waf_settings(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set WAF settings."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/waf", data)

    def get_waf_layers(self, domain_id: int) -> Any:
        """Get WAF layers."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/waf/layers")

    def get_waf_rules(self, domain_id: int, layer_id: int) -> Any:
        """Get WAF rules for a layer."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/waf/layers/{layer_id}/rules")

    def get_disabled_waf_rules(self, domain_id: int) -> Any:
        """Get disabled WAF rules."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/waf/disabled-rules")

    def switch_waf_group(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Switch WAF group on/off."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/waf/switch-group", data)

    def switch_waf_rule(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Switch WAF rule on/off."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/waf/switch-rule", data)

    # ==================== Page Rules Methods ====================

    def get_page_rules(self, domain_id: int) -> Any:
        """Get page rules."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/page-rules")

    def get_page_rules_waf(self, domain_id: int) -> Any:
        """Get WAF page rules."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/page-rules/waf")

    def get_page_rules_ratelimit(self, domain_id: int) -> Any:
        """Get rate limit page rules."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/page-rules/ratelimit")

    def get_page_rules_ddos(self, domain_id: int) -> Any:
        """Get DDoS page rules."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/page-rules/ddos")

    def get_page_rules_firewall(self, domain_id: int) -> Any:
        """Get firewall page rules."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/page-rules/firewall")

    def create_page_rule_path(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Create page rule path."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/page-rules/path", data)

    def set_page_rule_priority(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set page rule priority."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/page-rules/priority", data)

    def delete_page_rule_path(self, domain_id: int, path_id: int) -> Any:
        """Delete page rule path."""
        return self._http.delete(f"/api/v1/cdn/domains/{domain_id}/page-rules/path/{path_id}")

    def create_rule(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Create a rule."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/page-rules/rule", data)

    def delete_rule(self, domain_id: int, rule_id: int) -> Any:
        """Delete a rule."""
        return self._http.delete(f"/api/v1/cdn/domains/{domain_id}/page-rules/rule/{rule_id}")

    def set_direct_rule(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set direct rule."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/page-rules/direct", data)

    # ==================== Cluster Methods ====================

    def get_clusters(self, domain_id: int) -> Any:
        """Get clusters."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/clusters")

    def get_cluster_assignments(self, domain_id: int) -> Any:
        """Get cluster assignments."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/clusters/assignments")

    def add_cluster(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Add a cluster."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/clusters", data)

    def update_cluster(self, domain_id: int, cluster_id: int, data: Dict[str, Any]) -> Any:
        """Update a cluster."""
        return self._http.put(f"/api/v1/cdn/domains/{domain_id}/clusters/{cluster_id}", data)

    def delete_cluster(self, domain_id: int, cluster_id: int) -> Any:
        """Delete a cluster."""
        return self._http.delete(f"/api/v1/cdn/domains/{domain_id}/clusters/{cluster_id}")

    def add_server_to_cluster(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Add server to cluster."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/clusters/server", data)

    def remove_server_from_cluster(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Remove server from cluster."""
        return self._http.delete(f"/api/v1/cdn/domains/{domain_id}/clusters/server", data)

    # ==================== Log Forwarder Methods ====================

    def get_log_forwarders(self, domain_id: int) -> Any:
        """Get log forwarders."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/log-forwarders")

    def add_log_forwarder(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Add log forwarder."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/log-forwarders", data)

    def update_log_forwarder(self, domain_id: int, forwarder_id: int, data: Dict[str, Any]) -> Any:
        """Update log forwarder."""
        return self._http.put(f"/api/v1/cdn/domains/{domain_id}/log-forwarders/{forwarder_id}", data)

    def delete_log_forwarder(self, domain_id: int, forwarder_id: int) -> Any:
        """Delete log forwarder."""
        return self._http.delete(f"/api/v1/cdn/domains/{domain_id}/log-forwarders/{forwarder_id}")

    # ==================== Custom Pages Methods ====================

    def get_custom_pages(self, domain_id: int) -> Any:
        """Get custom pages."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/custom-pages")

    def set_custom_pages(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Set custom pages."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/custom-pages", data)

    def delete_custom_pages(self, domain_id: int) -> Any:
        """Delete custom pages."""
        return self._http.delete(f"/api/v1/cdn/domains/{domain_id}/custom-pages")

    # ==================== Plan Methods ====================

    def get_plans(self, domain_id: int) -> Any:
        """Get available plans."""
        return self._http.get(f"/api/v1/cdn/domains/{domain_id}/plans")

    def change_plan(self, domain_id: int, data: Dict[str, Any]) -> Any:
        """Change domain plan."""
        return self._http.post(f"/api/v1/cdn/domains/{domain_id}/plans/change", data)
