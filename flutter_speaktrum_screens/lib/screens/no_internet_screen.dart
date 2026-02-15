import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../app_colors.dart';
import '../globals.dart';

class NoInternetScreen extends StatelessWidget {
  const NoInternetScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // --- EASILY ADJUST SIZES HERE ---
    const double titleSize = 26.0;
    const double boxTextSize = 16.0;
    const double buttonTextSize = 18.0;

    return Scaffold(
      backgroundColor: AppColors.background,
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 30.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // 1. WiFi Bar Alert Icon
              Image.asset(
                'assets/images/no_internet_icon.png',
                height: 120,
                fit: BoxFit.contain,
              ),
              const SizedBox(height: 30),

              // 2. Main Message
              Text(
                "No Internet Connection!",
                textAlign: TextAlign.center,
                style: GoogleFonts.ubuntu(
                  color: AppColors.textTeal,
                  fontSize: titleSize,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 40),

              // 3. Instruction Box (Disclaimer Style)
              Container(
                padding: const EdgeInsets.all(20.0),
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.errorColor, width: 2),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  children: [
                    // Exclamation Icon in Box
                    Image.asset(
                      'assets/images/exclamation_icon.png',
                      height: 40,
                      color: AppColors.errorColor, // Ensures it matches the theme
                    ),
                    const SizedBox(height: 15),
                    Text(
                      "SpeakTrum needs an internet connection to continue.",
                      textAlign: TextAlign.center,
                      style: GoogleFonts.ubuntu(
                        color: AppColors.errorColor,
                        fontSize: boxTextSize,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 15),
                    Text(
                      "Please check your connection and try again.",
                      textAlign: TextAlign.center,
                      style: GoogleFonts.ubuntu(
                        color: AppColors.errorColor,
                        fontSize: boxTextSize,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 60),

              // 4. Try Again Button
              SizedBox(
                width: 200,
                height: 55,
                child: ElevatedButton(
                  onPressed: () {
                    // Logic: Future-proof for checking connection
                    // For now, it just goes back to the previous screen
                    Navigator.pop(context);
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppColors.mainTeal,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  child: Text(
                    "Try Again",
                    style: GoogleFonts.ubuntu(
                      color: isHighContrast.value ? AppColors.cardTextColor : Colors.white,
                      fontSize: buttonTextSize,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}