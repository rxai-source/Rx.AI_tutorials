import 'package:flutter_riverpod/flutter_riverpod.dart';

class ChatMessage {
  final String sender; // 'user' or 'agent'
  final String text;

  ChatMessage({required this.sender, required this.text});
}

class ChatNotifier extends Notifier<List<ChatMessage>> {
  @override
  List<ChatMessage> build() {
    return [
      ChatMessage(sender: 'agent', text: 'Welcome to the Rx.AI Boardroom. How can I help you today?'),
    ];
  }

  void sendMessage(String text) {
    // Add user message
    state = [...state, ChatMessage(sender: 'user', text: text)];
    
    // Simulate agent response after 1 second
    Future.delayed(const Duration(seconds: 1), () {
      state = [...state, ChatMessage(sender: 'agent', text: 'Simulated response to: "$text"\n\nI am processing this request based on the current boardroom stage.')];
    });
  }
}

final chatProvider = NotifierProvider<ChatNotifier, List<ChatMessage>>(ChatNotifier.new);
