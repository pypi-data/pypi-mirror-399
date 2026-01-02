from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Protocol, Sequence

from vibegate.checks import ToolResult
from vibegate.config import VibeGateConfig
from vibegate.evidence import EvidenceWriter
from vibegate.plugins.types import Finding


class ToolRunner(Protocol):
    def __call__(
        self,
        tool: str,
        args: Sequence[str],
        cwd: Path,
        timeout: int,
        env: dict[str, str],
    ) -> ToolResult: ...


@dataclass(frozen=True)
class PluginContext:
    repo_root: Path
    config: VibeGateConfig
    workspace_files: Sequence[Path]
    tool_runner: ToolRunner
    logger: logging.Logger
    evidence: EvidenceWriter


class CheckPlugin(Protocol):
    def run(self, context: PluginContext) -> Sequence[Finding]: ...


class EmitterPlugin(Protocol):
    def emit(
        self, context: PluginContext, findings: Sequence[Finding]
    ) -> Path | None: ...


class EvidenceHook(Protocol):
    def post_process(
        self, context: PluginContext, findings: Sequence[Finding]
    ) -> Sequence[Finding] | None: ...


@dataclass(frozen=True)
class CheckPackMetadata:
    """Metadata for a check pack."""

    pack_id: str
    pack_name: str
    description: str
    version: str = "1.0.0"
    author: str | None = None
    tags: Sequence[str] = ()


class CheckPack(Protocol):
    """Protocol for check packs that bundle multiple related checks."""

    @property
    def metadata(self) -> CheckPackMetadata:
        """Return pack metadata."""
        ...

    def register_checks(self) -> Sequence[CheckPlugin]:
        """Return all check plugins provided by this pack."""
        ...
