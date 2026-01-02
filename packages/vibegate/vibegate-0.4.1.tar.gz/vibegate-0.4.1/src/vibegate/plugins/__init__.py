"""Plugin interfaces and types for VibeGate."""

from vibegate.plugins.api import (
    CheckPack,
    CheckPackMetadata,
    CheckPlugin,
    EmitterPlugin,
    EvidenceHook,
    PluginContext,
)
from vibegate.plugins.types import Finding, FindingLocation, FixpackTask, Remediation

__all__ = [
    "CheckPlugin",
    "CheckPack",
    "CheckPackMetadata",
    "EmitterPlugin",
    "EvidenceHook",
    "PluginContext",
    "Finding",
    "FindingLocation",
    "FixpackTask",
    "Remediation",
]
