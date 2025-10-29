from models.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    conn.commit()
    print('Columns added successfully')
