import 'package:flutter/material.dart';
import '../app_colors.dart'; 
import 'parkinson_detail_screen.dart';

class EducationScreen extends StatelessWidget {
  const EducationScreen({super.key});

  @override
  Widget build(BuildContext context) {
    // Get screen height to scale layout dynamically
    final double screenHeight = MediaQuery.of(context).size.height;
    final bool isSmallScreen = screenHeight < 700; 

    return Scaffold(
      backgroundColor: AppColors.background, 
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppColors.mainTeal),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          'Education',
          style: TextStyle(
            color: AppColors.mainTeal, 
            fontSize: 22,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: SafeArea(
        child: LayoutBuilder(
          builder: (context, constraints) {
            return SingleChildScrollView(
              // Allow scrolling ONLY if the screen is really small
              physics: const ClampingScrollPhysics(), 
              child: ConstrainedBox(
                constraints: BoxConstraints(
                  minHeight: constraints.maxHeight,
                ),
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24.0, vertical: 10),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween, // 🚀 Distribute space to fill screen
                    children: [
                      // --- Top Illustration ---
                      // Icon size adapts: 60 on small phones, 70 on regular
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(Icons.psychology, size: isSmallScreen ? 60 : 70, color: AppColors.mainTeal.withOpacity(0.3)),
                          const SizedBox(width: 15),
                          Icon(Icons.graphic_eq, size: isSmallScreen ? 60 : 70, color: AppColors.mainTeal.withOpacity(0.3)),
                          const SizedBox(width: 15),
                          Icon(Icons.menu_book, size: isSmallScreen ? 60 : 70, color: AppColors.mainTeal.withOpacity(0.3)),
                        ],
                      ),
                      
                      const SizedBox(height: 10),

                      // --- BIGGER CARDS Section ---
                      Column(
                        children: [
                          _buildEducationCard(
                            icon: Icons.psychology,
                            title: "What is Parkinson's?",
                            subtitle: "Understanding early signs",
                            onTap: () {
                              Navigator.push(
                                context,
                                MaterialPageRoute(builder: (context) => const ParkinsonDetailScreen()),
                              );
                            },
                          ),
                          const SizedBox(height: 12), // Small gap between cards

                          _buildEducationCard(
                            icon: Icons.graphic_eq,
                            title: "Speech Changes",
                            subtitle: "Jitter, Shimmer & Pauses",
                            onTap: () {},
                          ),
                          const SizedBox(height: 12),

                          _buildEducationCard(
                            icon: Icons.medical_services,
                            title: "When to Seek Advice",
                            subtitle: "Early intervention guide",
                            onTap: () {},
                          ),
                        ],
                      ),
                      
                      const SizedBox(height: 15),

                      // --- "Did You Know?" Box ---
                      Container(
                        padding: const EdgeInsets.all(16.0),
                        decoration: BoxDecoration(
                          color: AppColors.mainTeal.withOpacity(0.1), 
                          borderRadius: BorderRadius.circular(16),
                          border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              children: [
                                Icon(Icons.lightbulb_outline, color: AppColors.mainTeal, size: 22),
                                const SizedBox(width: 8),
                                Text(
                                  'Did You Know?',
                                  style: TextStyle(
                                    color: AppColors.mainTeal, 
                                    fontSize: 16,
                                    fontWeight: FontWeight.bold,
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 6),
                            Text(
                              'Micro-tremors in voice pitch (Jitter) often appear before physical tremors.',
                              style: TextStyle(
                                color: AppColors.textTeal, 
                                fontSize: 14,
                                height: 1.3,
                              ),
                            ),
                          ],
                        ),
                      ),
                      
                      const SizedBox(height: 10),

                      // --- Footer Text ---
                      Text(
                        'SpeakTrum is not a diagnostic tool.',
                        style: TextStyle(
                          color: AppColors.textTeal.withOpacity(0.6),
                          fontSize: 12,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 5),
                    ],
                  ),
                ),
              ),
            );
          }
        ),
      ),
    );
  }

  // --- Helper Widget (Bigger Cards) ---
  Widget _buildEducationCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Container(
      decoration: BoxDecoration(
        color: AppColors.cardColor, 
        borderRadius: BorderRadius.circular(16), 
        border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth), 
        boxShadow: [
          if (AppColors.cardColor == Colors.white)
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 3),
            ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: onTap,
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            // 🚀 INCREASED PADDING: Makes the card taller and bigger
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 22), 
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: AppColors.mainTeal.withOpacity(0.1),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(icon, color: AppColors.mainTeal, size: 28), // Slightly bigger icon
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: TextStyle(
                          color: AppColors.mainTeal, 
                          fontSize: 18, // Bigger Title
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        subtitle,
                        style: TextStyle(
                          color: AppColors.textTeal, 
                          fontSize: 14, // Readable subtitle
                        ),
                      ),
                    ],
                  ),
                ),
                Icon(Icons.arrow_forward_ios, color: AppColors.textTeal, size: 16),
              ],
            ),
          ),
        ),
      ),
    );
  }
}