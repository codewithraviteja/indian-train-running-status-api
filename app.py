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
    current_arrival = None
    current_departure = None

    # -----------------------------
    # CURRENT RUNNING STATION
    # -----------------------------
    current_row = soup.find("tr", class_="table-success")

    if current_row:
        cols = current_row.find_all("td")

        if len(cols) >= 4:
            # Station name
            abbr = cols[0].find("abbr")
            current_station = abbr.text.strip() if abbr else cols[0].get_text(strip=True)

            # Arrival
            arrival_full = cols[1].get_text(" ", strip=True)
            arrival_delay_tag = cols[1].find("small")
            arrival_delay = arrival_delay_tag.text.strip() if arrival_delay_tag else "No Delay"
            current_arrival = arrival_full.replace(arrival_delay, "").strip()

            # Departure
            departure_full = cols[2].get_text(" ", strip=True)
            departure_delay_tag = cols[2].find("small")
            departure_delay = departure_delay_tag.text.strip() if departure_delay_tag else "No Delay"
            current_departure = departure_full.replace(departure_delay, "").strip()

            current_delay = arrival_delay
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

            # Arrival
            arrival_text = cols[1].get_text(" ", strip=True)
            arrival_delay_tag = cols[1].find("small")
            arrival_delay = arrival_delay_tag.text.strip() if arrival_delay_tag else "No Delay"

            # Departure
            departure_text = cols[2].get_text(" ", strip=True)
            departure_delay_tag = cols[2].find("small")
            departure_delay = departure_delay_tag.text.strip() if departure_delay_tag else "No Delay"

            stations.append({
                "station": station,
                "arrival": arrival_text.replace(arrival_delay, "").strip(),
                "arrivalDelay": arrival_delay,
                "departure": departure_text.replace(departure_delay, "").strip(),
                "departureDelay": departure_delay
            })

    # -----------------------------
    # ADD STATUS FIELD
    # -----------------------------
    current_index = None

    for i, s in enumerate(stations):
        if current_station and s["station"].strip().lower() == current_station.strip().lower():
            current_index = i
            break

    if current_index is not None:
        for i, s in enumerate(stations):
            if i < current_index:
                s["status"] = "departed"
            elif i == current_index:
                s["status"] = "current"
            else:
                s["status"] = "upcoming"
    else:
        for s in stations:
            s["status"] = "unknown"

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


