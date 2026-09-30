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
- **Spend queries sparingly and pace them** – see "First-pass probe signals" below for
  the list to use and the pacing budget.

### First-pass probe signals

This is the canonical short list every remote scan starts with. Keep it here only; the
workflow and the custom agent refer to this section rather than repeating it. Each token
covers a provider family across languages – e.g. `"openai"` catches `import openai`,
`from "openai"`, `Azure.AI.OpenAI`, `openai.azure.com` and `agent-framework-openai`.
Note that code search tokenises on `.` **and** `_`, so casing variants of the same
product need separate probes: `"SemanticKernel"` does *not* match Python's
`semantic_kernel`, which is why both appear below.

```
"openai"        "anthropic"      "azure.ai"        "langchain"
"generative-ai" "generativeai"   "huggingface"     "transformers"
"bedrock"       "sagemaker"      "llama_index"     "llamaindex"
"SemanticKernel" "semantic_kernel" "Microsoft.Agents.AI" "Microsoft.Extensions.AI"
"mistralai"     "cohere"         "ollama"
```

That is roughly 19 queries per repository. Because code search allows only about 10
requests per minute, work through one repository at a time and pause between batches
rather than firing the queries all at once; only drill into narrower signals from the
table above when a repository's language or an early hit justifies it. Budget at least
two minutes of searching per repository, plus time for listing repositories, reading
manifests and writing the report, when deciding how many repositories a run can cover.

If rate limiting cuts a scan short, or you drop any of these probes to save time, say so
explicitly in the report (for example "first pass did not probe for Cohere/Ollama") so
nobody reads a clean result as proof that those providers are absent.

Use the `text_matches` snippets returned by the search to triage, and fetch file
contents only for the candidates the snippet cannot settle.
