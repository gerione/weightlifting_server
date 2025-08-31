# Modify this Procfile to fit your needs
# web: gunicorn server:app

# web: gunicorn  --worker-class eventlet -w 1 appserver:app
# web: gunicorn -k gevent -w 1 appserver:app
web: flask db upgrade; gunicorn -w 2 appserver:app
# web: gunicorn appserver:app
