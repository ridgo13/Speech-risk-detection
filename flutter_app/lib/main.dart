// ignore_for_file: unused_import

import 'package:flutter/material.dart';

// 1. Import your new "One File" for auth
import 'screens/auth_screens.dart';
import 'screens/onboarding_screen.dart';

void main() {
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
      initialRoute: '/onboarding',

      routes: {
        // All these are inside 'auth_screens.dart' now:
        '/': (context) => const StartScreen(),
        '/signin': (context) => const SignInScreen(),
        '/signup': (context) => const CreateAccountScreen(),
        '/forgot-password': (context) => const ForgotPasswordScreen(),
        '/onboarding': (context) => const OnboardingScreen(),
      },
    );
  }
}
