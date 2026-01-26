import 'package:flutter/material.dart';
import 'app_colors.dart';
import 'globals.dart';

class OnboardingFlow extends StatefulWidget {
  final VoidCallback onFinish;
  const OnboardingFlow({super.key, required this.onFinish});

  @override
  State<OnboardingFlow> createState() => _OnboardingFlowState();
}

class _OnboardingFlowState extends State<OnboardingFlow> {
  int _step = 1; 

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppColors.mainTeal),
          onPressed: () => _step == 1 ? widget.onFinish() : setState(() => _step = 1),
        ),
        title: Text("Before You Begin", style: TextStyle(color: AppColors.mainTeal, fontWeight: FontWeight.bold)),
        centerTitle: true,
      ),
      body: Column(
        children: [
          Expanded(
            child: Stack(
              alignment: Alignment.center,
              children: [
                Positioned(
                  bottom: 0,
                  child: Image.asset(
                    'assets/images/avatar.png',
                    height: 400,
                    errorBuilder: (context, error, stackTrace) => const Icon(Icons.person, size: 200, color: Colors.grey),
                  ),
                ),
                Positioned(
                  top: 40,
                  child: Container(
                    width: 300,
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: AppColors.cardColor,
                      borderRadius: BorderRadius.circular(30),
                      border: Border.all(color: AppColors.mainTeal, width: 2),
                    ),
                    child: Text(
                      _step == 1 
                        ? "Hey! I'm Shanique.\nHere to guide you with your assessment"
                        : "1- Stay in a quiet environment\n2- Hold Phone 20-30cm away\n3- Sustain 'Ahhh' for 5 seconds",
                      textAlign: TextAlign.center,
                      style: TextStyle(color: AppColors.textTeal, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),
          ),
          Padding(
            padding: const EdgeInsets.all(30.0),
            child: SizedBox(
              width: double.infinity,
              height: 55,
              child: ElevatedButton(
                onPressed: () => _step == 1 ? setState(() => _step = 2) : print("Start Recording"),
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.mainTeal, shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(15))),
                child: Text(_step == 1 ? "NEXT" : "Start Recording", style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold)),
              ),
            ),
          ),
        ],
      ),
    );
  }
}