import 'package:flutter/material.dart';

// Global ValueNotifiers for Accessibility Settings
// Normally these would be changed by a Settings screen.
final ValueNotifier<bool> isHighContrast = ValueNotifier<bool>(false);
final ValueNotifier<bool> isLargerText = ValueNotifier<bool>(false);