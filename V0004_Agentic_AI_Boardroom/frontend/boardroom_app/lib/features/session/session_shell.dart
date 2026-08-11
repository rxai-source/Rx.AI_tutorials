import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../core/theme/app_theme.dart';
import '../../core/widgets/app_drawer.dart';
import '../../core/widgets/timeline_stepper.dart';
import 'providers/session_state_provider.dart';
import '../chat/chat_layout.dart';
import '../roundtable/roundtable_layout.dart';
import '../drafting/drafting_layout.dart';

class SessionShell extends ConsumerWidget {
  const SessionShell({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentStage = ref.watch(currentStageProvider);
    final isCriticSheetVisible = ref.watch(isCriticSheetVisibleProvider);

    return Scaffold(
      drawer: const AppDrawer(),
      body: Stack(
        children: [
          // Background Gradient
          Container(
            decoration: const BoxDecoration(
              gradient: RadialGradient(
                center: Alignment(0, -0.8),
                radius: 1.5,
                colors: [
                  Color(0x1F6366F1), // rgba(99, 102, 241, 0.12)
                  AppColors.bgBase,
                ],
              ),
            ),
          ),
          
          SafeArea(
            child: Column(
              children: [
                // Custom App Bar
                _buildAppBar(context, currentStage),
                
                // Timeline Stepper
                TimelineStepper(
                  currentStage: currentStage,
                  onStepTapped: (step) {
                    ref.read(currentStageProvider.notifier).setStage(step);
                    ref.read(isCriticSheetVisibleProvider.notifier).setVisible(false);
                  },
                ),

                // Workspace Layout Frames
                Expanded(
                  child: Padding(
                    padding: const EdgeInsets.all(12.0),
                    child: AnimatedSwitcher(
                      duration: const Duration(milliseconds: 300),
                      transitionBuilder: (child, animation) {
                        return FadeTransition(opacity: animation, child: child);
                      },
                      child: _buildWorkspace(currentStage),
                    ),
                  ),
                ),
              ],
            ),
          ),

          // Critic Bottom Sheet Overlay
          if (isCriticSheetVisible)
            GestureDetector(
              onTap: () => ref.read(isCriticSheetVisibleProvider.notifier).setVisible(false),
              child: Container(
                color: Colors.black54,
              ),
            ),
            
          if (isCriticSheetVisible)
            Align(
              alignment: Alignment.bottomCenter,
              child: _buildCriticBottomSheet(ref),
            ),
        ],
      ),
    );
  }

  Widget _buildAppBar(BuildContext context, int stage) {
    String tagText;
    switch (stage) {
      case 1:
      case 2:
        tagText = 'chat_only';
        break;
      case 3:
        tagText = 'split_screen';
        break;
      case 4:
        tagText = 'canvas';
        break;
      default:
        tagText = 'unknown';
    }

    return Container(
      height: 56,
      decoration: const BoxDecoration(
        color: Color(0xE6111622), // rgba(17, 22, 34, 0.9)
        border: Border(bottom: BorderSide(color: AppColors.borderColor)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Row(
            children: [
              Builder(
                builder: (context) => IconButton(
                  icon: const Icon(Icons.menu, color: AppColors.textMain),
                  onPressed: () => Scaffold.of(context).openDrawer(),
                ),
              ),
              const SizedBox(width: 8),
              Container(
                width: 26,
                height: 26,
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppColors.primary, AppColors.secondary],
                  ),
                  borderRadius: BorderRadius.circular(6),
                  boxShadow: const [
                    BoxShadow(
                      color: Color(0x666366F1),
                      blurRadius: 8,
                      offset: Offset(0, 2),
                    )
                  ],
                ),
                alignment: Alignment.center,
                child: const Icon(Icons.dashboard_customize, size: 14, color: Colors.white),
              ),
              const SizedBox(width: 8),
              const Text(
                'Rx.AI Boardroom',
                style: TextStyle(
                  fontFamily: 'Outfit',
                  fontWeight: FontWeight.w700,
                  fontSize: 16,
                  color: Colors.white,
                ),
              ),
            ],
          ),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
            decoration: BoxDecoration(
              color: const Color(0x0DFFFFFF),
              border: Border.all(color: AppColors.primary),
              borderRadius: BorderRadius.circular(6),
            ),
            child: Text(
              tagText,
              style: const TextStyle(
                fontFamily: 'Fira Code',
                fontSize: 10,
                color: AppColors.primary,
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildWorkspace(int stage) {
    switch (stage) {
      case 1:
        return const ChatLayout(key: ValueKey('chat_1'), stage: 1);
      case 2:
        return const ChatLayout(key: ValueKey('chat_2'), stage: 2);
      case 3:
        return const RoundtableLayout(key: ValueKey('roundtable'));
      case 4:
        return const DraftingLayout(key: ValueKey('drafting'));
      default:
        return const SizedBox.shrink(key: ValueKey('empty'));
    }
  }

  Widget _buildCriticBottomSheet(WidgetRef ref) {
    return Container(
      height: 350,
      decoration: const BoxDecoration(
        color: AppColors.bgSurface,
        border: Border(top: BorderSide(color: AppColors.borderColor)),
        borderRadius: BorderRadius.only(
          topLeft: Radius.circular(16),
          topRight: Radius.circular(16),
        ),
        boxShadow: [
          BoxShadow(color: Colors.black54, blurRadius: 24, offset: Offset(0, -8)),
        ],
      ),
      child: Column(
        children: [
          const SizedBox(height: 12),
          Container(
            width: 36,
            height: 4,
            decoration: BoxDecoration(
              color: const Color(0x33FFFFFF),
              borderRadius: BorderRadius.circular(2),
            ),
          ),
          const SizedBox(height: 12),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Row(
                  children: [
                    Icon(Icons.rate_review, size: 14, color: AppColors.warning),
                    SizedBox(width: 6),
                    Text(
                      'Critic Feedback Review',
                      style: TextStyle(
                        fontFamily: 'Outfit',
                        fontWeight: FontWeight.w600,
                        fontSize: 13,
                        color: AppColors.textMain,
                      ),
                    ),
                  ],
                ),
                IconButton(
                  icon: const Icon(Icons.close, size: 18),
                  onPressed: () => ref.read(isCriticSheetVisibleProvider.notifier).setVisible(false),
                  constraints: const BoxConstraints(),
                  padding: EdgeInsets.zero,
                ),
              ],
            ),
          ),
          const Divider(color: AppColors.borderColor, height: 1),
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                _buildCriticComment(
                  'The description of the robot dog is great, but we should make sure kids know it\'s a robotic toy and not a real dog so they don\'t get confused.',
                ),
                const SizedBox(height: 12),
                _buildCriticComment(
                  'Make sure Watson\'s reaction is clear. It highlights the mystery\'s stakes. Let\'s make him sound more surprised.',
                ),
                const SizedBox(height: 12),
                _buildCriticComment(
                  'The concept of \'Training Data\' is introduced well, but we should explicitly emphasize that if the training data is bad, the AI will make bad decisions (Garbage In, Garbage Out).',
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCriticComment(String text) {
    return Container(
      padding: const EdgeInsets.all(10),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        border: Border.all(color: AppColors.borderColor),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Row(
            children: [
              Text(
                'CRITIC',
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w700,
                  color: AppColors.warning,
                  letterSpacing: 0.5,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            text,
            style: const TextStyle(
              fontSize: 12,
              color: AppColors.textMuted,
              height: 1.4,
            ),
          ),
          const SizedBox(height: 6),
          Row(
            children: [
              _buildActionBtn('Accept', const Color(0xFF10B981)),
              const SizedBox(width: 6),
              _buildActionBtn('Reject', const Color(0xFFEF4444)),
              const SizedBox(width: 6),
              _buildActionBtn('Discuss', AppColors.textMain),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildActionBtn(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        border: Border.all(color: color.withOpacity(0.3)),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        label,
        style: TextStyle(
          fontSize: 10,
          fontWeight: FontWeight.w600,
          color: color,
        ),
      ),
    );
  }
}
