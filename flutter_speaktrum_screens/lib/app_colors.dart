import 'package:flutter/material.dart';
import 'globals.dart'; // [cite: 18]

class AppColors { // colours choosen
  //  STANDARD THEME 
  static const Color _standardBackground = Color(0xFFECE3DA); // Your Beige [cite: 21]
  static const Color _standardTeal = Color(0xFF146875);       // Your Button Teal [cite: 22]
  static const Color _standardTextTeal = Color(0xFF146875);   // Your Text Teal 
  static const Color _standardCard = Colors.white;            // Standard White [cite: 24]
  static const Color _standardError = Color(0xFFD32F2F);      // Red for Disclaimer

  //  HIGH CONTRAST THEME 
  static const Color _hcBackground = Colors.black; // [cite: 26]
  static const Color _hcMain = Color(0xFFFFD700); // Bright Yellow [cite: 27]
  static const Color _hcText = Colors.white; // [cite: 28]

  //  DYNAMIC GETTERS 
  static Color get background => isHighContrast.value ? _hcBackground : _standardBackground; // [cite: 30]
  static Color get mainTeal => isHighContrast.value ? _hcMain : _standardTeal; // [cite: 31]
  static Color get textTeal => isHighContrast.value ? _hcText : _standardTextTeal; // [cite: 32]
  static Color get cardColor => isHighContrast.value ? _hcBackground : _standardCard; // [cite: 33]
  
  // Special: Text inside cards needs to be White in HC, but Black in Standard [cite: 34]
  static Color get cardTextColor => isHighContrast.value ? _hcText : Colors.black; // [cite: 35]

  static Color get errorColor => isHighContrast.value ? _hcMain : _standardError;
  static Color get borderColor => isHighContrast.value ? _hcMain : Colors.transparent; // [cite: 36]
  static double get borderWidth => isHighContrast.value ? 2.0 : 0.0; // [cite: 37]
}