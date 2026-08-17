---
name: llm-tools
description: "Tools for working with Large Language Models: evaluation, knowledge base, and serving."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [LLM, Evaluation, Knowledge-Base, Serving]
    related_skills: []
---

# LLM Tools

This skill provides tools for working with Large Language Models (LLMs), including evaluation, knowledge base management, and model serving.

## Evaluation (lm-evaluation-harness)

Benchmark LLMs using the Language Model Evaluation Harness. See references for details.

## Knowledge Base (llm-wiki)

Build and maintain a persistent, interlinked Markdown knowledge base based on Andrej Karpathy's LLM Wiki pattern.

## Serving (vllm)

High-throughput LLM serving with OpenAI-compatible API using vLLM.

## Usage

Consult the original skills (now archived) for detailed usage instructions, or refer to the reference files stored under this skill's references/ directory.

## References

- `references/openrouter-pricing.md` — Check current OpenRouter model prices and account balance programmatically. Covers the per-token vs per-million conversion gotcha, provider-level pricing, and comparison with official API pricing.