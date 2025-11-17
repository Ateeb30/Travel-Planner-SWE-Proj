# api/index.py
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from api_main import app

# Mangum handler for Vercel
handler = Mangum(app, lifespan="off")