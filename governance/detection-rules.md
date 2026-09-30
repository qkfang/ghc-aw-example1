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
- Transitive dependencies in lockfiles (`package-lock.json`, `yarn.lock`, `poetry.lock`,
  `packages.lock.json`). A signal only counts when it appears in a first-party source
  file or in the direct dependencies of a manifest.

## Searching remotely (no clone)

When scanning repositories you have not checked out, use GitHub code search rather than
downloading the tree. Two constraints of that API change how the signals above must be
queried:

- Scope repository search with `owner:<owner>` – it matches both user and organisation
  accounts, while `org:<owner>` returns **zero** results for a user account and
  `user:<owner>` returns zero for an organisation.
- Scope *code* search with `repo:<owner>/<name>`, one repository at a time. Code search
  does **not** support the `owner:` qualifier (it returns zero results); `user:`/`org:`
  work but only for the matching account type.
- **Quote every signal.** A quoted phrase matches even when it contains dots or spaces
  (`"openai.azure.com"`, `"Microsoft.Agents.AI"`, `"from openai import"`); unquoted
  dotted names do not, because code search tokenises on `.`.
- **Never join signals with `OR`** – `Azure.AI.OpenAI OR Microsoft.SemanticKernel`
  returns nothing. Issue one query per signal.

Use the `text_matches` snippets returned by the search to triage, and fetch file
contents only for the candidates the snippet cannot settle.
