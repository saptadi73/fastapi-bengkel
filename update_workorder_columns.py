from models.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Check if column exists before renaming
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name='workorder' AND column_name='update_pembayaran';"))
    if result.fetchone():
        conn.execute(text('ALTER TABLE workorder RENAME COLUMN update_pembayaran TO dp;'))
        print('Renamed update_pembayaran to dp')
    else:
        print('Column update_pembayaran does not exist, skipping rename')

    conn.execute(text('ALTER TABLE workorder ADD COLUMN IF NOT EXISTS next_service_date DATE;'))
    conn.execute(text('ALTER TABLE workorder ADD COLUMN IF NOT EXISTS next_service_km NUMERIC(10,2);'))
    conn.commit()
    print('Workorder columns updated successfully')
