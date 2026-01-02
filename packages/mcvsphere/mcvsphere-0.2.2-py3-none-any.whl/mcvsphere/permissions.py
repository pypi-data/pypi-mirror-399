"""Permission escalation based on OAuth claims.

Defines permission levels and maps:
- Tools → Required permission level
- OAuth groups → Granted permission levels
"""

from enum import Enum


class PermissionLevel(Enum):
    """Permission levels for tool access, from least to most privileged."""

    READ_ONLY = "read_only"  # View-only operations
    POWER_OPS = "power_ops"  # Power on/off, snapshots
    VM_LIFECYCLE = "vm_lifecycle"  # Create/delete/modify VMs
    HOST_ADMIN = "host_admin"  # ESXi host operations
    FULL_ADMIN = "full_admin"  # Everything including guest ops, services


# Tool → Required Permission mapping
# Default is READ_ONLY if not listed
TOOL_PERMISSIONS: dict[str, PermissionLevel] = {
    # ═══════════════════════════════════════════════════════════════════════
    # READ_ONLY - Safe viewing operations (36 tools)
    # ═══════════════════════════════════════════════════════════════════════
    "list_vms": PermissionLevel.READ_ONLY,
    "get_vm_info": PermissionLevel.READ_ONLY,
    "list_snapshots": PermissionLevel.READ_ONLY,
    "get_vm_stats": PermissionLevel.READ_ONLY,
    "get_host_stats": PermissionLevel.READ_ONLY,
    "list_hosts": PermissionLevel.READ_ONLY,
    "get_recent_tasks": PermissionLevel.READ_ONLY,
    "get_recent_events": PermissionLevel.READ_ONLY,
    "get_alarms": PermissionLevel.READ_ONLY,
    "browse_datastore": PermissionLevel.READ_ONLY,
    "get_datastore_info": PermissionLevel.READ_ONLY,
    "get_network_info": PermissionLevel.READ_ONLY,
    "get_resource_pool_info": PermissionLevel.READ_ONLY,
    "list_templates": PermissionLevel.READ_ONLY,
    "get_vcenter_info": PermissionLevel.READ_ONLY,
    "list_disks": PermissionLevel.READ_ONLY,
    "list_nics": PermissionLevel.READ_ONLY,
    "list_ovf_networks": PermissionLevel.READ_ONLY,
    "get_host_info": PermissionLevel.READ_ONLY,
    "list_services": PermissionLevel.READ_ONLY,
    "get_ntp_config": PermissionLevel.READ_ONLY,
    "get_host_hardware": PermissionLevel.READ_ONLY,
    "get_host_networking": PermissionLevel.READ_ONLY,
    "list_folders": PermissionLevel.READ_ONLY,
    "list_recent_tasks": PermissionLevel.READ_ONLY,
    "list_recent_events": PermissionLevel.READ_ONLY,
    "list_clusters": PermissionLevel.READ_ONLY,
    "get_drs_recommendations": PermissionLevel.READ_ONLY,
    "get_serial_port": PermissionLevel.READ_ONLY,
    "wait_for_vm_tools": PermissionLevel.READ_ONLY,
    "get_vm_tools_status": PermissionLevel.READ_ONLY,
    "vm_screenshot": PermissionLevel.READ_ONLY,
    # ═══════════════════════════════════════════════════════════════════════
    # POWER_OPS - Power and snapshot operations (14 tools)
    # ═══════════════════════════════════════════════════════════════════════
    "power_on": PermissionLevel.POWER_OPS,
    "power_off": PermissionLevel.POWER_OPS,
    "shutdown_guest": PermissionLevel.POWER_OPS,
    "reboot_guest": PermissionLevel.POWER_OPS,
    "reset_vm": PermissionLevel.POWER_OPS,
    "suspend_vm": PermissionLevel.POWER_OPS,
    "standby_guest": PermissionLevel.POWER_OPS,
    "create_snapshot": PermissionLevel.POWER_OPS,
    "revert_to_snapshot": PermissionLevel.POWER_OPS,
    "revert_to_current_snapshot": PermissionLevel.POWER_OPS,
    "delete_snapshot": PermissionLevel.POWER_OPS,
    "delete_all_snapshots": PermissionLevel.POWER_OPS,
    "rename_snapshot": PermissionLevel.POWER_OPS,
    "connect_nic": PermissionLevel.POWER_OPS,  # Connect/disconnect is power-level
    # ═══════════════════════════════════════════════════════════════════════
    # VM_LIFECYCLE - Create/delete/modify VMs (28 tools)
    # ═══════════════════════════════════════════════════════════════════════
    "create_vm": PermissionLevel.VM_LIFECYCLE,
    "clone_vm": PermissionLevel.VM_LIFECYCLE,
    "delete_vm": PermissionLevel.VM_LIFECYCLE,
    "reconfigure_vm": PermissionLevel.VM_LIFECYCLE,
    "rename_vm": PermissionLevel.VM_LIFECYCLE,
    "add_disk": PermissionLevel.VM_LIFECYCLE,
    "remove_disk": PermissionLevel.VM_LIFECYCLE,
    "extend_disk": PermissionLevel.VM_LIFECYCLE,
    "attach_iso": PermissionLevel.VM_LIFECYCLE,
    "detach_iso": PermissionLevel.VM_LIFECYCLE,
    "add_nic": PermissionLevel.VM_LIFECYCLE,
    "remove_nic": PermissionLevel.VM_LIFECYCLE,
    "change_nic_network": PermissionLevel.VM_LIFECYCLE,
    "set_nic_mac": PermissionLevel.VM_LIFECYCLE,
    "deploy_ovf": PermissionLevel.VM_LIFECYCLE,
    "export_vm_ovf": PermissionLevel.VM_LIFECYCLE,
    "convert_to_template": PermissionLevel.VM_LIFECYCLE,
    "convert_to_vm": PermissionLevel.VM_LIFECYCLE,
    "deploy_from_template": PermissionLevel.VM_LIFECYCLE,
    "create_folder": PermissionLevel.VM_LIFECYCLE,
    "move_vm_to_folder": PermissionLevel.VM_LIFECYCLE,
    "storage_vmotion": PermissionLevel.VM_LIFECYCLE,
    "move_vm_disk": PermissionLevel.VM_LIFECYCLE,
    "setup_serial_port": PermissionLevel.VM_LIFECYCLE,
    "connect_serial_port": PermissionLevel.VM_LIFECYCLE,
    "clear_serial_port": PermissionLevel.VM_LIFECYCLE,
    "remove_serial_port": PermissionLevel.VM_LIFECYCLE,
    # Datastore modifications
    "download_from_datastore": PermissionLevel.VM_LIFECYCLE,
    "upload_to_datastore": PermissionLevel.VM_LIFECYCLE,
    "delete_datastore_file": PermissionLevel.VM_LIFECYCLE,
    "create_datastore_folder": PermissionLevel.VM_LIFECYCLE,
    "move_datastore_file": PermissionLevel.VM_LIFECYCLE,
    "copy_datastore_file": PermissionLevel.VM_LIFECYCLE,
    # ═══════════════════════════════════════════════════════════════════════
    # HOST_ADMIN - ESXi host operations (6 tools)
    # ═══════════════════════════════════════════════════════════════════════
    "enter_maintenance_mode": PermissionLevel.HOST_ADMIN,
    "exit_maintenance_mode": PermissionLevel.HOST_ADMIN,
    "reboot_host": PermissionLevel.HOST_ADMIN,
    "shutdown_host": PermissionLevel.HOST_ADMIN,
    "configure_ntp": PermissionLevel.HOST_ADMIN,
    "set_service_policy": PermissionLevel.HOST_ADMIN,
    # ═══════════════════════════════════════════════════════════════════════
    # FULL_ADMIN - Everything including guest OS and service control (11 tools)
    # ═══════════════════════════════════════════════════════════════════════
    "start_service": PermissionLevel.FULL_ADMIN,
    "stop_service": PermissionLevel.FULL_ADMIN,
    "restart_service": PermissionLevel.FULL_ADMIN,
    # Guest OS operations (requires guest credentials, high privilege)
    "run_command_in_guest": PermissionLevel.FULL_ADMIN,
    "list_guest_processes": PermissionLevel.FULL_ADMIN,
    "read_guest_file": PermissionLevel.FULL_ADMIN,
    "write_guest_file": PermissionLevel.FULL_ADMIN,
    "list_guest_directory": PermissionLevel.FULL_ADMIN,
    "create_guest_directory": PermissionLevel.FULL_ADMIN,
    "delete_guest_file": PermissionLevel.FULL_ADMIN,
}


# OAuth Group → Granted Permission Levels
# Users inherit all permissions from their groups (union of all group permissions)
GROUP_PERMISSIONS: dict[str, set[PermissionLevel]] = {
    # View-only access
    "vsphere-readers": {
        PermissionLevel.READ_ONLY,
    },
    # Operators can power on/off, manage snapshots
    "vsphere-operators": {
        PermissionLevel.READ_ONLY,
        PermissionLevel.POWER_OPS,
    },
    # Admins can create/delete/modify VMs
    "vsphere-admins": {
        PermissionLevel.READ_ONLY,
        PermissionLevel.POWER_OPS,
        PermissionLevel.VM_LIFECYCLE,
    },
    # Host admins can manage ESXi hosts
    "vsphere-host-admins": {
        PermissionLevel.READ_ONLY,
        PermissionLevel.POWER_OPS,
        PermissionLevel.VM_LIFECYCLE,
        PermissionLevel.HOST_ADMIN,
    },
    # Super admins have full access
    "vsphere-super-admins": {
        PermissionLevel.READ_ONLY,
        PermissionLevel.POWER_OPS,
        PermissionLevel.VM_LIFECYCLE,
        PermissionLevel.HOST_ADMIN,
        PermissionLevel.FULL_ADMIN,
    },
}


class PermissionDeniedError(Exception):
    """Raised when user lacks permission for an operation."""

    def __init__(self, username: str, tool_name: str, required: PermissionLevel):
        self.username = username
        self.tool_name = tool_name
        self.required = required
        super().__init__(
            f"Permission denied: {username} lacks '{required.value}' permission for '{tool_name}'"
        )


def get_user_permissions(groups: list[str] | None) -> set[PermissionLevel]:
    """Extract permissions from OAuth groups.

    Args:
        groups: List of OAuth group names from token claims.

    Returns:
        Set of granted permission levels (union of all group permissions).
        Returns empty set if no recognized groups (deny all access).
    """
    if not groups:
        return set()  # No groups = no permissions (enforces RBAC)

    permissions: set[PermissionLevel] = set()

    for group in groups:
        if group in GROUP_PERMISSIONS:
            permissions.update(GROUP_PERMISSIONS[group])

    # No fallback - unrecognized groups get no permissions
    return permissions


def get_required_permission(tool_name: str) -> PermissionLevel:
    """Get required permission level for a tool.

    Args:
        tool_name: Name of the MCP tool.

    Returns:
        Required permission level (defaults to READ_ONLY if not mapped).
    """
    return TOOL_PERMISSIONS.get(tool_name, PermissionLevel.READ_ONLY)


def check_permission(
    tool_name: str,
    groups: list[str] | None,
) -> bool:
    """Check if user has permission for a tool.

    Args:
        tool_name: Name of the MCP tool to check.
        groups: OAuth groups from token claims.

    Returns:
        True if user has required permission, False otherwise.
    """
    required = get_required_permission(tool_name)
    user_perms = get_user_permissions(groups)
    return required in user_perms
