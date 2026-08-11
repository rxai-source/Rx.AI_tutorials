import 'package:flutter_riverpod/flutter_riverpod.dart';

// Represents the current stage of the session (1 to 4)
class CurrentStageNotifier extends Notifier<int> {
  @override
  int build() => 1;
  void setStage(int stage) => state = stage;
}
final currentStageProvider = NotifierProvider<CurrentStageNotifier, int>(CurrentStageNotifier.new);

// Represents the active tab in the Roundtable layout (0 = Debate, 1 = Outline)
class ActiveTabNotifier extends Notifier<int> {
  @override
  int build() => 0;
  void setTab(int tab) => state = tab;
}
final activeTabProvider = NotifierProvider<ActiveTabNotifier, int>(ActiveTabNotifier.new);

// Represents the visibility of the Critic bottom sheet in the Drafting layout
class CriticSheetNotifier extends Notifier<bool> {
  @override
  bool build() => false;
  void setVisible(bool visible) => state = visible;
}
final isCriticSheetVisibleProvider = NotifierProvider<CriticSheetNotifier, bool>(CriticSheetNotifier.new);
