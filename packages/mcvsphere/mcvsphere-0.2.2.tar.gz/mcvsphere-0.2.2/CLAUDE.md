# mcvsphere - VMware vSphere MCP Server

MCP server providing Claude Code access to VMware vCenter/ESXi infrastructure.

## Two Operating Modes

### 1. STDIO Mode (Single User, No Auth)
Direct connection for local development or single-user setups.

```bash
export VCENTER_HOST=10.20.0.222
export VCENTER_USER=admin@vsphere.local
export VCENTER_PASSWORD='secret'
export VCENTER_INSECURE=true  # dev only

uv run mcvsphere
```

Add to Claude Code:
```bash
claude mcp add vsphere -- uv run --directory /path/to/mcvsphere mcvsphere
```

### 2. HTTP + OAuth Mode (Multi-User, Production)
Browser-based authentication via Authentik (or any OIDC provider).

```bash
./run-oauth.sh  # Starts HTTP server with OAuth
```

Add to Claude Code:
```bash
claude mcp add -t http vsphere https://mcp.l.supported.systems/mcp
```

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        STDIO MODE                           │
│  Claude Code ──stdio──► mcvsphere ──► vCenter/ESXi          │
│                         (no auth)                           │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                     HTTP + OAuth MODE                       │
│                                                             │
│  Claude Code ──HTTP──► mcvsphere ──► vCenter/ESXi           │
│       │                    │                                │
│       │    ┌───────────────┘                                │
│       │    │                                                │
│       └────┴──► Authentik (OIDC)                            │
│                 • OAuth 2.1 + PKCE                          │
│                 • Dynamic Client Registration               │
│                 • Group-based permissions                   │
└─────────────────────────────────────────────────────────────┘
```

## Environment Variables

### vCenter Connection (Required)
| Variable | Description | Example |
|----------|-------------|---------|
| `VCENTER_HOST` | vCenter/ESXi hostname or IP | `10.20.0.222` |
| `VCENTER_USER` | Service account username | `mcptest@vsphere.local` |
| `VCENTER_PASSWORD` | Service account password | `secret` |
| `VCENTER_INSECURE` | Skip SSL verification | `true` (dev only) |

### Transport (Optional)
| Variable | Description | Default |
|----------|-------------|---------|
| `MCP_TRANSPORT` | `stdio` or `streamable-http` | `stdio` |
| `MCP_HOST` | HTTP bind address | `0.0.0.0` |
| `MCP_PORT` | HTTP port | `8080` |

### OAuth (Only for HTTP mode)
| Variable | Description |
|----------|-------------|
| `OAUTH_ENABLED` | Set to `true` to enable |
| `OAUTH_ISSUER_URL` | OIDC discovery URL |
| `OAUTH_CLIENT_ID` | Authentik client ID |
| `OAUTH_CLIENT_SECRET` | Authentik client secret |
| `OAUTH_BASE_URL` | Public HTTPS URL for callbacks |

## Source Layout

```
src/mcvsphere/
├── __init__.py    # Entry point, CLI
├── server.py      # FastMCP server setup
├── auth.py        # OAuth/OIDC configuration (returns None if disabled)
├── config.py      # Pydantic settings model
├── connection.py  # vSphere connection management
├── middleware.py  # Permission checks & audit logging
├── permissions.py # RBAC permission definitions
└── tools/         # MCP tool implementations (94 tools)
    ├── vm_lifecycle.py
    ├── power_ops.py
    ├── snapshots.py
    └── ...
```

## OAuth Setup (Authentik)

### Prerequisites
- Authentik instance with HTTPS (e.g., `mcvsphere-auth.l.supported.systems`)
- Caddy reverse proxy for TLS termination
- Wildcard DNS for dev domains (e.g., `*.l.supported.systems`)

### Authentik Configuration
1. Create OAuth2/OpenID Provider (Confidential client)
2. Create Application linked to provider
3. Add redirect URI: `https://mcp.l.supported.systems/auth/callback`
4. Enable scopes: `openid`, `profile`, `email`, `groups`

### Key Files
| File | Purpose |
|------|---------|
| `run-oauth.sh` | Launch script with all OAuth env vars |
| `docker-compose.oauth.yml` | Authentik stack (PostgreSQL, Redis, server, worker) |
| `docker-compose.dev.yml` | Caddy proxy for host-running server |
| `.env.oauth` | OAuth environment variables (gitignored) |

### OAuth Flow
1. Claude Code connects to `https://mcp.l.supported.systems/mcp`
2. Server returns 401 → Claude discovers OAuth endpoints
3. Dynamic Client Registration at `/register`
4. PKCE authorization flow redirects to Authentik
5. User authenticates in browser
6. Token exchange → FastMCP issues JWT
7. Authenticated MCP requests succeed

**Note**: Authentik uses opaque access tokens that don't embed scope claims. The server validates authentication only, not scopes (`required_scopes=[]` in auth.py).

## Permission Groups

Map Authentik groups to vSphere permission levels:

| Group | Access Level |
|-------|--------------|
| `vsphere-super-admins` | Full access (create/delete VMs, host management) |
| `vsphere-admins` | VM management (power, snapshots, reconfigure) |
| `vsphere-operators` | Basic operations (console, monitoring) |
| `vsphere-viewers` | Read-only access |

## Troubleshooting

### STDIO mode: "Failed to connect to vCenter"
- Check `VCENTER_HOST`, `VCENTER_USER`, `VCENTER_PASSWORD`
- Try `VCENTER_INSECURE=true` for self-signed certs
- Verify network connectivity: `nc -zv $VCENTER_HOST 443`

### OAuth mode: "Bearer token rejected"
Check server logs (`/tmp/mcvsphere.log`) for specific failure:
- `Token missing required scopes` → Already fixed in auth.py
- `issuer mismatch` → Check `OAUTH_ISSUER_URL` matches Authentik exactly
- `audience mismatch` → Check client_id configuration

### OAuth mode: "Authentication successful but server still requires authentication"
Restart Claude Code session after completing OAuth flow.

### HTTP mode: Connection refused
- Check server is running: `pgrep -f mcvsphere`
- Check Caddy proxy: `docker logs caddy`
- Verify domain in Caddy labels: `docker inspect mcvsphere-proxy`

### Session conflicts
If switching between modes, kill existing sessions:
```bash
pkill -f mcvsphere
```
