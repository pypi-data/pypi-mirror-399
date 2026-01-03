"""Backward-compatible shim for agent payloads.

This module provides backward compatibility for imports from glaip_sdk.client._agent_payloads.
New code should import from glaip_sdk.client.payloads.agent package directly.

This file contains code that is duplicated in glaip_sdk.client.payloads.agent.__init__
for backward compatibility. The duplication is intentional.

Authors:
    Raymond Christopher (raymond.christopher@gdplabs.id)
"""

# pylint: disable=duplicate-code
import warnings

_warned = False


def _warn_deprecated_import() -> None:
    """Emit deprecation warning for importing from _agent_payloads.py shim."""
    global _warned
    if not _warned:
        warnings.warn(
            "Importing from glaip_sdk.client._agent_payloads is deprecated. "
            "Import from glaip_sdk.client.payloads.agent package directly instead.",
            DeprecationWarning,
            stacklevel=3,
        )
        _warned = True


# Import from new package structure
from glaip_sdk.client.payloads.agent import (  # noqa: E402
    AgentCreateRequest,
    AgentListParams,
    AgentListResult,
    AgentUpdateRequest,
    merge_payload_fields,
    resolve_language_model_fields,
)

_warn_deprecated_import()

# Re-export everything
__all__ = [
    "AgentCreateRequest",
    "AgentListParams",
    "AgentListResult",
    "AgentUpdateRequest",
    "merge_payload_fields",
    "resolve_language_model_fields",
]
