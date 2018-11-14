"""
appserver.py
- creates an application instance and runs the dev server
"""
from api import create_app, database
from api.models import Team, Lifter, Weightclass, Attempt, Competitions



app = create_app()


@app.shell_context_processor
def make_shell_context():
    return dict(db= database, app=app,
                Competitions=Competitions,
                Lifter=Lifter,
                Team=Team,
                Weightclass=Weightclass,
                Attempt=Attempt)

if __name__ == '__main__':
    app.run(host='0.0.0.0')