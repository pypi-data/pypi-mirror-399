# VibeGate Open-Core Roadmap

## Philosophy: Strong Open Source, Optional Collaboration

**VibeGate's open-core model:**

- **OSS remains powerful** for solo developers and local workflows
- **Paid features focus on collaboration**, not gatekeeping quality checks
- **The core engine stays open source** forever

This document outlines:
1. What stays open source (and why)
2. Phased development timeline
3. Future paid features (documentation only—not implemented)

## What Stays Open Source

These features will **always** be free and open source:

### Core Quality Engine
- Comprehensive check orchestration (formatting, linting, type checking, tests, security)
- Deterministic pass/fail decisions
- Evidence logging (audit trail)
- Fix pack generation
- Suppression system
- Tuning pipeline (label → tune → propose)
- Plugin system (custom checks and emitters)
- CLI tool
- Local-only operation

### Friendly Layer
- Plain reports (user-friendly explanations)
- Agent prompt packs (for AI coding assistants)
- Local LLM helpers (Ollama, OpenAI-compatible)
- Web UI (static viewer)

### Developer Experience
- Framework integration (FastAPI, Django, Flask)
- Profile system
- Configuration management
- Workspace scanning

**Rationale:** Solo developers should have full access to powerful quality tools without paying. The OSS version is production-ready and feature-complete.

## Development Phases

### v0.3 (Current) - Friendly Outputs + Local Providers

**Status:** ✅ Largely complete

**Features:**
- ✅ Plain reports in simple English
- ✅ `--detail` flag for simple/deep mode
- ✅ Local LLM helpers (Ollama)
- ✅ OpenAI-compatible provider support
- ✅ Agent prompt packs (MD + JSON)
- ✅ Web UI (static viewer)
- ✅ Tuning pipeline (label → tune → propose)

**Next:** Polish, documentation improvements, bug fixes.

### v0.4 - Enhanced Check Packs + Framework Intelligence

**Timeline:** Q1 2025

**Features:**
- **More check packs:** Additional defensive programming rules, framework-specific checks
- **Better grouping:** Smarter finding categorization (by impact, not just rule type)
- **Framework packs:** FastAPI, Django, Flask-specific rulesets
- **Improved AST analysis:** Better control flow understanding
- **Performance:** Faster check execution (parallel runs where safe)

**Still OSS:** All features in this phase remain open source.

### v0.5 - Plugin Ecosystem + Policy Packs

**Timeline:** Q2 2025

**Features:**
- **Plugin marketplace (docs):** Curated list of community plugins
- **Policy packs:** Pre-built rulesets for specific use cases (e.g., "PCI compliance", "HIPAA", "startups")
- **Better plugin authoring:** Improved plugin SDK, templates, testing tools
- **CI workflow templates:** GitHub Actions, GitLab CI, CircleCI examples
- **Comparison mode:** Compare runs over time (baseline vs current)

**Still OSS:** Core plugin system and policy packs remain OSS. Paid features (if any) focus on hosting and collaboration.

### v0.6 - Advanced Evolution + Collaboration (Paid Transition)

**Timeline:** Q3-Q4 2025

**OSS features:**
- Better tuning heuristics
- Improved proposal generation
- Regression testing for rule refinements
- Advanced AST patterns

**Paid features** (future, not implemented):
- **Hosted UI** with shared history
- **Team collaboration** (shared suppressions, approvals, policy templates)
- **Comparison dashboards** (track quality trends over time)

See `docs/COMMERCIAL.md` for paid feature details.

## Phased Rollout: OSS → Collaboration Features

### Phase 1: OSS Foundation (v0.1 - v0.5)

**Focus:** Make VibeGate best-in-class for solo developers.

**Delivered:**
- Complete quality orchestration
- Friendly outputs
- Local LLM helpers
- Plugin system
- Evolution pipeline

**Business model:** None. Pure OSS.

### Phase 2: Collaboration Layer (v0.6+)

**Focus:** Help teams coordinate around quality.

**Paid features** (not implemented, documentation only):
- Hosted UI + shared dashboards
- Team workflows (approvals, shared templates)
- CI integration wizard
- Auto-PR creation with fixpacks

**OSS remains:** All core features stay free. Paid features are collaboration addons.

### Phase 3: Enterprise Workflows (v1.0+)

**Focus:** Large organizations with compliance needs.

**Paid features** (not implemented, documentation only):
- Audit bundles for compliance
- SAML/SSO integration
- Advanced role-based access
- Custom SLA support

**OSS remains:** Core engine unchanged. Paid features are deployment/governance.

## What Won't Be Paywalled

These features will **never** require payment:

1. **Core quality checks** (formatting, linting, types, tests, security)
2. **Deterministic gate decisions**
3. **Evidence logging**
4. **Fix pack generation**
5. **Local LLM helpers** (Ollama, OpenAI-compatible)
6. **Plugin system** (authoring and using plugins)
7. **CLI tool**
8. **Local operation** (no cloud required)

## Future Paid Features (Documentation Only)

These are **not implemented** and purely speculative. See `docs/COMMERCIAL.md` for business context.

### Hosted UI (v0.6+)

**What:** Web-hosted VibeGate dashboard accessible to teams.

**Why paid:** Hosting costs, user management, data storage.

**OSS alternative:** Static UI viewer (already available).

### Team Workflows (v0.6+)

**What:** Shared suppressions, policy templates, approval flows.

**Why paid:** Collaboration infrastructure requires backend services.

**OSS alternative:** Git-based sharing (teams can version control `vibegate.yaml` and suppressions).

### CI Integration Wizard (v0.6+)

**What:** Visual wizard for setting up CI workflows with VibeGate.

**Why paid:** Requires cloud service to generate/update CI configs.

**OSS alternative:** Template-based setup (docs already provide examples).

### Auto-PR with Fixpacks (v0.6+)

**What:** Automatically create PRs that apply fixpack patches.

**Why paid:** Requires hosted service to manage PR lifecycle and verification.

**OSS alternative:** Manual application of fixpack (agent prompt pack already provides instructions).

### Model Routing/Benchmarking (v1.0+)

**What:** Automatically select best local model for your repo based on benchmarks.

**Why paid:** Requires infrastructure to run benchmarks and store results.

**OSS alternative:** Manual model selection (docs provide recommendations).

## Release Strategy

### Until v1.0: Free and Open

- All releases are OSS (MIT license)
- No paid features implemented
- Focus on building the best solo developer experience

### v1.0+: Open Core

- Core engine remains OSS (MIT license)
- Collaboration features available as paid tier
- Clear separation: deterministic core (OSS) vs collaboration layer (paid)

## Community Contributions

We encourage:
- **Plugin development** (share custom checks)
- **Policy pack creation** (share rulesets for specific use cases)
- **Framework integration** (add support for more frameworks)
- **Documentation improvements**
- **Bug reports and feature requests**

See `CONTRIBUTING.md` for guidelines.

## Long-Term Vision

**VibeGate becomes the standard quality orchestrator for Python projects.**

- **OSS:** Powers solo developers and small teams (like pytest/ruff do today)
- **Paid:** Powers large organizations that need collaboration and compliance
- **Community:** Thriving plugin ecosystem and shared policy packs

The gate stays deterministic. The ecosystem grows around it.

## FAQ

### Will OSS features be removed?

**No.** Features currently in OSS will never be moved to paid tiers.

### What if I don't want paid features?

**You never need them.** OSS VibeGate is production-ready and feature-complete.

### Can I self-host the paid features?

**Potentially.** If demand exists, we may offer self-hosted enterprise licenses. But the hosted option will always be easier.

### Will the LLM helper require payment?

**No.** Local LLM helpers (Ollama, OpenAI-compatible) will always be free. Cloud-hosted LLM routing (if built) would be paid, but local remains free.

### Can I contribute to paid features?

**Depends.** Collaboration features may be closed-source. Core engine contributions are always welcome.

## Next Steps

- Read `docs/COMMERCIAL.md` for business context
- Read `docs/PRODUCT_VISION.md` for product philosophy
- Read `CONTRIBUTING.md` to get involved
