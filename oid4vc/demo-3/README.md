## OID4VC ACA-Py Plugin Demo

This is a demo for developers to test and validate the current plugin functionality and to provide a fully working example of the functionality including w3c and ietf status lists. **Do not use for production deployments** 

This demo is configured to serve public subdomains through Nginx Proxy Manager.
Public domain values are kept in `.env` so the Docker Compose file does not
need to be edited per environment.

```
cp .env.example .env
# Edit .env:
# OID4VCI_PUBLIC_URL=https://issuer.your-domain.example
# AUTH_SERVER_PUBLIC_URL=https://auth.your-domain.example
# DEMO_PUBLIC_URL=https://demo.your-domain.example
# STATUS_LIST_PUBLIC_URI=https://issuer.your-domain.example/tenant/{tenant_id}/status/{list_number}
# WEBVH_SERVER_URL=https://webvh.your-domain.example
# PROXY_MANAGER_HTTP_PORT=80
# PROXY_MANAGER_HTTPS_PORT=443
# PROXY_MANAGER_ADMIN_PORT=81
docker compose up
```

Point DNS for these hostnames to this machine/server. Nginx Proxy Manager
listens on `PROXY_MANAGER_HTTP_PORT`, `PROXY_MANAGER_HTTPS_PORT`, and
`PROXY_MANAGER_ADMIN_PORT`.

Open the Proxy Manager UI at `http://localhost:81`. The default login is
`admin@example.com` / `changeme`; change it immediately, then create these
Proxy Hosts with SSL enabled:

| Public hostname | Local service |
| --- | --- |
| `issuer.your-domain.example` | `http://issuer:8082` |
| `auth.your-domain.example` | `http://auth-server:9001` |
| `demo.your-domain.example` | `http://demo-app:3000` |

`STATUS_LIST_PUBLIC_URI` must use the same public issuer hostname as
`OID4VCI_PUBLIC_URL`, with `/tenant/{tenant_id}/status/{list_number}` appended.

`WEBVH_SERVER_URL` must point to a DID WebVH server. The ACA-Py `webvh` plugin is
enabled in controller mode; configure tenant-specific WebVH settings through
`POST /did/webvh/configuration`.

`ISSUER_AGENT_ENDPOINT` defaults to `http://issuer:3000` for this local demo.
Only change it if you also expose ACA-Py inbound transport port `3000`.

### Demo Functionality

* Issue credentials via OpendID4VCI 1.0 - JWT, SD-JWT and mDOC
* Present Proof via OpendID4VP - JWT, SD-JWT (Not working, in development)
* Update the status of a JWT or SD-JWT credential
* Refresh an SD-JWT credetial
* Display credential records

### Current Status of the Demo

This demo works with the Bifold wallet and the Paradym wallet (exception of JWT type). Note, for mDOC support in Bifold core you need to import a trusted certificate created from the DID. Support for mDOC in Bifold is under active development.

Verification in the oid4vc plugin is still supporting an earlier draft of OID4VP and won't likely work with any modern wallet.

Overall the demo needs to be refactored due to the additional functionality added to index.js

### Credential Refresh

When a credential is refreshed it is updated and made available to the /credential endpoint.

To retrieve the credential a refresh token is required. In the future, dPOP will also be required.

You will need a mechanism to trigger the refresh in your wallet. One mechanism is to monitor the status of the credential via the credential status list. Bifold supports this option if configured to do so.
