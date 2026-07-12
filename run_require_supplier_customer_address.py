from sqlalchemy import text

from models.database import get_db


db = next(get_db())

try:
    # Backfill existing null or blank addresses before applying NOT NULL.
    db.execute(text("""
        UPDATE supplier
        SET alamat = 'Alamat belum diisi'
        WHERE alamat IS NULL OR btrim(alamat) = '';
    """))
    db.execute(text("""
        UPDATE customer
        SET alamat = 'Alamat belum diisi'
        WHERE alamat IS NULL OR btrim(alamat) = '';
    """))

    db.execute(text("""
        ALTER TABLE supplier
        ALTER COLUMN alamat SET NOT NULL;
    """))
    db.execute(text("""
        ALTER TABLE customer
        ALTER COLUMN alamat SET NOT NULL;
    """))

    db.commit()
    print("Supplier and customer address columns are now required.")
except Exception as e:
    db.rollback()
    print(f"Error: {e}")
finally:
    db.close()
