import 'package:flutter/material.dart';
import 'screens/education_screen.dart'; 
// import 'screens/login_design.dart'; // (You can keep this here, just don't use it yet)

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      
      // 👇 2. CHANGE THIS LINE TO POINT TO THE EDUCATION SCREEN
      home: const EducationScreen(), 
    );
  }
}

