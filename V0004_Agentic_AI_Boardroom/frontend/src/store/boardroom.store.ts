// frontend/src/store/boardroom.store.ts
/**
 * Zustand store — global state for the AI Boardroom frontend.
 */

import { create } from "zustand";
import type { WSMessage, WriterRoomResponse } from "../api/boardroom";

export interface BoardroomMessage {
  agent: string;
  content: string;
  timestamp: Date;
}

interface BoardroomStore {
  // Auth
  token: string | null;
  setToken: (token: string | null) => void;

  // Session
  sessionId: string | null;
  setSessionId: (id: string | null) => void;

  // Group chat messages (PUBLIC — scratchpads are NEVER here)
  messages: BoardroomMessage[];
  addMessage: (msg: BoardroomMessage) => void;
  clearMessages: () => void;

  // Workflow state
  status: string;
  setStatus: (status: string) => void;

  // Structured outputs
  writingPlan: Record<string, unknown> | null;
  smeReport: Record<string, unknown> | null;
  writerDraft: Record<string, unknown> | null;
  criticReport: Record<string, unknown> | null;
  finalOutput: string | null;
  setResponse: (response: WriterRoomResponse) => void;

  // WebSocket
  ws: WebSocket | null;
  setWs: (ws: WebSocket | null) => void;
  handleWsMessage: (msg: WSMessage) => void;
}

export const useBoardroomStore = create<BoardroomStore>((set, get) => ({
  // Auth
  token: null,
  setToken: (token) => set({ token }),

  // Session
  sessionId: null,
  setSessionId: (sessionId) => set({ sessionId }),

  // Messages
  messages: [],
  addMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),
  clearMessages: () => set({ messages: [] }),

  // Status
  status: "idle",
  setStatus: (status) => set({ status }),

  // Structured outputs
  writingPlan: null,
  smeReport: null,
  writerDraft: null,
  criticReport: null,
  finalOutput: null,
  setResponse: (response) =>
    set({
      writingPlan: response.writing_plan ?? null,
      smeReport: response.sme_report ?? null,
      writerDraft: response.writer_draft ?? null,
      criticReport: response.critic_report ?? null,
      finalOutput: response.final_output ?? null,
      status: response.status,
    }),

  // WebSocket
  ws: null,
  setWs: (ws) => set({ ws }),
  handleWsMessage: (msg: WSMessage) => {
    switch (msg.type) {
      case "status":
        set({ status: typeof msg.content === "string" ? msg.content : "updating" });
        break;
      case "agent_message": {
        const content = msg.content as Record<string, unknown>;
        // Only add PUBLIC agent messages to the group chat
        get().addMessage({
          agent: msg.agent ?? "system",
          content:
            typeof content === "string"
              ? content
              : JSON.stringify(content, null, 2),
          timestamp: new Date(),
        });
        break;
      }
      case "result":
        // Final result — update structured outputs
        if (msg.content && typeof msg.content === "object") {
          const c = msg.content as Record<string, unknown>;
          set({
            writingPlan: (c.writing_plan as Record<string, unknown>) ?? get().writingPlan,
            status: "done",
          });
        }
        break;
      case "error":
        set({ status: "error" });
        get().addMessage({
          agent: "system",
          content: `Error: ${JSON.stringify(msg.content)}`,
          timestamp: new Date(),
        });
        break;
    }
  },
}));
