# Rx.AI Boardroom: Formal API & WebSocket Contract

This document outlines the JSON schemas required to drive the Flutter UI seamlessly. The backend must emit these models over the WebSocket connection.

## 1. Outbound (Client to Server)

### 1.1 Send User Message
Sent when the user types a message into the `ChatInputWidget`.
```json
{
  "action": "send_message",
  "payload": {
    "text": "Make the mystery about a robotic dog."
  }
}
```

### 1.2 Tool Interaction / Critic Feedback
Sent when the user interacts with a UI widget (e.g., Critic Comment Cards).
```json
{
  "action": "accept_critique",
  "payload": {
    "comment_id": "c-123",
    "resolution": "accept"
  }
}
```

---

## 2. Inbound (Server to Client)

The Flutter `BoardroomEvent` model expects the following structure:
```json
{
  "type": "<event_type>",
  "payload": { ... }
}
```

### 2.1 Agent Response (`type: "agent_response"`)
Pushed when an agent completes a turn.
```json
{
  "type": "agent_response",
  "payload": {
    "sender": "director",
    "text": "I have initialized the Writer and Tech SME to process your request.",
    "is_clarification": false
  }
}
```

### 2.2 Layout / Stage Update (`type: "stage_update"`)
Pushed by the Orchestrator to dynamically alter the UI layout.
```json
{
  "type": "stage_update",
  "payload": {
    "stage": 3,
    "layout": "split_screen_prototype",
    "prototype_data": {
      "title": "Case of the Confused Canine",
      "concepts": ["training_data", "patterns"],
      "setting": "London Toy Emporium, Victorian",
      "characters": ["Sherlock Holmes", "Dr. Watson", "Barnaby (Robot Dog)"],
      "puzzle_beats": [
        "1. Barnaby welcomes the burglar...",
        "2. Holmes checks photo databases..."
      ]
    }
  }
}
```

### 2.3 Streaming Tokens (`type: "token"`)
Pushed rapidly while the Writer (or other agent) is drafting text. Handled by the `StreamingCanvas`.
```json
{
  "type": "token",
  "payload": {
    "agent": "writer",
    "content": "Once "
  }
}
```
