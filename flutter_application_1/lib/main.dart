import 'package:flutter/material.dart';
import 'globals.dart';         
import 'app_colors.dart';
import 'screens/profile_screen.dart'; // ✅ Start at Profile

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
          debugShowCheckedModeBanner: false,
          title: 'SpeakTrum',
          
          theme: ThemeData(
            scaffoldBackgroundColor: AppColors.background,
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

          // 🚀 START AT PROFILE (The Main Menu)
          home: const ProfileScreen(), 
        );
      },
    );
  }
}