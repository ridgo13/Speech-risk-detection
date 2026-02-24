import 'package:flutter/material.dart';
import '../app_colors.dart'; 

class PrivacyScreen extends StatelessWidget {
  const PrivacyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background, 
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        title: Text(
          "Privacy & Data",
          style: TextStyle(
            color: AppColors.mainTeal, // ✅ Yellow/White (On Black Background)
            fontSize: 22,
            fontWeight: FontWeight.bold,
          ),
        ),
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppColors.mainTeal), 
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            // =======================================================
            // 3 BIG INFO CARDS
            // =======================================================
            
            _buildInfoCard(
              icon: Icons.lock_outline,
              title: "End-to-End Encryption",
              subtitle: "Secure audio-only protocol",
            ),
            const SizedBox(height: 16),

            _buildInfoCard(
              icon: Icons.dns_outlined,
              title: "Secure Storage",
              subtitle: "HIPAA-compliant servers",
            ),
            const SizedBox(height: 16),

            _buildInfoCard(
              icon: Icons.back_hand_outlined,
              title: "Your Data",
              subtitle: "Revoke access anytime",
            ),

            const SizedBox(height: 40),

            // =======================================================
            // ACTION BUTTONS
            // =======================================================
            
            _buildActionButton(
              text: "Download My Data",
              color: AppColors.cardTextColor, // ✅ Force Black Text on White Button
              isRed: false,
              onTap: () {},
            ),
            const SizedBox(height: 16),

            _buildActionButton(
              text: "Delete Voice Recordings",
              color: AppColors.redColor, // ✅ Red is fine (it stands out)
              isRed: true,
              onTap: () {},
            ),

            const SizedBox(height: 20), 
          ],
        ),
      ),
    );
  }

  // 🔹 Helper: Big Info Card
  Widget _buildInfoCard({
    required IconData icon,
    required String title,
    required String subtitle,
  }) {
    // ✅ 1. DEFINE CONTENT COLOR
    // This forces text to be BLACK when inside the WHITE card
    final Color contentColor = AppColors.cardTextColor; 

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 16),
      decoration: BoxDecoration(
        color: AppColors.cardColor, // ✅ White Card
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth),
        boxShadow: [
          // Remove shadow in High Contrast (Wireframe style)
          if (AppColors.cardColor == Colors.white)
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
        ],
      ),
      child: Column(
        children: [
          // Icon Circle
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              // Light background for icon (Soft Teal or Grey in HC)
              color: contentColor.withOpacity(0.1), 
              shape: BoxShape.circle,
            ),
            child: Icon(icon, size: 32, color: contentColor), // ✅ Black Icon
          ),
          const SizedBox(height: 12),
          // Title
          Text(
            title,
            style: TextStyle(
              color: contentColor, // ✅ Black Text
              fontSize: 18,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 4),
          // Subtitle
          Text(
            subtitle,
            style: TextStyle(
              color: contentColor.withOpacity(0.7), // ✅ Dark Grey Text
              fontSize: 13,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  // 🔹 Helper: Action Button
  Widget _buildActionButton({
    required String text,
    required Color color,
    required bool isRed,
    required VoidCallback onTap,
  }) {
    // If it's the "Download" button in High Contrast, we want it to look like a Card
    // If it's Red, keep it Red.
    final Color buttonTextColor = isRed ? color : AppColors.cardTextColor;
    final Color borderColor = isRed ? color : AppColors.borderColor;

    return SizedBox(
      width: double.infinity,
      height: 55,
      child: OutlinedButton(
        style: OutlinedButton.styleFrom(
          foregroundColor: buttonTextColor,
          side: BorderSide(color: borderColor, width: isRed ? 1.5 : AppColors.borderWidth),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
          backgroundColor: isRed 
              ? color.withOpacity(0.05) 
              : AppColors.cardColor, // White Background
        ),
        onPressed: onTap,
        child: Text(
          text,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: buttonTextColor,
          ),
        ),
      ),
    );
  }
}