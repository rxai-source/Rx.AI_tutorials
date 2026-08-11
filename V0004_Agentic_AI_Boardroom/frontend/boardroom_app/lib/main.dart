import 'package:flutter/material.dart';
import 'package:hooks_riverpod/hooks_riverpod.dart';
import 'core/theme/app_theme.dart';
import 'features/session/session_shell.dart';


void main() {
  runApp(
    const ProviderScope(
      child: BoardroomApp(),
    ),
  );
}

class BoardroomApp extends StatelessWidget {
  const BoardroomApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Rx.AI Boardroom Director Console',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const SessionShell(),
    );
  }
}
