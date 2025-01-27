from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Usar la URL pública correcta
DATABASE_URL = os.getenv("DATABASE_PUBLIC_URL", "postgresql://postgres:WBvpQkJFuufMCnhVukvyxlttdUMmINYb@junction.proxy.rlwy.net:51532/railway")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()