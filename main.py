from logger import logger
from models import *
from database import engine
from crud import *
from database import engine, session

db = session()
Base.metadata.create_all(bind=engine)
