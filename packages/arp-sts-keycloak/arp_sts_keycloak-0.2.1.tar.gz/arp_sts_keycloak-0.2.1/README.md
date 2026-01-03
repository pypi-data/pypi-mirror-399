# ARP STS Keycloak

Keycloak-based dev STS helper for the ARP Standard. This package provides a small CLI
that writes a ready-to-run Keycloak docker compose file plus a preconfigured `arp-dev`
realm with ARP clients.

## Quick start

```bash
pip install arp-sts-keycloak
arp-sts-keycloak init --output ./arp-keycloak
cd ./arp-keycloak
docker compose up -d
```

Keycloak will be available at `http://localhost:8080`.

## Default realm

The bundled realm is named `arp-dev` and includes the following clients:

- `arp-daemon` (client secret: `arp-daemon-secret`)
- `arp-runtime` (client secret: `arp-runtime-secret`)
- `arp-tool-registry` (client secret: `arp-tool-registry-secret`)
- `arp-run-gateway` (client secret: `arp-run-gateway-secret`)
- `arp-run-coordinator` (client secret: `arp-run-coordinator-secret`)
- `arp-composite-executor` (client secret: `arp-composite-executor-secret`)
- `arp-atomic-executor` (client secret: `arp-atomic-executor-secret`)
- `arp-node-registry` (client secret: `arp-node-registry-secret`)
- `arp-selection-service` (client secret: `arp-selection-service-secret`)
- `arp-pdp` (client secret: `arp-pdp-secret`)

Each client is configured for client-credentials flow and includes an audience mapper
so the access token `aud` claim matches the client ID.

## Get a token (client credentials)

```bash
curl -sS \
  -X POST \
  http://localhost:8080/realms/arp-dev/protocol/openid-connect/token \
  -d 'grant_type=client_credentials' \
  -d 'client_id=arp-runtime' \
  -d 'client_secret=arp-runtime-secret'
```

Use the resulting `access_token` as `Authorization: Bearer <token>`.

## Service configuration hints

- Issuer: `http://localhost:8080/realms/arp-dev`
- OIDC discovery: `http://localhost:8080/realms/arp-dev/.well-known/openid-configuration`
- Audience: match the ARP service ID (for example `arp-runtime`)

## Notes

- This package is intended for local development and testing.
- `arp-sts-keycloak init` writes two files: `docker-compose.yml` and `realm-export.json`.
- Use `--force` to overwrite existing files.
