"""DID Web registrar."""

from urllib.parse import unquote

from acapy_agent.wallet.base import BaseWallet
from acapy_agent.wallet.did_info import DIDInfo
from acapy_agent.wallet.key_type import ED25519, KeyTypes

from .did_method import WEB

_B58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
_B58_INDEX = {char: index for index, char in enumerate(_B58_ALPHABET)}


def _b58_to_bytes(value: str) -> bytes:
    """Decode base58btc text."""
    number = 0
    for char in value:
        if char not in _B58_INDEX:
            raise ValueError(f"Invalid base58 character: {char}")
        number = number * 58 + _B58_INDEX[char]

    byte_length = (number.bit_length() + 7) // 8
    decoded = number.to_bytes(byte_length, "big") if byte_length else b""
    leading_zeroes = len(value) - len(value.lstrip(_B58_ALPHABET[0]))
    return b"\x00" * leading_zeroes + decoded


def _bytes_to_b58(value: bytes) -> str:
    """Encode bytes as base58btc text."""
    number = int.from_bytes(value, "big")
    encoded = ""
    while number:
        number, remainder = divmod(number, 58)
        encoded = _B58_ALPHABET[remainder] + encoded

    leading_zeroes = len(value) - len(value.lstrip(b"\x00"))
    return _B58_ALPHABET[0] * leading_zeroes + (encoded or "")


def did_web_document_url(did: str) -> str:
    """Return the HTTPS did.json URL for a did:web DID."""
    validate_did_web(did)
    parts = [unquote(part) for part in did.removeprefix("did:web:").split(":")]
    domain = parts[0]

    if len(parts) == 1:
        return f"https://{domain}/.well-known/did.json"

    path = "/".join(parts[1:])
    return f"https://{domain}/{path}/did.json"


def validate_did_web(did: str) -> None:
    """Validate the minimal shape required for a did:web identifier."""
    if not did.startswith("did:web:"):
        raise ValueError("DID must start with did:web:")

    method_specific_id = did.removeprefix("did:web:")
    if not method_specific_id:
        raise ValueError("DID must include a domain")

    if any(char in method_specific_id for char in ("/", "?", "#")):
        raise ValueError(
            "DID must not contain '/', '?' or '#'; use ':' for path parts"
        )


def build_did_web_document(did: str, verkey: str) -> dict:
    """Build a did:web DID document from an Ed25519 base58 verkey."""
    validate_did_web(did)

    public_key_bytes = _b58_to_bytes(verkey)
    if len(public_key_bytes) != 32:
        raise ValueError("DID Web Ed25519 verkey must decode to 32 bytes")

    multikey = "z" + _bytes_to_b58(b"\xed\x01" + public_key_bytes)
    verification_method_id = f"{did}#{multikey}"

    return {
        "@context": [
            "https://www.w3.org/ns/did/v1",
            "https://w3id.org/security/multikey/v1",
        ],
        "id": did,
        "verificationMethod": [
            {
                "id": verification_method_id,
                "type": "Multikey",
                "controller": did,
                "publicKeyMultibase": multikey,
            }
        ],
        "authentication": [verification_method_id],
        "assertionMethod": [verification_method_id],
        "capabilityInvocation": [verification_method_id],
        "capabilityDelegation": [verification_method_id],
    }


class DIDWebRegistrar:
    """Create local did:web records and documents for publication."""

    def __init__(self, context):
        """Initialize the registrar."""
        self.context = context

    async def create(self, did: str, key_type: str = "ed25519", seed=None) -> dict:
        """Create a local did:web DID and return its publishable DID document."""
        validate_did_web(did)
        normalized_key_type = key_type.lower()
        if normalized_key_type != ED25519.key_type:
            raise ValueError(f"Unsupported key type {key_type}")

        async with self.context.session() as session:
            key_types = session.inject_or(KeyTypes)
            if not key_types:
                raise Exception("Failed to inject supported key types enum")

            key_type_instance = key_types.from_key_type(normalized_key_type) or ED25519
            wallet = session.inject_or(BaseWallet)
            if not wallet:
                raise Exception("Failed to inject wallet instance")

            key_info = await wallet.create_key(key_type_instance, seed=seed)
            did_document = build_did_web_document(did, key_info.verkey)

            did_info = DIDInfo(
                did=did,
                verkey=key_info.verkey,
                metadata={"did_document_url": did_web_document_url(did)},
                method=WEB,
                key_type=key_type_instance,
            )
            await wallet.store_did(did_info)

            return {
                "did": did,
                "verkey": key_info.verkey,
                "key_type": key_type_instance.key_type,
                "did_document_url": did_web_document_url(did),
                "did_document": did_document,
            }
