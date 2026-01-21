import 'package:flutter/material.dart';

class EducationScreen extends StatelessWidget {
  const EducationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // -----------------------------------------------------------
    // ✅ THEME COLORS (Matching the design)
    // -----------------------------------------------------------
    final Color backgroundColor = const Color(0xFFF3EFE4); // Light Beige
    final Color mainTeal = const Color(0xFF135D66);       // Dark Teal (Titles, Icons)
    final Color textTeal = const Color(0xFF2C6E76);       // Lighter Teal (Subtitles, Body Text)
    final Color cardShadowColor = Colors.black.withOpacity(0.05);
    // -----------------------------------------------------------

    return Scaffold(
      backgroundColor: backgroundColor,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: mainTeal),
          onPressed: () {
            Navigator.pop(context); // Go back to the previous screen
          },
        ),
        title: Text(
          'Education',
          style: TextStyle(
            color: mainTeal,
            fontSize: 22,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          children: [
            // --- Top Illustration (Brain, Wave, Book) - NOW BIGGER ---
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 30.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.psychology, size: 90, color: mainTeal.withOpacity(0.3)),
                  const SizedBox(width: 15),
                  Icon(Icons.graphic_eq, size: 90, color: mainTeal.withOpacity(0.3)),
                  const SizedBox(width: 15),
                  Icon(Icons.menu_book, size: 90, color: mainTeal.withOpacity(0.3)),
                ],
              ),
            ),
            const SizedBox(height: 20),

            // --- Card 1: What is Parkinson's? ---
            _buildEducationCard(
              mainTeal: mainTeal,
              textTeal: textTeal,
              shadowColor: cardShadowColor,
              icon: Icons.psychology,
              title: "What is Parkinson's?",
              subtitle: "Understanding early motor signs",
              onTap: () {
                // Navigate to detail page
              },
            ),
            const SizedBox(height: 16),

            // --- Card 2: Speech Changes in PD ---
            _buildEducationCard(
              mainTeal: mainTeal,
              textTeal: textTeal,
              shadowColor: cardShadowColor,
              icon: Icons.graphic_eq,
              title: "Speech Changes in PD",
              subtitle: "Jitter, Shimmer & Pauses",
              onTap: () {
                // Navigate to detail page
              },
            ),
            const SizedBox(height: 16),

            // --- Card 3: When to Seek Advise ---
            _buildEducationCard(
              mainTeal: mainTeal,
              textTeal: textTeal,
              shadowColor: cardShadowColor,
              icon: Icons.medical_services,
              title: "When to Seek Advise",
              subtitle: "Guidance for early intervention",
              onTap: () {
                // Navigate to detail page
              },
            ),
            const SizedBox(height: 30),

            // --- "Did You Know?" Box ---
            Container(
              padding: const EdgeInsets.all(20.0),
              decoration: BoxDecoration(
                color: mainTeal.withOpacity(0.1), // Light teal background
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: mainTeal.withOpacity(0.3)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(Icons.lightbulb_outline, color: mainTeal),
                      const SizedBox(width: 10),
                      Text(
                        'Did You Know ?',
                        style: TextStyle(
                          color: mainTeal,
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),
                  Text(
                    'Micro-tremors in voice pitch (Jitter) are often one of the earliest signs of motor decline, appearing before physical tremors.',
                    style: TextStyle(
                      color: textTeal,
                      fontSize: 15,
                      height: 1.4,
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 30),

            // --- Footer Text ---
            Text(
              'SpeakTrum is not a diagnostic or medical tool.',
              style: TextStyle(
                color: textTeal.withOpacity(0.6),
                fontSize: 13,
              ),
              textAlign: TextAlign.center,
            ),
            const SizedBox(height: 20),
          ],
        ),
      ),
    );
  }

  // --- Helper Widget for the Education Cards ---
  Widget _buildEducationCard({
    required Color mainTeal,
    required Color textTeal,
    required Color shadowColor,
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: shadowColor,
            blurRadius: 15,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(20.0),
            child: Row(
              children: [
                // Circular Icon
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: mainTeal.withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(icon, color: mainTeal, size: 28),
                ),
                const SizedBox(width: 16),
                // Text Content
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: TextStyle(
                          color: mainTeal,
                          fontSize: 17,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: TextStyle(
                          color: textTeal,
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                // Arrow Icon
                Icon(Icons.arrow_forward_ios, color: textTeal, size: 18),
              ],
            ),
          ),
        ),
      ),
    );
  }
}