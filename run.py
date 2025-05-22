from app import create_app, db
from app.models import User, Pendaftaran, Berkas, Pembayaran, Pengumuman, KategoriPengumuman
from datetime import datetime
from flask.json.provider import DefaultJSONProvider
from decimal import Decimal
from sqlalchemy import case
import logging
import inspect


# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        try:
            if isinstance(obj, datetime):
                return obj.strftime('%Y-%m-%d %H:%M:%S')
            elif isinstance(obj, Decimal):
                return float(obj)
            elif inspect.isfunction(obj) or inspect.ismethod(obj):
                return None  # Skip functions and methods
            elif callable(obj):
                return None  # Skip other callable objects
            elif hasattr(obj, '__dict__'):
                # Convert model objects to basic dict excluding methods
                return {k: v for k, v in obj.__dict__.items() 
                       if not callable(v) and not k.startswith('_')}
            return super().default(obj)
        except Exception as e:
            logger.error(f"JSON serialization error: {e}")
            return None

app = create_app()
app.json_provider_class = CustomJSONProvider

# Initialize kategori pengumuman
def init_kategori():
    with app.app_context():
        try:
            kategori_list = ['Penting', 'Info', 'Pengumuman']
            for nama in kategori_list:
                if not KategoriPengumuman.query.filter_by(nama=nama).first():
                    kategori = KategoriPengumuman(nama=nama)
                    db.session.add(kategori)
            db.session.commit()
            logger.info('Kategori pengumuman berhasil diinisialisasi')
        except Exception as e:
            db.session.rollback()
            logger.error(f'Error initializing kategori: {str(e)}')

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Pendaftaran': Pendaftaran,
        'Berkas': Berkas, 
        'Pembayaran': Pembayaran,
        'Pengumuman': Pengumuman,
        'KategoriPengumuman': KategoriPengumuman
    }

if __name__ == '__main__':
    init_kategori()  # Initialize kategori before running app
    app.run(debug=True)
