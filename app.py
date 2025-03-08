from flask import Flask, render_template, request
import requests
from geopy.distance import geodesic

app = Flask(__name__)

# Your OpenCage API Key
api_key = 'd653cb4efaac4d62b692d2d2f4c09e44'

# List of clinic addresses
clinic_addresses = [
    "3367 South Mercy Road, Suite 205. Gilbert, AZ 85297",
    "8573 E. San Alberto, Suite E-100, Scottsdale, AZ 85258",
    "9150 W Indian School Road Suite 127, Phoenix, AZ 85037",
    "9827 N 95th Street, Suite 105, Scottsdale, AZ 85258",
    "7425 E Shea Blvd, Suite 101, Scottsdale, AZ 85260",
    "4824 E. Baseline Road, Suite 3-125, Mesa, AZ 85206",
    "4735 E. Union Hills Drive, Phoenix, AZ 85050",
    "4434 N 12th Street, Phoenix, AZ 85014",
    "13065 W McDowell Rd. Suite C130, Avondale, AZ 85392",
    "7205 S 51st Avenue, Suite 102, Laveen, AZ 85339",
    "4700 N 51st. Avenue, Suite 4, Phoenix, AZ 85031",
    "26224 N Tatum Blvd, Suite 1, Phoenix, AZ 85050",
    "14239 W. Bell Road, Suite 12. Surprise, AZ 85374"
]

def get_coordinates(address):
    # Using OpenCage API to get coordinates
    url = f'https://api.opencagedata.com/geocode/v1/json?q={address}&key={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if data['results']:
        lat = data['results'][0]['geometry']['lat']
        lng = data['results'][0]['geometry']['lng']
        return lat, lng
    else:
        return None, None

def find_closest_clinic(patient_address):
    lat_patient, lng_patient = get_coordinates(patient_address)
    
    if lat_patient is None or lng_patient is None:
        print("Could not get coordinates for the address.")
        return None

    # Create a DataFrame with clinic addresses and calculate distances
    distances = []
    for clinic_address in clinic_addresses:
        lat_clinic, lng_clinic = get_coordinates(clinic_address)
        if lat_clinic is not None and lng_clinic is not None:
            distance_km = geodesic((lat_patient, lng_patient), (lat_clinic, lng_clinic)).km
            distance_miles = distance_km * 0.621371  # Convert km to miles
            distances.append((clinic_address, distance_miles))
        else:
            distances.append((clinic_address, float('inf')))  # If coordinates can't be obtained

    # Sort distances to find the closest one
    distances.sort(key=lambda x: x[1])
    return distances[0]

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        patient_address = request.form['address']
        clinic, distance = find_closest_clinic(patient_address)

        if clinic:
            return render_template("index.html", clinic=clinic, distance=f"{distance:.2f} miles")
        else:
            return render_template("index.html", error="Could not find a nearby clinic.")

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
