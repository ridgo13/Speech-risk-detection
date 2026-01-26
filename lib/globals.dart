import 'package:flutter/material.dart';

// Global ValueNotifiers for Accessibility Settings
final ValueNotifier<bool> isHighContrast = ValueNotifier<bool>(false);
final ValueNotifier<bool> isLargerText = ValueNotifier<bool>(false);