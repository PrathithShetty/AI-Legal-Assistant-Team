"""Start the app:  python run.py   then open http://127.0.0.1:5000"""
from dotenv import load_dotenv

load_dotenv()  # read settings from .env before the app config is imported

from legal_assistant import create_app  # noqa: E402

app = create_app()

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
