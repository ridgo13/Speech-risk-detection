import 'package:flutter/material.dart';
import 'app_colors.dart'; // Rule #2: Import accessibility colors [cite: 43, 45]
import 'globals.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  int _activeView = 0; 

  void _changePage(int index) => setState(() => _activeView = index);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background, // Rule #1: Use dynamic background [cite: 40, 48]
      body: SafeArea(
        child: _buildCurrentBody(),
      ),
    );
  }

  Widget _buildCurrentBody() {
    if (_activeView == 1) {
      return _avatarPage(
        "Hey! I'm Shanique.\nHere to guide you with your assessment", 
        "NEXT", 
        2
      );
    }
    if (_activeView == 2) {
      return _avatarPage(
        "1- Please Stay in a quiet environment\n2- Hold Phone 20-30cm away from mouth\n3- Sustain the \"Ahhh\" sound clearly for 5 seconds", 
        "Start Recording", 
        0
      );
    }
    return _dashboardMain();
  }

  // --- 1. DASHBOARD VIEW ---
  Widget _dashboardMain() {
    return Column(
      children: [
        _customAppBar("Dashboard"),
        Expanded(
          child: ListView(
            padding: const EdgeInsets.symmetric(horizontal: 24),
            children: [
              _statusCard(),
              const SizedBox(height: 25),
              _recordingBtn(),
              const SizedBox(height: 25),
              _actionGrid(),
            ],
          ),
        ),
        _bottomNavBar(),
      ],
    );
  }

  // --- 2. AVATAR PAGE (Overlap-Proof Column Layout) ---
  Widget _avatarPage(String msg, String btnLabel, int nextIndex) {
    return Column(
      children: [
        _customAppBar("Before You Begin", showBack: true),
        Expanded(
          // Using a Column instead of a Stack prevents any overlap
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              // SPEECH BUBBLE
              CustomPaint(
                painter: SpeechBubblePainter(
                  color: AppColors.cardColor,
                  borderColor: AppColors.borderColor != Colors.transparent 
                      ? AppColors.borderColor 
                      : AppColors.mainTeal, // Rule #3: Use Main Teal [cite: 47]
                  borderWidth: 2.0,
                ),
                child: Container(
                  width: 320,
                  padding: const EdgeInsets.symmetric(horizontal: 22, vertical: 25), 
                  child: Text(
                    msg,
                    textAlign: TextAlign.center, 
                    style: TextStyle(
                      color: AppColors.textTeal, // Rule #3: Text Teal [cite: 49]
                      fontWeight: FontWeight.bold, 
                      fontSize: 19, 
                    ),
                  ),
                ),
              ),
              const SizedBox(height: 20), // Physical gap between bubble and face
              // AVATAR
              Expanded(
                child: Image.asset(
                  'assets/images/avatar.png',
                  fit: BoxFit.contain,
                  errorBuilder: (c, e, s) => const Icon(Icons.person, size: 150, color: Colors.grey),
                ),
              ),
            ],
          ),
        ),
        Padding(
          padding: const EdgeInsets.fromLTRB(40, 10, 40, 35),
          child: _fullWidthBtn(btnLabel, () => _changePage(nextIndex)),
        ),
      ],
    );
  }

  // --- UI COMPONENTS ---
  Widget _customAppBar(String title, {bool showBack = false}) {
    return Padding(
      padding: const EdgeInsets.all(15),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          showBack 
            ? IconButton(icon: Icon(Icons.arrow_back, color: AppColors.mainTeal), onPressed: () => _changePage(0)) 
            : const SizedBox(width: 48),
          Text(title, style: TextStyle(color: AppColors.mainTeal, fontSize: 24, fontWeight: FontWeight.bold)),
          IconButton(
            icon: Icon(Icons.settings, color: AppColors.mainTeal),
            onPressed: () => setState(() => isHighContrast.value = !isHighContrast.value),
          ),
        ],
      ),
    );
  }

  Widget _statusCard() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: AppColors.cardColor, 
        borderRadius: BorderRadius.circular(20),
        border: Border.all(color: AppColors.borderColor, width: AppColors.borderWidth),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("Last Voice Screening", style: TextStyle(color: AppColors.textTeal, fontWeight: FontWeight.bold, fontSize: 18)),
          const Text("12 March 2025", style: TextStyle(color: Colors.grey, fontSize: 14)),
          const SizedBox(height: 12),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
            decoration: BoxDecoration(color: const Color(0xFFFFD166), borderRadius: BorderRadius.circular(20)),
            child: const Text("Moderate", style: TextStyle(fontWeight: FontWeight.bold, color: Colors.black)),
          ),
        ],
      ),
    );
  }

  Widget _recordingBtn() {
    return SizedBox(
      width: double.infinity,
      height: 105,
      child: ElevatedButton(
        onPressed: () => _changePage(1),
        style: ElevatedButton.styleFrom(
          backgroundColor: AppColors.mainTeal, 
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        ),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: const [
            Icon(Icons.graphic_eq, color: Colors.white, size: 40),
            Text("Start Voice Recording", style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 18)),
          ],
        ),
      ),
    );
  }

  Widget _actionGrid() {
    return GridView.count(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      crossAxisCount: 2,
      crossAxisSpacing: 18,
      mainAxisSpacing: 18,
      childAspectRatio: 1.35, 
      children: [
        _gridBox("Result History", Icons.description),
        _gridBox("Progress Tracking", Icons.insert_chart),
        _gridBox("Learn More", Icons.menu_book),
        _gridBox("Privacy & Data", Icons.lock),
      ],
    );
  }

  Widget _gridBox(String t, IconData i) {
    return Container(
      decoration: BoxDecoration(color: AppColors.mainTeal, borderRadius: BorderRadius.circular(20)),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(i, color: Colors.white, size: 30),
          const SizedBox(height: 5),
          Text(t, textAlign: TextAlign.center, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 13)),
        ],
      ),
    );
  }

  Widget _fullWidthBtn(String t, VoidCallback a) {
    return SizedBox(
      width: double.infinity,
      height: 60,
      child: ElevatedButton(
        onPressed: a, 
        style: ElevatedButton.styleFrom(backgroundColor: AppColors.mainTeal, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15))),
        child: Text(t, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20)),
      ),
    );
  }

  Widget _bottomNavBar() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 20),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          Icon(Icons.home, size: 32, color: AppColors.cardTextColor), 
          const Icon(Icons.search, size: 32, color: Colors.grey),
          const Icon(Icons.person_outline, size: 32, color: Colors.grey),
        ],
      ),
    );
  }
}

// --- FIGMA SPEECH BUBBLE SHAPE ---
class SpeechBubblePainter extends CustomPainter {
  final Color color;
  final Color borderColor;
  final double borderWidth;

  SpeechBubblePainter({required this.color, required this.borderColor, required this.borderWidth});

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = color..style = PaintingStyle.fill;
    final borderPaint = Paint()..color = borderColor..style = PaintingStyle.stroke..strokeWidth = borderWidth;

    final path = Path()
      ..addRRect(RRect.fromRectAndRadius(Rect.fromLTWH(0, 0, size.width, size.height), const Radius.circular(35)))
      // Pointy tail pointing down
      ..moveTo(size.width * 0.25, size.height)
      ..lineTo(size.width * 0.20, size.height + 15)
      ..lineTo(size.width * 0.35, size.height)
      ..close();

    canvas.drawPath(path, paint);
    if (borderWidth > 0) canvas.drawPath(path, borderPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}