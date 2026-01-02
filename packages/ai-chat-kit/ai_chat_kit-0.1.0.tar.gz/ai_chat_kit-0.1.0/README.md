## ai-chat-kit

A minimal, production-lean AI Chat SDK/library built for:
- A **framework-agnostic TypeScript core**
- **Token streaming** compatible with **Server-Sent Events (SSE)**
- Adapters for **FastAPI** (backend) and **React** (frontend)
- Clean extension points (providers, memory) without coupling core to UI/HTTP

### Architecture

- **`core/`**
  - `ChatEngine`: orchestrates provider calls, streaming, and optional memory persistence
  - `Provider`: provider interface (`generate()` + `stream()` async generator)
  - `types`: strongly typed message/request/stream event types
  - `EventBus`: small typed event emitter for observability hooks

- **`providers/`**
  - `mockProvider`: deterministic mock provider that streams token-ish chunks

- **`memory/`**
  - `inMemory`: minimal memory store keyed by `userId`

- **`adapters/`**
  - `fastapi`: SSE endpoint `POST /chat/stream`
  - `react`: `useAIChat` hook consuming SSE via `fetch` + `ReadableStream`

- **`ui/`**
  - `ChatWindow`: minimal React component using `useAIChat`

### Streaming Protocol (SSE)

The FastAPI adapter emits SSE events:
- `event: token` with JSON `{"type":"token","token":"..."}` repeated per token
- `event: done` with JSON `{"type":"done","message":{"role":"assistant","content":"..."}, ...}`
- `event: error` with JSON `{"type":"error","error":{"message":"..."}}`

The React hook parses SSE frames delimited by blank lines (`\n\n`).

### Run the FastAPI backend

Install the Python package (local editable install):

```bash
python -m pip install -e ai-chat-kit
```

Create a small `server.py` (in your own backend project) and pass keys explicitly:

```py
from ai_chat_kit.adapters.fastapi.main import create_app

app = create_app(
  # Provide whichever providers you want to enable:
  gemini_api_key="YOUR_GEMINI_API_KEY",
  # openai_api_key="YOUR_OPENAI_API_KEY",
  # anthropic_api_key="YOUR_ANTHROPIC_API_KEY",
)
```

Start the server:

```bash
python -m uvicorn server:app --reload --port 8000
```

#### Real models (OpenAI / Anthropic / Gemini)

The FastAPI adapter will attempt a real streaming call based on `params.model`.

API keys are **not** loaded from `.env` / `.env.local`. Pass them to `create_app(...)` or set process env vars yourself.

#### Persist chat history with SQLite (FastAPI adapter)

By default the FastAPI adapter will persist chat history in a local SQLite DB file.
You can control the DB path with:

```bash
export AI_CHAT_KIT_SQLITE_PATH="/path/to/chat_history.sqlite3"
```

Test streaming:

```bash
curl -N -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -d '{"userId":"u1","messages":[{"role":"user","content":"Hello streaming"}]}'
```

### Use the React adapter

Example usage with the included UI component:

```tsx
import React from "react";
import { ChatWindow } from "./ai-chat-kit/ui/ChatWindow";

export default function App() {
  return <ChatWindow userId="u1" endpoint="http://localhost:8000/chat/stream" />;
}
```

### Core usage (TypeScript)

Using the core engine directly (no HTTP, no UI):

```ts
import { ChatEngine } from "./ai-chat-kit/core/ChatEngine";
import { MockProvider } from "./ai-chat-kit/providers/mockProvider";
import { InMemoryChatMemory } from "./ai-chat-kit/memory/inMemory";

const engine = new ChatEngine(new MockProvider(), { memory: new InMemoryChatMemory() });

const res = await engine.generate({
  userId: "u1",
  messages: [{ role: "user", content: "Hello" }],
});

console.log(res.message.content);

for await (const ev of engine.stream({ userId: "u1", messages: [{ role: "user", content: "Stream this" }] })) {
  if (ev.type === "token") process.stdout.write(ev.token);
  if (ev.type === "done") process.stdout.write("\n");
}
```

### Extension points (not implemented)

- **Providers**: implement `AIProvider` to connect OpenAI/Anthropic/local models, add retries, rate limits, tracing.
- **Memory**: replace in-memory with Redis/Postgres, add TTL, per-conversation IDs, metadata.
- **RAG**: augment `messages` with retrieved context before calling the provider.
- **Agents / tool calling**: expand stream events to include structured tool-call/request/response events.
- **Observability**: subscribe to `EventBus` for tokens/done/error; forward to logs/metrics/traces.
- **Langfuse / tracing**: wrap provider calls and emit spans without changing the core public API.

### Notes

- This repo intentionally stays minimal: no external AI SDK dependency, no WebSockets, no UI styling dependency.
- The FastAPI adapter is a reference implementation of the **wire protocol** (SSE events) consumed by the React hook.

