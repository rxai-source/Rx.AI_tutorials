import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import 'agent_badge.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: const Color(0xFF111622),
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.zero,
      ),
      child: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Padding(
              padding: const EdgeInsets.all(20.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Row(
                    children: [
                      Container(
                        width: 26,
                        height: 26,
                        decoration: BoxDecoration(
                          gradient: const LinearGradient(
                            colors: [AppColors.primary, AppColors.secondary],
                          ),
                          borderRadius: BorderRadius.circular(6),
                        ),
                        alignment: Alignment.center,
                        child: const Icon(Icons.dashboard_customize, size: 14, color: Colors.white),
                      ),
                      const SizedBox(width: 8),
                      Text(
                        'Rx.AI Console',
                        style: Theme.of(context).textTheme.titleMedium?.copyWith(
                              fontWeight: FontWeight.w700,
                            ),
                      ),
                    ],
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, size: 20),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
            ),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 20.0),
              child: Text(
                'SESSION DETAILS',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textDark,
                  letterSpacing: 1.5,
                ),
              ),
            ),
            const SizedBox(height: 8),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20.0),
              child: Container(
                padding: const EdgeInsets.all(10),
                decoration: AppTheme.glassDecorationMd,
                child: const Column(
                  children: [
                    _MetaRow(label: 'Session ID', value: 'sess_4a9b'),
                    SizedBox(height: 6),
                    _MetaRow(label: 'LLM Provider', value: 'Gemini 3.5'),
                    SizedBox(height: 6),
                    _MetaRow(label: 'Active Flow', value: 'writers_room'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            const Padding(
              padding: EdgeInsets.symmetric(horizontal: 20.0),
              child: Text(
                'ACTIVE ROSTER',
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.w600,
                  color: AppColors.textDark,
                  letterSpacing: 1.5,
                ),
              ),
            ),
            const SizedBox(height: 8),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: 20.0),
                children: const [
                  _AgentListItem(
                    role: AgentRole.director,
                    name: 'Director',
                    desc: 'Orchestrator',
                    statusColor: AppColors.success,
                  ),
                  SizedBox(height: 6),
                  _AgentListItem(
                    role: AgentRole.sme,
                    name: 'Tech SME',
                    desc: 'Factual Analyst',
                    statusColor: AppColors.textDark,
                  ),
                  SizedBox(height: 6),
                  _AgentListItem(
                    role: AgentRole.writer,
                    name: 'Writer',
                    desc: 'Storyteller',
                    statusColor: AppColors.textDark,
                  ),
                  SizedBox(height: 6),
                  _AgentListItem(
                    role: AgentRole.critic,
                    name: 'Critic',
                    desc: 'Quality Assurance',
                    statusColor: AppColors.textDark,
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _MetaRow extends StatelessWidget {
  final String label;
  final String value;

  const _MetaRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: AppColors.textMuted),
        ),
        Text(
          value,
          style: const TextStyle(
            fontSize: 12,
            fontFamily: 'Fira Code',
            fontWeight: FontWeight.w500,
            color: AppColors.textMain,
          ),
        ),
      ],
    );
  }
}

class _AgentListItem extends StatelessWidget {
  final AgentRole role;
  final String name;
  final String desc;
  final Color statusColor;

  const _AgentListItem({
    required this.role,
    required this.name,
    required this.desc,
    required this.statusColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: const Color(0x05FFFFFF),
        border: Border.all(color: AppColors.borderColor),
        borderRadius: BorderRadius.circular(10),
      ),
      child: Row(
        children: [
          AgentBadge(role: role, size: 24),
          const SizedBox(width: 8),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w500),
                ),
                Text(
                  desc,
                  style: const TextStyle(fontSize: 10, color: AppColors.textDark),
                ),
              ],
            ),
          ),
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: statusColor,
              boxShadow: statusColor != AppColors.textDark
                  ? [BoxShadow(color: statusColor, blurRadius: 6)]
                  : null,
            ),
          )
        ],
      ),
    );
  }
}
