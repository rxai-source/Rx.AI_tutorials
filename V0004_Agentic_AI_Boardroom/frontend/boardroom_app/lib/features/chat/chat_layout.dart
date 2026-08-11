import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_theme.dart';
import '../../core/widgets/chat_bubble.dart';
import '../../core/widgets/glass_panel.dart';
import '../../core/widgets/chat_input_widget.dart';
import '../session/providers/chat_provider.dart';

class ChatLayout extends ConsumerWidget {
  final int stage; // 1 = Requirements, 2 = Clarification

  const ChatLayout({super.key, required this.stage});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final chatMessages = ref.watch(chatProvider);

    return GlassPanel(
      header: const Row(
        children: [
          Icon(Icons.chat_bubble_outline, size: 14, color: AppColors.primary),
          SizedBox(width: 6),
          Text(
            'Dialogue Feed',
            style: TextStyle(
              fontSize: 12,
              fontWeight: FontWeight.w600,
              color: AppColors.textMain,
            ),
          ),
        ],
      ),
      child: Column(
        children: [
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.only(bottom: 16),
              itemCount: chatMessages.length,
              itemBuilder: (context, index) {
                final msg = chatMessages[index];
                
                // Map the string sender back to SenderRole
                SenderRole role;
                switch (msg.sender) {
                  case 'user':
                    role = SenderRole.user;
                    break;
                  case 'agent':
                    role = SenderRole.director; // Assume director for now in Stage 1/2
                    break;
                  default:
                    role = SenderRole.director;
                }

                // Simple mock time
                final timeStr = "${DateTime.now().hour.toString().padLeft(2, '0')}:${DateTime.now().minute.toString().padLeft(2, '0')}";

                return ChatBubble(
                  role: role,
                  text: msg.text,
                  time: timeStr,
                );
              },
            ),
          ),
          if (stage == 2 || stage == 1) ...[ // allow input in both stages for easier testing
            ChatInputWidget(
              onSend: (text) {
                ref.read(chatProvider.notifier).sendMessage(text);
              },
            ),
          ]
        ],
      ),
    );
  }
}
