# Application entry point
import os
from app import create_app
from config import Config

# Create app with the proper configuration
app = create_app(Config)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)