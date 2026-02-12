# General Instructions

- DO NOT make any commits or pushes to any repos without the user's explicit permission.
- Before commit and pushing, make sure under all circumstances that no secrets or private information is being committed.
- Shortcuts are not appropriate. When in doubt, you must work with the user for guidance.
- Anything is possible. Do not blame external factors after something doesn't work on the first try. Instead, investigate and test assumptions through debugging through first principles.
- Keep the README up to date with any changes to the app's user facing interfaces, features, or usage instructions. Keep it short, concise, and in the existing style.
- Make sure any comments in code are necessary. A necessary comment captures intent that cannot be encoded in names, types, or structure. Comments should be reserved for the "why", only used to record rationale, trade-offs, links to specs/papers, or non-obvious domain insights. They should add signal that code cannot.
- When writing documentation
  - Keep it very concise
  - No emojis or em dashes.
  - Documentation should be written exactly like it is for production-grade, polished, open-source applications.

# Dependency Context
- For libraries that are new to you or change frequently, you must refer to their official documentation or source code.
- There is a select set of repos cloned that constitute the dependencies for this project at `ai_working`. You must explore it directly when needed. It can be updated through the Claude command `/setup-reference-repos`  in this project.
  - `amplifier` - To understand the development environment. **Important** the architecture is highly modular, spread across multiple repos. You can discover the repos at `amplifier/docs/MODULES.md` and clone them as needed.
  - `rest-api-description` - GitHub's official OpenAPI descriptions for the REST API. This is the reference spec for the Issues API.
- When looking for something specific that might take a while, use a sub-agent to find it. Tell the sub-agent return the location (paths) of what is found so it can be referenced easily later.
- To figure out how things like `uv` work, start by using `uv --help`. This is a general pattern.

# Smoke Tests

`scripts/smoke_test.py` is the e2e smoke test for the server. It starts the server, calls every endpoint, and checks responses. It is not a unit test suite; it exists so the AI can quickly verify the server works end to end and diagnose failures from the output.
When you add, change, or remove an API endpoint, update the smoke test to cover it. The checks should mirror the real API surface: if a new route exists, there should be a check for it; if a route changes behavior, the check should match. Keep the two phases (no-auth and auth-enabled) in sync with the auth middleware's public paths list.

# Key Files

@README.md
@docs/ISSUES_SPEC.md -- The target API surface. Implementation should match these endpoints.
