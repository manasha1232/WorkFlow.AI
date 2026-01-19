from .database import Base, engine
from .models import User, ProcessedEmail
from . import crud

def init_db():
    print("🔧 Creating database tables...")
    Base.metadata.create_all(bind=engine)
