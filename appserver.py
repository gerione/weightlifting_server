"""
appserver.py
- creates an application instance and runs the dev server
"""
from surveyapi import create_app, database




app = create_app()


@app.shell_context_processor
def make_shell_context():
    return {'db': database}

if __name__ == '__main__':
    app.run(host='0.0.0.0')