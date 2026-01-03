# Local Models Guide

## Overview

VibeGate can use a local AI model to make code quality issues easier to understand. The helper runs **entirely on your machine**—no data leaves your computer.

This guide covers two approaches:
1. **Ollama** (easy path for most users)
2. **OpenAI-compatible servers** (advanced path for power users)

## Quick Start: Ollama (Recommended)

### 1. Install Ollama

**macOS:**
```bash
brew install ollama
```

**Linux:**
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

**Windows:**
Download from https://ollama.com/download

### 2. Pull a Model

```bash
# Recommended: Qwen2.5-Coder 7B (fast, good quality)
ollama pull qwen2.5-coder:7b

# Alternative: Better quality, more memory
ollama pull qwen2.5-coder:14b

# Alternative: Best quality, powerful machine required
ollama pull deepseek-coder-v2:16b
```

### 3. Run VibeGate Setup

```bash
vibegate init .
```

The wizard will detect Ollama and guide you through model selection.

### 4. Verify

```bash
vibegate run .
```

If LLM is enabled, you'll see enhanced explanations in `.vibegate/plain_report.md` and `artifacts/proposals/`.

## Let VibeGate Recommend a Model

Not sure which model to use? Let VibeGate analyze your system and recommend the best option.

### Command

```bash
vibegate llm recommend
```

**Output example:**
```
🔍 Analyzing your system resources...

🤖 Recommended LLM Configuration
==================================================

Provider:  ollama
Model:     qwen2.5-coder:14b
Timeout:   60 seconds

Why this recommendation?
Your system has 16.0GB RAM - good for medium-sized models. Qwen 2.5 Coder 14B offers a nice balance of quality and speed.
```

### Show Details

Want to see what VibeGate detected?

```bash
vibegate llm recommend --details
```

**Output includes:**
- Platform (macOS, Linux, Windows)
- Total RAM (GB)
- CPU cores
- NVIDIA VRAM (if detected)
- Apple Silicon detection (unified memory hint)

### During Setup

The recommendation feature is also available during `vibegate init`:

```bash
vibegate init .
```

When asked to choose a model:

```
📋 Choose your model:

   0. 🎯 Recommend for my machine (auto-detect)
   ✨ 1. Qwen 2.5 Coder 7B - Fast, code-focused (Recommended) (4GB RAM)
      2. Qwen 2.5 Coder 14B - Better quality, needs more RAM (8GB RAM)
      3. DeepSeek Coder V2 16B - High quality, slower (10GB RAM)
      4. CodeLlama 13B - Good quality, widely compatible (8GB RAM)
      5. Skip for now

Your choice [0]:
```

Select `0` to get a personalized recommendation based on your machine's resources.

### How It Works

The recommendation engine detects:

1. **Total RAM** (cross-platform: macOS, Linux, Windows)
2. **CPU cores** (for performance estimation)
3. **NVIDIA GPU VRAM** (if `nvidia-smi` is available)
4. **Apple Silicon** (M1/M2/M3 unified memory)

Based on these resources, it suggests:

- **< 8GB RAM**: `qwen2.5-coder:7b` (lightest)
- **8-16GB RAM**: `qwen2.5-coder:7b` (safe default)
- **16-24GB RAM or 8GB+ VRAM**: `qwen2.5-coder:14b` (better quality)
- **24GB+ RAM or 12GB+ VRAM**: `deepseek-coder-v2:16b` (best quality)

### Benefits

✅ **No guesswork** - Get a recommendation tailored to your hardware
✅ **Avoid out-of-memory errors** - Won't recommend models too large for your system
✅ **Maximize quality** - Suggests the best model your hardware can handle
✅ **100% local** - No network calls, just local resource detection

## Advanced: OpenAI-Compatible Servers

If you're running a local server like **vLLM**, **LM Studio**, or **llama.cpp server**, you can use it instead of Ollama.

### 1. Start Your Server

**Example with vLLM:**
```bash
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-7B-Instruct \
  --host 0.0.0.0 \
  --port 8000
```

**Example with LM Studio:**
1. Open LM Studio
2. Load a model (e.g., `qwen2.5-coder-7b-instruct`)
3. Start the local server (default: `http://localhost:1234/v1`)

**Example with llama.cpp:**
```bash
./server -m models/qwen2.5-coder-7b-q4_k_m.gguf \
  --host 127.0.0.1 \
  --port 8080
```

### 2. Configure VibeGate

Add to `vibegate.yaml`:

```yaml
llm:
  enabled: true
  provider: openai_compatible
  cache_dir: .vibegate/llm_cache
  openai_compatible:
    base_url: http://localhost:8000/v1  # Your server URL
    model: Qwen/Qwen2.5-Coder-7B-Instruct  # Model identifier
    temperature: 0.3
    timeout_sec: 60
    # extra_headers: {}  # Optional: for auth if your server requires it
  features:
    explain_findings: true
    generate_prompts: true
```

**Note:** Most local servers don't require authentication. If your server does, use `extra_headers`:

```yaml
    extra_headers:
      Authorization: "Bearer <your-token>"
```

### 3. Test

```bash
vibegate run .
```

## Model Recommendations

### Performance Comparison

| Model | Speed | Quality | Memory | CPU/GPU | Best For |
|-------|-------|---------|--------|---------|----------|
| **Qwen2.5-Coder 7B** | ⚡⚡⚡ | ⭐⭐⭐ | 4GB | CPU or small GPU | Default choice |
| **Qwen2.5-Coder 14B** | ⚡⚡ | ⭐⭐⭐⭐ | 8GB | Mid-range GPU | Better quality |
| **DeepSeek-Coder-V2 16B** | ⚡ | ⭐⭐⭐⭐⭐ | 10GB+ | High-end GPU | Best quality |
| **CodeLlama 7B** | ⚡⚡⚡ | ⭐⭐ | 4GB | CPU or small GPU | Older, still works |

### License Information

**Important:** Each model has its own license. Some are OSI-approved licenses (like Apache 2.0), while others are custom model licenses.

| Model | License | Commercial Use | Notes |
|-------|---------|----------------|-------|
| **Qwen2.5-Coder** | Apache 2.0 | ✅ Yes | Permissive OSI license |
| **DeepSeek-Coder-V2** | Model License (weights) / MIT (code) | ✅ Yes (with restrictions) | Check model license terms |
| **CodeLlama** | Llama License | ✅ Yes | Custom Meta license |

**Always check the model license before production use.**

### Choosing a Model

**For most users:**
- **Qwen2.5-Coder 7B** is the best balance of speed, quality, and memory usage
- Works on modest hardware (M1 Mac, modern laptop CPU, or any GPU with 4GB+ VRAM)

**For better quality:**
- **Qwen2.5-Coder 14B** if you have 8GB+ GPU or 16GB+ RAM
- Noticeably better explanations and context understanding

**For maximum quality:**
- **DeepSeek-Coder-V2 16B** if you have a high-end GPU (16GB+ VRAM)
- Best code understanding and fix suggestions, but slow on CPU

**For older hardware:**
- **CodeLlama 7B** works well on older machines
- Not as good as Qwen, but still helpful

## Configuration Reference

### Full Configuration Example

```yaml
llm:
  # Enable/disable LLM features
  enabled: true

  # Provider: "ollama" or "openai_compatible"
  provider: ollama

  # Cache directory (stores responses by fingerprint + model)
  cache_dir: .vibegate/llm_cache

  # Ollama-specific config
  ollama:
    base_url: http://localhost:11434
    model: qwen2.5-coder:7b
    temperature: 0.3  # Lower = more deterministic, higher = more creative

  # OpenAI-compatible config (alternative to ollama)
  openai_compatible:
    base_url: http://localhost:8000/v1
    model: Qwen/Qwen2.5-Coder-7B-Instruct
    temperature: 0.3
    timeout_sec: 60
    # extra_headers: {}  # Optional: for auth if your server requires it

  # Feature flags
  features:
    explain_findings: true  # Add explanations to plain report
    generate_prompts: true  # Generate agent prompts in proposals
```

### Temperature Guide

| Temperature | Behavior | Use Case |
|------------|----------|----------|
| **0.1 - 0.3** | More deterministic, focused | Default (recommended) |
| **0.4 - 0.6** | Balanced creativity | Experimental |
| **0.7 - 1.0** | More creative, varied | Not recommended |

**For VibeGate, use 0.3 or lower** to keep explanations consistent and focused.

## Troubleshooting

### Model Server Not Reachable

**Symptom:**
```
⚠️  LLM configured but not available. Proposals will not include AI content.
```

**Solutions:**

1. **Check Ollama is running:**
   ```bash
   ollama list  # Should show your models
   ```

   If not running:
   ```bash
   # macOS/Linux
   ollama serve

   # Or restart the service
   brew services restart ollama  # macOS
   systemctl restart ollama      # Linux
   ```

2. **Check the base URL:**
   ```bash
   curl http://localhost:11434/api/tags
   ```

   Should return JSON with model list. If not, Ollama isn't listening.

3. **Check firewall:**
   Make sure port 11434 (Ollama) or your custom port isn't blocked.

### Timeouts

**Symptom:**
LLM requests take forever or time out.

**Solutions:**

1. **Use a smaller model:**
   ```bash
   ollama pull qwen2.5-coder:7b  # Instead of 14b or 16b
   ```

2. **Check system resources:**
   ```bash
   top  # or htop
   ```

   If memory/CPU is maxed, close other apps or use a smaller model.

3. **Increase timeout in code** (if needed):
   Edit `src/vibegate/llm/ollama.py`:
   ```python
   # Increase from default (30s) to 120s
   response = ollama.chat(model=self.model, messages=messages, timeout=120.0)
   ```

### Slow Responses

**Symptom:**
LLM takes 10+ seconds per request.

**Solutions:**

1. **Use GPU if available:**
   ```bash
   # Check if Ollama is using GPU
   ollama ps
   ```

   If GPU not detected, reinstall Ollama with GPU support.

2. **Use quantized models:**
   ```bash
   # Qwen 7B with 4-bit quantization (faster, slightly lower quality)
   ollama pull qwen2.5-coder:7b-q4_0
   ```

3. **Check caching:**
   ```bash
   ls -lh .vibegate/llm_cache/
   ```

   Cached responses are instant. First run will be slow, subsequent runs use cache.

### Cache Behavior

**How it works:**

VibeGate caches LLM responses using:
- **Key:** `{finding.fingerprint}:{model_name}`
- **Storage:** `.vibegate/llm_cache/{hash}.json`

**Cache hits:**
- Same finding + same model = instant response (from cache)

**Cache misses:**
- New finding or different model = fresh LLM call

**Clear cache:**
```bash
rm -rf .vibegate/llm_cache/
```

### Model Won't Download

**Symptom:**
```bash
ollama pull qwen2.5-coder:7b
Error: connection refused
```

**Solutions:**

1. **Check internet connection:**
   ```bash
   ping ollama.com
   ```

2. **Check disk space:**
   ```bash
   df -h
   ```

   Models are 4-16GB. Make sure you have enough space.

3. **Try a different model:**
   ```bash
   ollama pull codellama:7b  # Smaller alternative
   ```

### Wrong Model Version

**Symptom:**
Model in `vibegate.yaml` doesn't match pulled model.

**Fix:**
```bash
# List pulled models
ollama list

# Update vibegate.yaml to match
# Example: if you have "qwen2.5-coder:14b" but config says "7b"
# Edit vibegate.yaml:
llm:
  ollama:
    model: qwen2.5-coder:14b  # Match what's in `ollama list`
```

## Disabling LLM Features

If you don't want to use LLM features:

### Option 1: Set `enabled: false`

```yaml
llm:
  enabled: false
```

### Option 2: Remove LLM Section Entirely

Just delete the `llm:` section from `vibegate.yaml`.

### Option 3: Uninstall Ollama (if not used elsewhere)

```bash
# macOS
brew uninstall ollama

# Linux
sudo systemctl stop ollama
sudo rm -rf /usr/local/bin/ollama
```

**VibeGate works perfectly without LLM features.** They're completely optional.

## Advanced: Custom Prompts

If you want to customize LLM prompts, edit `src/vibegate/llm/prompts.py`:

```python
def explanation_prompt(finding: Finding) -> str:
    return f"""You are a friendly code quality assistant.

Explain this finding in plain English:

Rule: {finding.rule_id}
Message: {finding.message}
File: {finding.location.path}:{finding.location.line}

Guidelines:
- Use simple language (no jargon)
- Explain why it matters
- Be concise (2-3 sentences max)
"""
```

## Advanced: Provider Comparison

| Feature | Ollama | OpenAI-Compatible | Cloud APIs |
|---------|--------|-------------------|------------|
| **Local** | ✅ Yes | ✅ Yes | ❌ No |
| **Privacy** | ✅ Full | ✅ Full | ❌ Data sent to cloud |
| **Easy setup** | ✅ Very easy | ⚠️ Moderate | ✅ Easy |
| **Performance** | ⚡ Good | ⚡⚡ Better (if GPU) | ⚡⚡⚡ Best (cloud GPUs) |
| **Cost** | Free | Free | 💵 Paid per token |

**VibeGate only supports local providers** (Ollama and OpenAI-compatible local servers).

Cloud APIs like OpenAI, Anthropic Claude, etc. are **intentionally not supported** to maintain privacy and keep all processing local.

## FAQ

### Q: Do I need a GPU?

**A:** No, but it helps.

- **CPU only:** Works fine with 7B models (expect 5-10s per request)
- **GPU:** Much faster (1-2s per request), especially for 14B+ models

### Q: How much memory do I need?

**A:** Depends on model size:

- **Qwen 7B:** 4GB RAM (6GB recommended)
- **Qwen 14B:** 8GB RAM (10GB recommended)
- **DeepSeek 16B:** 10GB RAM (16GB recommended)

### Q: Can I use multiple models?

**A:** Yes, but only one at a time.

Change `model:` in `vibegate.yaml` and re-run `vibegate run .`.

### Q: Does it work offline?

**A:** Yes, once the model is downloaded.

Ollama downloads models to `~/.ollama/models/`. After download, no internet needed.

### Q: How do I update a model?

```bash
ollama pull qwen2.5-coder:7b  # Re-pull to get latest version
```

### Q: Can I self-host on a different machine?

**A:** Yes!

Run Ollama on a server and point `base_url` to it:

```yaml
llm:
  ollama:
    base_url: http://my-server:11434  # Remote Ollama
```

Just make sure the server is accessible from where you run VibeGate.

### Q: Is my code sent anywhere?

**A:** No.

When LLM is enabled:
- Findings (error messages, file paths, rule IDs) are sent to your **local** LLM server
- No code or findings are ever sent to the cloud
- Everything stays on your machine (or your self-hosted server)

## Next Steps

- **Product vision:** `docs/PRODUCT_VISION.md`
- **Architecture:** `docs/ARCHITECTURE.md`
- **Roadmap:** `docs/OPEN_CORE_ROADMAP.md`
- **Contributing:** `CONTRIBUTING.md`
