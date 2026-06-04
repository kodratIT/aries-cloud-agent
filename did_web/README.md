# DID Web Plugin

This plugin adds a tenant-authenticated ACA-Py admin route for creating local
`did:web` records and returning the DID document that must be published at the
corresponding HTTPS `did.json` URL.

## Create DID Web

`POST /did/web/create`

```json
{
  "did": "did:web:issuer.example.com",
  "key_type": "ed25519"
}
```

The response includes `did_document_url` and `did_document`. The controller is
responsible for publishing that DID document at the URL.
