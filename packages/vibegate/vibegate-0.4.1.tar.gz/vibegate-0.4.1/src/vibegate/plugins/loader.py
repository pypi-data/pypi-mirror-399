from __future__ import annotations

from dataclasses import dataclass
from importlib import metadata
import logging
from typing import Any, Dict, Iterable, Sequence

from vibegate.config import PluginGroupConfig


@dataclass(frozen=True)
class LoadedPlugin:
    name: str
    plugin: Any
    config: Dict[str, Any]


@dataclass(frozen=True)
class LoadedCheckPack:
    """Loaded check pack with metadata and checks."""

    name: str
    pack: Any
    metadata: Any
    checks: Sequence[Any]
    load_error: str | None = None


def _entry_points_for_group(group: str) -> Sequence[metadata.EntryPoint]:
    entry_points: Any = metadata.entry_points()  # Type varies by Python version
    if hasattr(entry_points, "select"):
        return list(entry_points.select(group=group))
    if isinstance(entry_points, dict):
        return list(entry_points.get(group, []))
    return [entry_point for entry_point in entry_points if entry_point.group == group]


def _configured_names(config: PluginGroupConfig) -> set[str]:
    return set(config.enabled) | set(config.config.keys())


def _desired_names(config: PluginGroupConfig, available: Iterable[str]) -> list[str]:
    disabled = set(config.disabled)
    if config.enabled:
        return [name for name in config.enabled if name not in disabled]
    return [name for name in sorted(available) if name not in disabled]


def load_plugins(
    group: str,
    config: PluginGroupConfig,
    logger: logging.Logger,
) -> list[LoadedPlugin]:
    entry_points = _entry_points_for_group(group)
    entry_point_map = {entry_point.name: entry_point for entry_point in entry_points}

    for name in sorted(_configured_names(config)):
        if name not in entry_point_map:
            logger.warning(
                "Configured plugin '%s' for group '%s' cannot be loaded (entry point not found).",
                name,
                group,
            )

    loaded: list[LoadedPlugin] = []
    for name in _desired_names(config, entry_point_map.keys()):
        entry_point = entry_point_map.get(name)
        if entry_point is None:
            logger.warning(
                "Configured plugin '%s' for group '%s' cannot be loaded (entry point not found).",
                name,
                group,
            )
            continue
        try:
            plugin = entry_point.load()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to load plugin '%s' from group '%s': %s",
                name,
                group,
                exc,
            )
            continue
        loaded.append(
            LoadedPlugin(
                name=name,
                plugin=plugin,
                config=dict(config.config.get(name, {})),
            )
        )
    return loaded


def load_check_packs(
    logger: logging.Logger,
) -> list[LoadedCheckPack]:
    """Load all check packs from entry points.

    Entry point group: vibegate.checkpacks

    Each entry point should point to a CheckPack class or factory function.

    Returns packs in deterministic order sorted by entry point name.
    """
    entry_points = _entry_points_for_group("vibegate.checkpacks")
    # Sort entry points deterministically by name to ensure consistent ordering
    sorted_entry_points = sorted(entry_points, key=lambda ep: ep.name)
    loaded: list[LoadedCheckPack] = []

    for entry_point in sorted_entry_points:
        name = entry_point.name
        try:
            pack_factory = entry_point.load()
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to load check pack '%s': %s",
                name,
                exc,
            )
            loaded.append(
                LoadedCheckPack(
                    name=name,
                    pack=None,
                    metadata=None,
                    checks=[],
                    load_error=str(exc),
                )
            )
            continue

        try:
            pack_instance = pack_factory() if callable(pack_factory) else pack_factory
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to instantiate check pack '%s': %s",
                name,
                exc,
            )
            loaded.append(
                LoadedCheckPack(
                    name=name,
                    pack=None,
                    metadata=None,
                    checks=[],
                    load_error=str(exc),
                )
            )
            continue

        try:
            pack_metadata = pack_instance.metadata  # type: ignore[attr-defined]
            # Cast to Any first to avoid "Never is not iterable" error, then wrap in list
            checks_iterable: Any = pack_instance.register_checks()  # type: ignore[attr-defined]
            pack_checks = list(checks_iterable)
            loaded.append(
                LoadedCheckPack(
                    name=name,
                    pack=pack_instance,
                    metadata=pack_metadata,
                    checks=pack_checks,
                    load_error=None,
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to extract metadata/checks from pack '%s': %s",
                name,
                exc,
            )
            loaded.append(
                LoadedCheckPack(
                    name=name,
                    pack=pack_instance,
                    metadata=None,
                    checks=[],
                    load_error=str(exc),
                )
            )

    return loaded


def discover_all_plugins(
    logger: logging.Logger,
) -> dict[str, list[metadata.EntryPoint]]:
    """Discover all available plugins grouped by entry point group.

    Returns a mapping of group name to list of entry points.
    """
    all_plugins: dict[str, list[metadata.EntryPoint]] = {
        "vibegate.checks": [],
        "vibegate.emitters": [],
        "vibegate.checkpacks": [],
    }

    for group in all_plugins.keys():
        try:
            all_plugins[group] = list(_entry_points_for_group(group))
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to discover plugins for group '%s': %s",
                group,
                exc,
            )

    return all_plugins
