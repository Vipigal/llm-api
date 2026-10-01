# BEON.tech Q&A API

A FastAPI service that answers questions about BEON.tech using a local open-weight model served by [Ollama](https://ollama.com), orchestrated with [PydanticAI](https://ai.pydantic.dev).

The model answers **only** from a fixed knowledge base about BEON.tech. Anything else gets `"Sorry, I cant help with that"`.

## How it works

- `POST /question` validates and sanitizes the input (`app/main.py`).
- A PydanticAI agent (`app/agent.py`) calls Ollama through its OpenAI-compatible API and gets back structured output (`ScopedAnswer`, with `in_scope` and `response`), constrained by a JSON schema.
- If `in_scope` is false, the code returns the refusal message itself, so the refusal does not depend on the model getting the wording right.
- The API responds with `Answer`: `{"response": "..."}`.

## Requirements

- Python 3.12+
- Ollama running locally with the model pulled:

```bash
ollama pull qwen3:1.7b
```

## Running

Locally:

```bash
python -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload
```

With Docker (reaches Ollama on the host via `host.docker.internal`):

```bash
docker compose up --build
```

> On Linux, Ollama listens on `127.0.0.1` by default, so the container can't reach it. Start Ollama with `OLLAMA_HOST=0.0.0.0` instead.

## Configuration

| Env var                 | Default                     | Description                         |
| ----------------------- | --------------------------- | ----------------------------------- |
| `OLLAMA_BASE_URL`       | `http://localhost:11434/v1` | Ollama OpenAI-compatible endpoint   |
| `OLLAMA_MODEL`          | `qwen3:1.7b`                | Model name as listed by `ollama ls` |
| `PYDANTIC_AI_NO_BANNER` | unset                       | Set to `1` to hide the startup banner |

## Usage

```bash
curl -X POST localhost:8000/question \
  -H 'content-type: application/json' \
  -d '{"question": "What is BEON.tech mission?"}'
```

```json
{"response": "BEON.tech's mission is to place the brightest tech talent in the most disruptive and innovative U.S. companies."}
```

Out-of-scope questions return `{"response": "Sorry, I cant help with that"}`.

### Input rules

`question` is required, must be a string, and must be 1–500 characters after sanitization. Unknown fields are rejected. Sanitization normalizes Unicode (NFKC), strips control characters and collapses whitespace. Invalid input returns `422`.

## Logs

Each model run logs its start and its result with latency and token usage:

```
INFO app.agent: model run started model=qwen3:1.7b question_chars=26
INFO app.agent: model run finished latency_ms=6784 in_scope=True requests=1 input_tokens=279 output_tokens=156
```

## Changing the knowledge base

Edit `KNOWLEDGE` in `app/agent.py`. To change the refusal text, edit `REFUSAL`.
