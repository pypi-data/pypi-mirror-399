---
description: Create a git commit with a good message
argument-hint: [optional: specific message]
---

Create a git commit for the current changes.

## Steps
1. Run `git status` to see what files have changed
2. Run `git diff --staged` to review staged changes
3. If nothing is staged, suggest which files to add
4. Create a descriptive commit message following conventional commits format:
   - feat: new feature
   - fix: bug fix
   - docs: documentation changes
   - refactor: code refactoring
   - test: test changes
   - chore: maintenance tasks

$ARGUMENTS
