import 'package:flutter/material.dart';

// ==========================================
// 🎨 COLOR PALETTE (Matches your Design)
// ==========================================
class AppColors {
  static const Color kBackground = Color(0xFFF3EFE4); // Beige
  static const Color kMainTeal = Color(0xFF135D66); // Dark Teal
  static const Color kTextTeal = Color(0xFF2C6E76); // Light Teal
}

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _controller = PageController();
  int _currentPage = 0;

  // 📝 DATA FOR THE 3 SCREENS
  final List<Map<String, dynamic>> _pages = [
    {
      "icon": Icons.graphic_eq, // Voice Wave Icon
      "title": "Why We Use Voice Input",
      "text":
          "SpeakTrum analyzes voice patterns to highlight variations that may be associated with speech-related changes.\n\nIt is a supportive tool and does not provide full medical diagnoses or assessments.",
    },
    {
      "icon": Icons.psychology, // Brain/AI Icon
      "title": "How AI Supports You",
      "text":
          "SpeakTrum uses AI to analyze speech patterns and provide feedback for practice and awareness.\n\nThe AI does not make medical decisions or replace professional evaluation.",
    },
    {
      "icon": Icons.security, // Shield/Privacy Icon
      "title": "Your Privacy Comes First",
      "text":
          "Your voice data is handled securely and used only to support your experience within SpeakTrum.\n\nYou remain in control of your information, and your data is never used without your consent.",
    },
  ];

  // Function to finish onboarding and go Home
  void _completeOnboarding() {
    Navigator.pushNamedAndRemoveUntil(context, '/home', (route) => false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.kBackground,
      body: SafeArea(
        child: Column(
          children: [
            // ===========================
            // 1. TOP NAVIGATION BAR
            // ===========================
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  // Back Button (only show if not on first page)
                  IconButton(
                    icon: const Icon(
                      Icons.arrow_back,
                      color: AppColors.kMainTeal,
                    ),
                    onPressed: () {
                      if (_currentPage > 0) {
                        _controller.previousPage(
                          duration: const Duration(milliseconds: 300),
                          curve: Curves.easeInOut,
                        );
                      } else {
                        // Optional: Go back to Login if on first page
                        Navigator.pop(context);
                      }
                    },
                  ),
                  // Skip Button
                  TextButton(
                    onPressed: _completeOnboarding,
                    child: const Text(
                      "Skip",
                      style: TextStyle(
                        color: AppColors.kMainTeal,
                        fontWeight: FontWeight.bold,
                        fontSize: 16,
                      ),
                    ),
                  ),
                ],
              ),
            ),

            // ===========================
            // 2. SWIPEABLE PAGE CONTENT
            // ===========================
            Expanded(
              child: PageView.builder(
                controller: _controller,
                itemCount: _pages.length,
                onPageChanged: (index) {
                  setState(() {
                    _currentPage = index;
                  });
                },
                itemBuilder: (context, index) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 30),
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        // A. ICON
                        Icon(
                          _pages[index]['icon'],
                          size: 100,
                          color: AppColors.kMainTeal,
                        ),
                        const SizedBox(height: 40),

                        // B. TITLE
                        Text(
                          _pages[index]['title'],
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.w900, // Extra Bold
                            color: AppColors.kMainTeal,
                          ),
                        ),
                        const SizedBox(height: 30),

                        // C. WHITE CARD WITH TEXT
                        Container(
                          padding: const EdgeInsets.all(25),
                          decoration: BoxDecoration(
                            color: Colors.white,
                            borderRadius: BorderRadius.circular(
                              20,
                            ), // Rounded corners
                            boxShadow: [
                              BoxShadow(
                                color: Colors.black.withOpacity(0.1),
                                blurRadius: 10,
                                offset: const Offset(0, 5),
                              ),
                            ],
                          ),
                          child: Text(
                            _pages[index]['text'],
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              fontSize: 15,
                              color:
                                  AppColors.kTextTeal, // Teal text inside card
                              height: 1.5, // Line height for readability
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),

            // ===========================
            // 3. BOTTOM BUTTON & DOTS
            // ===========================
            Padding(
              padding: const EdgeInsets.only(bottom: 50, left: 30, right: 30),
              child: Column(
                children: [
                  // BUTTON
                  SizedBox(
                    width: 200,
                    height: 50,
                    child: ElevatedButton(
                      onPressed: () {
                        if (_currentPage == _pages.length - 1) {
                          _completeOnboarding();
                        } else {
                          _controller.nextPage(
                            duration: const Duration(milliseconds: 300),
                            curve: Curves.easeInOut,
                          );
                        }
                      },
                      style: ElevatedButton.styleFrom(
                        backgroundColor: AppColors.kMainTeal,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        elevation: 5,
                      ),
                      child: Text(
                        _currentPage == _pages.length - 1
                            ? "Get Started"
                            : "NEXT",
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Colors.white,
                        ),
                      ),
                    ),
                  ),
                  const SizedBox(height: 30),

                  // PAGINATION DOTS
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: List.generate(
                      _pages.length,
                      (index) => AnimatedContainer(
                        duration: const Duration(milliseconds: 300),
                        margin: const EdgeInsets.symmetric(horizontal: 5),
                        height: 10,
                        width: 10,
                        decoration: BoxDecoration(
                          color: _currentPage == index
                              ? AppColors.kMainTeal
                              : AppColors.kMainTeal.withOpacity(
                                  0.3,
                                ), // Dim inactive dots
                          shape: BoxShape.circle,
                        ),
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
