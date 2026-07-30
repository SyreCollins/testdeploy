from app.db.engine import init_db
from app.core.config import get_settings
from sqlmodel import Session, text

settings = get_settings()
engine = init_db(settings.database_url)

with Session(engine) as session:
    tables = session.exec(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")).all()
    for t in tables:
        count = session.exec(text(f'SELECT count(*) FROM "{t[0]}"')).one()
        print(f"  {t[0]}: {count[0]} rows")
