enum LayoutFrame {
  chatOnly,
  splitScreenPrototype,
  scriptwritingCanvas,
}

enum EventType {
  token,
  stageUpdate,
  agentResponse,
}

class BoardroomEvent {
  final EventType type;
  final dynamic payload;

  BoardroomEvent({required this.type, required this.payload});

  factory BoardroomEvent.fromJson(Map<String, dynamic> json) {
    EventType type;
    switch (json['type']) {
      case 'token':
        type = EventType.token;
        break;
      case 'stage_update':
        type = EventType.stageUpdate;
        break;
      case 'agent_response':
        type = EventType.agentResponse;
        break;
      default:
        throw Exception('Unknown event type');
    }
    return BoardroomEvent(type: type, payload: json['payload']);
  }
}
