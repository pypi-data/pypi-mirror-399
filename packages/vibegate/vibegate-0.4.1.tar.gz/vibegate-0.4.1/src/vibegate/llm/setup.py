"""Interactive setup wizard for LLM configuration."""

from __future__ import annotations

import logging
import platform
import shutil
import subprocess

import typer

logger = logging.getLogger(__name__)


# Model configurations with user-friendly descriptions
AVAILABLE_MODELS = [
    {
        "id": "qwen2.5-coder:7b",
        "name": "Qwen 2.5 Coder 7B",
        "description": "Fast, code-focused (Recommended)",
        "ram": "4GB",
        "recommended": True,
    },
    {
        "id": "qwen2.5-coder:14b",
        "name": "Qwen 2.5 Coder 14B",
        "description": "Better quality, needs more RAM",
        "ram": "8GB",
        "recommended": False,
    },
    {
        "id": "deepseek-coder-v2:16b",
        "name": "DeepSeek Coder V2 16B",
        "description": "High quality, slower",
        "ram": "10GB",
        "recommended": False,
    },
    {
        "id": "codellama:13b",
        "name": "CodeLlama 13B",
        "description": "Good quality, widely compatible",
        "ram": "8GB",
        "recommended": False,
    },
]


def check_ollama_installed() -> bool:
    """Check if Ollama is installed and available on PATH.

    Returns:
        True if ollama command is available
    """
    return shutil.which("ollama") is not None


def check_ollama_running() -> bool:
    """Check if Ollama server is running.

    Returns:
        True if Ollama server is responding
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_ollama_models() -> list[str]:
    """Get list of models already downloaded in Ollama.

    Returns:
        List of model names
    """
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0:
            return []

        # Parse output (skip header line)
        lines = result.stdout.strip().split("\n")[1:]
        models = []
        for line in lines:
            parts = line.split()
            if parts:
                models.append(parts[0])  # First column is model name
        return models
    except Exception as e:
        logger.debug(f"Failed to get Ollama models: {e}")
        return []


def print_ollama_install_instructions() -> None:  # pragma: no cover
    """Print instructions for installing Ollama based on platform."""
    system = platform.system().lower()

    typer.echo("\n📥 Ollama is not installed. Here's how to install it:\n")

    if system == "darwin":  # macOS
        typer.echo("macOS:")
        typer.secho(
            "  1. Visit: https://ollama.com/download", fg=typer.colors.CYAN, bold=True
        )
        typer.echo("  2. Download and run the macOS installer")
        typer.echo("  3. Or use Homebrew: brew install ollama")
    elif system == "linux":
        typer.echo("Linux:")
        typer.secho(
            "  Run: curl -fsSL https://ollama.com/install.sh | sh",
            fg=typer.colors.CYAN,
            bold=True,
        )
    elif system == "windows":
        typer.echo("Windows:")
        typer.secho(
            "  1. Visit: https://ollama.com/download", fg=typer.colors.CYAN, bold=True
        )
        typer.echo("  2. Download and run the Windows installer")
    else:
        typer.echo("Visit: https://ollama.com/download")

    typer.echo("\nAfter installing, run this command again to continue setup.")


def pull_model(model_id: str) -> bool:  # pragma: no cover
    """Pull/download an Ollama model.

    Args:
        model_id: Model identifier (e.g., "codellama:7b")

    Returns:
        True if successful
    """
    typer.echo(f"\n📦 Downloading {model_id}...")
    typer.echo("This may take a few minutes depending on your internet connection.\n")

    try:
        # Run ollama pull with live output
        process = subprocess.Popen(
            ["ollama", "pull", model_id],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Stream output
        if process.stdout:
            for line in process.stdout:
                typer.echo(line.rstrip())

        process.wait()

        if process.returncode == 0:
            typer.secho(
                f"\n✅ {model_id} downloaded successfully!", fg=typer.colors.GREEN
            )
            return True
        else:
            typer.secho(f"\n❌ Failed to download {model_id}", fg=typer.colors.RED)
            return False

    except Exception as e:
        typer.secho(f"\n❌ Error downloading model: {e}", fg=typer.colors.RED)
        return False


def _setup_openai_compatible() -> dict[str, str | bool]:  # pragma: no cover
    """Setup OpenAI-compatible provider (advanced users).

    Returns:
        Dictionary with OpenAI-compatible configuration
    """
    typer.echo("\n🔧 OpenAI-Compatible Server Setup")
    typer.echo("\nThis option works with local model servers like:")
    typer.echo("  • vLLM (vllm.ai)")
    typer.echo("  • SGLang (sgl-project.github.io)")
    typer.echo("  • LM Studio (lmstudio.ai)")
    typer.echo("  • text-generation-webui with OpenAI extension\n")

    # Get base URL
    base_url = typer.prompt(
        "Server base URL",
        default="http://localhost:8000/v1",
        show_default=True,
    )

    # Get model name
    typer.echo("\n📌 Model identifier (exact name from your server)")
    typer.echo("Examples:")
    typer.echo("  • Qwen/Qwen2.5-Coder-7B-Instruct")
    typer.echo("  • deepseek-ai/deepseek-coder-6.7b-instruct")
    typer.echo("  • codellama/CodeLlama-13b-Instruct-hf\n")

    model = typer.prompt("Model identifier")

    # Temperature
    temperature = typer.prompt(
        "Temperature (0.0-1.0, lower = more consistent)",
        default=0.3,
        type=float,
        show_default=True,
    )

    # Timeout
    timeout = typer.prompt(
        "Timeout in seconds",
        default=60,
        type=int,
        show_default=True,
    )

    typer.secho("\n✅ Configuration complete!", fg=typer.colors.GREEN)
    typer.echo(
        "\nNote: Make sure your OpenAI-compatible server is running before using VibeGate."
    )

    return {
        "provider": "openai_compatible",
        "base_url": base_url,
        "model": model,
        "temperature": temperature,
        "timeout_sec": timeout,
    }


def run_llm_setup_wizard() -> dict[str, str | bool] | None:  # pragma: no cover
    """Run the interactive LLM setup wizard.

    Returns:
        Dictionary with LLM configuration, or None if user skips
    """
    typer.echo("\n" + "=" * 70)
    typer.secho("🤖 AI Assistant Setup (Optional)", fg=typer.colors.CYAN, bold=True)
    typer.echo("=" * 70)

    typer.echo("\nVibeGate can use a local AI model to:")
    typer.echo("  • Explain issues in plain English")
    typer.echo("  • Generate fix prompts for your AI coding assistant")
    typer.echo("  • Make code quality fun and approachable")
    typer.echo("\n✨ This runs 100% locally - no data leaves your machine.\n")

    # Ask if user wants to set up LLM
    setup = typer.confirm("Would you like to set this up?", default=True)
    if not setup:
        typer.echo("\nNo problem! You can set this up later by running:")
        typer.secho("  vibegate init --force", fg=typer.colors.YELLOW)
        return None

    # Ask for provider type
    typer.echo("\n📋 Choose your local model backend:\n")
    typer.echo("  1. Ollama (Easy - recommended for beginners)")
    typer.echo("  2. OpenAI-compatible server (Advanced - vLLM, SGLang, LM Studio)")
    typer.echo("  3. Skip for now")

    provider_choice = typer.prompt(
        "\nYour choice", type=int, default=1, show_default=True
    )

    if provider_choice == 3:
        typer.echo("\nSkipping LLM setup. You can configure it later in vibegate.yaml")
        return None

    if provider_choice == 2:
        # OpenAI-compatible setup
        return _setup_openai_compatible()

    # Ollama setup (provider_choice == 1 or invalid)
    # Check if Ollama is installed
    typer.echo("\n🔍 Checking for Ollama...")
    if not check_ollama_installed():
        typer.secho("❌ Ollama not found", fg=typer.colors.RED)
        print_ollama_install_instructions()
        return None

    typer.secho("✅ Ollama is installed", fg=typer.colors.GREEN)

    # Check if Ollama is running
    if not check_ollama_running():
        typer.secho("\n⚠️  Ollama server is not running", fg=typer.colors.YELLOW)
        typer.echo("Start it with: ollama serve")
        typer.echo(
            "Or on macOS/Windows, Ollama should start automatically after installation.\n"
        )

        start_now = typer.confirm("Continue anyway?", default=True)
        if not start_now:
            return None

    # Get already installed models
    installed_models = get_ollama_models()
    if installed_models:
        typer.echo(f"\n📚 Models already installed: {', '.join(installed_models)}")

    # Show model options
    typer.echo("\n📋 Choose your model:\n")

    typer.echo("   0. 🎯 Recommend for my machine (auto-detect)")

    for idx, model in enumerate(AVAILABLE_MODELS, 1):
        prefix = "✨" if model["recommended"] else "  "
        already = " (already installed)" if model["id"] in installed_models else ""
        typer.echo(
            f"{prefix} {idx}. {model['name']} - {model['description']} ({model['ram']} RAM){already}"
        )

    typer.echo(f"   {len(AVAILABLE_MODELS) + 1}. Skip for now")

    # Get user choice
    choice = typer.prompt(
        "\nYour choice",
        type=int,
        default=0,
        show_default=True,
    )

    if choice < 0 or choice > len(AVAILABLE_MODELS) + 1:
        typer.secho("Invalid choice", fg=typer.colors.RED)
        return None

    if choice == len(AVAILABLE_MODELS) + 1:
        typer.echo("\nSkipping LLM setup. You can configure it later in vibegate.yaml")
        return None

    # Handle recommendation
    if choice == 0:
        from vibegate.llm.recommend import format_recommendation, recommend_llm_config

        typer.echo("\n🔍 Analyzing your system resources...\n")
        recommendation = recommend_llm_config()

        # Show recommendation
        typer.echo(format_recommendation(recommendation, show_details=True))
        typer.echo("")

        # Ask if user wants to use this recommendation
        use_recommendation = typer.confirm(
            "Would you like to use this recommendation?", default=True
        )

        if not use_recommendation:
            typer.echo(
                "\nNo problem! Choose manually from the list above, or run this wizard again."
            )
            return None

        # Use the recommended model
        model_id = recommendation.model
    else:
        selected_model = AVAILABLE_MODELS[choice - 1]
        model_id = selected_model["id"]

    # Pull model if not already installed
    if model_id not in installed_models:
        if not pull_model(model_id):
            typer.secho(
                "\n❌ Model download failed. Skipping LLM setup.",
                fg=typer.colors.RED,
            )
            return None
    else:
        typer.secho(f"\n✅ {model_id} is already installed", fg=typer.colors.GREEN)

    # Test the model
    typer.echo("\n🧪 Testing model...")
    try:
        import ollama  # type: ignore[import-untyped]

        client = ollama.Client(host="http://localhost:11434")
        response = client.generate(
            model=model_id,
            prompt="Reply with just 'OK' if you can read this.",
            options={"num_predict": 5},
        )
        if response and "response" in response:
            typer.secho("✅ Model is working!", fg=typer.colors.GREEN)
        else:
            typer.secho(
                "⚠️  Model test inconclusive, but continuing...",
                fg=typer.colors.YELLOW,
            )
    except Exception as e:
        logger.debug(f"Model test failed: {e}")
        typer.secho(
            "⚠️  Couldn't test model, but configuration will be saved",
            fg=typer.colors.YELLOW,
        )

    # Return configuration
    typer.secho("\n✅ LLM setup complete!", fg=typer.colors.GREEN, bold=True)

    return {
        "enabled": True,
        "provider": "ollama",
        "model": model_id,
    }


def get_llm_config_yaml(config: dict[str, str | bool]) -> str:
    """Generate YAML configuration block for LLM settings.

    Args:
        config: LLM configuration from wizard

    Returns:
        YAML string to append to vibegate.yaml
    """
    model = config.get("model", "codellama:7b")

    return f"""
llm:
  enabled: true
  provider: ollama
  cache_dir: .vibegate/llm_cache
  ollama:
    base_url: http://localhost:11434
    model: {model}
    temperature: 0.3
  features:
    explain_findings: true
    generate_prompts: true
"""
