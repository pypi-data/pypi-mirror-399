"""Machine-aware LLM configuration recommendations."""

from __future__ import annotations

import logging
import platform
import subprocess
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class SystemResources:
    """Detected system resources."""

    total_ram_gb: float
    cpu_cores: int
    nvidia_vram_gb: Optional[float]
    is_apple_silicon: bool
    platform_name: str


@dataclass(frozen=True)
class RecommendedLLMConfig:
    """Recommended LLM configuration for this machine."""

    provider: str  # "ollama" | "openai_compatible"
    model: str
    timeout_sec: int
    explanation: str
    detected_resources: SystemResources


def _get_total_ram_gb() -> float:
    """Get total system RAM in GB (cross-platform).

    Returns:
        Total RAM in GB, or 8.0 as fallback
    """
    try:
        system = platform.system().lower()

        if system == "darwin":  # macOS
            result = subprocess.run(
                ["sysctl", "-n", "hw.memsize"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                bytes_ram = int(result.stdout.strip())
                return bytes_ram / (1024**3)  # Convert to GB

        elif system == "linux":
            # Read /proc/meminfo
            with open("/proc/meminfo") as f:
                for line in f:
                    if line.startswith("MemTotal:"):
                        # Format: "MemTotal:       16384000 kB"
                        kb_ram = int(line.split()[1])
                        return kb_ram / (1024**2)  # Convert to GB

        elif system == "windows":
            # Try wmic (Windows Management Instrumentation)
            result = subprocess.run(
                ["wmic", "computersystem", "get", "totalphysicalmemory"],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if result.returncode == 0:
                lines = result.stdout.strip().split("\n")
                if len(lines) >= 2:
                    bytes_ram = int(lines[1].strip())
                    return bytes_ram / (1024**3)  # Convert to GB

    except Exception as e:
        logger.debug(f"Failed to detect RAM: {e}")

    return 8.0  # Fallback


def _get_cpu_cores() -> int:
    """Get number of CPU cores (cross-platform).

    Returns:
        Number of CPU cores, or 4 as fallback
    """
    try:
        import os

        cores = os.cpu_count()
        return cores if cores else 4
    except Exception as e:
        logger.debug(f"Failed to detect CPU cores: {e}")
        return 4


def _get_nvidia_vram_gb() -> Optional[float]:
    """Get NVIDIA GPU VRAM in GB if available.

    Returns:
        VRAM in GB, or None if no NVIDIA GPU detected
    """
    try:
        result = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=memory.total",
                "--format=csv,noheader,nounits",
            ],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            # Output is in MiB, can be multiple lines for multiple GPUs
            lines = result.stdout.strip().split("\n")
            if lines:
                # Use first GPU
                mib_vram = float(lines[0].strip())
                return mib_vram / 1024  # Convert to GB

    except FileNotFoundError:
        # nvidia-smi not found
        pass
    except Exception as e:
        logger.debug(f"Failed to detect NVIDIA VRAM: {e}")

    return None


def _is_apple_silicon() -> bool:
    """Check if running on Apple Silicon (M1/M2/M3).

    Returns:
        True if Apple Silicon detected
    """
    if platform.system().lower() != "darwin":
        return False

    try:
        result = subprocess.run(
            ["sysctl", "-n", "machdep.cpu.brand_string"],
            capture_output=True,
            text=True,
            timeout=2,
        )
        if result.returncode == 0:
            brand = result.stdout.strip().lower()
            # Apple Silicon chips have "apple" in brand string
            return "apple" in brand

    except Exception as e:
        logger.debug(f"Failed to detect Apple Silicon: {e}")

    return False


def detect_system_resources() -> SystemResources:
    """Detect system resources for LLM recommendation.

    Returns:
        Detected system resources
    """
    return SystemResources(
        total_ram_gb=_get_total_ram_gb(),
        cpu_cores=_get_cpu_cores(),
        nvidia_vram_gb=_get_nvidia_vram_gb(),
        is_apple_silicon=_is_apple_silicon(),
        platform_name=platform.system(),
    )


def recommend_llm_config(
    resources: Optional[SystemResources] = None,
) -> RecommendedLLMConfig:
    """Recommend LLM configuration based on system resources.

    Args:
        resources: Detected system resources (auto-detected if None)

    Returns:
        Recommended LLM configuration
    """
    if resources is None:
        resources = detect_system_resources()

    # Determine model based on resources
    # Decision tree:
    # - < 8GB RAM: qwen2.5-coder:7b (lightest)
    # - 8-16GB RAM: qwen2.5-coder:7b (safe default)
    # - 16-24GB RAM or 8GB+ VRAM: qwen2.5-coder:14b (better quality)
    # - 24GB+ RAM or 12GB+ VRAM: deepseek-coder-v2:16b (best quality)

    ram_gb = resources.total_ram_gb
    vram_gb = resources.nvidia_vram_gb or 0.0

    # Build explanation parts
    explanation_parts = []

    if ram_gb < 8:
        model = "qwen2.5-coder:7b"
        timeout_sec = 30
        explanation_parts.append(
            f"Your system has {ram_gb:.1f}GB RAM, so we recommend the lightweight 7B model."
        )
        explanation_parts.append(
            "This model is fast and works well on systems with limited memory."
        )

    elif ram_gb >= 24 or vram_gb >= 12:
        model = "deepseek-coder-v2:16b"
        timeout_sec = 90
        if vram_gb >= 12:
            explanation_parts.append(
                f"Your NVIDIA GPU has {vram_gb:.1f}GB VRAM - excellent for running larger models!"
            )
        else:
            explanation_parts.append(
                f"Your system has {ram_gb:.1f}GB RAM - plenty for high-quality models."
            )
        explanation_parts.append(
            "DeepSeek Coder V2 16B provides the best code understanding and suggestions."
        )
        if resources.is_apple_silicon:
            explanation_parts.append(
                "Apple Silicon's unified memory will help with inference speed."
            )

    elif ram_gb >= 16 or vram_gb >= 8:
        model = "qwen2.5-coder:14b"
        timeout_sec = 60
        if vram_gb >= 8:
            explanation_parts.append(
                f"Your NVIDIA GPU has {vram_gb:.1f}GB VRAM - great for medium models."
            )
        else:
            explanation_parts.append(
                f"Your system has {ram_gb:.1f}GB RAM - good for medium-sized models."
            )
        explanation_parts.append(
            "Qwen 2.5 Coder 14B offers a nice balance of quality and speed."
        )

    else:  # 8-16GB RAM
        model = "qwen2.5-coder:7b"
        timeout_sec = 30
        explanation_parts.append(
            f"Your system has {ram_gb:.1f}GB RAM - perfect for the 7B model."
        )
        explanation_parts.append(
            "This is our recommended default: fast, reliable, and code-focused."
        )
        if resources.is_apple_silicon:
            explanation_parts.append(
                "Apple Silicon neural engine will accelerate inference."
            )

    explanation = " ".join(explanation_parts)

    return RecommendedLLMConfig(
        provider="ollama",
        model=model,
        timeout_sec=timeout_sec,
        explanation=explanation,
        detected_resources=resources,
    )


def format_recommendation(rec: RecommendedLLMConfig, show_details: bool = False) -> str:
    """Format recommendation as user-friendly string.

    Args:
        rec: Recommendation to format
        show_details: Include detailed resource information

    Returns:
        Formatted string for display
    """
    lines = []

    lines.append("🤖 Recommended LLM Configuration")
    lines.append("=" * 50)
    lines.append("")
    lines.append(f"Provider:  {rec.provider}")
    lines.append(f"Model:     {rec.model}")
    lines.append(f"Timeout:   {rec.timeout_sec} seconds")
    lines.append("")
    lines.append("Why this recommendation?")
    lines.append(rec.explanation)

    if show_details:
        lines.append("")
        lines.append("Detected Resources:")
        lines.append("-" * 50)
        res = rec.detected_resources
        lines.append(f"Platform:     {res.platform_name}")
        lines.append(f"Total RAM:    {res.total_ram_gb:.1f} GB")
        lines.append(f"CPU Cores:    {res.cpu_cores}")

        if res.nvidia_vram_gb:
            lines.append(f"NVIDIA VRAM:  {res.nvidia_vram_gb:.1f} GB")
        else:
            lines.append("NVIDIA VRAM:  Not detected")

        if res.is_apple_silicon:
            lines.append("Apple Silicon: Yes (unified memory)")
        else:
            lines.append("Apple Silicon: No")

    return "\n".join(lines)
