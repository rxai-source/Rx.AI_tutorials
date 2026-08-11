import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

enum SenderRole { user, director, sme, writer, critic }

class ChatBubble extends StatelessWidget {
  final String text;
  final String time;
  final SenderRole role;

  const ChatBubble({
    super.key,
    required this.text,
    required this.time,
    this.role = SenderRole.user,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = role == SenderRole.user;
    
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        constraints: BoxConstraints(
          maxWidth: MediaQuery.of(context).size.width * 0.85,
        ),
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: isUser ? null : AppColors.bgCard,
          gradient: isUser
              ? const LinearGradient(
                  colors: [AppColors.primary, Color(0xFF4F46E5)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                )
              : null,
          border: isUser ? null : Border.all(color: AppColors.borderColor),
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 4),
            bottomRight: Radius.circular(isUser ? 4 : 16),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Text(
                  _getRoleName(role),
                  style: Theme.of(context).textTheme.labelSmall?.copyWith(
                        color: _getRoleColor(role),
                        fontWeight: FontWeight.w600,
                        letterSpacing: 0.5,
                      ),
                ),
                if (role == SenderRole.director) ...[
                  const SizedBox(width: 4),
                  const Text(
                    '(Clarification)',
                    style: TextStyle(
                      fontSize: 10,
                      color: AppColors.warning,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ]
              ],
            ),
            const SizedBox(height: 2),
            Text(
              text,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    fontSize: 13,
                    height: 1.4,
                    color: isUser ? Colors.white : AppColors.textMain,
                  ),
            ),
            const SizedBox(height: 4),
            Align(
              alignment: Alignment.centerRight,
              child: Text(
                time,
                style: Theme.of(context).textTheme.bodySmall?.copyWith(
                      fontSize: 10,
                      color: isUser ? Colors.white54 : AppColors.textDark,
                    ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  String _getRoleName(SenderRole role) {
    switch (role) {
      case SenderRole.user:
        return 'USER';
      case SenderRole.director:
        return 'DIRECTOR';
      case SenderRole.sme:
        return 'TECH SME';
      case SenderRole.writer:
        return 'WRITER';
      case SenderRole.critic:
        return 'CRITIC';
    }
  }

  Color _getRoleColor(SenderRole role) {
    switch (role) {
      case SenderRole.user:
        return Colors.white;
      case SenderRole.director:
        return const Color(0xFF818CF8); // Lighter Indigo
      case SenderRole.sme:
        return const Color(0xFF34D399); // Lighter Emerald
      case SenderRole.writer:
        return const Color(0xFFC084FC); // Lighter Purple
      case SenderRole.critic:
        return const Color(0xFFFBBF24); // Lighter Amber
    }
  }
}
