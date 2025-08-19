<!-- 
This is the default PR template for comprehensive changes.
For quick/minor changes, use the 'quick' template instead.
-->

## 📋 Pull Request Summary

### Type of Change
<!-- Mark the relevant option with an 'x' -->
- [ ] 🐛 Bug fix (non-breaking change that fixes an issue)
- [ ] ✨ New feature (non-breaking change that adds functionality)
- [ ] 💥 Breaking change (fix or feature that would cause existing functionality to change)
- [ ] 📖 Documentation update
- [ ] 🧪 Test improvements
- [ ] ♻️ Code refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] 🔒 Security fix
- [ ] 🏗️ Build/CI changes

### Description
<!-- Provide a clear and concise description of what this PR does -->


### Related Issues
<!-- Link to related issues using "Fixes #123" or "Relates to #123" -->
- Fixes #
- Relates to #

## 🧪 Testing

### Test Coverage
<!-- Run: python run_coverage.py --console-only -->
- [ ] All tests pass locally
- [ ] Coverage meets minimum threshold (70%)
- [ ] Coverage target achieved (85%) or improved
- [ ] New code is covered by tests (if applicable)

### Testing Checklist
- [ ] Unit tests added/updated
- [ ] Integration tests verified  
- [ ] CLI functionality tested
- [ ] Manual testing completed
- [ ] Edge cases considered

### Test Results
<!-- Include relevant test output or coverage report snippets -->
```
Current coverage: ___%
```

## 🔍 Code Quality

### Quality Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Code is well-commented
- [ ] No unnecessary console.log/print statements
- [ ] Error handling implemented appropriately

### Security Considerations
- [ ] No hardcoded secrets or credentials
- [ ] Input validation implemented
- [ ] Security implications considered
- [ ] Dependencies are secure

## 📖 Documentation

### Documentation Updates
- [ ] Code comments added/updated
- [ ] README updated (if needed)
- [ ] API documentation updated (if needed)
- [ ] Migration guide provided (for breaking changes)

## 🚀 Deployment

### Deployment Checklist
- [ ] Backward compatibility maintained (or breaking change noted)
- [ ] Environment variables documented (if added)
- [ ] Database migrations included (if needed)
- [ ] Rollback plan considered

## 👀 Review Instructions

### Focus Areas
<!-- What should reviewers pay special attention to? -->
- 
- 

### Testing Instructions
<!-- How should reviewers test this change? -->
1. 
2. 
3. 

## 📝 Additional Context

### Background
<!-- Why is this change needed? What problem does it solve? -->


### Implementation Notes  
<!-- Any specific implementation details reviewers should know -->


### Future Considerations
<!-- Any follow-up work or considerations for future PRs -->


---

## ✅ Pre-merge Checklist

### Author Checklist
- [ ] PR title follows format: `type: description`
- [ ] PR is focused and addresses one logical change
- [ ] Self-review completed
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] Ready for review

### Reviewer Checklist  
- [ ] Code is understandable and maintainable
- [ ] Tests are appropriate and comprehensive
- [ ] Security considerations addressed
- [ ] Performance impact considered
- [ ] Breaking changes documented

---

<!-- 
Trunk-Based Development Reminders:
- Keep PRs small and focused (<500 lines preferred)
- Merge quickly (within 24 hours)
- Ensure main branch is always deployable
- Use squash merge for clean history
-->

**Estimated Review Time:** ⏱️ _X minutes_ <!-- Help reviewers prioritize -->