import 'package:flutter/material.dart';
import '../theme/app_theme.dart';

class TimelineStepper extends StatelessWidget {
  final int currentStage;
  final Function(int) onStepTapped;

  const TimelineStepper({
    super.key,
    required this.currentStage,
    required this.onStepTapped,
  });

  @override
  Widget build(BuildContext context) {
    const double maxSteps = 4.0;
    final double progress = ((currentStage - 1) / (maxSteps - 1)).clamp(0.0, 1.0);

    return Container(
      height: 60,
      decoration: const BoxDecoration(
        color: Color(0x800A0B0E),
        border: Border(bottom: BorderSide(color: AppColors.borderColor)),
      ),
      padding: const EdgeInsets.symmetric(horizontal: 16),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 400),
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Base line
              Positioned(
                left: 0,
                right: 0,
                child: Container(
                  height: 2,
                  color: const Color(0x0FFFFFFF), // rgba(255, 255, 255, 0.06)
                ),
              ),
              // Progress line
              Positioned(
                left: 0,
                right: 0,
                child: FractionallySizedBox(
                  alignment: Alignment.centerLeft,
                  widthFactor: progress,
                  child: Container(
                    height: 2,
                    decoration: const BoxDecoration(
                      gradient: LinearGradient(
                        colors: [AppColors.primary, AppColors.secondary],
                      ),
                    ),
                  ),
                ),
              ),
              // Steps
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  _buildStepNode(context, 1, 'Requirements'),
                  _buildStepNode(context, 2, 'Clarification'),
                  _buildStepNode(context, 3, 'Roundtable'),
                  _buildStepNode(context, 4, 'Drafting'),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildStepNode(BuildContext context, int stepNum, String label) {
    final isActive = currentStage == stepNum;
    final isCompleted = currentStage > stepNum;

    Color borderColor = const Color(0x26FFFFFF);
    Color bgColor = const Color(0xFF111827);
    Color textColor = AppColors.textMuted;
    List<BoxShadow>? shadows;

    if (isActive) {
      borderColor = AppColors.primary;
      bgColor = AppColors.primary;
      textColor = Colors.white;
      shadows = [
        const BoxShadow(
          color: Color(0x806366F1),
          blurRadius: 10,
        )
      ];
    } else if (isCompleted) {
      borderColor = AppColors.success;
      bgColor = AppColors.success;
      textColor = Colors.white;
    }

    return GestureDetector(
      onTap: () => onStepTapped(stepNum),
      child: SizedBox(
        width: 80,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Container(
              width: 24,
              height: 24,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: bgColor,
                border: Border.all(color: borderColor, width: 1.5),
                boxShadow: shadows,
              ),
              alignment: Alignment.center,
              child: Text(
                stepNum.toString(),
                style: TextStyle(
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                  color: textColor,
                ),
              ),
            ),
            if (isActive) ...[
              const SizedBox(height: 4),
              Text(
                label.toUpperCase(),
                style: const TextStyle(
                  fontSize: 9,
                  fontWeight: FontWeight.w600,
                  color: AppColors.primary,
                  letterSpacing: 0.5,
                ),
              )
            ]
          ],
        ),
      ),
    );
  }
}
