from app.db.base import Base
from app.db.session import engine
# Import all models so Base has them registered
from app.models import User, Conversation, Participant, Message, ModerationLog

def init_db():
    print("Initializing Database Tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database Tables Created Successfully.")
    except Exception as e:
        print(f"Error creating database tables: {e}")
