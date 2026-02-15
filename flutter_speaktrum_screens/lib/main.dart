import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'globals.dart';
import 'screens/help_support_screen.dart';
import 'app_colors.dart';

void main() {
  runApp(const SpeakTrumApp());
}

class SpeakTrumApp extends StatelessWidget {
  const SpeakTrumApp({super.key});

  @override
  Widget build(BuildContext context) {
    return AnimatedBuilder(
      animation: Listenable.merge([isHighContrast, isLargerText]),
      builder: (context, child) {
        return MaterialApp(
          title: 'SpeakTrum',
          debugShowCheckedModeBanner: false,
          theme: ThemeData(
            useMaterial3: true,
            // Applies the bold Ubuntu theme globally
            textTheme: _buildBoldUbuntuTheme(context),
          ),
          builder: (context, child) {
            final double scale = isLargerText.value ? 1.2 : 1.0;
            return MediaQuery(
              data: MediaQuery.of(context).copyWith(
                textScaler: TextScaler.linear(scale),
              ),
              child: child!,
            );
          },
          home: const HelpSupportScreen(),
        );
      },
    );
  }

  // Helper function to force ALL Ubuntu text styles to be Bold and Teal
  TextTheme _buildBoldUbuntuTheme(BuildContext context) {
    final baseTheme = GoogleFonts.ubuntuTextTheme(Theme.of(context).textTheme);
    return baseTheme.copyWith(
      displayLarge: baseTheme.displayLarge?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      displayMedium: baseTheme.displayMedium?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      displaySmall: baseTheme.displaySmall?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      headlineLarge: baseTheme.headlineLarge?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      headlineMedium: baseTheme.headlineMedium?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      headlineSmall: baseTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      titleLarge: baseTheme.titleLarge?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      titleMedium: baseTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      titleSmall: baseTheme.titleSmall?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      bodyLarge: baseTheme.bodyLarge?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      bodyMedium: baseTheme.bodyMedium?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      bodySmall: baseTheme.bodySmall?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      labelLarge: baseTheme.labelLarge?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      labelMedium: baseTheme.labelMedium?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
      labelSmall: baseTheme.labelSmall?.copyWith(fontWeight: FontWeight.bold, color: AppColors.textTeal),
    );
  }
}