## Setup environment (for development)

- using uv:

```bash
uv sync
```

- without uv:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

### ida-pro-mcp setup

```bash
uv add ida-pro-mcp
uv run ida-pro-mcp --install
```

## usage

```bash
uv run ctf-agent
```