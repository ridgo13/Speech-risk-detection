import 'package:flutter/material.dart';
import '../globals.dart';    
import '../app_colors.dart'; 

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _isVoiceGuidance = true;
  bool _isDataSharing = true;

  @override
  Widget build(BuildContext context) {
    // 🔔 CRITICAL FIX: Wrap the WHOLE screen in a listener.
    // This forces the background and text to change COLOR instantly.
    return AnimatedBuilder(
      animation: Listenable.merge([isHighContrast, isLargerText]),
      builder: (context, child) {
        
        return Scaffold(
          backgroundColor: AppColors.background, // ✅ Updates Instantly now
          appBar: AppBar(
            backgroundColor: Colors.transparent,
            elevation: 0,
            leading: IconButton(
              icon: Icon(Icons.arrow_back, color: AppColors.mainTeal),
              onPressed: () => Navigator.pop(context),
            ),
          ),
          body: SingleChildScrollView(
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Column(
              children: [
                Text("Settings", style: TextStyle(color: AppColors.mainTeal, fontSize: 26, fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Text("Customize your experience", style: TextStyle(color: AppColors.textTeal, fontSize: 16)),
                const SizedBox(height: 30),

                _buildSectionHeader("DISPLAY & AUDIO"),
                
                // Toggle 1: High Contrast
                _buildToggleCard(
                  title: "High Contrast Mode", 
                  value: isHighContrast.value, // Read directly from global
                  onChanged: (val) { 
                    isHighContrast.value = val; 
                  }
                ),
                const SizedBox(height: 12),
                
                // Toggle 2: Larger Text
                _buildToggleCard(
                  title: "Larger Text", 
                  value: isLargerText.value, // Read directly from global
                  onChanged: (val) { 
                    isLargerText.value = val; 
                  }
                ),
                const SizedBox(height: 12),
                
                // Toggle 3: Voice Guidance
                _buildToggleCard(
                  title: "Voice Guidance",
                  subtitle: "Enables Avatar instructions.",
                  value: _isVoiceGuidance,
                  onChanged: (val) => setState(() => _isVoiceGuidance = val),
                ),

                const SizedBox(height: 30),
                _buildSectionHeader("PRIVACY"),

                _buildToggleCard(
                  title: "Data Sharing Consent",
                  subtitle: "Allow anonymous data usage.",
                  value: _isDataSharing,
                  onChanged: (val) => setState(() => _isDataSharing = val),
                ),
                const SizedBox(height: 12),

                _buildNavCard(title: "Download Personal Data", onTap: () {}),

                const SizedBox(height: 40),

                TextButton(
                  onPressed: () { isHighContrast.value = false; isLargerText.value = false; },
                  child: Text("Reset to Default Settings", style: TextStyle(color: AppColors.redColor, fontSize: 15, fontWeight: FontWeight.w600)),
                ),
                const SizedBox(height: 30),
              ],
            ),
          ),
        );
      }
    );
  }

  Widget _buildSectionHeader(String title) {
    return Align(
      alignment: Alignment.centerLeft,
      child: Padding(
        padding: const EdgeInsets.only(bottom: 12.0),
        child: Text(title, style: TextStyle(color: AppColors.mainTeal, fontSize: 13, fontWeight: FontWeight.bold, letterSpacing: 1.0)),
      ),
    );
  }

  // 🔹 Helper: Toggle Switch Card
  Widget _buildToggleCard({required String title, String? subtitle, required bool value, required Function(bool) onChanged}) {
    // Force specific colors for the switch based on mode
    final bool isHC = isHighContrast.value;
    final Color activeTrack = isHC ? Colors.white : const Color(0xFF135D66);
    final Color activeDot   = isHC ? Colors.black : Colors.white;

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppColors.cardColor, 
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth),
        boxShadow: isHC ? [] : [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: TextStyle(color: AppColors.cardTextColor, fontSize: 16, fontWeight: FontWeight.bold)),
                if (subtitle != null) ...[
                  const SizedBox(height: 4),
                  Text(subtitle, style: TextStyle(color: AppColors.cardTextColor.withOpacity(0.7), fontSize: 12)),
                ],
              ],
            ),
          ),
          
          Switch(
            value: value,
            activeColor: activeDot,       
            activeTrackColor: activeTrack, 
            inactiveThumbColor: Colors.white,
            inactiveTrackColor: isHC ? Colors.grey : Colors.grey.shade300,
            onChanged: onChanged,
          ),
        ],
      ),
    );
  }

  // 🔹 Helper: Navigation Card
  Widget _buildNavCard({required String title, required VoidCallback onTap}) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth),
        boxShadow: isHighContrast.value ? [] : [BoxShadow(color: Colors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, 4))],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(12),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 18),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(title, style: TextStyle(color: AppColors.cardTextColor, fontSize: 16, fontWeight: FontWeight.bold)),
                Icon(Icons.arrow_forward_ios, size: 16, color: AppColors.cardTextColor),
              ],
            ),
          ),
        ),
      ),
    );
  }
}