from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)
@app.route('/')
def home():
    return "Indian Train Running Status API is Live 🚆"

@app.route('/train')
def train():
    train_no = request.args.get('trainNo')
    date = request.args.get('date')

    url = f"https://runningstatus.in/status/{train_no}-on-{date}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    stations = []
    current_station = None
    current_delay = None
    current_pf = None

    # -----------------------------
    # CURRENT RUNNING STATION
    # -----------------------------
# -----------------------------
# CURRENT RUNNING STATION
# -----------------------------
    current_arrival = None
    current_departure = None

    current_row = soup.find("tr", class_="table-success")

    if current_row:
        cols = current_row.find_all("td")

        if len(cols) >= 4:
            # Station name
            abbr = cols[0].find("abbr")
            current_station = abbr.text.strip() if abbr else cols[0].get_text(strip=True)

            # Arrival full text
            arrival_full = cols[1].get_text(" ", strip=True)

            # Arrival delay
            arrival_delay_tag = cols[1].find("small")
            arrival_delay = arrival_delay_tag.text.strip() if arrival_delay_tag else "No Delay"

            # Clean arrival time (remove delay text)
            current_arrival = arrival_full.replace(arrival_delay, "").strip()

            # Departure full text
            departure_full = cols[2].get_text(" ", strip=True)

            # Departure delay
            departure_delay_tag = cols[2].find("small")
            departure_delay = departure_delay_tag.text.strip() if departure_delay_tag else "No Delay"

            # Clean departure time
            current_departure = departure_full.replace(departure_delay, "").strip()

            # Use arrival delay as current delay
            current_delay = arrival_delay

            # Platform
            current_pf = cols[3].get_text(strip=True)


    # -----------------------------
    # ALL STATIONS
    # -----------------------------
    rows = soup.find_all("tr")

    for row in rows:
        cols = row.find_all("td")

        if len(cols) >= 3:

            # Station name
            abbr = cols[0].find("abbr")
            station = abbr.text.strip() if abbr else cols[0].get_text(strip=True)

            # Arrival time
            arrival_text = cols[1].get_text(" ", strip=True)

            arrival_delay_tag = cols[1].find("small")
            arrival_delay = arrival_delay_tag.text.strip() if arrival_delay_tag else "No Delay"

            # Departure time
            departure_text = cols[2].get_text(" ", strip=True)

            departure_delay_tag = cols[2].find("small")
            departure_delay = departure_delay_tag.text.strip() if departure_delay_tag else "No Delay"

            current_pf = cols[3].get_text(strip=True)

            stations.append({
                "station": station,
                "arrival": arrival_text.replace(arrival_delay, "").strip(),
                "arrivalDelay": arrival_delay,
                "departure": departure_text.replace(departure_delay, "").strip(),
                "departureDelay": departure_delay,
                
            })

    return jsonify({
        "trainNo": train_no,
        "currentStation": current_station,
        "currentArrival": current_arrival,
        "currentDeparture": current_departure,
        "currentDelay": current_delay,
        "platform": current_pf,
        "stations": stations
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

