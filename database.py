from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# URL de la base de datos directamente en el código, se volvio a la urloriginal

DATABASE_URL = "postgresql://postgres:GrVAydIjIxIJvmVZgNBkAaHpVRmkIotr@autorack.proxy.rlwy.net:36139/railway"

# Asegurarse de usar postgresql:// en lugar de postgres://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()