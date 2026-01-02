# OAuth & RBAC Architecture for mcvsphere

## Overview

mcvsphere supports multi-user OAuth 2.1 authentication with Role-Based Access Control (RBAC). This enables:

1. **Single Sign-On** via any OIDC provider (Authentik, Keycloak, Auth0, etc.)
2. **User Identity** for audit logging - know WHO made each request
3. **Group-Based Permissions** - control what users can do based on OAuth groups
4. **Audit Trail** - every tool invocation logged with user identity and timing

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      MCP Client (Claude Code)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ 1. OAuth 2.1 + PKCE flow
                             │    (browser opens for login)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      OIDC Provider                               │
│              (Authentik, Keycloak, Auth0, etc.)                  │
│                                                                  │
│   - Issues JWT access tokens                                     │
│   - Validates user credentials                                   │
│   - Includes groups claim in token                               │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ 2. JWT Bearer token
                             │    Authorization: Bearer <jwt>
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                        mcvsphere                                 │
│                   (FastMCP + pyvmomi)                            │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   OIDCProxy (FastMCP)                    │    │
│  │  - Validates JWT signature via JWKS endpoint             │    │
│  │  - Extracts user identity (preferred_username, email)    │    │
│  │  - Extracts groups from token claims                     │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   RBACMiddleware                         │    │
│  │  - Intercepts ALL tool calls via on_call_tool()          │    │
│  │  - Maps OAuth groups → Permission levels                 │    │
│  │  - Denies access if user lacks required permission       │    │
│  │  - Logs audit events with user identity                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                              │                                   │
│                              ▼                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │                   VMware Tools (94)                      │    │
│  │  - Execute vCenter/ESXi operations via pyvmomi           │    │
│  │  - Single service account connection to vCenter          │    │
│  └─────────────────────────────────────────────────────────┘    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ 3. pyvmomi (service account)
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                     vCenter / ESXi                               │
│  - Receives API calls as service account                        │
│  - mcvsphere audit logs show real user identity                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## RBAC Permission Model

### Permission Levels

mcvsphere defines 5 permission levels, from least to most privileged:

| Level | Description | Example Tools |
|-------|-------------|---------------|
| `READ_ONLY` | View-only operations | `list_vms`, `get_vm_info`, `vm_screenshot` |
| `POWER_OPS` | Power and snapshot operations | `power_on`, `create_snapshot`, `reboot_guest` |
| `VM_LIFECYCLE` | Create/delete/modify VMs | `create_vm`, `clone_vm`, `add_disk`, `deploy_ovf` |
| `HOST_ADMIN` | ESXi host operations | `reboot_host`, `enter_maintenance_mode` |
| `FULL_ADMIN` | Everything including guest OS ops | `run_command_in_guest`, `restart_service` |

### OAuth Groups → Permissions

Users are granted permissions based on their OAuth group memberships:

| OAuth Group | Permissions Granted |
|-------------|---------------------|
| `vsphere-readers` | READ_ONLY |
| `vsphere-operators` | READ_ONLY, POWER_OPS |
| `vsphere-admins` | READ_ONLY, POWER_OPS, VM_LIFECYCLE |
| `vsphere-host-admins` | READ_ONLY, POWER_OPS, VM_LIFECYCLE, HOST_ADMIN |
| `vsphere-super-admins` | ALL (full access) |

**Security Note:** Users with NO recognized groups are denied ALL access. There is no default permission.

### Tool → Permission Mapping

All 94 tools are mapped to permission levels in `src/mcvsphere/permissions.py`:

```python
# READ_ONLY - 32 tools
"list_vms", "get_vm_info", "list_snapshots", "get_vm_stats", ...

# POWER_OPS - 14 tools
"power_on", "power_off", "create_snapshot", "revert_to_snapshot", ...

# VM_LIFECYCLE - 33 tools
"create_vm", "clone_vm", "delete_vm", "add_disk", "deploy_ovf", ...

# HOST_ADMIN - 6 tools
"enter_maintenance_mode", "reboot_host", "shutdown_host", ...

# FULL_ADMIN - 11 tools
"run_command_in_guest", "write_guest_file", "restart_service", ...
```

---

## Implementation Details

### Key Files

| File | Purpose |
|------|---------|
| `src/mcvsphere/auth.py` | OIDCProxy configuration |
| `src/mcvsphere/permissions.py` | Permission levels and tool mappings |
| `src/mcvsphere/middleware.py` | RBACMiddleware implementation |
| `src/mcvsphere/audit.py` | Audit logging with user context |
| `src/mcvsphere/server.py` | Server setup with OAuth + RBAC |

### RBACMiddleware Flow

```python
class RBACMiddleware(Middleware):
    """Intercepts all tool calls to enforce permissions."""

    async def on_call_tool(self, context, call_next):
        # 1. Extract user from OAuth token
        claims = self._extract_user_from_context(context.fastmcp_context)
        username = claims.get("preferred_username", "unknown")
        groups = claims.get("groups", [])

        # 2. Check permission
        tool_name = context.message.name
        if not check_permission(tool_name, groups):
            required = get_required_permission(tool_name)
            audit_permission_denied(tool_name, {...}, required.value)
            raise PermissionDeniedError(username, tool_name, required)

        # 3. Execute tool with timing
        start = time.perf_counter()
        result = await call_next(context)
        duration_ms = (time.perf_counter() - start) * 1000

        # 4. Audit log
        audit_log(tool_name, {...}, result="success", duration_ms=duration_ms)
        return result
```

### Audit Log Format

```json
{
  "timestamp": "2025-12-27T08:15:32.123456+00:00",
  "user": "ryan@example.com",
  "groups": ["vsphere-admins", "vsphere-operators"],
  "tool": "power_on",
  "args": {"vm_name": "web-server"},
  "duration_ms": 1234.56,
  "result": "success"
}
```

Permission denied events:
```json
{
  "timestamp": "2025-12-27T08:15:32.123456+00:00",
  "user": "guest@example.com",
  "groups": ["vsphere-readers"],
  "tool": "delete_vm",
  "args": {"vm_name": "web-server"},
  "required_permission": "vm_lifecycle",
  "event": "PERMISSION_DENIED"
}
```

---

## Configuration

### Environment Variables

```bash
# ═══════════════════════════════════════════════════════════════
# OAuth Configuration
# ═══════════════════════════════════════════════════════════════
OAUTH_ENABLED=true
OAUTH_ISSUER_URL=https://auth.example.com/application/o/mcvsphere/
OAUTH_CLIENT_ID=<from-oidc-provider>
OAUTH_CLIENT_SECRET=<from-oidc-provider>
OAUTH_BASE_URL=https://mcp.example.com  # Public URL for callbacks
OAUTH_SCOPES='["openid", "profile", "email", "groups"]'

# ═══════════════════════════════════════════════════════════════
# Transport (must be HTTP for OAuth)
# ═══════════════════════════════════════════════════════════════
MCP_TRANSPORT=streamable-http
MCP_HOST=0.0.0.0
MCP_PORT=8080

# ═══════════════════════════════════════════════════════════════
# vCenter Connection (service account)
# ═══════════════════════════════════════════════════════════════
VCENTER_HOST=vcenter.example.com
VCENTER_USER=svc-mcvsphere@vsphere.local
VCENTER_PASSWORD=<service-account-password>
VCENTER_INSECURE=false

# ═══════════════════════════════════════════════════════════════
# Optional
# ═══════════════════════════════════════════════════════════════
LOG_LEVEL=INFO
```

### Server Startup Banner

When OAuth is enabled, the server shows:
```
mcvsphere v0.2.1
────────────────────────────────────────
Starting HTTP transport on 0.0.0.0:8080
OAuth: ENABLED via https://auth.example.com/application/o/mcvsphere/
RBAC: ENABLED - permissions enforced via groups
────────────────────────────────────────
```

---

## OIDC Provider Setup

### Authentik (Recommended)

1. **Create OAuth2/OIDC Provider:**
   - Name: `mcvsphere`
   - Client Type: **Confidential**
   - Redirect URIs:
     - `http://localhost:*/callback` (for local dev)
     - `https://mcp.example.com/auth/callback`
   - Signing Key: Select RS256 certificate

2. **Create Application:**
   - Name: `mcvsphere`
   - Slug: `mcvsphere`
   - Provider: Select provider from step 1

3. **Create Groups:**
   - `vsphere-readers`
   - `vsphere-operators`
   - `vsphere-admins`
   - `vsphere-host-admins`
   - `vsphere-super-admins`

4. **Add Scope Mapping for Groups:**
   - Ensure `groups` claim is included in tokens
   - Authentik includes this by default

5. **Note Credentials:**
   - Copy Client ID and Client Secret
   - Discovery URL: `https://auth.example.com/application/o/mcvsphere/.well-known/openid-configuration`

### Other Providers

The same pattern works with Keycloak, Auth0, Okta, etc. Key requirements:
- OIDC Discovery endpoint (`.well-known/openid-configuration`)
- JWT access tokens (not opaque)
- `groups` claim in tokens with group names

---

## OAuth Flow

```
1. Client connects to mcvsphere
   → POST /mcp (no auth)
   → Server returns 401 + OAuth metadata URL

2. Client initiates OAuth flow
   → Opens browser to OIDC provider
   → User logs in
   → Provider redirects with authorization code

3. Client exchanges code for tokens
   → POST to provider token endpoint
   → Receives JWT access token

4. Client reconnects with token
   → POST /mcp with Authorization: Bearer <jwt>
   → Server validates JWT via JWKS
   → Server extracts user + groups
   → RBACMiddleware checks permissions
   → User can invoke allowed tools

5. Tool invocation
   → Client: "power on web-server"
   → Middleware: Validate user has POWER_OPS
   → Tool: Execute pyvmomi call
   → Audit: Log with user identity
   → Client: Receive response
```

---

## Implementation Status

### Completed

- [x] OIDCProxy configuration (`auth.py`)
- [x] Permission levels and tool mappings (`permissions.py`)
- [x] RBACMiddleware with FastMCP integration (`middleware.py`)
- [x] Audit logging with user context (`audit.py`)
- [x] Server integration with OAuth + RBAC (`server.py`)
- [x] Startup banner showing OAuth/RBAC status
- [x] Security fix: deny-by-default for no groups
- [x] Authentik setup with 5 vsphere-* groups

### Future Enhancements

- [ ] Per-user vCenter credential mapping (Vault integration)
- [ ] Rate limiting per user
- [ ] Session management and token refresh
- [ ] Admin tools for permission management
- [ ] Prometheus metrics for RBAC decisions

---

## Security Considerations

1. **Default Deny**: Users without recognized groups get NO access
2. **Token Validation**: JWTs validated via OIDC provider's JWKS endpoint
3. **Audit Trail**: All operations logged with user identity
4. **Secrets**: Client secrets should be stored securely (env vars, Docker secrets, Vault)
5. **HTTPS**: Production deployments should use TLS (via Caddy, nginx, etc.)
6. **Service Account**: Use minimal vCenter permissions for the service account

---

## Troubleshooting

### "401 Unauthorized" on all requests
- Check `OAUTH_ISSUER_URL` points to valid OIDC discovery endpoint
- Verify client ID and secret match provider configuration
- Ensure token hasn't expired

### "Permission denied" errors
- Check user's group memberships in OIDC provider
- Verify groups claim is included in JWT (decode at jwt.io)
- Confirm group names match exactly (e.g., `vsphere-admins` not `vsphere_admins`)

### Token validation fails
- Ensure OIDC provider issues JWTs (not opaque tokens)
- Check signing key is configured in provider
- Verify `OAUTH_BASE_URL` matches redirect URI in provider

### Audit logs not showing user
- Check `groups` scope is requested
- Verify token contains `preferred_username` or `email` claim
