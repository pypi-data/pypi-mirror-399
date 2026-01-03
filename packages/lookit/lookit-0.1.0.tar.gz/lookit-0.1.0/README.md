# Lookit

LLM-first vision toolkit for GUI grounding, OCR, and more. Built with [LangChain](https://github.com/langchain-ai/langchain) and [Qwen3-VL](https://ollama.com/library/qwen3-vl). Outputs minimal plain text optimized for token efficiency.

## Installation

### 1. Install CLI

```bash
pip install lookit
```

### 2. Configure Environment

Works with any OpenAI-compatible API ([Ollama](https://ollama.com/library/qwen3-vl), vLLM, OpenRouter, etc.):

**macOS / Linux:**

```bash
# Add to ~/.zshrc (macOS) or ~/.bashrc (Linux)
cat << 'EOF' >> ~/.zshrc
# Ollama local
export LOOKIT_API_KEY="ollama"
export LOOKIT_MODEL="qwen3-vl"
export LOOKIT_BASE_URL="http://localhost:11434/v1"
EOF

source ~/.zshrc
```

For better results, use Ollama Cloud with the larger model ([get API key](https://ollama.com/settings/keys)):

```bash
export LOOKIT_API_KEY="your-ollama-api-key"
export LOOKIT_MODEL="qwen3-vl:235b-cloud"
export LOOKIT_BASE_URL="https://ollama.com/v1"
```

## Skills Setup

Skills follow the [Agent Skills specification](https://agentskills.io/specification).

| Skill | Description |
|-------|-------------|
| `computer-use` | GUI grounding for desktop screenshots |
| `mobile-use` | GUI grounding for mobile screenshots |
| `ocr` | Text extraction from screenshots |

<details>
<summary>Claude Code</summary>

```bash
mkdir -p ~/.claude/skills/{computer-use,mobile-use,ocr}

curl -sL https://raw.githubusercontent.com/atom2ueki/lookit/main/skills/computer-use/SKILL.md -o ~/.claude/skills/computer-use/SKILL.md
curl -sL https://raw.githubusercontent.com/atom2ueki/lookit/main/skills/mobile-use/SKILL.md -o ~/.claude/skills/mobile-use/SKILL.md
curl -sL https://raw.githubusercontent.com/atom2ueki/lookit/main/skills/ocr/SKILL.md -o ~/.claude/skills/ocr/SKILL.md
```

</details>

<details>
<summary>DeepAgents CLI</summary>

[DeepAgents](https://github.com/langchain-ai/deepagents) is an agent framework built on LangChain and LangGraph.

```bash
# Install deepagents CLI
pip install deepagents-cli

# Create skill directories
mkdir -p ~/.deepagents/default/skills/{computer-use,mobile-use,ocr}

# Download skills
curl -sL https://raw.githubusercontent.com/atom2ueki/lookit/main/skills/computer-use/SKILL.md -o ~/.deepagents/default/skills/computer-use/SKILL.md
curl -sL https://raw.githubusercontent.com/atom2ueki/lookit/main/skills/mobile-use/SKILL.md -o ~/.deepagents/default/skills/mobile-use/SKILL.md
curl -sL https://raw.githubusercontent.com/atom2ueki/lookit/main/skills/ocr/SKILL.md -o ~/.deepagents/default/skills/ocr/SKILL.md

# Verify skills installed
deepagents skills list
```

</details>

<details>
<summary>Programmatic Integration</summary>

For integrating skills into your own LangChain agents, see [deepagents PR #611](https://github.com/langchain-ai/deepagents/pull/611) (WIP).

```python
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend
from deepagents.middleware import SkillsMiddleware

# Create backend and skills middleware
backend = FilesystemBackend()
skills_middleware = SkillsMiddleware(
    backend=backend,
    registries=[
        {"path": "/skills/user/", "name": "user"},
        {"path": "/skills/project/", "name": "project"},
    ],
)

# Create agent with skills middleware
agent = create_deep_agent(
    model="openai:gpt-4o",
    middleware=[skills_middleware],
)

# Agent will automatically discover and use lookit skills
result = agent.invoke({
    "messages": [{"role": "user", "content": "Click the submit button in screenshot.png"}]
})
```

</details>

## Usage

Same screenshot, different modes and prompts = different results:

| OCR Mode | Computer Mode |
|----------|---------------|
| `lookit "extract the transaction history" -s screenshot.png --mode ocr` | `lookit "click search" -s screenshot.png --mode computer` |
| ![Screenshot](assets/example_screenshot.png) | ![Result](assets/example_result.png) |
| `Max Now Pte. Ltd.`<br>`Singapore SG`<br>`24 Dec 2025 10:07:13`<br>`SGD 70.85`<br>`140 points`<br>`Pending`<br>`...` | `left_click 2910,365` |

## Output Format

### Action Modes (computer/mobile)

```
left_click 960,324
type "hello world"
swipe 500,800 to 500,200
key Control+c
scroll -100
```

### OCR Mode

Returns extracted text directly.

## Arguments

| Argument | Description |
|----------|-------------|
| `query` | Natural language instruction |
| `-s, --screenshot` | Path to screenshot (required) |
| `--mode` | `computer`, `mobile`, or `ocr` (required) |
| `--debug` | Debug mode (for humans): print info to stderr, save annotated image |

## Actions

### Computer

`left_click`, `right_click`, `double_click`, `type`, `key`, `scroll`, `mouse_move`

### Mobile

`click`, `long_press`, `swipe`, `type`, `system_button`

## License

MIT
