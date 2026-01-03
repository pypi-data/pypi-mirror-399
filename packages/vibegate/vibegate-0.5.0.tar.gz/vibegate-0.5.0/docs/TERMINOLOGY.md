# VibeGate Terminology Guide

## Overview

This document defines the terms used in VibeGate and explains the writing style for contributors.

## Core Concepts

### Checks

**User-facing term:** "checks"

**What it means:** Quality checks that VibeGate runs (formatting, linting, type checking, tests, etc.)

**Examples:**
- "VibeGate runs comprehensive checks on your code."
- "All checks passed!"
- "Enable/disable specific checks in vibegate.yaml"

**NOT:**
- ~~"signals"~~ (deprecated user-facing term)
- ~~"rules"~~ (too generic)
- ~~"validators"~~ (not our terminology)

**Internal code:** May use "check", "signal", or "rule" as identifiers. Only user-facing text must say "checks".

### Findings

**User-facing term:** "issues" or "findings"

**What it means:** Problems discovered by checks.

**Examples:**
- "We found 12 issues that need your attention."
- "This finding indicates a type mismatch."
- "Review findings in the report."

**NOT:**
- ~~"errors"~~ (too technical, not all findings are errors)
- ~~"violations"~~ (sounds punitive)
- ~~"hits"~~ (ambiguous)

### Proof Log / Evidence Trail

**User-facing term:** "proof log" or "run log"

**What it means:** The evidence.jsonl file that records what VibeGate did.

**Examples:**
- "VibeGate creates a proof log in evidence/vibegate.jsonl"
- "The run log shows every check that was executed."
- "Proof logs are useful for compliance audits."

**NOT:**
- ~~"evidence artifacts"~~ (too jargony for normal humans)
- ~~"audit trail"~~ (sounds bureaucratic)
- ~~"execution log"~~ (too technical)

**Technical docs:** "evidence.jsonl" or "evidence trail" is fine in technical documentation.

### Action Plan / Fix Pack

**User-facing term:** "action plan"

**What it means:** The fixpack.json/fixpack.md files with remediation steps.

**Examples:**
- "Check the action plan in artifacts/fixpack.md"
- "The fix pack lists every issue as a task."
- "Follow the action plan to resolve issues."

**NOT:**
- ~~"remediation pack"~~ (too formal)
- ~~"patch pack"~~ (sounds like software patches)
- ~~"task list"~~ (too generic)

**Technical docs:** "fix pack" is fine in technical documentation (it's the actual file name).

### Friendly Report / Technical Report

**User-facing terms:** "friendly report" and "technical report"

**What they mean:**
- **Friendly report** (`.vibegate/plain_report.md`): Plain English summary for everyone
- **Technical report** (`artifacts/vibegate_report.md`): Detailed findings for developers

**Examples:**
- "Open the friendly report for a quick summary."
- "Check the technical report for exact file paths and line numbers."

**NOT:**
- ~~"plain report"~~ (sounds basic)
- ~~"simple report"~~ (sounds condescending)
- ~~"detailed report"~~ (vague)

**Internal:** File names use "plain_report" and "vibegate_report" (that's fine, user-facing docs should say "friendly").

### Gate Decision

**User-facing term:** "gate decision" or "result"

**What it means:** Whether VibeGate passed or failed.

**Examples:**
- "The gate decision is: PASS"
- "Your code passed the quality gate!"
- "Result: FAIL (3 blocking issues)"

**NOT:**
- ~~"verdict"~~ (sounds judicial)
- ~~"outcome"~~ (too generic)
- ~~"status"~~ (ambiguous)

### Suppressions vs Labels

**User-facing terms:** "suppressions" and "labels"

**What they mean:**
- **Suppressions** (`.vibegate/suppressions.yaml`): Affect CI/CD behavior (findings are suppressed and don't cause failures)
- **Labels** (`.vibegate/labels.yaml`): Quality tracking only (mark findings as false positive / true positive / acceptable risk)

**Examples:**
- "Add suppressions to .vibegate/suppressions.yaml to prevent failures."
- "Use labels to track false positives for quality improvement."
- "Suppressions affect the gate; labels don't."

**NOT:**
- ~~"whitelist"~~ (loaded term, avoid)
- ~~"exemptions"~~ (too formal)
- ~~"annotations"~~ (too generic)

## Writing Style Guide

### For Normal Humans (Default)

**Tone:** Friendly, conversational, approachable

**Language:**
- Use simple words (not jargon)
- Explain acronyms on first use
- Short sentences
- Active voice

**Examples:**

✅ **Good:**
> We found 5 type errors in your code. Type errors can cause crashes at runtime.

❌ **Bad:**
> Type checking identified 5 findings with severity=high and confidence=medium. These violations of PEP 484 may result in runtime exceptions.

✅ **Good:**
> VibeGate runs quality checks on your code.

❌ **Bad:**
> VibeGate executes deterministic validation procedures against your codebase.

### For Technical Depth (Opt-In)

**Tone:** Precise, detailed, technical

**Language:**
- Use exact terms (rule IDs, file paths, line numbers)
- Include technical details
- Reference standards and tools

**Examples:**

✅ **Good (technical report):**
> Finding: `F401` in `src/app.py:12` - Imported module 'os' is unused. Severity: low, Confidence: high. Fingerprint: sha256:abc123...

❌ **Bad (should be in technical report, not friendly report):**
> You have an unused import.

**When to use:**
- Technical report (`artifacts/vibegate_report.md`)
- Evidence log (`evidence/vibegate.jsonl`)
- API responses (JSON)
- Developer documentation (ARCHITECTURE.md, CONTRIBUTING.md)

**When not to use:**
- Friendly report (`.vibegate/plain_report.md`)
- User-facing CLI output
- Marketing materials
- README.md (default section)

## Acronyms and Abbreviations

### Explain on First Use

**Good:**
> VibeGate uses AST (Abstract Syntax Tree) analysis to detect code patterns.

**Bad:**
> VibeGate uses AST analysis. (assumes reader knows what AST is)

### Common Acronyms We Use

| Acronym | Expansion | When to Explain |
|---------|-----------|-----------------|
| **AST** | Abstract Syntax Tree | Always (first use) |
| **CI/CD** | Continuous Integration / Continuous Deployment | First use in user docs |
| **LLM** | Large Language Model | First use in user docs |
| **JSONL** | JSON Lines | First use |
| **CLI** | Command Line Interface | Can assume (very common) |
| **API** | Application Programming Interface | Can assume (very common) |

## Common Phrases

### ✅ Recommended Phrases

**For actions:**
- "Run checks on your code"
- "Review the friendly report"
- "Fix the issues"
- "Check the proof log"

**For status:**
- "All checks passed!"
- "Found 5 issues"
- "No blocking problems"
- "Your code is ready to ship"

**For explanations:**
- "This matters because..."
- "Here's what to do:"
- "Why we check this:"

### ❌ Phrases to Avoid

**Too technical:**
- ~~"Execute validation signals"~~
- ~~"Emit evidence artifacts"~~
- ~~"Parse findings payload"~~

**Too formal:**
- ~~"Herein lies the output"~~
- ~~"Aforementioned issues"~~
- ~~"Pursuant to the configuration"~~

**Too vague:**
- ~~"Stuff was found"~~
- ~~"Some problems exist"~~
- ~~"Things are wrong"~~

## Capitalization

### Product Names

- **VibeGate** (always capitalized, never "vibegate" in prose)
- **Ollama** (proper noun, capitalize)
- **Qwen** (proper noun, capitalize)

### Commands and File Names

- `vibegate run .` (lowercase, code font)
- `vibegate.yaml` (lowercase, code font)
- `.vibegate/plain_report.md` (lowercase, code font)

### Concepts

- "quality checks" (lowercase)
- "friendly report" (lowercase)
- "proof log" (lowercase)
- "PASS" or "FAIL" (all caps when referring to gate decision)

## Examples in Context

### User-Facing CLI Output

✅ **Good:**
```
Running checks...

Issues found: 5
  - Blocking: 3
  - Warnings: 2

Decision: FAIL (3 blocking issues)

Next steps:
  - Review findings: .vibegate/plain_report.md
  - Fix high-priority issues first
  - Run vibegate run . to verify
```

❌ **Bad:**
```
Executing validation procedures...

Findings surfaced: 5
  - Severity=high: 3
  - Severity=low: 2

Gate verdict: REJECT

Suggested remediation workflow:
  - Inspect evidence artifacts
  - Apply fixpack patches
  - Re-execute validation runner
```

### Documentation

✅ **Good (README.md):**
> VibeGate makes code quality checks friendly and actionable. It runs all your Python checks in one command and creates easy-to-read reports.

❌ **Bad:**
> VibeGate is a deterministic production readiness validation orchestrator that emits evidence-based quality artifacts.

## Contributor Guidelines

### When Writing Docs

1. **Start friendly** - Default to simple language
2. **Add depth optionally** - Technical details in separate sections
3. **Define terms** - Explain acronyms and jargon on first use
4. **Use examples** - Show, don't just tell
5. **Be concise** - Shorter is better

### When Writing Code

**User-facing strings** (CLI output, reports):
- Use friendly terminology ("checks", "issues", "friendly report")
- Explain what's happening in simple terms

**Internal code** (variable names, function names):
- Use whatever makes sense for code clarity
- `signal`, `finding`, `rule` are all fine as identifiers

**Comments and docstrings:**
- Be precise and technical
- Target: developers who know Python well

## Review Checklist

When reviewing docs or user-facing output:

- [ ] No "signals" in user-facing text (use "checks")
- [ ] Acronyms explained on first use
- [ ] Friendly tone by default
- [ ] Technical depth available (but not default)
- [ ] Examples included
- [ ] Consistent terminology (checks, issues, findings, friendly report, proof log)

## Questions?

If you're unsure whether to use friendly or technical language:

**Ask:** "Is this for a human reading casually, or a developer debugging?"

- **Human reading casually:** Friendly
- **Developer debugging:** Technical

When in doubt, start friendly and add technical details optionally.
