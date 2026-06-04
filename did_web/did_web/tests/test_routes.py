import json
from typing import cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from acapy_agent.admin.request_context import AdminRequestContext
from acapy_agent.utils.testing import create_test_profile
from aiohttp import web
from did_web import routes as test_module


class TestRoutes(IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.profile = await create_test_profile(
            settings={
                "admin.admin_api_key": "admin_api_key",
                "admin.admin_insecure_mode": False,
            }
        )
        self.context = AdminRequestContext.test_context({}, self.profile)
        self.request_dict = {
            "context": self.context,
            "outbound_message_router": MagicMock(),
        }
        self.request = MagicMock(
            app={},
            match_info={},
            query={},
            __getitem__=lambda _, k: self.request_dict[k],
            headers={"x-api-key": "admin_api_key"},
            json=AsyncMock(return_value={}),
        )

    @patch("did_web.routes.DIDWebRegistrar")
    async def test_create_did_web(self, mock_did_web_registrar):
        mock_did_info = {
            "did": "did:web:issuer.example.com",
            "verkey": "7mbbTXhnPx8ux4LBVRPoHxpSACPRF9axYU4uwiKNhzUH",
            "key_type": "ed25519",
            "did_document_url": "https://issuer.example.com/.well-known/did.json",
            "did_document": {
                "@context": [
                    "https://www.w3.org/ns/did/v1",
                    "https://w3id.org/security/multikey/v1",
                ],
                "id": "did:web:issuer.example.com",
            },
        }
        mock_did_web_registrar.return_value.create = AsyncMock(
            return_value=mock_did_info
        )

        self.request.json = AsyncMock(
            return_value={
                "did": mock_did_info["did"],
                "key_type": mock_did_info["key_type"],
            }
        )

        result = await test_module.did_web_create(self.request)
        body = cast(bytes, result.body)

        assert result.status == 200
        assert json.loads(body) == mock_did_info
        mock_did_web_registrar.return_value.create.assert_awaited_once_with(
            "did:web:issuer.example.com", "ed25519", None
        )

    @patch("did_web.routes.DIDWebRegistrar")
    async def test_create_did_web_invalid_did(self, mock_did_web_registrar):
        mock_did_web_registrar.return_value.create = AsyncMock(
            side_effect=ValueError("DID must start with did:web:")
        )
        self.request.json = AsyncMock(return_value={"did": "did:key:z6MkExample"})

        with pytest.raises(web.HTTPBadRequest, match="DID must start with did:web:"):
            await test_module.did_web_create(self.request)
