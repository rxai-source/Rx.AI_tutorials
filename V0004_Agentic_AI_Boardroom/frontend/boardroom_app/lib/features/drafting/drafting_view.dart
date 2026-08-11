import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import '../../core/theme/app_theme.dart';

class DraftingView extends HookConsumerWidget {
  const DraftingView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return DefaultTabController(
      length: 2,
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          children: [
            Container(
              decoration: BoxDecoration(
                color: AppColors.bgCard.withOpacity(0.5),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: AppColors.borderColor),
              ),
              padding: const EdgeInsets.all(4),
              child: TabBar(
                indicator: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppColors.primary, AppColors.secondary],
                  ),
                  borderRadius: BorderRadius.circular(6),
                ),
                indicatorSize: TabBarIndicatorSize.tab,
                labelColor: Colors.white,
                unselectedLabelColor: AppColors.textMuted,
                labelStyle: Theme.of(context).textTheme.titleSmall?.copyWith(fontSize: 13),
                dividerColor: Colors.transparent,
                tabs: const [
                  Tab(text: "Draft Canvas"),
                  Tab(text: "Critic Reviews"),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: TabBarView(
                children: [
                  _buildDraftCanvas(context),
                  _buildCriticReviews(context),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildDraftCanvas(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0D0F17),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      padding: const EdgeInsets.all(16),
      child: SingleChildScrollView(
        child: RichText(
          text: TextSpan(
            style: Theme.of(context).textTheme.bodyMedium?.copyWith(
              color: const Color(0xFFE5E7EB),
              height: 1.6,
              fontSize: 14,
            ),
            children: const [
              TextSpan(text: "The Agentic Orchestration framework begins by initializing the communication buses. "),
              TextSpan(text: "Each agent subscribes to the relevant event topics to ensure real-time synchronization. "),
              TextSpan(text: "This enables the system to maintain a coherent state across distributed nodes.\n\n"),
              TextSpan(text: "As the technical boundaries are set, the creative components dynamically adapt to fit within the constraints... "),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCriticReviews(BuildContext context) {
    return Container(
      decoration: AppTheme.glassDecorationLg,
      padding: const EdgeInsets.all(12),
      child: ListView(
        children: [
          _buildCriticCard(context, "Tone is too dry. Need more engaging metaphors in the second paragraph."),
          const SizedBox(height: 10),
          _buildCriticCard(context, "The explanation of event topics is slightly ambiguous. Provide a brief example."),
        ],
      ),
    );
  }

  Widget _buildCriticCard(BuildContext context, String content) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.bgCard,
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.rate_review_outlined, color: AppColors.warning, size: 14),
              const SizedBox(width: 6),
              Text(
                "CRITIC FEEDBACK",
                style: Theme.of(context).textTheme.labelSmall?.copyWith(
                  color: AppColors.warning,
                  fontSize: 10,
                  letterSpacing: 0.5,
                  fontWeight: FontWeight.w700,
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            content,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              fontSize: 13,
              color: AppColors.textMain,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              _buildActionButton(context, "Accept", AppColors.success),
              const SizedBox(width: 8),
              _buildActionButton(context, "Discuss", AppColors.primary),
              const SizedBox(width: 8),
              _buildActionButton(context, "Reject", AppColors.error),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildActionButton(BuildContext context, String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Text(
        label,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
          color: color,
          fontSize: 11,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
