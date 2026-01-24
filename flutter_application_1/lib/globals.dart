import 'package:flutter/material.dart';

// ✅ The "Radio Stations" the whole app listens to
final ValueNotifier<bool> isHighContrast = ValueNotifier(false);
final ValueNotifier<bool> isLargerText = ValueNotifier(false);