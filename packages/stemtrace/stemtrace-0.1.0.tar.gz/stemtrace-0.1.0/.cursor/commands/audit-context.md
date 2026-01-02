# Audit Context

Perform a systematic audit of all project context files (`.context/`), progress tracking (`progress.md`), cursor rules (`.cursor/rules/`), and root documentation to find issues and inconsistencies.

## Your Task

1. **Read all context files** in `.context/`, `progress.md`, and `.cursor/rules/`
2. **Cross-reference** for contradictions, duplications, and stale information
3. **Generate a structured report** with the format below
4. **Offer fix options** and wait for user input before making changes

## Issue Categories to Detect

### 🔴 Critical Issues
- **Contradictions**: Same concept described differently across files
- **Outdated Information**: Progress/status that doesn't match actual codebase
- **Stale Decisions**: Open questions that were already decided

### 🟡 Bloat Issues
- **Duplication**: Same information repeated across multiple files
- **Over-documentation**: Excessive detail for the current codebase size
- **Verbose Examples**: Code examples longer than necessary

### 🟢 Consistency Issues
- **Terminology Drift**: Same concept called different names
- **Format Inconsistency**: Different styles for same type of content
- **Missing Cross-References**: Topics mentioned but not linked to source

## Report Format

```markdown
# Context Audit Report

## Summary
- Files analyzed: X
- Critical issues: X
- Bloat issues: X
- Consistency issues: X

## 🔴 Critical Issues

### Issue N: [Title]
- **Type**: Contradiction/Outdated/Stale
- **Files**: file1.md, file2.md
- **Details**: What's wrong
- **Fix Option A**: [Description]
- **Fix Option B**: [Description]

## 🟡 Bloat Issues
[Same format]

## 🟢 Consistency Issues
[Same format]

## Recommended Actions

### Quick Wins (< 5 min each)
1. [Action]

### Consolidation Tasks (> 5 min)
1. [Action with scope]
```

## Fix Principles

When proposing fixes:

### For Contradictions
- Identify the authoritative source (usually the most specific file)
- Update all other files to match

### For Duplication
Keep detail in the most appropriate file per purpose:
- `project-brief.md`: High-level constraints only
- `product-context.md`: User-facing behavior
- `system-patterns.md`: Architecture with diagrams
- `tech-context.md`: Configuration, versions, setup
- `project-structure.md`: Directory layout ONLY
- Replace duplicates with: "See [file] for details"

### For Bloat
- Simplify code examples to minimum viable
- Remove speculative "future considerations"
- Collapse verbose explanations into bullets
- Remove sections that restate what's in code

### For Outdated Info
- Compare against actual codebase (check if files/dirs exist)
- Delete stale items
- Update `progress.md` status

## After Report

Present these options to the user:

1. **Fix All** - Apply all recommended fixes
2. **Fix Critical Only** - Just critical issues
3. **Fix Quick Wins** - Fast fixes only
4. **Fix Specific** - Let user pick by issue number
5. **Manual Review** - No changes, user will fix manually
6. **Deep Dive** - Explain a specific issue in more detail

Wait for user input before making any changes.

## Post-Audit Reminder

After completing fixes, remind the user:

> 💡 **Tip**: Run `audit-context` periodically (after major features) to prevent context drift.

