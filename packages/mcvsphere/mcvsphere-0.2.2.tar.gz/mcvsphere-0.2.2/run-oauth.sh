#!/bin/bash
# Run mcvsphere with OAuth configuration

export COMPOSE_PROJECT_NAME=mcvsphere
export AUTHENTIK_SECRET_KEY=jeDUPs4aABdWlayZ9kYrwfdCqFpgNIispvsJnwnUr4KqxWhd
export AUTHENTIK_DB_PASSWORD=+tIlOB4O3QaDKbUBlBskb6I8lk4SgNri
export AUTHENTIK_BOOTSTRAP_EMAIL=admin@localhost
export AUTHENTIK_BOOTSTRAP_PASSWORD=mcvsphere-admin-123
export AUTHENTIK_PORT=9000
export AUTHENTIK_HTTPS_PORT=9443
export AUTHENTIK_HOST=mcvsphere-auth.l.supported.systems

export VCENTER_HOST=10.20.0.222
export VCENTER_USER=mcptest@vsphere.local
export VCENTER_PASSWORD='BtooVtooVqes1!'
export VCENTER_INSECURE=true
export VCENTER_NETWORK='VM Network'

export OAUTH_ENABLED=true
export MCP_TRANSPORT=streamable-http
export MCP_HOST=0.0.0.0
export MCP_PORT=8080

export OAUTH_ISSUER_URL=https://mcvsphere-auth.l.supported.systems/application/o/mcvsphere/
export OAUTH_CLIENT_ID=YFaCL3wXaGjtaE8L32PYmhIYMaAHF3MQygymQSeR
export OAUTH_CLIENT_SECRET=bXvmNvDfnGqX3IgsgvC5XwQJY6rmCuiPkt1aDNhsh5Im2RXkIQBI0AOLG5kCBlwZzqEENvs7HEYF6oiLLBDspd2JF8xT8ojlzjMSFEL7oM9LNl5ZL3psaG7GbtRI7TZ9
export OAUTH_BASE_URL=https://mcp.l.supported.systems
export OAUTH_SCOPES='["openid", "profile", "email", "groups"]'

exec uv run mcvsphere
