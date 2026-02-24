import 'package:flutter/material.dart';
import '../app_colors.dart'; 
import 'settings_screen.dart';
import 'privacy_screen.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // -----------------------------------------------------------
    // 🎨 TEXT STYLES 
    // -----------------------------------------------------------
    final TextStyle nameStyle = TextStyle(
      color: AppColors.mainTeal, 
      fontSize: 22, 
      fontWeight: FontWeight.bold,
    );
    final TextStyle emailStyle = TextStyle(
      color: AppColors.textTeal, 
      fontSize: 14,
    );
    
    // -----------------------------------------------------------
    // 📦 CARD STYLES
    // -----------------------------------------------------------
    final TextStyle cardLabelStyle = TextStyle(fontSize: 13);
    final TextStyle cardValueStyle = TextStyle(fontSize: 26, fontWeight: FontWeight.bold);
    final TextStyle menuButtonStyle = TextStyle(fontSize: 16, fontWeight: FontWeight.w600);

    return Scaffold(
      backgroundColor: AppColors.background, 
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        toolbarHeight: 45, 
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppColors.mainTeal), 
          onPressed: () => Navigator.pop(context),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            children: [
              Expanded(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly, 
                  children: [
                    // --- 1. Profile Section ---
                    Column(
                      children: [
                        Stack(
                          alignment: Alignment.bottomRight,
                          children: [
                            Container(
                              width: 90, height: 90,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle, 
                                color: AppColors.cardColor, // Black in HC
                                border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth),
                              ),
                              child: Icon(Icons.person_outline, size: 50, color: AppColors.cardTextColor),
                            ),
                            Container(
                              padding: const EdgeInsets.all(6),
                              decoration: BoxDecoration(
                                color: AppColors.mainTeal, shape: BoxShape.circle,
                                border: Border.all(color: AppColors.background, width: 2),
                              ),
                              child: Icon(Icons.edit, size: 14, color: AppColors.background), // Contrast Icon
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        Text("Jordan Lee", style: nameStyle),
                        Text("jordan.l@email.com", style: emailStyle),
                      ],
                    ),

                    // --- 2. Stats Cards ---
                    Row(
                      children: [
                        Expanded(
                          child: _buildStatCard(
                            icon: Icons.show_chart,
                            label: "Screenings",
                            value: "12",
                            labelStyle: cardLabelStyle,
                            valueStyle: cardValueStyle,
                          ),
                        ),
                        const SizedBox(width: 15),
                        Expanded(
                          child: _buildStatCard(
                            icon: Icons.calendar_today,
                            label: "Check-up",
                            value: "Oct24",
                            labelStyle: cardLabelStyle,
                            valueStyle: cardValueStyle,
                          ),
                        ),
                      ],
                    ),

                    // --- 3. Menu Buttons ---
                    Column(
                      children: [
                        _buildMenuButton(
                          icon: Icons.shield_outlined, text: "Data & Privacy",
                          style: menuButtonStyle,
                          onTap: () {
                             Navigator.push(context, MaterialPageRoute(builder: (context) => const PrivacyScreen()));
                          },
                        ),
                        const SizedBox(height: 12),
                        
                        _buildMenuButton(
                          icon: Icons.settings_outlined, text: "Settings",
                          style: menuButtonStyle,
                          onTap: () {
                             Navigator.push(context, MaterialPageRoute(builder: (context) => const SettingsScreen()));
                          },
                        ),
                        
                        const SizedBox(height: 12),
                        _buildMenuButton(
                          icon: Icons.headset_mic_outlined, text: "Help & Support",
                          style: menuButtonStyle,
                          onTap: () {},
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // --- Footer Area ---
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const SizedBox(height: 10),
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(color: AppColors.redColor, width: 2),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        backgroundColor: AppColors.redColor.withOpacity(0.1),
                      ),
                      onPressed: () {},
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.logout, color: AppColors.redColor, size: 22),
                          const SizedBox(width: 10),
                          Text("Log Out", style: TextStyle(color: AppColors.redColor, fontSize: 16, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 15),
                  Text("SpeakTrum", style: TextStyle(color: AppColors.mainTeal, fontWeight: FontWeight.bold, fontSize: 16)),
                  Text("Version 1.0", style: TextStyle(color: AppColors.textTeal.withOpacity(0.6), fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 5),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  // --- Helper: Stat Card ---
  Widget _buildStatCard({
    required IconData icon, required String label, required String value,
    required TextStyle labelStyle, required TextStyle valueStyle,
  }) {
    // ✅ Use cardTextColor (White in HC)
    final Color contentColor = AppColors.cardTextColor; 

    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
      decoration: BoxDecoration(
        color: AppColors.cardColor, // Black in HC
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth),
        boxShadow: [BoxShadow(color: Colors.white.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: Column(
        children: [
          Icon(icon, color: contentColor, size: 26), 
          const SizedBox(height: 8),
          Text(label, style: labelStyle.copyWith(color: contentColor), textAlign: TextAlign.center),
          const SizedBox(height: 2),
          Text(value, style: valueStyle.copyWith(color: contentColor)),
        ],
      ),
    );
  }

  // --- Helper: Menu Button ---
  Widget _buildMenuButton({
    required IconData icon, required String text,
    required TextStyle style,
    required VoidCallback onTap, 
  }) {
    final Color contentColor = AppColors.cardTextColor; 

    return Container(
      height: 52,
      decoration: BoxDecoration(
        color: AppColors.cardColor,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: Colors.white.withOpacity(0.05), blurRadius: 5, offset: const Offset(0, 2))],
        border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Icon(icon, color: contentColor, size: 24), 
                const SizedBox(width: 16),
                Expanded(child: Text(text, style: style.copyWith(color: contentColor))), 
                Icon(Icons.arrow_forward_ios, size: 16, color: contentColor), 
              ],
            ),
          ),
        ),
      ),
    );
  }
}