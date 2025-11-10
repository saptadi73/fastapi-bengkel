from models.database import Base, engine
from sqlalchemy.schema import CreateTable
import models

# Get all tables in order
tables = Base.metadata.sorted_tables

# Generate CREATE TABLE statements
with open('database_baru/full_schema.sql', 'w') as f:
    for table in tables:
        create_stmt = str(CreateTable(table).compile(engine))
        f.write(create_stmt + ';\n\n')
    print("Full schema SQL generated in database_baru/full_schema.sql")
