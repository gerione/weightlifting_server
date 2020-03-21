# web: flask db upgrade; gunicorn appserver:app
web: flask db upgrade; gunicorn  --worker-class eventlet -w 1 appserver:app