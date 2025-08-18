import os
from dotenv import load_dotenv
# Explicitly specify path to .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(dotenv_path)

from app import create_app
app = create_app()

if __name__ == '__main__':
    app.run(debug=True)