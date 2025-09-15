from models.database import Base, engine
from models.customer import Customer, Vehicle

if __name__ == "__main__":
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done.")
