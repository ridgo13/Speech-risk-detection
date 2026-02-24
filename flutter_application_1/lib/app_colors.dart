import 'package:flutter/material.dart';
import 'globals.dart'; 

class AppColors {
  // ----------------------------------------------------------------------
  // 🖤 BACKGROUND
  // Normal: Soft Beige
  // High Contrast: PURE BLACK (#000000)
  // ----------------------------------------------------------------------
  static Color get background => isHighContrast.value 
      ? Colors.black 
      : const Color(0xFFF3EFE4);

  // ----------------------------------------------------------------------
  // 📦 CARD BACKGROUND
  // Normal: White
  // High Contrast: PURE BLACK (Wireframe Style - No fill, just border)
  // ----------------------------------------------------------------------
  static Color get cardColor => isHighContrast.value 
      ? Colors.black 
      : Colors.white;

  // ----------------------------------------------------------------------
  // 🤍 PRIMARY TEXT & HEADERS
  // Normal: Teal
  // High Contrast: PURE WHITE (#FFFFFF)
  // ----------------------------------------------------------------------
  static Color get mainTeal => isHighContrast.value 
      ? Colors.white
      : const Color(0xFF135D66);

  // ----------------------------------------------------------------------
  // 🤍 SECONDARY TEXT
  // Normal: Lighter Teal
  // High Contrast: PURE WHITE (#FFFFFF) - No gray text allowed
  // ----------------------------------------------------------------------
  static Color get textTeal => isHighContrast.value 
      ? Colors.white 
      : const Color(0xFF2C6E76);

  // ----------------------------------------------------------------------
  // 🔤 TEXT INSIDE CARDS
  // Normal: Teal
  // High Contrast: PURE WHITE (#FFFFFF) (Since cards are now black)
  // ----------------------------------------------------------------------
  static Color get cardTextColor => isHighContrast.value 
      ? Colors.white 
      : const Color(0xFF135D66); 

  // ----------------------------------------------------------------------
  // 🔴 DANGER / RESET
  // Normal: Soft Red
  // High Contrast: PURE RED (#FF0000)
  // ----------------------------------------------------------------------
  static Color get redColor => isHighContrast.value
      ? const Color(0xFFFF0000) 
      : const Color(0xFFD32F2F); 

  // ----------------------------------------------------------------------
  // ⬜ BORDERS (CRITICAL)
  // Normal: Thin Teal
  // High Contrast: PURE WHITE (2px-3px) - Defines the shapes
  // ----------------------------------------------------------------------
  static Color get borderColor => isHighContrast.value 
      ? Colors.white 
      : const Color(0xFF135D66);

  static double get borderWidth => isHighContrast.value 
      ? 2.0 // Thick visible borders
      : 1.5;

  // ----------------------------------------------------------------------
  // 🟦 FOCUS / SELECTION (Cyan)
  // Use this for active states if needed
  // ----------------------------------------------------------------------
  static Color get focusColor => const Color(0xFF00FFFF);
}