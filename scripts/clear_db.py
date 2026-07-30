from app.db.engine import init_db
from app.core.config import get_settings
from sqlmodel import Session, text

settings = get_settings()
engine = init_db(settings.database_url)

with Session(engine) as session:
    tables = session.exec(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).all()
    table_names = [t[0] for t in tables]
    print("Tables to clear:", table_names)
    for t in table_names:
        session.exec(text(f'TRUNCATE TABLE "{t}" CASCADE'))
    session.commit()
    print("All tables cleared.")
