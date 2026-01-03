"""MizbanCloud Cloud Module."""

from typing import Any, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..http_client import HttpClient


class Cloud:
    """Cloud IaaS management: servers, firewall, networks, volumes, snapshots, SSH keys."""

    def __init__(self, http_client: "HttpClient"):
        self._http = http_client

    # ==================== Server Methods ====================

    def list_servers(self) -> Any:
        """List all servers."""
        return self._http.get("/api/v1/cloud/servers")

    def get_server(self, server_id: int) -> Any:
        """Get server details."""
        return self._http.get(f"/api/v1/cloud/servers/{server_id}")

    def poll_server(self, server_id: int) -> Any:
        """Poll server status."""
        return self._http.get(f"/api/v1/cloud/servers/{server_id}/poll")

    def create_server(self, data: Dict[str, Any]) -> Any:
        """Create a new server."""
        return self._http.post("/api/v1/cloud/servers", data)

    def delete_server(self, server_id: int) -> Any:
        """Delete a server."""
        return self._http.delete(f"/api/v1/cloud/servers/{server_id}")

    def rename_server(self, server_id: int, name: str) -> Any:
        """Rename a server."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/rename", {"name": name})

    def resize_server(self, server_id: int, data: Dict[str, Any]) -> Any:
        """Resize a server."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/resize", data)

    def reload_os(self, server_id: int, data: Dict[str, Any]) -> Any:
        """Reload operating system."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/reload-os", data)

    # ==================== Power Management Methods ====================

    def power_on(self, server_id: int) -> Any:
        """Power on server."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/power-on")

    def power_off(self, server_id: int) -> Any:
        """Power off server (hard)."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/power-off")

    def reboot(self, server_id: int) -> Any:
        """Reboot server (hard)."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/reboot")

    def restart(self, server_id: int) -> Any:
        """Restart server (soft/graceful)."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/restart")

    # ==================== Access Methods ====================

    def get_vnc(self, server_id: int) -> Any:
        """Get VNC console URL."""
        return self._http.get(f"/api/v1/cloud/servers/{server_id}/vnc")

    def reset_password(self, server_id: int) -> Any:
        """Reset server password."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/reset-password")

    def get_initial_password(self, server_id: int) -> Any:
        """Get initial server password."""
        return self._http.get(f"/api/v1/cloud/servers/{server_id}/initial-password")

    # ==================== Rescue Mode Methods ====================

    def rescue(self, server_id: int, data: Optional[Dict[str, Any]] = None) -> Any:
        """Enter rescue mode."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/rescue", data)

    def unrescue(self, server_id: int) -> Any:
        """Exit rescue mode."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/unrescue")

    # ==================== Autopilot Methods ====================

    def enable_autopilot(self, server_id: int) -> Any:
        """Enable autopilot."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/autopilot/enable")

    def disable_autopilot(self, server_id: int) -> Any:
        """Disable autopilot."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/autopilot/disable")

    # ==================== Monitoring Methods ====================

    def get_logs(self, server_id: int) -> Any:
        """Get server logs."""
        return self._http.get(f"/api/v1/cloud/servers/{server_id}/logs")

    def get_charts(self, server_id: int) -> Any:
        """Get server charts/metrics."""
        return self._http.get(f"/api/v1/cloud/servers/{server_id}/charts")

    def get_traffic_usage(self, server_id: int) -> Any:
        """Get traffic usage."""
        return self._http.get(f"/api/v1/cloud/servers/{server_id}/traffic-usage")

    def get_traffics(self, server_id: int) -> Any:
        """Get traffic details."""
        return self._http.get(f"/api/v1/cloud/servers/{server_id}/traffics")

    # ==================== Test Server Methods ====================

    def convert_to_permanent(self, server_id: int) -> Any:
        """Convert test server to permanent."""
        return self._http.post(f"/api/v1/cloud/servers/{server_id}/convert-to-permanent")

    # ==================== Security Group Methods ====================

    def list_security_groups(self) -> Any:
        """List security groups."""
        return self._http.get("/api/v1/cloud/security-groups")

    def create_security_group(self, data: Dict[str, Any]) -> Any:
        """Create security group."""
        return self._http.post("/api/v1/cloud/security-groups", data)

    def delete_security_group(self, group_id: int) -> Any:
        """Delete security group."""
        return self._http.delete(f"/api/v1/cloud/security-groups/{group_id}")

    def add_security_rule(self, data: Dict[str, Any]) -> Any:
        """Add security rule."""
        return self._http.post("/api/v1/cloud/security-rules", data)

    def remove_security_rule(self, rule_id: int) -> Any:
        """Remove security rule."""
        return self._http.delete(f"/api/v1/cloud/security-rules/{rule_id}")

    def attach_firewall(self, data: Dict[str, Any]) -> Any:
        """Attach firewall to server."""
        return self._http.post("/api/v1/cloud/servers/attach-firewall", data)

    def detach_firewall(self, data: Dict[str, Any]) -> Any:
        """Detach firewall from server."""
        return self._http.post("/api/v1/cloud/servers/detach-firewall", data)

    # ==================== Private Network Methods ====================

    def list_private_networks(self) -> Any:
        """List private networks."""
        return self._http.get("/api/v1/cloud/private-networks")

    def create_private_network(self, data: Dict[str, Any]) -> Any:
        """Create private network."""
        return self._http.post("/api/v1/cloud/private-networks", data)

    def update_private_network(self, network_id: int, data: Dict[str, Any]) -> Any:
        """Update private network."""
        return self._http.put(f"/api/v1/cloud/private-networks/{network_id}", data)

    def delete_private_network(self, network_id: int) -> Any:
        """Delete private network."""
        return self._http.delete(f"/api/v1/cloud/private-networks/{network_id}")

    def attach_to_private_network(self, data: Dict[str, Any]) -> Any:
        """Attach server to private network."""
        return self._http.post("/api/v1/cloud/private-networks/attach", data)

    def detach_from_private_network(self, data: Dict[str, Any]) -> Any:
        """Detach server from private network."""
        return self._http.post("/api/v1/cloud/private-networks/detach", data)

    def purge_network_attachments(self, network_id: int) -> Any:
        """Purge all network attachments."""
        return self._http.post(f"/api/v1/cloud/private-networks/{network_id}/purge")

    # ==================== Public Network Methods ====================

    def attach_public_network(self, data: Dict[str, Any]) -> Any:
        """Attach public network to server."""
        return self._http.post("/api/v1/cloud/servers/attach-public-network", data)

    def detach_public_network(self, data: Dict[str, Any]) -> Any:
        """Detach public network from server."""
        return self._http.post("/api/v1/cloud/servers/detach-public-network", data)

    # ==================== Volume Methods ====================

    def list_volumes(self) -> Any:
        """List volumes."""
        return self._http.get("/api/v1/cloud/volumes")

    def get_volume(self, volume_id: int) -> Any:
        """Get volume details."""
        return self._http.get(f"/api/v1/cloud/volumes/{volume_id}")

    def create_volume(self, data: Dict[str, Any]) -> Any:
        """Create volume."""
        return self._http.post("/api/v1/cloud/volumes", data)

    def update_volume(self, volume_id: int, data: Dict[str, Any]) -> Any:
        """Update volume."""
        return self._http.put(f"/api/v1/cloud/volumes/{volume_id}", data)

    def delete_volume(self, volume_id: int) -> Any:
        """Delete volume."""
        return self._http.delete(f"/api/v1/cloud/volumes/{volume_id}")

    def attach_volume(self, data: Dict[str, Any]) -> Any:
        """Attach volume to server."""
        return self._http.post("/api/v1/cloud/volumes/attach", data)

    def detach_volume(self, data: Dict[str, Any]) -> Any:
        """Detach volume from server."""
        return self._http.post("/api/v1/cloud/volumes/detach", data)

    def sync_volumes(self) -> Any:
        """Sync volumes."""
        return self._http.post("/api/v1/cloud/volumes/sync")

    # ==================== Snapshot Methods ====================

    def list_snapshots(self) -> Any:
        """List snapshots."""
        return self._http.get("/api/v1/cloud/snapshots")

    def get_snapshot(self, snapshot_id: int) -> Any:
        """Get snapshot details."""
        return self._http.get(f"/api/v1/cloud/snapshots/{snapshot_id}")

    def create_snapshot(self, data: Dict[str, Any]) -> Any:
        """Create snapshot."""
        return self._http.post("/api/v1/cloud/snapshots", data)

    def delete_snapshot(self, snapshot_id: int) -> Any:
        """Delete snapshot."""
        return self._http.delete(f"/api/v1/cloud/snapshots/{snapshot_id}")

    def sync_snapshots(self) -> Any:
        """Sync snapshots."""
        return self._http.post("/api/v1/cloud/snapshots/sync")

    # ==================== SSH Key Methods ====================

    def list_ssh_keys(self) -> Any:
        """List SSH keys."""
        return self._http.get("/api/v1/cloud/ssh-keys")

    def get_ssh_key(self, key_id: int) -> Any:
        """Get SSH key details."""
        return self._http.get(f"/api/v1/cloud/ssh-keys/{key_id}")

    def create_ssh_key(self, data: Dict[str, Any]) -> Any:
        """Create SSH key."""
        return self._http.post("/api/v1/cloud/ssh-keys", data)

    def delete_ssh_key(self, key_id: int) -> Any:
        """Delete SSH key."""
        return self._http.delete(f"/api/v1/cloud/ssh-keys/{key_id}")

    def generate_random_ssh_key(self) -> Any:
        """Generate random SSH key pair."""
        return self._http.post("/api/v1/cloud/ssh-keys/generate")
