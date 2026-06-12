// frontend/src/api/boardroom.ts
/**
 * AI Boardroom API client.
 * Handles REST calls and the authenticated WebSocket connection.
 */

const BASE_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";
const WS_BASE = BASE_URL.replace(/^http/, "ws");

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  const res = await fetch(`${BASE_URL}/auth/token`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password }),
  });
  if (!res.ok) throw new Error("Login failed");
  return res.json();
}

// ---------------------------------------------------------------------------
// AI Writer Room — REST
// ---------------------------------------------------------------------------

export interface WriterRoomRequest {
  user_request: string;
  llm_provider?: "gemini" | "openrouter";
  run_full_pipeline?: boolean;
}

export interface WriterRoomResponse {
  session_id: string;
  status: string;
  writing_plan?: Record<string, unknown>;
  sme_report?: Record<string, unknown>;
  writer_draft?: Record<string, unknown>;
  critic_report?: Record<string, unknown>;
  final_output?: string;
  messages: Array<{ agent: string; content: string }>;
  error?: string;
}

export async function submitWritingRequest(
  token: string,
  payload: WriterRoomRequest
): Promise<WriterRoomResponse> {
  const res = await fetch(`${BASE_URL}/ai_writer_room`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail ?? "Request failed");
  }
  return res.json();
}

// ---------------------------------------------------------------------------
// AI Writer Room — WebSocket (JWT via Sec-WebSocket-Protocol)
// ---------------------------------------------------------------------------

export type WSMessageType = "status" | "agent_message" | "result" | "error";

export interface WSMessage {
  type: WSMessageType;
  agent?: string;
  content: unknown;
}

export type WSMessageHandler = (message: WSMessage) => void;

/**
 * Open an authenticated WebSocket connection to the boardroom.
 *
 * The JWT is passed via the Sec-WebSocket-Protocol header:
 *   Sec-WebSocket-Protocol: bearer, <jwt_token>
 *
 * After the connection opens, send the writing request and listen for updates.
 */
export function openBoardroomSocket(
  token: string,
  sessionId: string,
  onMessage: WSMessageHandler,
  onClose?: () => void
): WebSocket {
  // Pass JWT via subprotocol — browser WebSocket API supports this
  const ws = new WebSocket(
    `${WS_BASE}/ws/boardroom/${sessionId}`,
    ["bearer", token]   // Sec-WebSocket-Protocol: bearer, <token>
  );

  ws.onmessage = (event) => {
    try {
      const msg: WSMessage = JSON.parse(event.data);
      onMessage(msg);
    } catch {
      console.error("Invalid WS message:", event.data);
    }
  };

  ws.onclose = () => onClose?.();

  ws.onerror = (e) => {
    console.error("WebSocket error:", e);
  };

  return ws;
}
