import 'package:flutter/material.dart';
import 'globals.dart'; 

class AppColors {
  // 🎨 STANDARD THEME (Our Design Spec)
  static const Color _standardBackground = Color(0xFFF3EFE4); // Beige
  static const Color _standardTeal = Color(0xFF135D66);       // Main Teal
  static const Color _standardTextTeal = Color(0xFF2C6E76);   // Text Teal
  static const Color _standardCard = Colors.white;            // White Card

  // 🏁 HIGH CONTRAST THEME (Black & Yellow/White)
  static const Color _hcBackground = Colors.black;
  static const Color _hcMain = Color(0xFFFFD700); // Bright Yellow
  static const Color _hcText = Colors.white;

  // 🔥 DYNAMIC GETTERS
  static Color get background => isHighContrast.value ? _hcBackground : _standardBackground;
  static Color get mainTeal => isHighContrast.value ? _hcMain : _standardTeal;
  static Color get textTeal => isHighContrast.value ? _hcText : _standardTextTeal;
  static Color get cardColor => isHighContrast.value ? _hcBackground : _standardCard;
  static Color get cardTextColor => isHighContrast.value ? _hcText : Colors.black;

  // Borders only appear in High Contrast mode
  static Color get borderColor => isHighContrast.value ? _hcMain : Colors.transparent;
  static double get borderWidth => isHighContrast.value ? 2.0 : 0.0;
}