# Commit Changes

Generate and execute git commit(s) for the current changes, following project conventions.

## Your Task

1. **Check git status** to see what files have changed
2. **Analyze changes** to understand what was done
3. **Group logically** - if unrelated changes, suggest separate commits
4. **Generate commit message(s)** following conventional commits
5. **Present for approval** before executing

## Commit Message Format

```
<type>: <description>
```

### Types
- `feat`: New feature
- `fix`: Bug fix  
- `docs`: Documentation only
- `refactor`: Code restructuring
- `test`: Adding/updating tests
- `chore`: Maintenance (deps, config, build)

### Description
- Lowercase, no period
- Imperative mood ("add" not "added")
- Under 50 chars if possible
- Describe WHAT changed, not WHY or phase context

## Examples

```
feat: add CLI server and consume commands
test: add FastAPI integration tests
fix: resolve union return type in static router
chore: add Dockerfile and docker-compose
refactor: move inline imports to file top
```

## Anti-Patterns

❌ `Phase 5: Add tests and Docker` (mentions phases)
❌ `Various improvements` (too vague)
❌ `Updated files` (meaningless)
❌ `feat: add server command, tests, docker, and fix bug` (multiple unrelated things)
❌ `refactor: remove AI-generated comments` (never mention AI in commits)
❌ `fix: clean up AI tells` (exposes implementation detail)

When cleaning up code patterns, use neutral descriptions:
- "simplify comments" not "remove AI comments"
- "clean up redundant code" not "remove AI-generated code"

## Process

### Step 1: Show Status
Run `git status` and `git diff --stat` to see changes.
**Ignore any `.cursor/` or `.context/` files** - these are local and should not be committed.

### Step 2: Analyze & Group
If changes span multiple unrelated areas, suggest splitting into commits:

```
Suggested commits:
1. test: add FastAPI integration tests
2. feat: implement CLI server and consume commands
3. chore: add Dockerfile and docker-compose

Proceed with these commits? [y/n/edit]
```

### Step 3: Stage & Commit
For each commit:
1. Stage relevant files: `git add <files>`
   - **Never stage `.cursor/` or `.context/` files** - these are local/ignored
2. Commit with message: `git commit -m "<message>"`

### Step 4: Summary
Show final `git log --oneline -n <count>` to confirm.

## Notes

- Always run `make check` passes before committing
- Don't auto-push; let user decide when to push
- If unsure about grouping, ask user
- **Never stage `.cursor/` or `.context/` directories** - these are local project intelligence files ignored by git

