# Flutter UI Scaffold Walkthrough (Mobile)

I have successfully initialized the `boardroom_app` Flutter project and implemented the static UI based on the mobile mockup.

## Changes Made

1. **Project Initialization**
   - Ran `flutter create` to properly scaffold the `android`, `ios`, and `web` directories without disturbing our `lib` structure.
   - Updated `pubspec.yaml` to fetch all necessary dependencies, setting flexible versions to resolve dependency clashes (and later using `flutter pub get`).

2. **Core Theme and Shared Components**
   - `AppTheme`: Established a customized design system using the `Outfit` and `Inter` Google fonts, along with our defined dark mode color palette (Indigo, Purple, Emerald, Amber, Red).
   - Created reusable widgets:
     - `ChatBubble`: Supports multiple roles (User, Director, Tech SME, Writer, Critic) with distinct coloring.
     - `AgentBadge`: Circular indicator containing agent initials.
     - `TimelineStepper`: A mobile-optimized stepper at the top showing the 4 primary stages.
     - `AppDrawer`: A slide-in drawer showing session details and active roster status.
     - `GlassPanel`: Custom glassmorphism container used across different frames.
     - `ChatInputWidget`: A text input field used when clarification is requested.

3. **State Management (Riverpod 3.0)**
   - Used Riverpod's modern `NotifierProvider` to manage UI state, maintaining separation from the views:
     - `currentStageProvider`: Tracks progression from Stage 1 to Stage 4.
     - `activeTabProvider`: Toggles between Debate (0) and Outline (1) in Stage 3.
     - `isCriticSheetVisibleProvider`: Handles the opening/closing of the Critic Feedback bottom sheet.

4. **Layout Frames**
   - **Chat Layout (Stages 1 & 2)**: Shows dialogue feed. At Stage 2, it also presents the `ChatInputWidget` for User Clarification.
   - **Roundtable Layout (Stage 3)**: Incorporates a segmented `TabBar` separating the *Roundtable Debate* from the *Story Outline*.
   - **Drafting Layout (Stage 4)**: A full-screen streaming draft view with a Floating Action Button (FAB) that triggers the Critic Feedback slide-up bottom sheet.

> [!NOTE]
> The "Auto Play" and "Reset Simulation" buttons have been intentionally excluded from the Flutter application's App Drawer, as requested in your prompt.

## Verification
- Code was successfully checked against `flutter analyze`. There are no blocking syntax errors (only a few informational logs regarding Flutter's recent `Color.withOpacity` deprecation which are perfectly safe to ignore at this stage).
- The `widget_test.dart` has been updated to successfully run and verify that the `BoardroomApp` shell loads correctly.

You can now navigate into `frontend/boardroom_app` and run the application (`flutter run -d chrome` or run on an emulator) to see the completed layout in action!
