import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../app_colors.dart';
import '../globals.dart';

// We change this to a StatefulWidget to manage the chat history
class InAppChatScreen extends StatefulWidget {
  const InAppChatScreen({super.key});

  @override
  State<InAppChatScreen> createState() => _InAppChatScreenState();
}

class _InAppChatScreenState extends State<InAppChatScreen> {
  // 1. Define the Chat History
  final List<Map<String, dynamic>> _messages = [
    {
      "text": "Hello! I'm the SpeakTrum Assistant. How can I help you today?",
      "isUser": false,
    },
  ];

  // 2. Define Pre-defined Issues and Answers
  final List<Map<String, String>> _options = [
    {"q": "How to record my voice?", "a": "To record, go to the Home screen and tap the 'Start Voice Recording' option. Follow the on-screen prompts given by the avatar to complete the session."},
    {"q": "Is my data private?", "a": "Yes! All recordings are encrypted and stored securely. We never share your data with third parties."},
    {"q": "App is crashing", "a": "We're sorry to hear that. Please ensure you have the latest update from the Play Store or try restarting your device."},
    {"q": "How to see results?", "a": "Your analysis results will appear in the 'Result Summary' tab once the AI has finished processing your voice sample it will automatically redirect you to that tab, you can also access your previous or current results from the 'Result History' option from the main Dashboard."},
  ];

  // 3. Logic to handle user selecting an option
  void _handleOptionTap(String question, String answer) {
    setState(() {
      // Add user's question to chat
      _messages.add({"text": question, "isUser": true});
      
      // Add app's response after a tiny delay to feel natural
      Future.delayed(const Duration(milliseconds: 500), () {
        setState(() {
          _messages.add({"text": answer, "isUser": false});
        });
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final Color contentColor = isHighContrast.value ? AppColors.cardTextColor : AppColors.textTeal;

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
        leading: IconButton(
          icon: Icon(Icons.arrow_back, color: AppColors.textTeal),
          onPressed: () => Navigator.pop(context),
        ),
        title: Text(
          "Chat Support",
          style: GoogleFonts.ubuntu(
            color: AppColors.textTeal,
            fontWeight: FontWeight.bold,
            fontSize: 24,
          ),
        ),
      ),
      body: Column(
        children: [
          // --- CHAT MESSAGES AREA ---
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final msg = _messages[index];
                return _ChatBubble(
                  text: msg["text"],
                  isUser: msg["isUser"],
                  contentColor: contentColor,
                );
              },
            ),
          ),

          // --- QUICK REPLY OPTIONS ---
          Container(
            padding: const EdgeInsets.symmetric(vertical: 10),
            child: Column(
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Text(
                    "Select an issue or type below:",
                    style: GoogleFonts.ubuntu(
                      color: AppColors.textTeal,
                      fontWeight: FontWeight.bold,
                      fontSize: 14,
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                SizedBox(
                  height: 45,
                  child: ListView.builder(
                    scrollDirection: Axis.horizontal,
                    padding: const EdgeInsets.symmetric(horizontal: 12),
                    itemCount: _options.length,
                    itemBuilder: (context, index) {
                      return Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 4),
                        child: ActionChip(
                          backgroundColor: AppColors.mainTeal,
                          label: Text(
                            _options[index]["q"]!,
                            style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
                          ),
                          onPressed: () => _handleOptionTap(_options[index]["q"]!, _options[index]["a"]!),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),

          // --- FUTURE PROOF INPUT FIELD ---
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.white,
              boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 4)],
            ),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    enabled: false, // Disabled for now (Future proof)
                    decoration: InputDecoration(
                      hintText: "Live Chat & AI Coming Soon...",
                      hintStyle: GoogleFonts.ubuntu(fontWeight: FontWeight.bold),
                      border: OutlineInputBorder(borderRadius: BorderRadius.circular(30)),
                      contentPadding: const EdgeInsets.symmetric(horizontal: 20),
                    ),
                  ),
                ),
                const SizedBox(width: 10),
                CircleAvatar(
                  backgroundColor: AppColors.textTeal.withOpacity(0.5),
                  child: const Icon(Icons.send, color: Colors.white),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

// --- SUB-WIDGET: CHAT BUBBLE ---
class _ChatBubble extends StatelessWidget {
  final String text;
  final bool isUser;
  final Color contentColor;

  const _ChatBubble({required this.text, required this.isUser, required this.contentColor});

  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        decoration: BoxDecoration(
          color: isUser ? AppColors.mainTeal : Colors.white,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isUser ? 16 : 0),
            bottomRight: Radius.circular(isUser ? 0 : 16),
          ),
          border: isUser ? null : Border.all(color: AppColors.textTeal.withOpacity(0.2)),
        ),
        child: Text(
          text,
          style: GoogleFonts.ubuntu(
            fontWeight: FontWeight.bold,
            color: isUser ? Colors.white : AppColors.textTeal,
            fontSize: 15,
          ),
        ),
      ),
    );
  }
}