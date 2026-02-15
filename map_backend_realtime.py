from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

@app.route('/nearby-healthcare', methods=['GET'])
def get_nearby_healthcare():
    # 1. Get coordinates from the Flutter app request
    lat = request.args.get('lat')
    lng = request.args.get('lng')
    
    if not lat or not lng:
        return jsonify({"error": "Missing coordinates"}), 400

    # 2. Real-time Overpass API Query
    # [out:json] = return data in JSON format
    # (around:5000, {lat}, {lng}) = search within 5000 meters of the user
    overpass_url = "https://overpass-api.de/api/interpreter"
    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"~"hospital|clinic"](around:5000,{lat},{lng});
      way["amenity"~"hospital|clinic"](around:5000,{lat},{lng});
    );
    out center;
    """
    
    try:
        response = requests.get(overpass_url, params={'data': query})
        data = response.json()
        
        real_time_results = []
        for element in data.get('elements', []):
            tags = element.get('tags', {})
            # Get coordinates (Overpass 'center' for ways, or 'lat/lon' for nodes)
            h_lat = element.get('lat') or element.get('center', {}).get('lat')
            h_lng = element.get('lon') or element.get('center', {}).get('lon')
            
            real_time_results.append({
                "name": tags.get("name", "Healthcare Facility"),
                "type": tags.get("amenity", "Health").capitalize(),
                "address": tags.get("addr:street", "Nearby Area"),
                "phone": tags.get("phone") or tags.get("contact:phone"), # Real phone from OSM
                "website": tags.get("website") or tags.get("contact:website"), # Real web from OSM
                "lat": h_lat,
                "lng": h_lng,
                "status": "Open", # OSM status can be complex, using a default
                "rating": "4.5", # OSM doesn't have ratings like Google
                "reviews": "100"
            })
            
        return jsonify(real_time_results)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Use 0.0.0.0 so your mobile emulator can reach the server
    app.run(debug=True, host='0.0.0.0', port=5000)