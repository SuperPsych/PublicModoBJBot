from mitmproxy import http
import json

# Change this to your preferred log file location
TARGET_URL = "https://run.steam-powered-games.com/fullstate/html5/evoplay/blackjack/?operator=6223"

play = None  # Global variable to store the parsed JSON response

def response(flow: http.HTTPFlow) -> None:
    global play  # Declare play as global to update it inside the function

    if flow.request.pretty_url == TARGET_URL:
        # Parse the response body as JSON and store it in the variable 'play'
        try:
            play = json.loads(flow.response.text)  # Parse JSON from the response body
            with open("play_data.json", "w") as json_file:
                json.dump(play, json_file, indent=4)
            print(f"Stored response JSON in 'play': {play}")  # Print the JSON to verify
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            play = None  # Handle case where response is not valid JSON