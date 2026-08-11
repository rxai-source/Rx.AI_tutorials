import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppColors {
  static const Color bgBase = Color(0xFF0A0B0E);
  static const Color bgSurface = Color(0xB3111622); // rgba(17, 22, 34, 0.7)
  static const Color bgCard = Color(0x991A2030); // rgba(26, 32, 48, 0.6)
  static const Color bgInput = Color(0xCC0A0B0E); // rgba(10, 11, 14, 0.8)
  static const Color borderColor = Color(0x14FFFFFF); // rgba(255, 255, 255, 0.08)
  static const Color borderFocus = Color(0x996366F1); // rgba(99, 102, 241, 0.6)

  static const Color primary = Color(0xFF6366F1);
  static const Color primaryGlow = Color(0x266366F1); // rgba(99, 102, 241, 0.15)
  static const Color secondary = Color(0xFFA855F7);
  static const Color success = Color(0xFF10B981);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);

  static const Color textMain = Color(0xFFF3F4F6);
  static const Color textMuted = Color(0xFF9CA3AF);
  static const Color textDark = Color(0xFF6B7280);
}

class AppTheme {
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: AppColors.bgBase,
      primaryColor: AppColors.primary,
      colorScheme: const ColorScheme.dark(
        primary: AppColors.primary,
        secondary: AppColors.secondary,
        surface: AppColors.bgSurface,
        error: AppColors.error,
        onPrimary: Colors.white,
        onSecondary: Colors.white,
        onSurface: AppColors.textMain,
      ),
      textTheme: TextTheme(
        displayLarge: GoogleFonts.outfit(color: AppColors.textMain, fontWeight: FontWeight.w700),
        displayMedium: GoogleFonts.outfit(color: AppColors.textMain, fontWeight: FontWeight.w600),
        displaySmall: GoogleFonts.outfit(color: AppColors.textMain, fontWeight: FontWeight.w600),
        headlineMedium: GoogleFonts.outfit(color: AppColors.textMain, fontWeight: FontWeight.w600),
        headlineSmall: GoogleFonts.outfit(color: AppColors.textMain, fontWeight: FontWeight.w600),
        titleLarge: GoogleFonts.outfit(color: AppColors.textMain, fontWeight: FontWeight.w600),
        titleMedium: GoogleFonts.outfit(color: AppColors.textMain, fontWeight: FontWeight.w500),
        titleSmall: GoogleFonts.outfit(color: AppColors.textMain, fontWeight: FontWeight.w500),
        bodyLarge: GoogleFonts.inter(color: AppColors.textMain, fontWeight: FontWeight.w400),
        bodyMedium: GoogleFonts.inter(color: AppColors.textMain, fontWeight: FontWeight.w400),
        bodySmall: GoogleFonts.inter(color: AppColors.textMuted, fontWeight: FontWeight.w400),
        labelLarge: GoogleFonts.inter(color: AppColors.textMain, fontWeight: FontWeight.w600),
        labelSmall: GoogleFonts.inter(color: AppColors.textMuted, fontWeight: FontWeight.w500),
      ),
      dividerColor: AppColors.borderColor,
      appBarTheme: const AppBarTheme(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
    );
  }

  static BoxDecoration get glassDecorationLg {
    return BoxDecoration(
      color: AppColors.bgSurface,
      borderRadius: BorderRadius.circular(16),
      border: Border.all(color: AppColors.borderColor, width: 1),
      boxShadow: const [
        BoxShadow(
          color: Colors.black26,
          blurRadius: 16,
          offset: Offset(0, 4),
        )
      ],
    );
  }

  static BoxDecoration get glassDecorationMd {
    return BoxDecoration(
      color: AppColors.bgCard,
      borderRadius: BorderRadius.circular(10),
      border: Border.all(color: AppColors.borderColor, width: 1),
    );
  }
}

extension TextStyleExtensions on TextStyle {
  TextStyle get mono => GoogleFonts.firaCode(
        textStyle: this,
      );
}
