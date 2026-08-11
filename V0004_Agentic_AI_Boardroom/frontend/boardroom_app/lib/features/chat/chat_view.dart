import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../core/theme/app_theme.dart';

class ChatView extends HookConsumerWidget {
  final int stage;
  const ChatView({super.key, required this.stage});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Padding(
      padding: const EdgeInsets.all(12.0),
      child: Column(
        children: [
          Expanded(
            child: Container(
              decoration: AppTheme.glassDecorationLg,
              child: Column(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                    decoration: BoxDecoration(
                      border: Border(bottom: BorderSide(color: AppColors.borderColor)),
                      color: Colors.white.withOpacity(0.02),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text(
                          stage == 1 ? "Writers' Room Initialization" : "Director Briefing",
                          style: Theme.of(context).textTheme.titleSmall,
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                          decoration: BoxDecoration(
                            color: Colors.white.withOpacity(0.05),
                            borderRadius: BorderRadius.circular(6),
                            border: Border.all(color: AppColors.borderColor),
                          ),
                          child: Text("SYS_LOG", style: Theme.of(context).textTheme.bodySmall?.mono.copyWith(fontSize: 10)),
                        )
                      ],
                    ),
                  ),
                  Expanded(
                    child: ListView(
                      padding: const EdgeInsets.all(12),
                      children: [
                        _buildBubble(context, "Director", "Initializing session context...", isAgent: true, roleColor: const Color(0xFF818CF8)),
                        const SizedBox(height: 12),
                        if (stage == 2)
                          _buildBubble(context, "Tech SME", "Drafting technical boundaries.", isAgent: true, roleColor: const Color(0xFF34D399)),
                      ],
                    ),
                  )
                ],
              ),
            ),
          ),
          if (stage == 2)
            _buildClarificationBox(context),
        ],
      ),
    );
  }

  Widget _buildBubble(BuildContext context, String sender, String message, {required bool isAgent, required Color roleColor}) {
    return Align(
      alignment: isAgent ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.85),
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: isAgent ? AppColors.bgCard : AppColors.primary,
          border: isAgent ? Border.all(color: AppColors.borderColor) : null,
          borderRadius: BorderRadius.circular(16).copyWith(
            topLeft: isAgent ? const Radius.circular(4) : const Radius.circular(16),
            bottomRight: isAgent ? const Radius.circular(16) : const Radius.circular(4),
          ),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              sender.toUpperCase(),
              style: Theme.of(context).textTheme.labelSmall?.copyWith(
                color: isAgent ? roleColor : Colors.white70,
                fontSize: 10,
                letterSpacing: 0.5,
              ),
            ),
            const SizedBox(height: 4),
            Text(
              message,
              style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                color: isAgent ? AppColors.textMain : Colors.white,
                fontSize: 13,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildClarificationBox(BuildContext context) {
    return Container(
      margin: const EdgeInsets.only(top: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.warning.withOpacity(0.08),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.warning),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.warning_amber_rounded, color: AppColors.warning, size: 16),
              const SizedBox(width: 6),
              Text(
                "Clarification Needed",
                style: Theme.of(context).textTheme.labelLarge?.copyWith(
                  color: AppColors.warning,
                  fontSize: 12,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: Container(
                  height: 36,
                  decoration: BoxDecoration(
                    color: AppColors.bgInput,
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: AppColors.borderColor),
                  ),
                  child: TextField(
                    decoration: InputDecoration(
                      hintText: "Type your clarification...",
                      hintStyle: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 12),
                      border: InputBorder.none,
                      contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                    ),
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Container(
                width: 36,
                height: 36,
                decoration: BoxDecoration(
                  color: AppColors.primary,
                  borderRadius: BorderRadius.circular(10),
                ),
                child: const Icon(Icons.send, color: Colors.white, size: 16),
              )
            ],
          )
        ],
      ),
    );
  }
}
