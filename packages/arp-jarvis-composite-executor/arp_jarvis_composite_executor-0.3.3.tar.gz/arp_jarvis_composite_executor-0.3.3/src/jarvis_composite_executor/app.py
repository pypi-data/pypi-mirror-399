from __future__ import annotations

import os

from arp_llm.settings import load_chat_model_from_env

from .auth import auth_client_from_env_optional, auth_settings_from_env_or_dev_secure
from .clients import NodeRegistryGatewayClient, SelectionGatewayClient
from .config import load_composite_config_from_env
from .executor import CompositeExecutor
from .utils import normalize_base_url


def create_app():
    selection_url = _require_url("JARVIS_SELECTION_URL", fallback="ARP_SELECTION_URL")
    node_registry_url = _require_url("JARVIS_NODE_REGISTRY_URL", fallback="ARP_NODE_REGISTRY_URL")

    if (auth_client := auth_client_from_env_optional()) is None:
        raise RuntimeError("ARP_AUTH_CLIENT_ID and ARP_AUTH_CLIENT_SECRET are required for outbound auth.")

    selection_service = SelectionGatewayClient(
        base_url=selection_url,
        auth_client=auth_client,
        audience=_audience_from_env("JARVIS_SELECTION_AUDIENCE"),
    )
    node_registry = NodeRegistryGatewayClient(
        base_url=node_registry_url,
        auth_client=auth_client,
        audience=_audience_from_env("JARVIS_NODE_REGISTRY_AUDIENCE"),
    )

    llm = load_chat_model_from_env()
    config = load_composite_config_from_env()

    return CompositeExecutor(
        selection_service=selection_service,
        node_registry=node_registry,
        llm=llm,
        config=config,
    ).create_app(
        title="JARVIS Composite Executor",
        auth_settings=auth_settings_from_env_or_dev_secure(),
    )


def _require_url(name: str, *, fallback: str | None = None) -> str:
    value = (os.environ.get(name) or "").strip()
    if not value and fallback:
        value = (os.environ.get(fallback) or "").strip()
    if not value:
        raise RuntimeError(f"{name} is required to start the Composite Executor")
    return normalize_base_url(value)


def _audience_from_env(name: str) -> str | None:
    value = (os.environ.get(name) or "").strip()
    if value:
        return value
    return None


app = create_app()
