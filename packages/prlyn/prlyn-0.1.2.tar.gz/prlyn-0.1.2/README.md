# prlyn (Prompt Linter)

[![PyPI version](https://img.shields.io/pypi/v/prlyn.svg)](https://pypi.org/project/prlyn/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/Mishtert/prlyn/actions/workflows/ci.yml/badge.svg)](https://github.com/Mishtert/prlyn/actions/workflows/ci.yml)
[![Downloads](https://img.shields.io/pypi/dm/prlyn?color=blueviolet)](https://pypi.org/project/prlyn/)

Stop guessing. Start measuring.

**prlyn** brings engineering discipline to prompt development. It's a static analysis tool that turns "this prompt feels off" into actionable metrics you can track, optimize, and ship with confidence.

## The Problem

You iterate on a system prompt for hours. It works. You ship it. Three weeks later, someone changes one paragraph and your RAG pipeline starts hallucinating. You have no idea what broke or why.

Prompts aren't just text. They're instructions to billion-parameter systems with failure modes you can't predict by eyeballing. You need tooling.

## What prlyn Does

It analyzes your prompts before they hit production and tells you:

**Security vulnerabilities** — Is your delimiter strategy strong enough? Can a user trick the model into ignoring your safety instructions? Are you accidentally teaching the model to leak its own instructions?

**Structural flaws** — Does your prompt have clear command verbs or is it wishy-washy? Are critical instructions buried in the middle where the model might miss them? Does the semantic flow make sense or are you jumping between unrelated topics?

**Model-specific issues** — GPT-4 has recency bias. Claude 3.5 handles long contexts differently. prlyn adjusts its scoring based on which model you're targeting.

**Regressions over time** — Every scan gets saved. Run `prlyn --diff` to see how your latest changes affected quality scores. No more "wait, wasn't this working yesterday?"

## Quick Start

No installation needed. Just run:

```bash
uvx prlyn "Your prompt here..."
```

You'll get a score and specific issues to fix. That's it.

## Installation

If you want it installed locally:

```bash
pip install prlyn
prlyn "Your prompt..."
```

The first run downloads a small Spacy model automatically. After that, everything runs locally on your machine.

## CLI Usage

**Basic analysis:**
```bash
uvx prlyn "Your prompt here..."
```

**Target a specific model:**
```bash
prlyn "..." --model gpt-4
prlyn "..." --model claude-3.5
```

The model flag adjusts scoring thresholds. GPT-4 penalizes buried instructions harder because of recency bias. Claude 3.5 is more lenient on long contexts.

**Track changes between iterations:**
```bash
# First iteration
prlyn "Initial draft..."

# Make changes, then compare
prlyn "Improved draft..." --diff
```

The diff shows you exactly which metrics improved and which got worse. Every run saves to `.prlyn/` automatically.

## For AI Agents (MCP Server)

Here's where it gets interesting. prlyn runs as an MCP server, which means AI coding assistants like Claude, Cursor, or Windsurf can call it directly to analyze and rewrite their own prompts.

Think of it as a linter that your AI pair programmer runs on itself.

### What Your Agent Can Do

prlyn exposes two MCP tools:

**`analyze_prompt`** — Runs the full analysis suite on any prompt text. Returns a structured report with scores for ambiguity, flow cohesion, instructional strength, security vulnerabilities, and token usage. Your agent sees exactly what's wrong and why.

**`get_improvement_template`** — Takes a prompt and returns specific rewrite instructions. Not vague advice like "be clearer." Actual edits: "Move sentence 3 to the beginning. Replace 'try to' with 'must'. Add a delimiter after line 7." Your agent uses this template to fix the prompt, then re-analyzes to verify improvement.

### Recommended Workflow

Your agent should:
1. Draft a prompt
2. Call `analyze_prompt(draft)` to get scores
3. If quality score < 0.8, call `get_improvement_template(draft)`
4. Apply the template instructions to rewrite
5. Call `analyze_prompt(rewritten_prompt)` to confirm it's better
6. Show you the final version

This is self-correcting prompt engineering. The agent tightens its own instructions without you having to debug why "act as a helpful assistant" produces garbage outputs.

### Setup Instructions

Add this to your MCP configuration (works for Claude Desktop, Cursor, Windsurf, Antigravity):

```json
{
  "mcpServers": {
    "prlyn": {
      "command": "uvx",
      "args": ["prlyn"]
    }
  }
}
```

**Claude Desktop**: Edit `claude_desktop_config.json` and restart. You'll see a hammer icon when connected.

**Cursor/Windsurf/Antigravity**: Add to your MCP settings and restart.

### How to Use It

Once configured, you don't need to do anything special. Just ask your agent to analyze or improve a prompt:

```
"Run prlyn on this system prompt and tell me what's wrong"
```

```
"Use prlyn to optimize this instruction set for GPT-4"
```

Your agent will call the MCP tools automatically and show you the results. If it finds issues, it can rewrite the prompt using the improvement template and show you a before/after comparison.

## How It Works

prlyn runs three layers of analysis:

**Linguistic structure** — Using Spacy for POS tagging and SentenceTransformers for semantic embeddings, it measures flow cohesion, instructional strength, and position-based density. It catches the "lost middle" problem where important instructions get buried in long contexts.

**Security patterns** — It looks for delimiter strength, defensive anchors (mandatory safety instructions), and reflexive leakage (instructions that accidentally teach the model to reveal itself). These are design-time vulnerabilities, not runtime attacks.

**Model-aware scoring** — Use `--model gpt-4` or `--model claude-3.5` to adjust thresholds based on known model behaviors. GPT-4 gets penalized harder for burying instructions late in the prompt. Claude 3.5 gets more lenient scoring because of its superior long-context retrieval.

Token counts use `tiktoken` for accuracy. Everything runs locally. No data leaves your machine.

## Metrics Explained

**Actionable Ratio** — Percentage of sentences with strong command verbs. Low score means your prompt is vague. Target 0.6+.

**Flow Cohesion** — Semantic similarity between adjacent sections. Scores below 0.5 suggest disjointed logic that confuses the model.

**Instructional Strength** — Weighted verb analysis. "Must" scores higher than "try" or "consider." Weak verbs create ambiguous instructions.

**Position Score** — Measures whether critical instructions are front-loaded or back-loaded. Models pay more attention to edges of the context window.

**Delimiter Strength** — Evaluates your separation strategy between system instructions and user input. Weak delimiters enable injection attacks.

## For Developers

Want to contribute?

```bash
git clone https://github.com/Mishtert/prlyn.git
cd prlyn
uv sync
uv run pytest
uv run pre-commit run --all-files
```

The CI pipeline runs four stages on every PR: quality (ruff + mypy), security (bandit), tests (pytest), and build verification. See [CONTRIBUTING.md](https://github.com/Mishtert/prlyn/blob/main/CONTRIBUTING.md) for details.

## Privacy

Everything runs locally. prlyn doesn't send data anywhere. We track usage through public PyPI download stats only.

## Why This Matters

Most prompt engineering is vibes-based. Someone edits a sentence, tests it a few times, decides it's better, and ships. When things break in production, you debug by trial and error.

prlyn gives you numbers. Track them over time. Set thresholds in CI. Catch regressions before users do. Treat prompts like the production code they are.

The models are getting better, but they're not perfect. Your prompts need to be engineered, not just written. Start here.
