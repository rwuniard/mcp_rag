# Quick Implementation Guide

Get up and running with trunk-based development in 5 minutes.

## 🚀 Quick Start

### 1. Install Development Dependencies (30 seconds)

```bash
# Add development dependencies to your project
uv add --dev black isort flake8 mypy bandit safety coverage
```

### 2. Configure Branch Protection (2 minutes)

**Option A: GitHub Web UI**
1. Go to **Settings** → **Branches** → **Add rule**
2. Branch pattern: `main`
3. Check these boxes:
   - ✅ Require status checks: `test`, `quality`, `security`, `integration`
   - ✅ Require pull request reviews (1 reviewer)
   - ✅ Require branches up to date
   - ✅ Include administrators
4. Set merge preferences:
   - ✅ Allow squash merging
   - ❌ Disable merge commits and rebase

**Option B: GitHub CLI (if you have it)**
```bash
# Replace {owner}/{repo} with your actual repo
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"checks":[{"context":"test"},{"context":"quality"},{"context":"security"},{"context":"integration"}]}' \
  --field required_pull_request_reviews='{"required_approving_review_count":1}' \
  --field enforce_admins=true
```

### 3. Test the Setup (30 seconds)

```bash
# Test that CI works
python run_coverage.py --console-only

# Verify coverage meets minimum threshold
# Should show: "Current coverage: 70%" or higher
```

## ✅ Verification Checklist

- [ ] CI workflow file exists: `.github/workflows/ci.yml`
- [ ] Branch protection enabled on `main`
- [ ] PR templates available
- [ ] Coverage tool working: `python run_coverage.py --console-only`
- [ ] All current tests pass

## 🔄 First Workflow Test

Create your first trunk-based development PR:

```bash
# 1. Create test branch
git checkout -b test/trunk-workflow-setup

# 2. Make a small change
echo "# Trunk-Based Development Setup Complete" >> WORKFLOW_TEST.md

# 3. Commit and push
git add WORKFLOW_TEST.md
git commit -m "test: verify trunk-based development workflow"
git push -u origin test/trunk-workflow-setup

# 4. Create PR with quick template
gh pr create --template quick.md --title "test: trunk-based development setup" --body "Testing the new workflow"
```

**Expected behavior:**
- ✅ CI should trigger automatically
- ✅ Status checks should appear in PR
- ✅ Coverage check should pass (70%+)
- ✅ PR should require 1 approval
- ❌ Direct push to main should be blocked

## 📊 Current Status Check

Your project status after setup:

| Component | Coverage | Status |
|-----------|----------|---------|
| Overall Project | 70% | ✅ Above minimum |
| Text Processor | 95% | ✅ Excellent |
| Word Processor | 94% | ✅ Excellent |
| PDF Processor | 94% | ✅ Excellent |
| Document Processor | 93% | ✅ Excellent |

**Quality Gates:**
- 🚫 **Blocks merge**: Coverage <70%, failing tests, critical security
- ⚠️ **Warns but allows**: Coverage <85%
- ℹ️ **Advisory only**: Style issues, type checking

## 🛠️ Essential Commands

### Daily Development
```bash
# Start new feature
git checkout main && git pull origin main
git checkout -b feature/your-feature-name

# Test before committing
python run_coverage.py --console-only

# Create PR
gh pr create --template quick.md      # For minor changes
gh pr create --template default.md    # For substantial changes
```

### Troubleshooting
```bash
# Check CI status
gh pr checks

# View detailed CI logs
gh run list
gh run view <run-id>

# Test locally what CI will test
python run_coverage.py --console-only
uv run black --check .
uv run flake8 .
```

## 🎯 Success Criteria

After implementation, you should achieve:

**Process Metrics:**
- PR cycle time: <24 hours
- Review response: <4 hours
- Main branch: Always deployable

**Quality Metrics:**
- Coverage: Maintained above 70%, trending toward 85%
- Security: Zero critical vulnerabilities
- Reliability: >95% green builds

## 🔧 Customization Options

### Adjust Coverage Thresholds
Edit `.github/workflows/ci.yml` line 140:
```yaml
MIN_COVERAGE=70    # Change minimum threshold
TARGET_COVERAGE=85 # Change warning threshold
```

### Add/Remove Status Checks
Edit branch protection rules to require/unrequire:
- `quality` (code style)
- `security` (vulnerability scanning)
- `integration` (CLI testing)
- `test` (coverage - recommended to keep)

### Modify PR Templates
Edit files in `.github/PULL_REQUEST_TEMPLATE/`:
- `default.md` - Comprehensive changes
- `quick.md` - Minor changes

## 📚 Next Steps

1. **Read the full guide**: [TRUNK_BASED_DEVELOPMENT.md](TRUNK_BASED_DEVELOPMENT.md)
2. **Configure secrets** (optional): PyPI token for automated publishing
3. **Train your team** on the new workflow
4. **Monitor metrics** and adjust thresholds as needed
5. **Gradually improve coverage** toward 85% target

## 🚨 Common Issues

**CI not running?**
- Check workflow file is in `.github/workflows/ci.yml`
- Verify branch protection settings
- Push to trigger workflow

**Coverage failing?**
- Run `python run_coverage.py --console-only` locally
- Check if new code lacks tests
- Verify threshold settings in CI

**Can't merge PR?**
- Ensure all status checks pass
- Get required approvals
- Update branch if behind main
- Resolve any merge conflicts

## 💡 Tips for Success

1. **Start small**: Make your first few PRs simple to build confidence
2. **Test locally**: Always run coverage tool before pushing
3. **Communicate**: Keep team informed during transition
4. **Iterate**: Adjust thresholds and rules based on experience
5. **Monitor**: Watch for bottlenecks and optimize accordingly

---

**Ready to go!** Your trunk-based development workflow is now active. Create your first PR to test it out! 🎉