# check_wo.py
from models.database import SessionLocal
from models.workorder import Workorder
from sqlalchemy import func
from datetime import date

db = SessionLocal()
rows = db.query(Workorder).filter(func.date(Workorder.tanggal_masuk) == date(2025, 11, 9)).all()
print(f'Found {len(rows)} workorders on 2025-11-09')
for r in rows:
    print(r.id, getattr(r, 'no_wo', None), r.tanggal_masuk)
db.close()