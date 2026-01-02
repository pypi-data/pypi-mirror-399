# Address PR Review Comments & CI Failures

Check open PRs for review comments and CI failures, then fix them.

## Repository

- **Repo**: `iansokolskyi/celery-flow`
- **Auth**: Must be authenticated as `iansokolskyi`

## Your Task

1. **List open PRs** and let user select one (or use current branch's PR)
2. **Check CI status** for failing checks
3. **Fetch review comments** from the PR
4. **Categorize issues by severity** and present to user
5. **Fix ALL issues** (Critical → Major → Minor → Nitpick)
6. **Commit fixes** following `/commit` conventions
7. **Push to PR branch** automatically

## Issue Severity Levels

CodeRabbit and other review tools use severity markers. **Parse and respect these:**

| Severity | Marker | Action Required |
|----------|--------|-----------------|
| 🔴 Critical | `_🔴 Critical_` | **FIX FIRST** — blocks merge |
| 🟠 Major | `_🟠 Major_` | **FIX** — significant issue |
| 🟡 Minor | `_🟡 Minor_` | **FIX** — low-risk improvement |
| Nitpick | `🧹 Nitpick` | **FIX** — code quality improvement |

**Address ALL issues.** Fix in priority order (Critical → Major → Minor → Nitpick).
**NEVER skip issues.** If a fix seems wrong, discuss with user first.

## Process

### Step 1: Find PR

Check for PR on current branch:
```bash
gh pr view --repo iansokolskyi/celery-flow --json number,title,headRefName,url
```

Or list all open PRs:
```bash
gh pr list --repo iansokolskyi/celery-flow --state open
```

### Step 2: Check CI Status

Get status of all checks:
```bash
gh pr checks <number> --repo iansokolskyi/celery-flow
```

For failed checks, get the logs:
```bash
gh run view <run-id> --repo iansokolskyi/celery-flow --log-failed
```

To find the run ID from a failed check:
```bash
gh pr checks <number> --repo iansokolskyi/celery-flow --json name,state,link
```

### Step 3: Fetch Review Comments

Get all review comments (including automated reviews):
```bash
gh pr view <number> --repo iansokolskyi/celery-flow --comments --json comments,reviews
```

Also check the PR conversation:
```bash
gh api repos/iansokolskyi/celery-flow/pulls/<number>/comments
gh api repos/iansokolskyi/celery-flow/pulls/<number>/reviews
```

**Read the full comment body.** CodeRabbit comments include:
- Severity marker and issue title
- Detailed explanation of the problem
- **Recommended approach** with specific fix steps
- **AI agent prompts** — ready-to-use instructions
- Code examples and edge cases to consider

### Step 4: Summarize All Issues BY SEVERITY

Parse review comment bodies for severity markers and categorize:

```
PR #15: Add E2E testing infrastructure

❌ CI Failures (MUST FIX):
1. [ci.yml] test (3.12): pytest failed - test_graph.py::test_duration assertion error

🔴 Critical Issues (MUST FIX):
1. [index.css:76] Remove !important to fix CI linting failure

🟠 Major Issues (MUST FIX):
1. [.pre-commit-config.yaml:31] git add -u stages unintended files

🟡 Minor Issues:
1. [format.ts:1] Consider edge cases for negative values

🧹 Nitpicks:
1. [TaskGraph.tsx:208] Consider extracting helper function

---
Total: 5 issues to fix

Proceed with fixes? [y/n]
```

**Important:** Fix ALL issues in priority order. Never skip any.

### Step 5: Fix Issues

**Priority order (fix ALL in order):**
1. CI failures (blocking merge)
2. 🔴 Critical review comments
3. 🟠 Major review comments
4. 🟡 Minor review comments
5. 🧹 Nitpick comments

**For CI failures:**
1. Parse the error from logs
2. Identify the file and line
3. **Reproduce locally first** — always validate the issue locally before fixing:
   - For Python tests: `pytest <test_file>::<test_name> -v`
   - For Playwright tests: `cd src/celery_flow/server/ui/frontend && npx playwright test <file>:<line>`
   - For lint issues: `make lint` or `npm run check`
4. Fix the root cause
5. Run the same local command again to verify the fix works
6. Only then move on to commit

**For review comments:**
1. **Read the FULL comment** — CodeRabbit comments contain valuable context:
   - **Recommended approach** — specific fix suggestions
   - **AI agent prompts** — copy-paste instructions for implementation
   - **Scenarios/edge cases** — what to consider
   - **Code examples** — sometimes includes exact fixes
2. Read the relevant file and surrounding context
3. Apply the fix using the recommended approach from the comment
4. If the comment relates to tests, run tests locally before committing
5. Move to next issue

**Don't skim comments.** The full comment text often has everything needed for a precise fix.

### Step 6: Commit Fixes

Follow `/commit` conventions:
- Group related fixes logically
- Use appropriate commit types (`fix:`, `refactor:`, `docs:`, etc.)
- **Never mention review tools or bots in commit messages**
- Use neutral descriptions:
  - ✅ `fix: add error handling for empty input`
  - ✅ `docs: fix typo in docstring`
  - ❌ `fix: address coderabbit review comments`
  - ❌ `fix: resolve automated review issues`

### Step 7: Push to PR Branch

After committing, push to the PR's head branch:
```bash
git push origin <head-branch>
```

Show confirmation:
```
✅ Pushed fixes to origin/dev
   PR #15 updated: https://github.com/iansokolskyi/celery-flow/pull/15
```

## Commit Message Examples

When fixing review comments, use specific descriptions:

```
fix: add null check in graph traversal
fix: handle empty task list gracefully
docs: correct parameter description in docstring
refactor: simplify conditional logic in consumer
test: add missing edge case coverage
style: fix inconsistent indentation
```

## Anti-Patterns

❌ `fix: address review comments` (too vague)
❌ `fix: coderabbit suggestions` (mentions tool)
❌ `fix: PR feedback` (not specific)
❌ `chore: resolve automated review` (mentions automation)

## CI Check Commands Reference

```bash
# List all checks on a PR
gh pr checks 15 --repo iansokolskyi/celery-flow

# Get JSON for parsing
gh pr checks 15 --repo iansokolskyi/celery-flow --json name,state,conclusion

# List workflow runs
gh run list --repo iansokolskyi/celery-flow --branch dev

# View failed run logs
gh run view <run-id> --repo iansokolskyi/celery-flow --log-failed

# View specific job logs
gh run view <run-id> --repo iansokolskyi/celery-flow --job <job-id> --log
```

## Notes

- **Address ALL issues** — CI failures, Critical, Major, Minor, and Nitpicks
- Always verify you're on the correct branch before making changes
- If PR has conflicts, inform user and stop
- Group related fixes into one commit
- After push, CI will re-run automatically
- Wait for CI to pass before marking PR ready for review

## Common Severity Patterns

Look for these patterns in review comment bodies:

```
_⚠️ Potential issue_ | _🔴 Critical_  → Fix first
_⚠️ Potential issue_ | _🟠 Major_     → Fix second  
_⚠️ Potential issue_ | _🟡 Minor_     → Fix third
🧹 Nitpick comments (15)              → Fix last
```

**Fix ALL issues.** Parse the severity marker and work through them in priority order.

