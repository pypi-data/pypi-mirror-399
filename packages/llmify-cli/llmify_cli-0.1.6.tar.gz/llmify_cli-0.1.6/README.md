![LLM-ify](Public/assets/llmify.png)

# LLM-ify

LLM-ify turns any website documentation into local, readable docs in seconds. It also generates `llms.txt` and `llms-full.txt` plus full markdown/text captures for single pages or entire sites, so your LLM has clean, structured context.

## Install + Run (Recommended)

```python
pip install llmify-cli
```

```bash
llmify
```

Run Crawl4AI setup (after install):

```bash
llmify setup
```

## Update

```bash
pip install -U llmify-cli
```

## What is llms.txt?

`llms.txt` is a standardized format for making website content more accessible to Large Language Models (LLMs). It provides:

- `llms.txt`: A concise index of all pages with titles and descriptions
- `llms-full.txt`: Complete content of all pages for comprehensive access

## Features

- Turn documentation websites into local, searchable markdown
- Full website or single-page capture
- LLM-friendly index (`llms.txt`) + full corpus (`llms-full.txt`)
- Per-page doc files + glossary for fast navigation
- OpenAI or OpenRouter support
- Interactive terminal UI

## Prerequisites

- Python 3.7+
- OpenAI API key ([Get one here](https://platform.openai.com))
- Crawl4AI browser dependencies (run `llmify setup` after install)

## Developer Quick Run

```bash
git clone https://github.com/Chillbruhhh/LLM-ify.git
cd LLM-ify
python -m venv venv
venv\Scripts\activate  # Windows
# or: source venv/bin/activate (macOS/Linux)
pip install -r requirements.txt
crawl4ai-setup
python main.py
```

Build packages (wheel + sdist):

```bash
python -m build
```

## API Key Setup

Set up your OpenAI API key:

   Option A: Using .env file (recommended)

   ```bash
   cp .env.example .env
   # Edit .env and configure:
   # - Add OPENAI_API_KEY (required)
   ```

   Option B: Using environment variables

   ```bash
   export OPENAI_API_KEY="your-openai-api-key"
   ```

   Option C: Using command line arguments
   (See the TUI for input fields)

### OpenRouter (Optional)

LLM-ify can also use OpenRouter. Set the key and choose the provider in the TUI settings:

```bash
OPENROUTER_API_KEY="your-openrouter-api-key"
```

### Ollama (Optional)

LLM-ify can use a local Ollama server. Select `ollama` in the TUI and set the model name (for example `llama3.1:8b`). Ollama runs at `http://localhost:11434/v1` by default.

## Usage (TUI)

Launch the terminal UI:

```bash
python main.py
```

Enter a URL, choose a mode (full website or single page), and run. Settings are saved in `config.json` automatically.

### Model Provider + Model Name

Choose the provider in Settings, then set the model name for that provider:

- OpenAI default: `gpt-4.1-nano`
- OpenRouter default: `openai/gpt-4.1-nano`
- Ollama: set your local model name (for example `llama3.1:8b`)

## Output Format

### llms.txt

```
# https://example.com llms.txt

- [Page Title](https://example.com/page1): Brief description of the page content here
- [Another Page](https://example.com/page2): Another concise description of page content
```

### llms-full.txt

```
# https://example.com llms-full.txt

<|llm-ify-page-1-lllmstxt|>
## Page Title
Full markdown content of the page...

<|llm-ify-page-2-lllmstxt|>
## Another Page
Full markdown content of another page...
```

## Output Locations

Output files are written under `collected-texts/llmify-<domain>/` by default. Example:

```
collected-texts/llmify-docs.example.com/GLOSSARY.md
collected-texts/llmify-docs.example.com/docs/<page-title>.md
collected-texts/llmify-docs.example.com/llms-files/llms.md
collected-texts/llmify-docs.example.com/llms-files/llms-full.md
collected-texts/llmify-docs.example.com/seeds.json
```

## Agent Instructions

See `INSTRUCTIONS.md` for guidance on how LLM agents should navigate
the generated documentation and glossary.

## Contributing

See `CONTRIBUTING.md` for setup, workflow, and PR guidelines.

## Changelog

See `CHANGELOG.md` for release notes.

## License

PolyForm Noncommercial - see `LICENSE` for details.
