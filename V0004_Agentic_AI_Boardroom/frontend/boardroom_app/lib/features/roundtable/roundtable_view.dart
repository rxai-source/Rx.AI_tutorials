import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'package:flutter_highlighter/flutter_highlighter.dart';
import 'package:flutter_highlighter/themes/a11y-dark.dart';
import '../../core/theme/app_theme.dart';

class RoundtableView extends HookConsumerWidget {
  const RoundtableView({super.key});

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
                  Tab(text: "Debate Feed"),
                  Tab(text: "Prototype"),
                ],
              ),
            ),
            const SizedBox(height: 12),
            Expanded(
              child: TabBarView(
                children: [
                  _buildDebateFeed(context),
                  _buildPrototypeViewer(context),
                ],
              ),
            )
          ],
        ),
      ),
    );
  }

  Widget _buildDebateFeed(BuildContext context) {
    return Container(
      decoration: AppTheme.glassDecorationLg,
      padding: const EdgeInsets.all(12),
      child: ListView(
        children: [
          _buildDebateCard(context, "Tech SME", "The current concept lacks clear technical boundaries. We need to define the constraints first.", const Color(0xFF34D399)),
          const SizedBox(height: 10),
          _buildDebateCard(context, "Creative Writer", "Constraints might limit the narrative flow. Let's draft a broad vision before narrowing it down.", const Color(0xFFC084FC)),
        ],
      ),
    );
  }

  Widget _buildDebateCard(BuildContext context, String role, String content, Color roleColor) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.02),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            role.toUpperCase(),
            style: Theme.of(context).textTheme.labelSmall?.copyWith(
              color: roleColor,
              fontSize: 10,
              letterSpacing: 0.5,
            ),
          ),
          const SizedBox(height: 6),
          Text(
            content,
            style: Theme.of(context).textTheme.bodySmall?.copyWith(
              fontSize: 13,
              color: AppColors.textMuted,
            ),
          )
        ],
      ),
    );
  }

  Widget _buildPrototypeViewer(BuildContext context) {
    const jsonPayload = '''{
  "theme": "Agentic Orchestration",
  "characters": [
    {"role": "Director", "traits": ["decisive", "analytical"]}
  ],
  "plot_points": [
    "Identify constraints",
    "Brainstorming loop",
    "Final synthesis"
  ]
}''';

    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0F121D),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderColor),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: [
              _buildConceptTag(context, "Agentic orchestration"),
              _buildConceptTag(context, "Multi-agent systems"),
            ],
          ),
          const SizedBox(height: 12),
          Expanded(
            child: Container(
              width: double.infinity,
              decoration: BoxDecoration(
                color: const Color(0xFF08090F),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: Colors.white.withOpacity(0.03)),
              ),
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(12),
                child: HighlightView(
                  jsonPayload,
                  language: 'json',
                  theme: a11yDarkTheme,
                  padding: EdgeInsets.zero,
                  textStyle: Theme.of(context).textTheme.bodySmall?.mono.copyWith(
                    fontSize: 11,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildConceptTag(BuildContext context, String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.12),
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.primary.withOpacity(0.25)),
      ),
      child: Text(
        text,
        style: Theme.of(context).textTheme.labelSmall?.copyWith(
          color: const Color(0xFFA5B4FC),
          fontSize: 10,
        ),
      ),
    );
  }
}
