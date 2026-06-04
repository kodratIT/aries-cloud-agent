"""DID Web ACA-Py plugin."""

import logging

from acapy_agent.config.injection_context import InjectionContext
from acapy_agent.wallet.did_method import DIDMethods

from .did_method import WEB

LOGGER = logging.getLogger(__name__)


async def setup(context: InjectionContext):
    """Register the did:web method."""
    LOGGER.info("did_web plugin setup...")
    did_methods = context.inject(DIDMethods)
    did_methods.register(WEB)
