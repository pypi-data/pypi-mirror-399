# Create Pull Request

Create a GitHub Pull Request using the `gh` CLI.

## Repository

- **Repo**: `iansokolskyi/celery-flow`
- **Auth**: Must be authenticated as `iansokolskyi`

## Default Behavior

- **Base branch**: `main`
- **Head branch**: `dev` (or current branch if not on dev)

Override with arguments: `/pr base:release head:feature/my-feature`

## Your Task

1. **Verify repo and auth** before proceeding
2. **Check current branch** and confirm head/base branches
3. **Check for unpushed commits** and push if needed
4. **Generate PR title and body** from commits
5. **Create PR** using `gh pr create`
6. **Show PR URL** for easy access

## Process

### Step 0: Verify Repository and Auth

```bash
# Check we're in the right repo
git remote get-url origin
# Should be: git@github.com:iansokolskyi/celery-flow.git
# Or: https://github.com/iansokolskyi/celery-flow.git

# Check gh auth status
gh auth status
# Should show: Logged in to github.com as iansokolskyi
```

If not authenticated correctly, stop and inform user to run:
```bash
gh auth login
```

### Step 1: Confirm Branches

```bash
git branch --show-current
git log origin/main..HEAD --oneline
```

Show user:
```
Creating PR:
  base: main
  head: dev (3 commits ahead)

Commits to include:
  abc1234 feat: add new feature
  def5678 test: add tests
  ghi9012 chore: update deps

Continue? [y/n]
```

### Step 2: Push if Needed

Check for unpushed commits:
```bash
git log origin/<head-branch>..HEAD --oneline
```

If there are unpushed commits, **automatically push them** before creating PR:
```bash
git push origin <head-branch>
```

Do not ask for confirmation — just push and inform the user:
```
Pushing 4 commits to origin/dev...
✓ Pushed successfully
```

### Step 3: Generate PR Content

**Title**: Use the first commit message if single commit, otherwise summarize:
- Single commit: Use commit message as title
- Multiple commits: Generate summary title (e.g., "Add E2E testing infrastructure")

**Body**: List all commits with their messages:
```markdown
## Changes

- feat: add new feature
- test: add tests  
- chore: update deps

## Summary

<Brief description of what this PR accomplishes>
```

### Step 4: Create PR

Always specify the repo explicitly:

```bash
gh pr create --repo iansokolskyi/celery-flow --base main --head dev --title "..." --body "..."
```

Or open in browser for manual editing:
```bash
gh pr create --repo iansokolskyi/celery-flow --base main --head dev --web
```

### Step 5: Show Result

Display the PR URL:
```
✅ PR created: https://github.com/owner/repo/pull/123
```

## Examples

### Default (dev → main)
```
/pr
```

### Custom branches
```
/pr base:release head:feature/auth
```

### Open in browser for editing
```
/pr --web
```

## Notes

- Requires `gh` CLI installed and authenticated as `iansokolskyi`
- Always use `--repo iansokolskyi/celery-flow` flag
- Verify auth with `gh auth status` before creating PR
- If `gh` is not available, provide manual instructions
- Always confirm before creating PR
- Don't auto-merge; let user review and merge manually

