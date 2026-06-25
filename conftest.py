
from sqlalchemy import create_engine
from pytest import fixture
from models import Base
from sqlalchemy.orm import sessionmaker

@fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    yield session

    session.close()
    Base.metadata.drop_all(bind=engine)
    

