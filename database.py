from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Intenta obtener la URL de la variable de entorno, si no existe usa un valor por defecto
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:WBvpQkJFuufMCnhVukvyxlttdUMmINYb@postgres.railway.internal:5432/railway")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()