import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({super.key});

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: AppColors.bgSurface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.horizontal(right: Radius.circular(16)),
      ),
      child: SafeArea(
        child: Column(
          children: [
            const SizedBox(height: 24),
            // Brand Header
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Row(
                children: [
                  Container(
                    width: 36,
                    height: 36,
                    decoration: BoxDecoration(
                      gradient: const LinearGradient(
                        colors: [AppColors.primary, AppColors.secondary],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(10),
                      boxShadow: [
                        BoxShadow(
                          color: AppColors.primary.withOpacity(0.4),
                          blurRadius: 15,
                          offset: const Offset(0, 4),
                        )
                      ],
                      border: Border.all(color: Colors.white.withOpacity(0.2)),
                    ),
                    child: const Icon(Icons.hub_outlined, color: Colors.white, size: 20),
                  ),
                  const SizedBox(width: 12),
                  Text(
                    "Rx.AI Boardroom",
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.w700,
                        ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),
            
            // Session Details
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    "SESSION DETAILS",
                    style: Theme.of(context).textTheme.labelSmall?.copyWith(
                          fontSize: 10,
                          letterSpacing: 1.5,
                        ),
                  ),
                  const SizedBox(height: 12),
                  Container(
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: AppColors.bgCard,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: AppColors.borderColor),
                    ),
                    child: Column(
                      children: [
                        _buildMetaRow(context, "ID", "S-9021"),
                        const SizedBox(height: 8),
                        _buildMetaRow(context, "Topic", "Agentic UI"),
                        const SizedBox(height: 8),
                        _buildMetaRow(context, "Status", "Active"),
                      ],
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 32),

            // Active Roster
            Expanded(
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      "ACTIVE ROSTER",
                      style: Theme.of(context).textTheme.labelSmall?.copyWith(
                            fontSize: 10,
                            letterSpacing: 1.5,
                          ),
                    ),
                    const SizedBox(height: 12),
                    _buildAgentItem(context, "D", "Director", "Managing", const Color(0xFF818CF8), true),
                    const SizedBox(height: 8),
                    _buildAgentItem(context, "T", "Tech SME", "Thinking...", const Color(0xFF34D399), false),
                    const SizedBox(height: 8),
                    _buildAgentItem(context, "W", "Writer", "Idle", const Color(0xFFC084FC), false),
                    const SizedBox(height: 8),
                    _buildAgentItem(context, "C", "Critic", "Idle", const Color(0xFFFBBF24), false),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetaRow(BuildContext context, String label, String value) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          label,
          style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 12),
        ),
        Text(
          value,
          style: Theme.of(context).textTheme.bodyMedium?.mono.copyWith(fontSize: 12),
        ),
      ],
    );
  }

  Widget _buildAgentItem(BuildContext context, String avatar, String name, String status, Color roleColor, bool isActive) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.02),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: AppColors.borderColor),
      ),
      child: Row(
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: Colors.white.withOpacity(0.1),
            ),
            alignment: Alignment.center,
            child: Text(
              avatar,
              style: Theme.of(context).textTheme.labelLarge?.copyWith(fontSize: 12),
            ),
          ),
          const SizedBox(width: 10),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  name,
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontSize: 13, fontWeight: FontWeight.w500),
                ),
                Text(
                  status,
                  style: Theme.of(context).textTheme.bodySmall?.copyWith(fontSize: 10, color: roleColor),
                ),
              ],
            ),
          ),
          Container(
            width: 8,
            height: 8,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              color: isActive ? AppColors.success : AppColors.warning,
              boxShadow: [
                BoxShadow(
                  color: (isActive ? AppColors.success : AppColors.warning).withOpacity(0.5),
                  blurRadius: 8,
                )
              ],
            ),
          )
        ],
      ),
    );
  }
}
