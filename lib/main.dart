import 'package:flutter/material.dart';
import 'DashboardScreen.dart'; //
import 'globals.dart';   // [cite: 13, 14]

void main() {
  runApp(
    AnimatedBuilder(
      animation: Listenable.merge([isHighContrast, isLargerText]), // [cite: 56]
      builder: (context, child) {
        return MaterialApp(
          debugShowCheckedModeBanner: false,
          title: 'SpeakTrum',
          builder: (context, child) {
            // This handles the LARGE TEXT logic from your group document [cite: 62]
            final double scale = isLargerText.value ? 1.2 : 1.0; 
            return MediaQuery(
              data: MediaQuery.of(context).copyWith(
                textScaler: TextScaler.linear(scale), // [cite: 64]
              ),
              child: child!,
            );
          },
          // Change this from MainAppFlow to DashboardScreen
          home: const DashboardScreen(), 
        );
      },
    ),
  );
}