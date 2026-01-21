import 'package:flutter/material.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // -----------------------------------------------------------
    // ✅ COMPACT THEME SETTINGS
    // -----------------------------------------------------------
    final Color backgroundColor = const Color(0xFFF3EFE4);
    final Color mainTeal = const Color(0xFF135D66);
    final Color textTeal = const Color(0xFF2C6E76);
    final Color redColor = const Color(0xFFD32F2F);

    // Font Styles (Tuned for Pixel 5 density)
    final TextStyle nameStyle = TextStyle(
      color: mainTeal, fontSize: 22, fontWeight: FontWeight.bold,
    );
    final TextStyle emailStyle = TextStyle(
      color: textTeal, fontSize: 14,
    );
    final TextStyle cardLabelStyle = TextStyle(
      color: mainTeal, fontSize: 13,
    );
    final TextStyle cardValueStyle = TextStyle(
      color: mainTeal, fontSize: 26, fontWeight: FontWeight.bold,
    );
    final TextStyle menuButtonStyle = TextStyle(
      color: mainTeal, fontSize: 16, fontWeight: FontWeight.w600,
    );
    // -----------------------------------------------------------

    return Scaffold(
      backgroundColor: backgroundColor,
      // Short AppBar to save vertical space
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        toolbarHeight: 45, 
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: mainTeal),
          onPressed: () => Navigator.pop(context),
        ),
      ),
      // ✅ COLUMN WITH EXPANDED: GUARANTEES ONE SCREEN FIT
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: Column(
            children: [
              // ========================================================
              // PART 1: DYNAMIC CONTENT AREA
              // (Uses "Expanded" to fill available space evenly)
              // ========================================================
              Expanded(
                child: Column(
                  // 👇 THIS IS THE KEY: Distributes items evenly so they never overlap
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
                              decoration: const BoxDecoration(
                                shape: BoxShape.circle, color: Colors.white,
                              ),
                              child: Icon(Icons.person_outline, size: 50, color: mainTeal),
                            ),
                            Container(
                              padding: const EdgeInsets.all(6),
                              decoration: BoxDecoration(
                                color: mainTeal, shape: BoxShape.circle,
                                border: Border.all(color: backgroundColor, width: 2),
                              ),
                              child: const Icon(Icons.edit, size: 14, color: Colors.white),
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
                            mainTeal: mainTeal,
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
                            mainTeal: mainTeal,
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
                          mainTeal: mainTeal, style: menuButtonStyle,
                        ),
                        const SizedBox(height: 12),
                        _buildMenuButton(
                          icon: Icons.settings_outlined, text: "Settings",
                          mainTeal: mainTeal, style: menuButtonStyle,
                        ),
                        const SizedBox(height: 12),
                        _buildMenuButton(
                          icon: Icons.headset_mic_outlined, text: "Help & Support",
                          mainTeal: mainTeal, style: menuButtonStyle,
                        ),
                      ],
                    ),
                  ],
                ),
              ),

              // ========================================================
              // PART 2: FOOTER AREA (Fixed at bottom)
              // ========================================================
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const SizedBox(height: 10),
                  // Log Out Button
                  SizedBox(
                    width: double.infinity,
                    height: 50,
                    child: OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        side: BorderSide(color: redColor),
                        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                        backgroundColor: redColor.withOpacity(0.05),
                      ),
                      onPressed: () {},
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.logout, color: redColor, size: 22),
                          const SizedBox(width: 10),
                          Text("Log Out", style: TextStyle(color: redColor, fontSize: 16, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  ),
                  const SizedBox(height: 15),
                  Text("SpeakTrum", style: TextStyle(color: mainTeal, fontWeight: FontWeight.bold, fontSize: 16)),
                  Text("Version 1.0", style: TextStyle(color: textTeal.withOpacity(0.6), fontSize: 12, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 5), // Small buffer from bottom edge
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
    required Color mainTeal, required TextStyle labelStyle, required TextStyle valueStyle,
  }) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 16, horizontal: 8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: Column(
        children: [
          Icon(icon, color: mainTeal, size: 26),
          const SizedBox(height: 8),
          Text(label, style: labelStyle, textAlign: TextAlign.center),
          const SizedBox(height: 2),
          Text(value, style: valueStyle),
        ],
      ),
    );
  }

  // --- Helper: Menu Button ---
  Widget _buildMenuButton({
    required IconData icon, required String text,
    required Color mainTeal, required TextStyle style,
  }) {
    return Container(
      height: 52,
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 5, offset: const Offset(0, 2))],
        border: Border.all(color: mainTeal, width: 1.5),
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {},
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16),
            child: Row(
              children: [
                Icon(icon, color: mainTeal, size: 24),
                const SizedBox(width: 16),
                Expanded(child: Text(text, style: style)),
                Icon(Icons.arrow_forward_ios, size: 16, color: mainTeal),
              ],
            ),
          ),
        ),
      ),
    );
  }
}