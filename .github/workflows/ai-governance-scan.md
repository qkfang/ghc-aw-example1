---
description: >-
  Scans repositories for AI/LLM usage and flags any AI solution that is not
  recorded in the AI Governance Register (governance/ai-register.yml).
on:
  schedule: weekly on monday
  workflow_dispatch:
    inputs:
      scope:
        description: "What to scan: 'repo' (this repository only) or 'org' (every repository in the owner organisation)"
        required: false
        default: repo
        type: choice
        options:
          - repo
          - org
  push:
    branches: [main]
    paths:
      - "governance/**"
      - "samples/**"

permissions:
  contents: read
  issues: read

engine: copilot

tools:
  github:
    # For org-wide scans set the GH_AW_GITHUB_MCP_SERVER_TOKEN secret to a
    # fine-grained PAT (or use a GitHub App) with read access to "Contents"
    # and "Metadata" on every repository in the organisation.
    toolsets: [repos, search, issues]
  bash:
    - "cat *"
    - "ls *"
    - "find *"
    - "grep *"
    - "rg *"
    - "head *"
    - "wc *"

safe-outputs:
  create-issue:
    title-prefix: "[AI Governance] "
    labels: [ai-governance, needs-triage]
    max: 1

timeout-minutes: 20
---

# AI Governance Register Compliance Scan

You are an AI governance auditor for the **${{ github.repository_owner }}** organisation.
Your job is to find AI solutions (code that calls an LLM, generative AI service, or ML
model) that have **not** been logged in the AI Governance Register.

Scan scope for this run: `${{ github.event.inputs.scope }}` (if empty, treat it as `repo`).

## Inputs

1. Read the register: `governance/ai-register.yml` in this repository
   (`${{ github.repository }}`). Each entry lists a `repository` and the `paths`
   inside it that the entry covers.
2. Read the detection rules: `governance/detection-rules.md`. Use its strong
   signals, weak signals and exclusions.

## Step 1 – Discover AI usage

- **scope = `repo`**: scan the checked-out workspace with `grep`/`find`
  (skip `.git/`, `.github/`, `governance/`, `node_modules/`, `vendor/`, `.venv/`).
- **scope = `org`**: use the GitHub `search_code` tool with queries such as
  `org:${{ github.repository_owner }} "from openai import"`,
  `org:${{ github.repository_owner }} "@anthropic-ai/sdk" filename:package.json`,
  `org:${{ github.repository_owner }} "Azure.AI.OpenAI"`,
  `org:${{ github.repository_owner }} "openai.azure.com"`, etc. – one query per
  strong signal in the detection rules. Also list the organisation's repositories
  and, for recently pushed repositories, inspect dependency manifests
  (`package.json`, `requirements.txt`, `pyproject.toml`, `*.csproj`, `pom.xml`,
  `go.mod`) with `get_file_contents`. Ignore archived repositories.

For every hit, open the file and confirm it is real AI usage (not a mock, test
fixture that only mentions AI, or documentation). Group hits into **solutions**:
one solution = one repository + the top-level folder / app that contains the AI code.

## Step 2 – Compare against the register

A solution is **registered** when there is a register entry whose `repository`
matches (case-insensitive) and one of whose `paths` is a prefix of the solution's
file paths (`/` means the whole repository). Also flag registered entries where
the code uses a provider or model that is **not** listed in the entry – this is
"scope drift".

## Step 3 – Report

- If every solution is registered and there is no scope drift, do **not** create
  an issue; call the `noop` safe output with a one-line summary instead.
- Otherwise create **one** issue titled
  `Unregistered AI solutions detected (<N> found)` containing:
  - A summary table: Repository | Path | Provider / SDK | Model(s) | Evidence (file link + line) | Suggested owner (last committer, if known)
  - A "Scope drift" table for registered solutions using unlisted providers/models.
  - A ready-to-paste YAML snippet per unregistered solution that follows the
    format of `governance/ai-register.yml`, with unknown fields set to `TODO`.
  - A short "Next steps" section asking the owners to complete the register entry
    and link the governance review.

Rules:
- Never include secret values in the issue – only reference variable names.
- Be precise: prefer fewer, well-evidenced findings over speculative ones.
- Link to files using `https://github.com/<owner>/<repo>/blob/<default-branch>/<path>#L<line>`.
