# slot-sorter/run.py
import webbrowser
from threading import Timer
from slot_sorter import create_app

# Configuration
HOST = 'localhost'
PORT = 8000
URL = f"http://{HOST}:{PORT}"

app = create_app()

def open_browser():
    """Opens the default web browser to the application's URL."""
    webbrowser.open(URL)

if __name__ == '__main__':
    # Run the browser-opening function on a timer 1 second after starting the server
    Timer(1, open_browser).start()
    # Run the Flask app
    app.run(host=HOST, port=PORT, debug=True)