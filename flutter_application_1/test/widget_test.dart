import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

// ✅ Make sure this matches your project name!
import 'package:flutter_application_1/main.dart'; 

void main() {
  testWidgets('App launch smoke test', (WidgetTester tester) async {
    // 1. Build our app (SpeakTrumApp, not MyApp)
    await tester.pumpWidget(const SpeakTrumApp());

    // 2. Verify that the app actually loads
    // We look for the "Education" title since that is your home screen now.
    expect(find.text('Education'), findsOneWidget);
    
    // 3. Verify we verify the "What is Parkinson's?" card exists
    expect(find.text("What is Parkinson's?"), findsOneWidget);
  });
}