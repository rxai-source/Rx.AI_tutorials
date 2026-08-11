import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_theme.dart';
import '../../core/widgets/glass_panel.dart';
import '../../core/widgets/chat_bubble.dart';
import '../session/providers/session_state_provider.dart';
import 'widgets/story_prototype_viewer.dart';

class RoundtableLayout extends ConsumerWidget {
  const RoundtableLayout({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final activeTab = ref.watch(activeTabProvider);

    return Column(
      children: [
        // Tab Bar
        Container(
          margin: const EdgeInsets.only(bottom: 8),
          padding: const EdgeInsets.all(4),
          decoration: BoxDecoration(
            color: const Color(0x801A2030), // rgba(26, 32, 48, 0.5)
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: AppColors.borderColor),
          ),
          child: Row(
            children: [
              _TabButton(
                title: 'Roundtable Debate',
                isActive: activeTab == 0,
                onTap: () => ref.read(activeTabProvider.notifier).setTab(0),
              ),
              _TabButton(
                title: 'Story Outline',
                isActive: activeTab == 1,
                onTap: () => ref.read(activeTabProvider.notifier).setTab(1),
              ),
            ],
          ),
        ),
        // Tab Content
        Expanded(
          child: activeTab == 0 ? const _DebatePanel() : const StoryPrototypeViewer(
            jsonString: '''{
  "title": "Sherlock Holmes and the Case of the Confused Canine",
  "concepts": ["Training Data", "Pattern Recognition"],
  "setting": "London Toy Emporium, Victorian",
  "characters": [
    "Sherlock Holmes",
    "Dr. Watson",
    "Barnaby (Robot Dog)"
  ],
  "puzzle_beats": [
    "1. Barnaby welcomes the burglar...",
    "2. Holmes checks photo databases...",
    "3. Retrained models solve crime."
  ]
}'''
          ),
        ),
      ],
    );
  }
}

class _TabButton extends StatelessWidget {
  final String title;
  final bool isActive;
  final VoidCallback onTap;

  const _TabButton({
    required this.title,
    required this.isActive,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 8),
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(6),
            gradient: isActive
                ? const LinearGradient(
                    colors: [AppColors.primary, AppColors.secondary],
                  )
                : null,
            color: isActive ? null : Colors.transparent,
          ),
          alignment: Alignment.center,
          child: Text(
            title,
            style: TextStyle(
              color: isActive ? Colors.white : AppColors.textMuted,
              fontWeight: FontWeight.w600,
              fontSize: 12,
              fontFamily: 'Outfit',
            ),
          ),
        ),
      ),
    );
  }
}

class _DebatePanel extends StatelessWidget {
  const _DebatePanel();

  @override
  Widget build(BuildContext context) {
    return GlassPanel(
      child: ListView(
        children: const [
          ChatBubble(
            role: SenderRole.sme,
            text: 'I suggest focusing on the concept of "Training Data". It is fundamental to how AI recognizes patterns.',
            time: '14:03',
          ),
          ChatBubble(
            role: SenderRole.writer,
            text: 'Great idea! What if the mystery revolves around corrupted training data? Like a robotic guard dog that fails to recognize a thief because its training images were swapped.',
            time: '14:04',
          ),
          ChatBubble(
            role: SenderRole.critic,
            text: 'I like it. But ensure the language remains simple for 8-10 year olds. Avoid technical jargon without analogies.',
            time: '14:05',
          ),
        ],
      ),
    );
  }
}
