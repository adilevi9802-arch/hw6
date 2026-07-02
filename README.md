# HW6 — KB + Local Tool Server + Web UI Function

**Dataset:** Netflix Shows (Kaggle) · **Live API:** RapidAPI "Streaming Availability" · **Web UI:** Open WebUI

The assignment has three parts: (1) a Knowledge Base built inside Open WebUI from
a Kaggle CSV, (2) a local Python server that calls an external API for "live"
questions the static CSV can't answer, and (3) an Open WebUI tool that calls that
server so the assistant can mix KB answers with live lookups.

## Project structure

```
oz-hw5/
├── services/
│   └── tools_server/            # Local Python microservice (part 2)
│       ├── app/
│       │   ├── __init__.py      # create_app() application factory
│       │   ├── config.py        # env-driven config (plain dict)
│       │   ├── routes.py        # /health and /streaming routes
│       │   └── rapidapi_client.py  # RapidAPI calls + payload shaping
│       ├── wsgi.py              # gunicorn entrypoint (wsgi:app)
│       ├── Dockerfile
│       └── requirements.txt
├── webui_tool/
│   └── open_webui_tool.py       # Open WebUI tool definition (part 3)
├── docker-compose.yml
├── .env.example
└── README.md
```

### Design notes
- **Functional/declarative:** config is a plain dict; the app is assembled by
  `create_app()`; routes and the RapidAPI client are functions with config
  injected explicitly — no OO boilerplate.
- **Framework exception:** `open_webui_tool.py` uses a `Tools`/`Valves` class
  because Open WebUI *requires* that shape; its logic still lives in a plain
  helper function.
- **Docs:** Python uses docstrings (Google style) rather than JSDoc, which is a
  JavaScript-only standard — there is no JS in this project.
- **Right-sized architecture:** the workload is a synchronous request→response
  lookup, so it is a single service. No message broker (RabbitMQ/Redis) is
  introduced because there is no async work or inter-service messaging to justify
  one.

## 1. Knowledge Base (in Open WebUI, no code)
1. Download the Netflix Shows CSV from Kaggle.
2. Open WebUI → **Workspace → Knowledge** → create a KB (e.g. `netflix-shows`), upload the CSV.
3. Attach the KB to a model/workspace so it is used for RAG on dataset questions
   (genre, cast, release year, rating, country of a title in the CSV, etc.).

## 2. Local Python server

### Run with Docker (recommended)
```bash
cp .env.example .env          # then edit .env and set RAPIDAPI_KEY
docker compose up --build -d
```
The server listens on http://localhost:5005 (served by gunicorn).

### Run without Docker
```bash
cd services/tools_server
pip install -r requirements.txt
export RAPIDAPI_KEY=<your key>   # PowerShell: $env:RAPIDAPI_KEY="<your key>"
python wsgi.py                   # http://localhost:5005
```

### Endpoints
| Method | Path                              | Description                         |
|--------|-----------------------------------|-------------------------------------|
| GET    | `/health`                         | Liveness probe → `{"status":"ok"}`  |
| GET    | `/streaming?title=<t>&country=us` | Live streaming availability + price |

Test:
```bash
curl "http://localhost:5005/health"
curl "http://localhost:5005/streaming?title=Stranger%20Things&country=us"
```
> `/streaming` requires a RapidAPI key **subscribed** to the "Streaming
> Availability" API, otherwise RapidAPI returns `403 not subscribed`.

### Tests
```bash
cd services/tools_server
pip install -r requirements.txt
pytest
```

## 3. Web UI Function/Tool
1. Open WebUI → **Workspace → Tools → Create new tool**, paste [webui_tool/open_webui_tool.py](webui_tool/open_webui_tool.py).
2. Enable it on the model, then set the tool's **Valve** `server_url`:
   - Running the full compose stack (Open WebUI in Docker) → `http://tools_server:5005`
     (Open WebUI reaches the tool server by its compose service name).
   - Running Open WebUI outside Docker → `http://localhost:5005`.

## Result
- Questions about the CSV (e.g. "What genre is *Narcos*?") → answered from the **KB**.
- "Live" questions (e.g. "Where can I stream *Stranger Things* right now, and how much does it cost?") →
  the assistant calls `get_streaming_availability`, which hits the tools_server, which calls RapidAPI.
