import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../core/theme/app_theme.dart';
import '../session/providers/session_state_provider.dart';
import 'providers/streaming_canvas_provider.dart';

class DraftingLayout extends ConsumerWidget {
  const DraftingLayout({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final streamAsyncValue = ref.watch(streamingCanvasProvider);

    return Stack(
      children: [
        // Main Canvas
        Container(
          decoration: AppTheme.glassDecorationLg,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: const BoxDecoration(
                  border: Border(bottom: BorderSide(color: AppColors.borderColor)),
                  color: Color(0x05FFFFFF),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    const Row(
                      children: [
                        Icon(Icons.edit_document, size: 14, color: AppColors.success),
                        SizedBox(width: 6),
                        Text(
                          'Streaming Draft',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.w600,
                            color: AppColors.textMain,
                          ),
                        ),
                      ],
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                      decoration: BoxDecoration(
                        color: const Color(0x0DFFFFFF),
                        border: Border.all(color: AppColors.borderColor),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: const Text(
                        'Writer Streaming',
                        style: TextStyle(
                          fontFamily: 'Fira Code',
                          fontSize: 9,
                          color: AppColors.textMuted,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              Expanded(
                child: Container(
                  color: const Color(0xFF0D0F17),
                  padding: const EdgeInsets.all(16),
                  child: ListView(
                    padding: const EdgeInsets.only(bottom: 60), // Space for FAB
                    children: [
                      streamAsyncValue.when(
                        data: (text) => Text(
                          text,
                          style: const TextStyle(
                            color: Color(0xFFE5E7EB),
                            fontSize: 13,
                            height: 1.6,
                          ),
                        ),
                        loading: () => const Center(
                          child: CircularProgressIndicator(color: AppColors.primary),
                        ),
                        error: (err, stack) => Text(
                          'Error: $err',
                          style: const TextStyle(color: AppColors.error),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
        
        // Critic FAB
        Positioned(
          bottom: 16,
          right: 16,
          child: GestureDetector(
            onTap: () => ref.read(isCriticSheetVisibleProvider.notifier).setVisible(true),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppColors.warning, Color(0xFFD97706)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(30),
                boxShadow: const [
                  BoxShadow(color: Color(0x66F59E0B), blurRadius: 12, offset: Offset(0, 4)),
                ],
              ),
              child: const Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(Icons.message, size: 14, color: Colors.white),
                  SizedBox(width: 6),
                  Text(
                    'Review Comments (3)',
                    style: TextStyle(
                      fontFamily: 'Outfit',
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}
