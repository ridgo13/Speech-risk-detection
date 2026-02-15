import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
// Import url_launcher to open external apps like dialer and email
import 'package:url_launcher/url_launcher.dart';
import '../app_colors.dart';
import '../globals.dart';
import 'in_app_chat_screen.dart'; // Import the placeholder chat screen

class ContactUsScreen extends StatelessWidget {
  const ContactUsScreen({super.key});

  // --- Helper Functions for Launching Apps ---

  // Function to launch the phone dialer
  Future<void> _makePhoneCall(String phoneNumber) async {
    final Uri launchUri = Uri(scheme: 'tel', path: phoneNumber);
    if (await canLaunchUrl(launchUri)) {
      await launchUrl(launchUri);
    } else {
      debugPrint('Could not launch dialer for $phoneNumber');
    }
  }

  // Function to launch the default email app
  Future<void> _sendEmail(String emailAddress) async {
    final Uri launchUri = Uri(
      scheme: 'mailto',
      path: emailAddress,
    );
    if (await canLaunchUrl(launchUri)) {
      await launchUrl(launchUri);
    } else {
      debugPrint('Could not launch email app for $emailAddress');
    }
  }

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
          onPressed: () => Navigator.pop(context), // Goes back to Help & Support
        ),
        title: Text(
          "Contact Us",
          style: GoogleFonts.ubuntu(
            color: AppColors.textTeal,
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
      ),
      body: SingleChildScrollView(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.center,
            children: [
              const SizedBox(height: 20),
              // --- 1. Top Illustration ---
              Image.asset(
                'assets/images/contact_us_illustration.png',
                height: 150,
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 30),

              // --- 2. Headline & Subtext ---
              Text(
                "Get In Touch",
                style: GoogleFonts.ubuntu(
                  color: AppColors.textTeal,
                  fontSize: 28,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 12),
              Text(
                "If you have any Inquires get in touch with us\nWe will be happy to help you",
                textAlign: TextAlign.center,
                style: GoogleFonts.ubuntu(
                  color: AppColors.textTeal,
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  height: 1.4,
                ),
              ),
              const SizedBox(height: 60),

              // --- 3. The Three Functional Buttons ---
              
              // Button 1: Phone Call
              _ContactButton(
                text: "+(60) 1234-56789",
                iconAssetPath: 'assets/images/icon_phone.png',
                onTap: () {
                  // Future-proof: passes the number to the dialer
                  _makePhoneCall('+60123456789'); 
                },
              ),
              const SizedBox(height: 20),
               
              // Button 2: Email
              _ContactButton(
                text: "company.speaktrum.info.@gmail.com",
                iconAssetPath: 'assets/images/icon_email.png',
                onTap: () {
                   // Future-proof: opens email app with address pre-filled
                  _sendEmail('company.speaktrum.info.@gmail.com');
                },
              ),
              const SizedBox(height: 20),
              
              // Button 3: In-App Chat (Navigates to placeholder screen)
              _ContactButton(
                text: "In-App Chat Support",
                iconAssetPath: 'assets/images/icon_chat.png',
                onTap: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => const InAppChatScreen()),
                  );
                },
              ),

              const SizedBox(height: 40),

              // --- 4. Medical Disclaimer Box ---
              // Matches the exact style from the previous screen and reference image.
              Container(
                padding: const EdgeInsets.all(16.0),
                decoration: BoxDecoration(
                  // White background for the card itself
                  color: Colors.white, 
                  borderRadius: BorderRadius.circular(12),
                  // Red border
                  border: Border.all(color: AppColors.errorColor, width: 1.5),
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
                          style: GoogleFonts.ubuntu(
                            color: AppColors.errorColor,
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      "SpeakTrum is not a diagnostic or medical tool. It is intended for educational and support purposes only.",
                      style: GoogleFonts.ubuntu(
                        color: AppColors.textTeal,
                        fontSize: 14,
                        fontWeight: FontWeight.bold,
                        height: 1.4,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 30),
            ],
          ),
        ),
      ),
    );
  }
}

// --- REUSABLE CONTACT BUTTON WIDGET ---
// Handles style, PNG assets, and accessibility rules for the three buttons.
class _ContactButton extends StatelessWidget {
  final String text;
  final String iconAssetPath; // Path to your PNG icon asset
  final VoidCallback onTap;

  const _ContactButton({
    required this.text,
    required this.iconAssetPath,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    // Accessibility Rule: White text/icon normally, Yellow if High Contrast is ON.
    final Color contentColor = isHighContrast.value ? AppColors.cardTextColor : Colors.white;

    return SizedBox(
      width: double.infinity,
      height: 65,
      child: ElevatedButton(
        onPressed: onTap,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.mainTeal,
          elevation: 3,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12), // Rounded corners as per image
          ),
          padding: const EdgeInsets.symmetric(horizontal: 20),
        ),
        child: Row(
          children: [
            // 1. PNG Asset Icon on the left
            // Using Image.asset with color filter to match text color
            Image.asset(
              iconAssetPath,
              width: 28,
              height: 28,
              color: contentColor,
            ),
            const SizedBox(width: 20),
            // 2. Text
            Expanded(
              child: Text(
                text,
                style: GoogleFonts.ubuntu(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: contentColor, // White or Yellow based on accessibility
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }
}