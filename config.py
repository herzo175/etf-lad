import os

import dotenv


dotenv.load_dotenv()

POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))
LOOKBACK_PERIOD = int(os.getenv("LOOKBACK_PERIOD", "7"))
IEX_KEY = os.getenv("IEX_KEY")
APCA_API_KEY_ID = os.getenv("APCA_API_KEY_ID")
APCA_API_KEY_SECRET = os.getenv("APCA_API_KEY_SECRET")
APCA_ENDPOINT = os.getenv("APCA_ENDPOINT", "https://paper-api.alpaca.markets")
PICKLE_FILE_NAME = os.getenv("PICKLE_FILE_NAME", "pool.pkl")
