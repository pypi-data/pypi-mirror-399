# VibeGate Product Vision

## The Problem

**Modern development moves fast, but production needs trust.**

Today's AI-powered coding tools (GitHub Copilot, Claude Code, Cursor, etc.) help developers write code incredibly quickly—"vibe coding" at high velocity. But there's a gap:

- **Vibe-coded code is fast to write** but inconsistent in quality
- **Production deployments need reliability** that raw velocity doesn't guarantee
- **Quality gates exist** (pytest, ruff, pyright, etc.) but they're scattered, noisy, and hard for humans to interpret

The result? Teams either:
1. Skip quality checks (ship fast, break things)
2. Run checks manually (slow, inconsistent, easy to forget)
3. Have fragile CI that's constantly red and ignored

**VibeGate solves this by being the bridge between velocity and trust.**

## The Solution

VibeGate is a **deterministic quality gate with a friendly surface layer**.

### The Powerhouse Engine (Deterministic Core)

Under the hood, VibeGate is a comprehensive quality orchestrator that:

- **Runs all your checks in one command** (formatting, linting, type checking, tests, security scans)
- **Produces deterministic results** (same code + same config = same outcome, always)
- **Creates an audit trail** (evidence.jsonl proof log for compliance and debugging)
- **Generates actionable fix packs** (JSON/markdown task lists with remediation steps)

**This is the gate.** It's deterministic. It never changes. It doesn't need AI. It's the foundation of trust.

### The Friendly Surface (Human Layer)

On top of the engine, VibeGate adds a translation layer:

- **Plain English reports** (explains "what's wrong" and "why it matters" in simple terms)
- **Agent prompt packs** (copy-paste instructions for AI coding assistants)
- **Optional local LLM helpers** (translate technical findings into friendly explanations)

**This is the interface.** It makes the gate accessible to humans and AI agents.

## Why "Friendly by Default" is a Differentiator

### The Industry Problem

Existing quality tools are built for experts:

- **pytest**: Outputs cryptic stack traces
- **ruff**: Shows error codes like `F401` with no context
- **pyright**: Assumes you understand Python's type system deeply
- **bandit**: Security alerts with CWE numbers and severity scores

These tools are powerful, but they're **not accessible**. New developers, non-technical stakeholders, and AI agents all struggle to interpret their output.

### VibeGate's Approach

**Powerhouse engine, friendly surface.**

VibeGate doesn't dumb down the checks—it runs the same rigorous analysis as the experts. But it translates the results:

| Tool Output | VibeGate Translation |
|-------------|---------------------|
| `F401: 'os' imported but unused` | **Unused Code**: You imported `os` but never used it. This clutters your code. |
| `error: Argument 1 to "foo" has incompatible type "str"; expected "int"` | **Type Mismatch**: Function `foo` expects a number, but you're passing text. This will crash at runtime. |
| `B404: Consider possible security implications associated with subprocess module` | **Security Risk**: Using `subprocess` can be dangerous if inputs aren't validated. Make sure user input can't execute shell commands. |

The **gate decision (PASS/FAIL) never changes**. But the way it's communicated is radically different.

## What the Optional Helper Model Does (and Doesn't Do)

### What It Does

The optional local LLM helper is used ONLY for:

1. **Translating findings into plain English**
   - Input: `error: Argument 1 to "foo" has incompatible type "str"; expected "int"`
   - Output: "Function `foo` expects a number, but you're passing text. This will cause a runtime error."

2. **Generating better fix prompts for AI coding assistants**
   - Input: Cluster of 15 similar type errors in src/validators.py
   - Output: "In src/validators.py, update function signatures to match actual usage patterns. The functions currently expect `int` but callers are passing `str | int`. Either narrow the callers or widen the function types using unions."

3. **Context-aware suggestions**
   - Input: Finding + surrounding code context
   - Output: "This pattern appears in your AST visitor classes. Catching generic `Exception` is actually correct here because node transformers need to handle any parsing errors gracefully."

### What It Doesn't Do

The helper model **cannot and does not**:

- **Decide pass/fail**: The gate decision is always deterministic, never influenced by AI
- **Suppress findings**: Only explicit suppressions in `.vibegate/suppressions.yaml` suppress findings
- **Modify code**: The helper only generates text (explanations and prompts)
- **Send data externally**: All inference happens locally on the user's machine

### Why This Matters

**Trust comes from determinism. Friendliness comes from translation.**

By keeping the gate deterministic and only using LLMs for the surface layer, VibeGate gives you:

- **Reproducible results** (same code always produces same outcome)
- **Compliance-friendly audit trails** (evidence.jsonl is deterministic and tamper-evident)
- **Friendly explanations** (when you need them, without compromising trust)

## The "Friendly by Default" Design Principle

VibeGate follows this hierarchy:

### 1. Default: Plain English for Humans

The main artifact is `.vibegate/plain_report.md`:

```markdown
# Your Code Quality Report

## What Needs Attention

We found 12 issues that need your attention.

### Type Errors (5 issues)

- Function `calculate_total` expects a number, but you're passing text in `app/cart.py` (line 42)
- Missing return type on `get_user` in `app/users.py` (line 18)
...

**Why this matters:** Type errors can cause your program to crash or behave unexpectedly.
```

**This is what users see by default.** No jargon, no acronyms, just clear explanations.

### 2. Opt-in: Technical Depth

Run `vibegate run . --detail deep --no-view` to get:

- Full finding lists with fingerprints
- Severity breakdowns
- Technical error codes
- Links to proof logs

The **same gate decision**, but more detail for those who want it.

### 3. Always Available: Technical Report

For CI/CD and automation, `artifacts/vibegate_report.md` always includes:

- Exact file paths and line numbers
- Rule IDs and severity levels
- Machine-readable fix pack (`artifacts/fixpack.json`)
- Evidence trail (`evidence/vibegate.jsonl`)

**The technical details are never hidden.** They're just not the default for human consumption.

## Comparison to Alternatives

### VibeGate vs Traditional Quality Tools

| Aspect | pytest/ruff/pyright | VibeGate |
|--------|---------------------|----------|
| **Output** | Technical, expert-focused | Plain English by default |
| **Orchestration** | Run separately | One command runs all |
| **Audit trail** | None | evidence.jsonl proof log |
| **Fix guidance** | None | Fix pack with remediation steps |
| **AI integration** | None | Agent prompt pack for coding assistants |

### VibeGate vs SonarQube/Codacy/CodeClimate

| Aspect | SonarQube/Codacy | VibeGate |
|--------|------------------|----------|
| **Deployment** | Cloud or self-hosted server | CLI, runs locally |
| **Data privacy** | Sends code to cloud | All processing local |
| **LLM helpers** | Proprietary AI (cloud) | Local Ollama (user's machine) |
| **Cost** | Paid tiers for features | OSS (future paid for collaboration) |

### VibeGate vs Pre-commit Hooks

| Aspect | Pre-commit Hooks | VibeGate |
|--------|-----------------|----------|
| **Scope** | Individual checks | Comprehensive gate |
| **Output** | Tool-specific errors | Unified friendly report |
| **Evidence** | None | Audit trail + fix pack |
| **Evolution** | Static config | Tuning pipeline for quality improvement |

## Philosophy: Deterministic Core, Optional Helper

VibeGate's architecture reflects this philosophy:

```
┌─────────────────────────────────────────────┐
│         Deterministic Quality Engine        │
│  (ruff, pyright, pytest, bandit, etc.)      │
│                                             │
│  - Runs checks                              │
│  - Produces findings                        │
│  - Generates fix pack                       │
│  - Writes evidence.jsonl                    │
│  - Decides PASS/FAIL                        │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│          Friendly Translation Layer          │
│        (Optional Local LLM Helper)           │
│                                             │
│  - Translates findings to plain English     │
│  - Generates agent prompts                  │
│  - Suggests context-aware fixes             │
│                                             │
│  **Does NOT affect gate decision**          │
└─────────────────────────────────────────────┘
```

This separation ensures:
- **Trust** (determinism at the core)
- **Accessibility** (friendly surface for everyone)
- **Privacy** (local processing, no cloud required)

## Why This Matters Now

**AI-powered coding is accelerating development velocity, but we need quality gates that match the pace.**

Traditional quality tools were built for humans who write code slowly and carefully. But in the age of AI coding assistants:

- **Code is written faster than humans can review it**
- **AI agents need structured feedback** (not just raw error output)
- **Teams need trust without slowing down**

VibeGate is designed for this new reality:

- **Friendly enough** for non-experts to understand
- **Deterministic enough** for compliance and production trust
- **Fast enough** to run on every commit
- **Structured enough** for AI agents to consume

## Success Criteria

VibeGate succeeds when:

1. **Developers run it without being told** (because the output is actually helpful)
2. **Non-technical stakeholders can read the reports** (plain English actually works)
3. **AI coding assistants use the agent prompt packs** (structured fixes work better than raw errors)
4. **Production deployments have audit trails** (evidence.jsonl becomes the source of truth)
5. **Teams trust the gate** (deterministic results build confidence over time)

## What's Next

See `docs/OPEN_CORE_ROADMAP.md` for the phased development plan and `docs/COMMERCIAL.md` for the business model.
