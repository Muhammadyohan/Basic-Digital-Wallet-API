from sqlmodel import create_engine, Session

connect_args = {}

engine = create_engine(
    "postgresql+pg8000://postgres:123456@localhost/DigitalWalletDB",
    connect_args=connect_args,
)


def get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()
