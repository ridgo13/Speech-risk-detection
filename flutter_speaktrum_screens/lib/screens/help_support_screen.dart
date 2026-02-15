import 'package:flutter/material.dart';
import '../app_colors.dart'; // Rule #2
import '../globals.dart';   // Fixes the isHighContrast error
import 'faq_screen.dart'; // This connects the two files
import 'contact_us_screen.dart';

class HelpSupportScreen extends StatelessWidget {
  const HelpSupportScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppColors.textTeal),
          onPressed: () => print("Back Pressed"),
        ),
        title: Text(
          "Help & Support",
          style: TextStyle(
            color: AppColors.textTeal,
            fontWeight: FontWeight.bold,
            fontSize: 26,
          ),
        ),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 50),
              Image.asset(
                'assets/images/support_illustration.png',
                height: 200,
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 24),
              Text(
                "Hello, How can we",
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: AppColors.textTeal,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              Text(
                "Help You?",
                textAlign: TextAlign.center,
                style: TextStyle(
                  color: AppColors.textTeal,
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 110),
              _SupportButton(
  text: "FAQs",
  leadingIcon: Icons.help_outline_rounded, 
  onTap: () {
    // This pushes the FAQ screen on top of the current screen
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const FaqScreen()),
    );
  },
),
              const SizedBox(height: 26),
              _SupportButton(
                text: "Contact Support",
                leadingIcon: Icons.headset_mic_outlined,
                onTap: () {
                  // Navigate to the Contact Us screen
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const ContactUsScreen()),
                  );
                },
              ),
              const SizedBox(height: 30),
              // Medical Disclaimer Box
              Container(
  padding: const EdgeInsets.all(16.0),
  decoration: BoxDecoration(
    color: AppColors.cardColor, // Keeping your background color
    borderRadius: BorderRadius.circular(12),
    // --- UPDATED BORDER BELOW ---
    border: Border.all(
      color: AppColors.errorColor, // Changed to your Red/Error color
      width: 1.5,                  // Matched the width from the Contact screen
    ),
  ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.error_outline, color: AppColors.errorColor, size: 24),
                        const SizedBox(width: 10),
                        Text(
                          "Medical Disclaimer:",
                          style: TextStyle(
                            color: AppColors.errorColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 14,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      "SpeakTrum is not a diagnostic or medical tool. It is intended for educational and support purposes only.",
                      style: TextStyle(
                        color: AppColors.textTeal,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}

class _SupportButton extends StatelessWidget {
  final String text;
  final IconData leadingIcon;
  final VoidCallback onTap;

  const _SupportButton({
    required this.text,
    required this.leadingIcon,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    // Content color logic: White for Standard, Yellow for HC [cite: 35]
    final Color contentColor = isHighContrast.value ? AppColors.cardTextColor : Colors.white;

    return SizedBox(
      width: double.infinity,
      height: 65,
      child: ElevatedButton(
        onPressed: onTap,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.mainTeal,
          elevation: 2,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
          padding: const EdgeInsets.symmetric(horizontal: 20),
        ),
        child: Row(
          children: [
            Icon(leadingIcon, size: 28, color: contentColor),
            const SizedBox(width: 16),
            Expanded(
              child: Text(
                text,
                style: TextStyle(
                  fontSize: 22,
                  fontWeight: FontWeight.bold,
                  color: contentColor,
                ),
              ),
            ),
            Icon(Icons.keyboard_arrow_right, size: 28, color: contentColor),
          ],
        ),
      ),
    );
  }
}