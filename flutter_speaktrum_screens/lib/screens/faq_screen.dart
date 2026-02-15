import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../app_colors.dart';
import '../globals.dart';

class FaqScreen extends StatelessWidget {
  const FaqScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // List of questions and answers
    final List<Map<String, String>> faqs = [
      {
        "q": "Is SpeakTrum a medical diagnosis tool?",
        "a": "No. SpeakTrum is a supportive screening app that analyzes voice patterns to highlight potential irregularities. It is informational only and not a replacement for professional medical advice. Users should consult a healthcare professional for diagnosis or treatment."
      },
      {
        "q": "What is SpeakTrum used for?",
        "a": "SpeakTrum helps analyze speech patterns using AI to identify potential neurological risk indicators and provide early insights for monitoring speech-related changes over time."
      },
      {
        "q": "How is my speech data stored?",
        "a": "Your speech recordings are securely stored and linked only to your account. They are used solely for analysis and are not shared with third parties."
      },
      {
        "q": "Can I rely on SpeakTrum results to track my progress?",
        "a": "SpeakTrum results are designed to support monitoring trends over time, not to provide a medical diagnosis. They are best used as a supplementary tracking tool alongside professional advice."
      },
      {
        "q": "Can I use SpeakTrum on multiple devices?",
        "a": "Yes. You can access your SpeakTrum account from multiple devices using the same login, and your data will remain synced to your account."
      },
    ];

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppColors.textTeal),
          onPressed: () => Navigator.pop(context), // This goes back
        ),
        title: Text(
          "FAQ",
          style: TextStyle(
            color: AppColors.textTeal,
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
      ),
      body: SingleChildScrollView(
        child: Column(
          children: [
            const SizedBox(height: 20),
            // --- 1. Question Mark Image ---
            Image.asset(
              'assets/images/faq_question_mark.png', 
              height: 120,
              fit: BoxFit.contain,
            ),
            const SizedBox(height: 40),

            // --- 2. FAQ List ---
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: ListView.separated(
                shrinkWrap: true,
                physics: const NeverScrollableScrollPhysics(),
                itemCount: faqs.length,
                separatorBuilder: (context, index) => Divider(
                  color: AppColors.textTeal.withOpacity(0.4),
                  thickness: 2,
                ),
                itemBuilder: (context, index) {
                  final Color contentColor = isHighContrast.value 
                      ? AppColors.cardTextColor 
                      : AppColors.textTeal;

                  return Theme(
                    data: Theme.of(context).copyWith(dividerColor: Colors.transparent),
                    child: ExpansionTile(
                      tilePadding: EdgeInsets.zero,
                      iconColor: contentColor,
                      collapsedIconColor: contentColor,
                      title: Text(
                        faqs[index]["q"]!,
                        style: GoogleFonts.ubuntu(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: contentColor,
                        ),
                      ),
                      children: [
                        Padding(
                          padding: const EdgeInsets.only(bottom: 16, top: 8),
                          child: Text(
                            faqs[index]["a"]!,
                            style: GoogleFonts.ubuntu(
                              fontSize: 16,
                              fontWeight: FontWeight.w500,
                              color: contentColor.withOpacity(0.8),
                              height: 1.5,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
            // Bottom Line for the last item
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Divider(
                color: (isHighContrast.value ? AppColors.cardTextColor : AppColors.textTeal)
                    .withOpacity(0.4), 
                thickness: 2,
              ),
            ),
            const SizedBox(height: 40),
          ], // Added: Closes Column children
        ), // Added: Closes Column
      ), // Added: Closes SingleChildScrollView
    ); // Added: Closes Scaffold
  } // Added: Closes build method
} // Added: Closes FaqScreen class
