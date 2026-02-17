import 'package:shared_preferences/shared_preferences.dart';

class PreferencesService {
  // 🔑 Keys
  static const String weeklyReminderKey = "weekly_reminder_enabled";
  static const String lastScreeningKey = "last_screening_date";

  // ================================
  // WEEKLY REMINDER
  // ================================

  Future<void> setWeeklyReminderEnabled(bool value) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(weeklyReminderKey, value);
  }

  Future<bool> isWeeklyReminderEnabled() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getBool(weeklyReminderKey) ?? false;
  }

  // ================================
  // LAST SCREENING DATE (optional future use)
  // ================================

  Future<void> setLastScreeningDate(String date) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(lastScreeningKey, date);
  }

  Future<String?> getLastScreeningDate() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(lastScreeningKey);
  }
}
