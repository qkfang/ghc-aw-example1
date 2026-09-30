# AI Usage Detection Rules

These are the signals the AI Governance Scan agent looks for. A single weak signal
is not enough on its own – the agent should confirm by reading the surrounding code.

## Strong signals (AI solution almost certainly present)

| Category | Examples |
|----------|----------|
| Python SDK imports | `import openai`, `from openai import`, `import anthropic`, `from azure.ai.inference`, `from azure.ai.openai`, `from azure.ai.projects`, `import agent_framework` (`agent-framework-*` packages), `import google.generativeai`, `from langchain`, `import llama_index`, `from semantic_kernel`, `import transformers`, `import mistralai`, `import cohere`, `import ollama` |
| JS/TS SDK imports | `from "openai"`, `@azure/openai`, `@anthropic-ai/sdk`, `@google/generative-ai`, `langchain`, `@langchain/*`, `ai` (Vercel AI SDK), `@huggingface/inference` |
| .NET packages | `Azure.AI.OpenAI`, `Azure.AI.Projects`, `Microsoft.SemanticKernel`, `Microsoft.Extensions.AI`, `Microsoft.Agents.AI`, `Microsoft.Agents.AI.Foundry`, `OpenAI` |
| Java packages | `com.azure:azure-ai-openai`, `dev.langchain4j`, `com.theokanning.openai-gpt3-java`, `spring-ai` |
| Dependency manifests | Any of the above in `requirements.txt`, `pyproject.toml`, `package.json`, `*.csproj`, `pom.xml`, `build.gradle`, `go.mod` |
| API endpoints | `api.openai.com`, `*.openai.azure.com`, `api.anthropic.com`, `generativelanguage.googleapis.com`, `*.cognitiveservices.azure.com`, `api-inference.huggingface.co`, `bedrock-runtime` |
| Infrastructure as Code | `Microsoft.CognitiveServices/accounts` (kind `OpenAI`/`AIServices`), `azurerm_cognitive_account`, `Microsoft.MachineLearningServices`, `aws_bedrock*`, `aws_sagemaker*` |

## Weak signals (investigate, do not report alone)

- Environment variables such as `OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `ANTHROPIC_API_KEY`, `HF_TOKEN`
- Words like `prompt`, `completion`, `embedding`, `llm`, `gpt`, `chat model` in code
- Model files: `*.onnx`, `*.safetensors`, `*.gguf`, `*.pt`, `*.h5`

## Exclusions

- Test fixtures, mocks and documentation that only *mention* AI.
- This repository's `governance/` folder and `.github/` folder.
- Vendored third-party code (`node_modules/`, `vendor/`, `.venv/`).
- Transitive dependencies in lockfiles. A signal only counts when it appears in a
  first-party source file or in the *direct* dependencies of a manifest – not in any
  lockfile (`package-lock.json`, `pnpm-lock.yaml`, `yarn.lock`, `poetry.lock`,
  `Pipfile.lock`, `uv.lock`, `packages.lock.json`, `go.sum`, or any other `*.lock`).

## Searching remotely (no clone)

When scanning repositories you have not checked out, use GitHub code search rather than
downloading the tree. Several constraints of those APIs change how the signals above
must be queried:

- Scope repository search with `owner:<owner>` – it matches both user and organisation
  accounts, while `org:<owner>` returns **zero** results for a user account and
  `user:<owner>` returns zero for an organisation.
- Scope *code* search with `repo:<owner>/<name>`, one repository at a time. Code search
  does **not** support the `owner:` qualifier (it returns zero results); `user:`/`org:`
  work but only for the matching account type. Scoping per repository is also what keeps
  a scan inside the caller's repository budget – list repositories first, bound the list
  to that budget (default **5** when the caller does not set one), and only then search
  the kept repositories.
- **Quote every signal.** A quoted phrase matches even when it contains dots or spaces
  (`"openai.azure.com"`, `"Microsoft.Agents.AI"`, `"from openai import"`); unquoted
  dotted names do not, because code search tokenises on `.`.
- **Never join signals with `OR`** – `Azure.AI.OpenAI OR Microsoft.SemanticKernel`
  returns nothing. Issue one query per signal.
- **Spend queries sparingly.** Code search allows roughly 10 requests per minute, so
  probe each repository with the first-pass signals below rather than the full table
  above, and only drill into narrower signals when the repository's language or an
  early hit justifies it. If rate limiting cuts a scan short, report the reduced
  coverage instead of treating unsearched repositories as clean.

### First-pass probe signals

This is the canonical short list every remote scan starts with – roughly eight queries
per repository. Keep it here only; the workflow and the custom agent refer to this
section rather than repeating it.

```
"openai"  "anthropic"  "azure.ai"  "langchain"
"SemanticKernel"  "Microsoft.Agents.AI"  "huggingface"  "bedrock"
```

Use the `text_matches` snippets returned by the search to triage, and fetch file
contents only for the candidates the snippet cannot settle.
