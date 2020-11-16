#!flask/bin/python

# Import app variable from our app package
import app.wsgi as wsgi

if __name__ == '__main__':
    # DEVELOPMENT (Internal-facing, Debug on)
    app = wsgi.create_app()
    app.app_context().push()
    app.run(debug=True, host='0.0.0.0', port=5001)
