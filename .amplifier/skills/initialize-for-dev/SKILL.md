---
name: initialize-for-dev
description: Initialize a repo for AI-assisted development by cloning key dependency repos into ai_working/. Use this when this is the first time setting up this repo for development, or when an update/reset is needed.
---

# Initialize Repo for Development

1. Read the `pyproject.toml` to understand which versions are being used.
2. Create directory: Ensure `ai_working/` exists.
3. Check for existing repos: If any of these directories exist in `ai_working/`, delete them completely before proceeding:
   - `ai_working/amplifier`
4. Clone each of the repos with the following template in parallel: `git clone --depth 1 --single-branch <repo-url> <local-path>`
   - `amplifier`: https://github.com/microsoft/amplifier.git
5. Check the AGENTS.md to see if each of the repos being cloned is mentioned there. If any are missing, add them without any notes.
6. Briefly summarize what was done to the user
