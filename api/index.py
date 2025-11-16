# api/index.py
import sys
import os

# Add parent directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangum import Mangum
from api_main import app

# Vercel serverless handler
handler = Mangum(app)