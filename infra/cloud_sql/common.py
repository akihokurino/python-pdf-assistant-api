import os

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from infra import secret_manager

if os.getenv("IS_LOCAL", "") == "true":
    DATABASE_URL = "mysql+pymysql://root:root@localhost/app"
else:
    DATABASE_URL = secret_manager.get_secret("cloud-sql-connection", "latest")

Base = declarative_base()
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
