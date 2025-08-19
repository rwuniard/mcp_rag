# Branch Protection Configuration

This document provides step-by-step instructions to configure branch protection rules for trunk-based development.

## GitHub Web UI Configuration

### 1. Navigate to Settings
1. Go to your repository on GitHub
2. Click on **Settings** tab
3. In the left sidebar, click **Branches**

### 2. Add Branch Protection Rule
1. Click **Add rule**
2. In **Branch name pattern**, enter: `main`

### 3. Configure Protection Settings

#### Required Status Checks
- ✅ **Require status checks to pass before merging**
- ✅ **Require branches to be up to date before merging**
- **Required status checks:**
  - `test` (Test & Coverage)
  - `quality` (Code Quality)
  - `security` (Security Scan)
  - `integration` (Integration Tests)

#### Pull Request Requirements
- ✅ **Require a pull request before merging**
- **Required number of reviewers:** `1`
- ✅ **Dismiss stale pull request approvals when new commits are pushed**
- ✅ **Require review from code owners** (if CODEOWNERS file exists)

#### Additional Restrictions
- ✅ **Restrict pushes that create files that exceed the file size limit**
- ✅ **Require conversation resolution before merging**
- ✅ **Require signed commits** (optional, recommended for security)

#### Administrative Settings
- ✅ **Include administrators** (applies rules to admins too)
- ✅ **Allow force pushes** → **Nobody** (disable force pushes)
- ✅ **Allow deletions** → **Disable** (prevent branch deletion)

### 4. Auto-merge Settings (Optional)
- ✅ **Allow auto-merge**
- **Preferred merge method:** **Squash merging**
- ✅ **Automatically delete head branches**

## Alternative: GitHub CLI Configuration

If you prefer command-line setup, use these commands:

```bash
# Enable branch protection for main
gh api repos/{owner}/{repo}/branches/main/protection \
  --method PUT \
  --field required_status_checks='{"strict":true,"checks":[{"context":"test"},{"context":"quality"},{"context":"security"},{"context":"integration"}]}' \
  --field enforce_admins=true \
  --field required_pull_request_reviews='{"required_approving_review_count":1,"dismiss_stale_reviews":true}' \
  --field restrictions=null \
  --field allow_force_pushes=false \
  --field allow_deletions=false

# Enable auto-delete of feature branches
gh api repos/{owner}/{repo} \
  --method PATCH \
  --field delete_branch_on_merge=true

# Set squash merge as default
gh api repos/{owner}/{repo} \
  --method PATCH \
  --field allow_squash_merge=true \
  --field allow_merge_commit=false \
  --field allow_rebase_merge=false
```

## Configuration Verification

After setup, verify your configuration:

1. **Check branch protection:**
   ```bash
   gh api repos/{owner}/{repo}/branches/main/protection
   ```

2. **Test with a sample PR:**
   ```bash
   git checkout -b test-protection
   echo "test" > test.txt
   git add test.txt && git commit -m "test: branch protection"
   git push -u origin test-protection
   gh pr create --title "Test branch protection" --body "Testing trunk-based development setup"
   ```

3. **Verify protection is working:**
   - Try to push directly to main (should fail)
   - Check that PR requires status checks
   - Verify reviewer requirements

## Troubleshooting

### Common Issues

**Status checks not appearing:**
- Make sure the workflow names in CI match the required checks
- Verify workflows are on the main branch
- Check workflow syntax with `gh workflow view`

**Can't merge despite checks passing:**
- Ensure branch is up to date with main
- Check if all required status checks have completed
- Verify reviewer approval is present

**Admin bypassing rules:**
- Ensure "Include administrators" is checked
- Consider using CODEOWNERS for critical files

### Status Check Names Reference

These are the job names from your CI workflow that should be required:

- `test` - Critical: Tests and coverage enforcement
- `quality` - Code style and formatting
- `security` - Security vulnerability scanning  
- `integration` - CLI and package integration tests

Note: `test-matrix` and `release` are intentionally not required (non-blocking)

## Emergency Procedures

### Hotfix Process
For critical production issues:

1. **Create hotfix branch from main:**
   ```bash
   git checkout main
   git pull origin main
   git checkout -b hotfix/critical-issue-description
   ```

2. **Make minimal fix and test:**
   ```bash
   # Make changes
   python run_coverage.py --console-only  # Quick test
   ```

3. **Fast-track PR with emergency label:**
   ```bash
   git push -u origin hotfix/critical-issue-description
   gh pr create --title "🚨 HOTFIX: Description" \
     --body "Emergency fix for critical issue" \
     --label "emergency,hotfix"
   ```

4. **Admin can merge with reduced reviews if needed:**
   - Temporarily reduce required reviewers to 0
   - Merge immediately
   - Restore protection rules

### Temporary Rule Modification
```bash
# Reduce to 0 reviewers temporarily
gh api repos/{owner}/{repo}/branches/main/protection/required_pull_request_reviews \
  --method PATCH \
  --field required_approving_review_count=0

# Restore to 1 reviewer
gh api repos/{owner}/{repo}/branches/main/protection/required_pull_request_reviews \
  --method PATCH \
  --field required_approving_review_count=1
```