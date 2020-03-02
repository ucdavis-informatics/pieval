#!flask/bin/python

# Import app variable from our app package
from app import app

if __name__ == '__main__':
    # DEVELOPMENT (Internal-facing, Debug on)
    app.run(debug=True, host='0.0.0.0', port=5001)
