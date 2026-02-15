import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../app_colors.dart';
import '../globals.dart';

class EmptyHistoryScreen extends StatelessWidget {
  const EmptyHistoryScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // --- EASILY ADJUST SIZES HERE ---
    const double titleSize = 24.0;
    const double mainTextSize = 22.0;
    const double subTextSize = 15.0;
    
    // Your specific requested color: 485B5E
    const Color customGreyTeal = Color(0xFF485B5E);

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppColors.textTeal),
          onPressed: () {
            // Future-proof: Currently pops back
            Navigator.pop(context);
          },
        ),
        title: Text(
          "Result History",
          style: GoogleFonts.ubuntu(
            color: AppColors.textTeal,
            fontWeight: FontWeight.bold,
            fontSize: titleSize,
          ),
        ),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 40.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 1. Empty File Icon
              Image.asset(
                'assets/images/empty_history_icon.png',
                height: 180,
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 30),

              // 2. "No screenings yet" Text
              Text(
                "No screenings yet",
                textAlign: TextAlign.center,
                style: GoogleFonts.ubuntu(
                  color: isHighContrast.value ? AppColors.cardTextColor : customGreyTeal,
                  fontSize: mainTextSize,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 15),

              // 3. Detailed Subtext
              Text(
                "You haven’t completed a voice screening yet. Start your first screening to track your voice patterns over time.",
                textAlign: TextAlign.center,
                style: GoogleFonts.ubuntu(
                  color: isHighContrast.value ? AppColors.cardTextColor : customGreyTeal,
                  fontSize: subTextSize,
                  fontWeight: FontWeight.bold,
                  height: 1.5,
                ),
              ),
              const SizedBox(height: 100), // Pushes content slightly upward
            ],
          ),
        ),
      ),
    );
  }
}