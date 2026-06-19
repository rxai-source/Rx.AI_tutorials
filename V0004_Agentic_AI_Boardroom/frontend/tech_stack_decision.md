# Tech Stack Finalization: Flutter Mobile Application

Following a review of the mobile application requirements and your personal preference, we have finalized the frontend tech stack for the AI Boardroom mobile application.

---

## 📱 Core Tech Stack

| Layer | Technology Choice | Rationale |
| :--- | :--- | :--- |
| **Framework** | **Flutter (Dart)** | Native compilation for iOS and Android, high performance with Impeller rendering engine, and pixel-perfect UI customizability to support custom layouts (`chat_only`, `split_screen_prototype`, `scriptwriting_canvas`). |
| **State Management** | **Flutter Riverpod** | Provides compile-time safety, excellent testability, and decouples the business logic from the UI lifecycle. Ideal for handling real-time WebSocket state streams. |
| **Networking (HTTP & WS)**| **Dio** + **web_socket_channel** | `Dio` offers advanced capabilities like interceptors, global configuration, and request cancellation. `web_socket_channel` provides robust stream wrappers for backend WebSocket connections. |
| **JSON Serialization** | **Freezed** + **Json Serializable** | Type-safe code generation for complex union types (like matching incoming WebSocket event models `status`, `agent_message`, `result`, and `error`). |
| **Local Cache/Storage** | **Isar Database** or **Hive** | Ultra-fast local key-value store to cache user sessions, API tokens, and offline message history. |
| **Theming** | **FlexColorScheme** | Easily implement premium, modern color palettes (sleek dark modes, deep space grays, high contrast accents) that conform to Material 3 guidelines. |

---

## 📂 Proposed Flutter Directory Structure

To keep components clean and modular, we will structure the Flutter application under `/frontend/boardroom_flutter` as follows:

```text
lib/
├── core/
│   ├── theme/          # App theme, custom gradients, glassmorphism card decorations
│   ├── network/        # Dio client, WebSocket service handlers
│   └── constants/      # App config constants, routes
├── features/
│   ├── auth/           # Login screen, token store, and auth controller
│   ├── boardroom/
│   │   ├── domain/     # Models: BoardroomMessage, WriterRoomResponse, WSMessage
│   │   ├── data/       # Api client, Websocket stream provider
│   │   ├── presentation/
│   │   │   ├── controllers/ # BoardroomStateNotifier (Zustand equivalent)
│   │   │   ├── screens/     # BoardroomDashboardScreen (dynamic layout selector)
│   │   │   └── widgets/     # Specialized Widgets:
│   │   │                    #  - ChatWidget
│   │   │                    #  - ClarificationPromptWidget
│   │   │                    #  - StoryPrototypeViewer
│   │   │                    #  - StreamingDraftCanvas
│   │   │                    #  - CriticSidebar
│   │   │                    #  - StageProgressBar
```

---

## 🔄 Stateful Layout Architecture

In Flutter, the app layout will dynamically swap components based on the active stage. The state controller will expose the current `LayoutFrame` enum value:

```dart
enum LayoutFrame {
  chatOnly,
  splitScreenPrototype,
  scriptwritingCanvas,
}
```

The UI dashboard will listen to changes in `LayoutFrame` and transition using animated switchers (`AnimatedSwitcher`) to provide smooth visual morphing between screens:

- **`LayoutFrame.chatOnly`**: Displays standard Chat/Clarification interface.
- **`LayoutFrame.splitScreenPrototype`**: Uses a `Row` layout with adjustable flex for `ChatWidget` and `StoryPrototypeViewer`.
- **`LayoutFrame.scriptwritingCanvas`**: Replaces the dashboard with a full-screen `StreamingDraftCanvas` scrollable sheet, paired with a drawer-based or split-screen `CriticSidebar`.
