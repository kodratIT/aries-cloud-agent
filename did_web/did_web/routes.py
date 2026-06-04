"""DID Web admin routes."""

import logging
from typing import Mapping

from acapy_agent.admin.decorators.auth import tenant_authentication
from acapy_agent.admin.request_context import AdminRequestContext
from acapy_agent.messaging.models.openapi import OpenAPISchema
from aiohttp import web
from aiohttp_apispec import docs, json_schema, response_schema
from marshmallow import fields
from marshmallow.validate import OneOf

from .registrar import DIDWebRegistrar

LOGGER = logging.getLogger(__name__)


class DIDWebRequestJSONSchema(OpenAPISchema):
    """Request schema for DID Web creation."""

    did = fields.String(
        required=True,
        metadata={
            "description": "DID Web identifier to store in the tenant wallet",
            "example": "did:web:issuer.example.com",
        },
    )

    key_type = fields.String(
        required=False,
        load_default="ed25519",
        validate=OneOf(["ed25519", "Ed25519"]),
        metadata={
            "description": "Key type to use for DID Web creation",
            "example": "ed25519",
        },
    )

    seed = fields.String(
        required=False,
        metadata={
            "description": "Optional seed to use for DID key material",
            "example": "000000000000000000000000Trustee1",
        },
    )


class DIDWebResponseSchema(OpenAPISchema):
    """Response schema for DID Web creation."""

    did = fields.Str(
        required=True,
        metadata={
            "description": "DID Web identifier that was created",
            "example": "did:web:issuer.example.com",
        },
    )
    verkey = fields.Str(required=True)
    key_type = fields.Str(required=True)
    did_document_url = fields.Str(required=True)
    did_document = fields.Raw(required=True)


@docs(tags=["did-web"], summary="Create a did:web DID.")
@json_schema(DIDWebRequestJSONSchema())
@response_schema(DIDWebResponseSchema(), 200)
@tenant_authentication
async def did_web_create(request: web.BaseRequest):
    """Request handler for creating a DID Web DID."""
    LOGGER.debug("Received create DID Web request")

    context: AdminRequestContext = request["context"]
    body = await request.json()

    try:
        did_info = await DIDWebRegistrar(context).create(
            body["did"], body.get("key_type", "ed25519"), body.get("seed") or None
        )
        return web.json_response(did_info)
    except ValueError as error:
        raise web.HTTPBadRequest(reason=str(error)) from error
    except Exception as error:
        raise web.HTTPInternalServerError(reason=str(error)) from error


async def register(app: web.Application):
    """Register endpoints."""
    app.add_routes([web.post("/did/web/create", did_web_create)])


def post_process_routes(app: web.Application):
    """Amend swagger API."""
    app_state: Mapping = app._state
    if "tags" not in app_state["swagger_dict"]:
        app_state["swagger_dict"]["tags"] = []

    app_state["swagger_dict"]["tags"].append(
        {
            "name": "did-web",
            "description": "DID Web plugin API",
        }
    )
