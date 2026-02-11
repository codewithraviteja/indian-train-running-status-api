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

    # Current running row
    current_row = soup.find("tr", class_="table-success")

    if current_row:
        cols = current_row.find_all("td")

        if len(cols) >= 4:
            abbr = cols[0].find("abbr")
            current_station = abbr.text.strip() if abbr else cols[0].text.strip()
            current_delay = cols[1].text.strip()
            current_pf = cols[3].text.strip()

    # All stations
    rows = soup.find_all("tr")

    for row in rows:
        cols = row.find_all("td")

        if len(cols) >= 3:
            station = cols[0].text.strip()
            arrival = cols[1].text.strip()
            departure = cols[2].text.strip()

            stations.append({
                "station": station,
                "arrival": arrival,
                "departure": departure
            })

    return jsonify({
        "trainNo": train_no,
        "currentStation": current_station,
        "delayInfo": current_delay,
        "platform": current_pf,
        "stations": stations
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
