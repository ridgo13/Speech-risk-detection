import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:geolocator/geolocator.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:url_launcher/url_launcher.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart'; // This provides the LatLng class

void main() => runApp(const MaterialApp(
  debugShowCheckedModeBanner: false, 
  home: MapScreen()
));

class MapScreen extends StatefulWidget {
  const MapScreen({super.key});
  @override
  State<MapScreen> createState() => _MapScreenState();
}

class _MapScreenState extends State<MapScreen> {
  List _facilities = [];
  LatLng? _currentPosition;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _determinePosition();
  }

  Future<void> _determinePosition() async {
  debugPrint("--- GPS Process Started ---");
  try {
    // 1. Request GPS Permission
    LocationPermission permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied || permission == LocationPermission.deniedForever) {
      debugPrint("Location permissions are denied.");
      _useFallbackLocation(); // Move to fallback if denied
      return;
    }

    // 2. Get current coordinates with a 5-second timeout
    // If the emulator is "stuck," this will throw an error after 5s
    Position position = await Geolocator.getCurrentPosition(
      desiredAccuracy: LocationAccuracy.high,
      timeLimit: const Duration(seconds: 5), 
    );

    debugPrint("Real GPS Found: ${position.latitude}, ${position.longitude}");
    _fetchHealthcareData(position.latitude, position.longitude);

  } catch (e) {
    debugPrint("GPS Error or Timeout: $e");
    _useFallbackLocation();
  }
}

// 3. Fallback logic so you don't stay on the loading screen forever
void _useFallbackLocation() {
  debugPrint("Switching to Fallback Location: Puchong, Selangor");
  // Coordinates for Puchong: 3.0327, 101.6185
  _fetchHealthcareData(3.0327, 101.6185);
}

// 4. Fetch from your Python Backend
Future<void> _fetchHealthcareData(double lat, double lng) async {
  if (mounted) {
    setState(() {
      _currentPosition = LatLng(lat, lng);
    });
  }

  try {
    // 10.0.2.2 is the bridge to your computer's localhost
    final url = 'http://10.0.2.2:5000/nearby-healthcare?lat=$lat&lng=$lng';
    debugPrint("Calling Backend: $url");
    
    final response = await http.get(Uri.parse(url)).timeout(const Duration(seconds: 10));
    
    if (response.statusCode == 200 && mounted) {
      setState(() {
        _facilities = json.decode(response.body);
        _isLoading = false; // FINALLY STOPS THE SPINNER
      });
      debugPrint("Successfully loaded ${_facilities.length} facilities.");
    } else {
      debugPrint("Server Error: ${response.statusCode}");
      if (mounted) setState(() => _isLoading = false);
    }
  } catch (e) {
    debugPrint("Connection to Backend Failed: $e");
    if (mounted) setState(() => _isLoading = false);
  }
}

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        title: Text("Nearby Healthcare\nFacilities", 
          textAlign: TextAlign.center, 
          style: GoogleFonts.ubuntu(fontWeight: FontWeight.bold, fontSize: 18, color: const Color(0xFF1B4D4D))),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
        leading: const Icon(Icons.arrow_back, color: Color(0xFF485B5E)),
      ),
      body: _isLoading 
        ? const Center(child: CircularProgressIndicator(color: Colors.teal)) 
        : Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                // MAP CONTAINER WITH ROUNDED CORNERS
                Container(
                  height: 180,
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(20),
                    boxShadow: [BoxShadow(color: Colors.black12, blurRadius: 4)],
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: FlutterMap(
                    options: MapOptions(
                      initialCenter: _currentPosition ?? const LatLng(0, 0), 
                      initialZoom: 14
                    ),
                    children: [
                      TileLayer(urlTemplate: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png'),
                      MarkerLayer(markers: [
                        if (_currentPosition != null)
                          Marker(
                            point: _currentPosition!, 
                            child: const Icon(Icons.person_pin_circle, color: Colors.blue, size: 40)
                          ),
                        ..._facilities.map((f) => Marker(
                          point: LatLng(f['lat'], f['lng']),
                          child: const Icon(Icons.location_on, color: Colors.red),
                        )),
                      ]),
                    ],
                  ),
                ),
                const SizedBox(height: 20),
                Expanded(
                  child: ListView.builder(
                    itemCount: _facilities.length,
                    itemBuilder: (context, index) => _FacilityItem(data: _facilities[index]),
                  ),
                ),
              ],
            ),
          ),
    );
  }
}

class _FacilityItem extends StatelessWidget {
  final Map data;
  const _FacilityItem({required this.data});

  @override
  Widget build(BuildContext context) {
    // Define your logic colors here
    const Color greenTheme = Colors.green;
    const Color blueTheme = Color(0xFF004A7C);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(data['name'] ?? "Unknown Facility", 
          style: GoogleFonts.ubuntu(fontWeight: FontWeight.bold, fontSize: 18, color: const Color(0xFF1B4D4D))),
        const SizedBox(height: 4),
        Text(
          "${data['rating']} ★ (${data['reviews']}) - ${data['type']}\nOpen 24 hours - ${data['address']}",
          style: GoogleFonts.ubuntu(fontSize: 12, fontWeight: FontWeight.bold, color: const Color(0xFF485B5E)),
        ),
        const SizedBox(height: 12),
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            // CALL BUTTON (Hidden if no number)
            if (data['phone'] != null)
              _ActionButton(
                label: "Call", 
                color: greenTheme, 
                icon: Icons.phone, 
                onPressed: () => launchUrl(Uri.parse("tel:${data['phone']}"))
              ),
            
            const SizedBox(width: 8),

            // DIRECTIONS BUTTON (Always show)
            _ActionButton(
              label: "Directions", 
              color: greenTheme, 
              icon: Icons.directions,
              onPressed: () => launchUrl(Uri.parse("https://www.google.com/maps/search/?api=1&query=${data['lat']},${data['lng']}"))
            ),

            const SizedBox(width: 8),

            // WEBSITE BUTTON (Hidden if no website)
            if (data['website'] != null)
              _ActionButton(
                label: "Website", 
                color: blueTheme, 
                icon: Icons.language,
                onPressed: () => launchUrl(Uri.parse(data['website']))
              ),
          ],
        ),
        const Divider(height: 40),
      ],
    );
  }
}

class _ActionButton extends StatelessWidget {
  final String label;
  final Color color;
  final IconData icon;
  final VoidCallback onPressed;

  const _ActionButton({
    required this.label, 
    required this.color, 
    required this.icon, 
    required this.onPressed
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          side: BorderSide(color: color),
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
          padding: const EdgeInsets.symmetric(vertical: 8),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 4),
            Text(label, style: GoogleFonts.ubuntu(color: color, fontWeight: FontWeight.bold, fontSize: 11)),
          ],
        ),
      ),
    );
  }
}