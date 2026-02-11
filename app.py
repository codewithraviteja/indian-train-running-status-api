from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

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

    # Find current running row using class
    current_row = soup.find("tr", class_="table-success")

    if current_row:
        cols = current_row.find_all("td")

        if len(cols) >= 4:
            # Only station name (clean)
            abbr = cols[0].find("abbr")
            if abbr:
                current_station = abbr.text.strip()
            else:
                current_station = cols[0].text.strip()

            current_delay = cols[1].text.strip()
            current_pf = cols[3].text.strip()

    # Get full route stations
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

app.run(port=5000)
