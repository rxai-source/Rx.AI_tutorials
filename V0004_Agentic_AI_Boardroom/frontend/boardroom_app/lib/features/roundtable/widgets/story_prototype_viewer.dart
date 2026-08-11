import 'dart:convert';
import 'package:flutter/material.dart';
import '../../../core/theme/app_theme.dart';

class StoryPrototypeViewer extends StatelessWidget {
  final String jsonString;

  const StoryPrototypeViewer({
    super.key,
    required this.jsonString,
  });

  @override
  Widget build(BuildContext context) {
    Map<String, dynamic> data;
    try {
      data = jsonDecode(jsonString);
    } catch (e) {
      data = {"error": "Invalid JSON: $e"};
    }

    final title = data['title'] ?? 'Untitled';
    final concepts = List<String>.from(data['concepts'] ?? []);
    
    return Container(
      decoration: BoxDecoration(
        color: const Color(0xFF0F121D),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderColor),
      ),
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Wrap(
            spacing: 6,
            runSpacing: 6,
            children: concepts.map((c) => _buildTag(c)).toList(),
          ),
          const SizedBox(height: 8),
          Container(
            padding: const EdgeInsets.only(left: 8),
            decoration: const BoxDecoration(
              border: Border(left: BorderSide(color: AppColors.primary, width: 2)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: const TextStyle(color: Colors.white, fontSize: 13, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 2),
                const Text(
                  'Ages 8-10 | Educational',
                  style: TextStyle(color: AppColors.textMuted, fontSize: 10),
                ),
              ],
            ),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: const Color(0xFF08090F),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(color: const Color(0x08FFFFFF)),
              ),
              child: SingleChildScrollView(
                child: Text(
                  jsonString, // Keep raw JSON formatting for the view
                  style: const TextStyle().mono.copyWith(
                        color: const Color(0xFF93C5FD),
                        fontSize: 10,
                        height: 1.4,
                      ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTag(String label) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: const Color(0x1F6366F1),
        border: Border.all(color: const Color(0x406366F1)),
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        label,
        style: const TextStyle(
          color: Color(0xFFA5B4FC),
          fontSize: 9,
          fontWeight: FontWeight.w600,
        ),
      ),
    );
  }
}
