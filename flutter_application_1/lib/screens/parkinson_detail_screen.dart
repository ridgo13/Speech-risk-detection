import 'package:flutter/material.dart';
import '../app_colors.dart'; 

class ParkinsonDetailScreen extends StatelessWidget {
  const ParkinsonDetailScreen({super.key});

  @override
  Widget build(BuildContext context) {
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
          "What is Parkinson's?",
          style: TextStyle(
            color: AppColors.mainTeal, 
            fontSize: 20,
            fontWeight: FontWeight.bold,
          ),
        ),
        centerTitle: true,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // --- Top Definition Box ---
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: AppColors.cardColor, 
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth),
                boxShadow: [
                  if (AppColors.cardColor == Colors.white && AppColors.background != Colors.black)
                    BoxShadow(
                      color: Colors.black.withOpacity(0.05),
                      blurRadius: 10,
                      offset: const Offset(0, 4),
                    ),
                ],
              ),
              child: Text(
                "Parkinson’s is a progressive neurological condition that affects motor functions. It occurs when brain cells that produce dopamine begin to decline, leading to changes in movement and speech.",
                style: TextStyle(
                  color: AppColors.cardTextColor, 
                  fontSize: 16,
                  height: 1.5, 
                ),
              ),
            ),

            const SizedBox(height: 30),

            Text(
              'WHY VOICE MATTERS',
              style: TextStyle(
                color: AppColors.mainTeal, 
                fontSize: 14,
                fontWeight: FontWeight.bold,
                letterSpacing: 1.2, 
              ),
            ),

            const SizedBox(height: 15),

            // --- Card 1: Early Detection ---
            _buildFeatureCard(
              title: "Early Detection",
              description: "Changes in tone and pitch often appear years before physical tremors.",
              imagePath: "assets/images/voice_icon.png", 
            ),

            const SizedBox(height: 15),

            // --- Card 2: AI Analysis ---
            _buildFeatureCard(
              title: "AI Analysis",
              description: 'SpeakTrum detects "invisible" variations like Jitter (pitch) and Shimmer (volume).',
              imagePath: "assets/images/microscope_icon.png", 
            ),

            const SizedBox(height: 15),

            // --- Card 3: Non-Invasive ---
            _buildFeatureCard(
              title: "Non-Invasive",
              description: "Voice screening is a low-cost, accessible way to monitor your health remotely.",
              imagePath: "assets/images/phone_icon.png", 
            ),
            
            const SizedBox(height: 30),
          ],
        ),
      ),
    );
  }

  // --- Helper Widget: Uses IMAGES now ---
  Widget _buildFeatureCard({
    required String title,
    required String description,
    required String imagePath, 
  }) {
    final Color textColor = AppColors.cardTextColor;

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.cardColor, 
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth),
        boxShadow: [
           if (AppColors.cardColor == Colors.white && AppColors.background != Colors.black)
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            ),
        ],
      ),
      child: Row(
        // ✅ FIXED: Changed from .start to .center to align images vertically
        crossAxisAlignment: CrossAxisAlignment.center, 
        children: [
          // ✅ IMAGE DISPLAY
          Container(
             decoration: BoxDecoration(
               shape: BoxShape.circle,
               border: Border.all(color: Colors.transparent, width: 0), 
             ),
             child: ClipOval(
               child: Image.asset(
                 imagePath,
                 width: 50, 
                 height: 50,
                 fit: BoxFit.cover,
                 errorBuilder: (context, error, stackTrace) {
                   return const Icon(Icons.image_not_supported, color: Colors.grey); 
                 },
               ),
             ),
          ),
          const SizedBox(width: 15),
          
          // Text Content
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  title,
                  style: TextStyle(
                    color: textColor,
                    fontWeight: FontWeight.bold,
                    fontSize: 16,
                  ),
                ),
                const SizedBox(height: 5),
                Text(
                  description,
                  style: TextStyle(
                    color: textColor.withOpacity(0.8),
                    fontSize: 14,
                    height: 1.4,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}