from app import create_app, db
from app.models import User
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User}

if __name__ == "__main__":
    logger.info('Starting application...')
    app.run(debug=True, port=5000)
