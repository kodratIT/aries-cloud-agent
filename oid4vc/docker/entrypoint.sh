#!/bin/bash
set -e

if [ -z "$OID4VCI_PUBLIC_URL" ]; then
        echo "OID4VCI_PUBLIC_URL must be set to the public issuer URL."
        exit 1
fi

export OID4VCI_ENDPOINT="${OID4VCI_PUBLIC_URL%/}"
export STATUS_LIST_PUBLIC_URI=${STATUS_LIST_PUBLIC_URI:-${OID4VCI_ENDPOINT}/tenant/{tenant_id}/status/{list_number}}

echo "OID4VCI_ENDPOINT: $OID4VCI_ENDPOINT"
echo "STATUS_LIST_PUBLIC_URI: $STATUS_LIST_PUBLIC_URI"

exec "$@"
