
import sys
sys.path.insert(0, '.')
from database import Base, engine
from models import User, QueryLog

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("Database initialized successfully!")
