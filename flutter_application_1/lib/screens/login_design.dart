import 'package:flutter/material.dart';

class LoginDesignScreen extends StatefulWidget {
  const LoginDesignScreen({super.key});

  @override
  State<LoginDesignScreen> createState() => _LoginDesignScreenState();
}

class _LoginDesignScreenState extends State<LoginDesignScreen> {
  bool _isPasswordVisible = false;

  @override
  Widget build(BuildContext context) {
    // -----------------------------------------------------------
    // ✅ YOUR NEW THEME COLORS
    // -----------------------------------------------------------
    final Color backgroundColor = const Color(0xFFECE3DA); // "Linen"
    final Color mainTeal = const Color(0xFF146875);        // "Stormy Teal" (Buttons/Logo)
    final Color textTeal = const Color(0xFF0F4C55);        // Darker version for text
    // -----------------------------------------------------------

    return Scaffold(
      backgroundColor: backgroundColor, // Applied here
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              // --- Back Button ---
              Align(
                alignment: Alignment.centerLeft,
                child: IconButton(
                  icon: Icon(Icons.arrow_back, color: mainTeal),
                  onPressed: () {
                    // Navigate back logic
                  },
                ),
              ),
              
              const SizedBox(height: 20),

              // --- The Logo (Using your Teal color) ---
              Container(
                height: 100,
                width: 100,
                decoration: const BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.transparent, 
                ),
                child: Icon(Icons.mic_none_outlined, size: 80, color: mainTeal),
              ),

              const SizedBox(height: 40),

              // --- Welcome Text ---
              Text(
                'Welcome Back!',
                style: TextStyle(
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                  color: mainTeal,
                ),
              ),
              const SizedBox(height: 10),
              Text(
                'Sign in to your account',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.w600,
                  color: textTeal,
                ),
              ),

              const SizedBox(height: 50),

              // --- Email Field ---
              _buildShadowTextField(
                hintText: "Email",
                icon: Icons.email_outlined,
                iconColor: mainTeal,
              ),

              const SizedBox(height: 20),

              // --- Password Field ---
              Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(12),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 10,
                      offset: const Offset(0, 5),
                    ),
                  ],
                ),
                child: TextField(
                  obscureText: !_isPasswordVisible,
                  decoration: InputDecoration(
                    border: InputBorder.none,
                    contentPadding: const EdgeInsets.symmetric(vertical: 16),
                    prefixIcon: Icon(Icons.lock_outline, color: mainTeal),
                    hintText: "Password",
                    hintStyle: const TextStyle(color: Colors.grey),
                    suffixIcon: IconButton(
                      icon: Icon(
                        _isPasswordVisible ? Icons.visibility : Icons.visibility_off,
                        color: mainTeal,
                      ),
                      onPressed: () {
                        setState(() {
                          _isPasswordVisible = !_isPasswordVisible;
                        });
                      },
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 40),

              // --- Sign In Button (Using your Teal color) ---
              SizedBox(
                width: double.infinity,
                height: 55,
                child: ElevatedButton(
                  style: ElevatedButton.styleFrom(
                    backgroundColor: mainTeal, // ✅ Button is now Stormy Teal
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 5,
                  ),
                  onPressed: () {
                    // Sign in logic
                  },
                  child: const Text(
                    'Sign in',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // --- Footer Links ---
              Column(
                children: [
                  TextButton(
                    onPressed: () {},
                    child: Text(
                      'Forgot Password?',
                      style: TextStyle(color: textTeal),
                    ),
                  ),
                  GestureDetector(
                    onTap: () {},
                    child: Text(
                      'Create an account',
                      style: TextStyle(
                        color: textTeal,
                        decoration: TextDecoration.underline,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // Helper widget with Color added
  Widget _buildShadowTextField({
    required String hintText, 
    required IconData icon,
    required Color iconColor,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: TextField(
        decoration: InputDecoration(
          border: InputBorder.none,
          contentPadding: const EdgeInsets.symmetric(vertical: 16),
          prefixIcon: Icon(icon, color: iconColor),
          hintText: hintText,
          hintStyle: const TextStyle(color: Colors.grey),
        ),
      ),
    );
  }
}