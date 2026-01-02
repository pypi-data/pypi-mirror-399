# miu-studio

Web server for miu AI agent framework.

## Installation

```bash
uv add miu-studio
```

## Usage

```bash
# Run the server
miu-studio

# Or with Python module
python -m miu_studio

# Custom port
miu-studio --port 3000
```

## Features

- REST API for agent interactions
- WebSocket for real-time chat
- Session management
- Static web chat interface

## API Endpoints

- `GET /api/v1/health` - Health check
- `GET /api/v1/sessions` - List sessions
- `POST /api/v1/sessions` - Create session
- `POST /api/v1/chat/invoke` - Synchronous chat
- `POST /api/v1/chat/stream` - Streaming chat (SSE)
- `WS /api/v1/chat/ws/{session_id}` - WebSocket chat

## License

MIT
