"""
appserver.py
- creates an application instance and runs the dev server
"""
from surveyapi.application import create_app
from surveyapi.models import db





app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': db}

if __name__ == '__main__':
    app.run(host='0.0.0.0')