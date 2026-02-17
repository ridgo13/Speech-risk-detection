// ignore_for_file: unused_import

import 'package:flutter/material.dart';
import 'package:speaktrum_risk_detection/screens/DashboardScreen.dart';
import 'services/notification_service.dart';
import 'screens/settings_screen.dart';

// 1. Import your new "One File" for auth
import 'screens/auth_screens.dart';
import 'screens/onboarding_screen.dart';

final NotificationService notificationService = NotificationService();

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await notificationService.init();
  runApp(const SpeakTrumApp());
}

class SpeakTrumApp extends StatelessWidget {
  const SpeakTrumApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'SpeakTrum',
      theme: ThemeData(fontFamily: 'Roboto', useMaterial3: true),

      // START HERE
      home: const SettingsScreen(),
    );
  }
}
