import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
load_dotenv()

import server

server.run()