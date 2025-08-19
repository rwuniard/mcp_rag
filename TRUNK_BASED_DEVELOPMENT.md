# Trunk-Based Development Workflow

This document outlines the trunk-based development workflow for the MCP RAG project, designed to enable rapid iteration while maintaining high code quality and security standards.

## 🎯 Core Principles

### 1. **Always Deployable Main Branch**
- Main branch is always in a releasable state
- All commits to main trigger automated deployment
- Broken builds are fixed immediately (within hours)

### 2. **Short-Lived Feature Branches**
- Feature branches live for **<24-48 hours maximum**
- Target **<500 lines changed** per PR
- Merge frequently to avoid integration conflicts

### 3. **Fast Feedback Loops**
- Automated CI/CD provides feedback within minutes
- Code reviews completed within 24 hours
- Issues detected and fixed quickly

### 4. **Quality Gates**
- **Blocking**: Coverage <70%, failing tests, critical security issues
- **Warning**: Coverage <85% (allows merge with notification)
- **Advisory**: Style/typing issues, non-critical security findings

## 🔄 Development Workflow

### Starting New Work

1. **Always start from main:**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create focused feature branch:**
   ```bash
   # Use descriptive branch names
   git checkout -b feature/add-document-processor
   git checkout -b fix/memory-leak-in-search
   git checkout -b docs/update-installation-guide
   ```

3. **Make small, focused changes:**
   - One logical change per branch
   - Keep changes under 500 lines when possible
   - Write tests alongside code

### Development Best Practices

4. **Test locally before pushing:**
   ```bash
   # Run comprehensive tests and coverage
   python run_coverage.py --console-only
   
   # Quick test during development
   python -m unittest discover tests -v
   ```

5. **Commit frequently with clear messages:**
   ```bash
   git commit -m "feat: add Word document processor with 94% coverage"
   git commit -m "fix: resolve memory leak in similarity search"
   git commit -m "docs: update installation instructions for uv"
   ```

### Creating Pull Requests

6. **Push and create PR:**
   ```bash
   git push -u origin feature/add-document-processor
   
   # Use appropriate template
   gh pr create --template default.md  # For substantial changes
   gh pr create --template quick.md    # For minor changes
   ```

7. **PR Requirements:**
   - Descriptive title: `type: description`
   - Complete PR template
   - All CI checks passing
   - Self-review completed

### Code Review Process

8. **Review Standards:**
   - **Response time**: <4 hours during work hours
   - **Review time**: <24 hours for completion
   - **Focus areas**: Correctness, maintainability, security
   - **Approval required**: 1 reviewer minimum

9. **Reviewer Responsibilities:**
   - Test the changes locally if needed
   - Check code quality and design
   - Verify tests and documentation
   - Approve when ready or request changes

### Merging and Integration

10. **Merge Requirements:**
    - All status checks passing
    - Coverage meets minimum threshold (70%)
    - At least 1 approval
    - No unresolved conversations

11. **Merge Process:**
    - Use **squash merge** for clean history
    - Update commit message if needed
    - Feature branch auto-deleted after merge

## 🛠️ Technical Implementation

### CI/CD Pipeline

Our GitHub Actions workflow includes:

1. **Code Quality** (`quality`)
   - Black formatting check
   - isort import sorting
   - flake8 linting
   - mypy type checking

2. **Security Scanning** (`security`)  
   - bandit security linting
   - safety dependency checking
   - Trivy vulnerability scanning

3. **Testing & Coverage** (`test`) - **BLOCKING**
   - Full test suite execution
   - Coverage threshold enforcement (70% min, 85% target)
   - Coverage reports and artifacts

4. **Integration Testing** (`integration`)
   - CLI entry points validation
   - Package build verification
   - Coverage tool testing

5. **Multi-Python Testing** (`test-matrix`) - **NON-BLOCKING**
   - Python 3.11 and 3.13 compatibility
   - Runs only on PRs for efficiency

6. **Automated Release** (`release`)
   - Triggers on main branch merges
   - Creates GitHub releases
   - Optional PyPI publishing

### Coverage Strategy

**Intelligent Coverage Thresholds:**
- **Minimum Threshold**: 70% (prevents regression, allows innovation)
- **Target Threshold**: 85% (aspirational goal, warns but doesn't block)
- **Core Components**: 90%+ (critical processors maintain high standards)

**Current Status:**
- Overall Project: 70% ✅
- Text Processor: 95% ✅
- Word Processor: 94% ✅  
- PDF Processor: 94% ✅
- Document Processor: 93% ✅

### Branch Protection Rules

Main branch is protected with:
- **Required status checks**: `test`, `quality`, `security`, `integration`
- **Required reviews**: 1 reviewer minimum
- **Up-to-date branches**: Must be current with main
- **No direct pushes**: All changes via PR
- **Auto-delete**: Feature branches removed after merge
- **Squash merge**: Clean commit history

## 📊 Workflow Examples

### Feature Development

```bash
# 1. Start new feature
git checkout main && git pull origin main
git checkout -b feature/add-powerpoint-support

# 2. Develop with tests
# - Implement PowerPointProcessor class
# - Write comprehensive unit tests  
# - Update documentation
python run_coverage.py --console-only  # Verify >70% coverage

# 3. Create focused PR
git add . && git commit -m "feat: add PowerPoint document processing support"
git push -u origin feature/add-powerpoint-support
gh pr create --template default.md

# 4. Address review feedback
git commit -m "fix: improve error handling per review"
git push

# 5. Squash merge after approval
# Branch auto-deleted, changes deployed
```

### Bug Fix

```bash
# 1. Create hotfix branch
git checkout main && git pull origin main  
git checkout -b fix/search-timeout-issue

# 2. Make minimal fix
# - Identify root cause
# - Implement targeted fix
# - Add regression test
python run_coverage.py --console-only  # Quick verification

# 3. Fast-track PR
git add . && git commit -m "fix: resolve search timeout in large documents"
git push -u origin fix/search-timeout-issue
gh pr create --template quick.md

# 4. Expedite review and merge
# Deploy fix immediately
```

### Documentation Update

```bash
# 1. Quick documentation change
git checkout -b docs/clarify-installation-steps

# 2. Update docs
# - Improve README clarity
# - Fix typos
# - Update examples

# 3. Simple PR  
git add . && git commit -m "docs: clarify uv installation instructions"
git push -u origin docs/clarify-installation-steps
gh pr create --template quick.md

# 4. Quick review and merge
```

## 🚨 Emergency Procedures

### Critical Hotfix Process

For production-breaking issues:

1. **Create emergency branch:**
   ```bash
   git checkout main && git pull origin main
   git checkout -b hotfix/critical-security-fix
   ```

2. **Make minimal fix:**
   ```bash
   # Fix only the critical issue
   # Add regression test
   python run_coverage.py --console-only
   ```

3. **Emergency PR:**
   ```bash
   git push -u origin hotfix/critical-security-fix
   gh pr create --title "🚨 HOTFIX: Critical security vulnerability" \
     --body "Emergency fix for critical security issue" \
     --label "emergency,security"
   ```

4. **Admin override if needed:**
   - Temporarily reduce required reviewers
   - Merge immediately
   - Restore protection rules
   - Communicate to team

### Broken Main Branch Recovery

If main branch is broken:

1. **Immediate response:**
   - Stop all feature development
   - Identify breaking commit
   - Create fix or revert

2. **Quick fix:**
   ```bash
   git checkout -b fix/restore-main-branch
   # Apply fix
   gh pr create --label "urgent,main-branch-fix"
   ```

3. **Communication:**
   - Notify team in Slack/email
   - Update status page if customer-facing
   - Document root cause

## 📈 Success Metrics

### Process Metrics
- **PR Cycle Time**: <24 hours (creation to merge)
- **Main Branch Stability**: >99% green builds
- **Review Response Time**: <4 hours during work hours
- **Feature Delivery**: Faster with same quality

### Quality Metrics  
- **Code Coverage**: Trending toward 85%
- **Security Issues**: Zero critical vulnerabilities
- **Test Reliability**: >95% consistent pass rate
- **Technical Debt**: Controlled and decreasing

### Team Metrics
- **Developer Satisfaction**: High confidence in deployments
- **Reduced Context Switching**: Smaller, focused PRs
- **Knowledge Sharing**: Better through code reviews
- **Innovation Speed**: Fast experimentation with safety

## 🎓 Team Guidelines

### For Developers

**Do:**
- Keep PRs small and focused
- Write tests for new code
- Respond to reviews quickly  
- Update documentation
- Test locally before pushing

**Don't:**
- Let branches live longer than 48 hours
- Create PRs with >500 lines changed
- Skip testing or coverage checks
- Ignore CI failures
- Force push to shared branches

### For Reviewers

**Do:**
- Respond within 4 hours during work hours
- Focus on correctness and maintainability
- Test changes if uncertain
- Approve when ready
- Provide constructive feedback

**Don't:**
- Nitpick on style (automated tools handle this)
- Block on personal preferences
- Take longer than 24 hours for review
- Skip testing complex changes
- Approve without understanding

## 🔧 Tools and Commands

### Essential Commands

```bash
# Development workflow
python run_coverage.py --open          # Full testing with HTML report
python run_coverage.py --console-only  # Quick testing
gh pr create --template quick.md       # Minor changes PR
gh pr create --template default.md     # Substantial changes PR

# Branch management
git checkout main && git pull origin main  # Update main
git branch -d feature/old-branch           # Delete local branch
gh pr list --state open                    # View open PRs

# CI troubleshooting  
gh run list                    # View recent workflow runs
gh run view <run-id>          # View specific run details
gh workflow view              # View workflow configuration
```

### Useful GitHub CLI

```bash
# Create PR with auto-fill
gh pr create --fill

# View PR checks
gh pr checks

# Merge PR after approval
gh pr merge --squash

# View repository status
gh pr status
gh issue list
```

## 📚 Additional Resources

- **Branch Protection Setup**: [.github/branch-protection-config.md](.github/branch-protection-config.md)
- **CI/CD Configuration**: [.github/workflows/ci.yml](.github/workflows/ci.yml)
- **Coverage Documentation**: [README.md](README.md#testing--coverage)
- **PR Templates**: [.github/PULL_REQUEST_TEMPLATE/](.github/PULL_REQUEST_TEMPLATE/)

## 🤝 Getting Help

- **Process Questions**: Create GitHub Discussion or Slack thread
- **Technical Issues**: Create GitHub Issue with `help-wanted` label
- **Emergency Support**: Contact team leads directly
- **CI/CD Problems**: Check [troubleshooting guide](.github/branch-protection-config.md#troubleshooting)

---

**Remember**: Trunk-based development is about enabling fast, safe delivery. When in doubt, prioritize smaller changes and faster feedback over perfect solutions.