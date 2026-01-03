#!/usr/bin/env bash
# Setup branch protection rules for VibeGate repository
# Requires: gh CLI (GitHub CLI) - install with: brew install gh
# Run: ./scripts/setup_branch_protection.sh

set -euo pipefail

REPO="maxadamsky/VibeGate"
BRANCH="main"

echo "Setting up branch protection for ${REPO}:${BRANCH}..."

# Check if gh is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed"
    echo "Install with: brew install gh"
    echo "Then run: gh auth login"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "Error: Not authenticated with GitHub"
    echo "Run: gh auth login"
    exit 1
fi

# Update branch protection rules
echo "Configuring branch protection rules..."

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/${REPO}/branches/${BRANCH}/protection" \
  --input - <<'EOF'
{
  "required_status_checks": {
    "strict": true,
    "contexts": ["ci", "commitlint"]
  },
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": true,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "required_linear_history": true,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "block_creations": false,
  "required_conversation_resolution": true,
  "lock_branch": false,
  "allow_fork_syncing": false
}
EOF

echo "✅ Branch protection rules configured successfully!"
echo ""
echo "Configuration applied:"
echo "  - Required status checks: ci, commitlint"
echo "  - Require branches to be up to date: true"
echo "  - Required pull request reviews: 0 approvals"
echo "  - Dismiss stale reviews: true"
echo "  - Require linear history: true"
echo "  - Allow force pushes: false"
echo "  - Allow deletions: false"
echo "  - Require conversation resolution: true"
echo "  - Enforce for admins: false (allows bypass)"
echo ""
echo "View settings at: https://github.com/${REPO}/settings/branches"
