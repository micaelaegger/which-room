import os
from dotenv import load_dotenv

load_dotenv()
url = os.getenv("TIME_EDIT_URL")

print(url)
