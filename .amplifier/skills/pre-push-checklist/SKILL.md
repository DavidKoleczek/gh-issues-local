---
name: pre-push-checklist
description: Pre-commit/push checklist that reviews staged changes, syncs with upstream, runs spelling/grammar checks, runs all dev checks from the README, and generates a commit message. Use before committing and pushing.
---

# Pre-Push Checklist

## Understand Changes

1. Look at the currently staged changes (`git diff --cached`) to identify what was changed and why.
2. Check if there are changes to pull from upstream (`git fetch && git log HEAD..@{u} --oneline`). If there are, sync carefully:
   1. Stash the current changes (`git stash --include-untracked`).
   2. Pull from upstream (`git pull`).
   3. Re-apply the stash (`git stash pop`) and resolve any merge conflicts that arise. Take great care to make sure none of the user's changes are lost.

## Checks

1. Review the staged diff for spelling and grammar mistakes in user-facing strings, comments, and documentation. Fix any found.
2. Read the `README.md` and find the "## Development" section. Run each of the checks listed there. Fix any issues that are simple. If a fix would require more complex changes, stop and consult with the user before proceeding.
3. Commit up with a short commit message following the existing style of commit messages in the repo's git log. Place the commit message at the very end of your response.

Finally, commit and push the changes to the repo.
