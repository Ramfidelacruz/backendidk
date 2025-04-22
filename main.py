from fastapi import FastAPI, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List
import models
import schemas
from fastapi.middleware.cors import CORSMiddleware
from database import SessionLocal, engine
import jwt
from passlib.context import CryptContext
from football_api import get_champions_matches, get_team_matches, get_upcoming_matches, get_available_teams, get_future_matches, get_team_detailed_stats, predict_match
import random




models.Base.metadata.create_all(bind=engine)

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "tu_clave_secreta"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://frontpredicciones-production.up.railway.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)                                     

@app.get("/matches/")
async def get_matches():
    return get_champions_matches()

@app.get("/matches/formatted/")
async def get_formatted_matches():
    return get_formatted_matches()

@app.get("/matches/upcoming")
async def upcoming_matches():
    return get_upcoming_matches()

@app.get("/matches/team/{team_name}")
async def team_matches(team_name: str):
    return get_team_matches(team_name)

@app.get("/teams/")
async def available_teams():
    teams = get_available_teams()
    return [
        {
            "id": index,
            "name": team,
            "points": 0
        } for index, team in enumerate(teams)
    ]

@app.get("/probabilities/")
def get_probabilities(teams: List[str] = Query(...)):
    # Simulación de partidos y probabilidades
    matches = []
    for i in range(len(teams)):
        for j in range(i + 1, len(teams)):
            home_team = teams[i]
            away_team = teams[j]
            # Generar probabilidades aleatorias para la simulación
            home_win_probability = random.uniform(30, 70)
            away_win_probability = 100 - home_win_probability
            matches.append({
                "homeTeam": home_team,
                "awayTeam": away_team,
                "probabilidad_victoria_local": round(home_win_probability, 2),
                "probabilidad_victoria_visitante": round(away_win_probability, 2)
            })
    return matches

@app.get("/predict/{home_team}/{away_team}")
async def predict_match_endpoint(home_team: str, away_team: str):
    prediction = predict_match(home_team, away_team)  # Asegúrate de que esto esté correcto
    return prediction

@app.get("/matches/future/")
async def future_matches():
    return get_future_matches()


@app.get("/team/stats/{team_name}")
async def team_stats(team_name: str):
    return get_team_detailed_stats(team_name)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    print(f"Solicitud para crear usuario: {user.email}")
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    print(f"Usuario creado: {db_user.email}")
    return db_user

@app.post("/token/")
def login(user_credentials: schemas.UserLogin, db: Session = Depends(get_db)):
    print(f"Intento de inicio de sesión para: {user_credentials.email}")
    user = db.query(models.User).filter(models.User.email == user_credentials.email).first()
    if not user or not pwd_context.verify(user_credentials.password, user.hashed_password):
        print("Credenciales incorrectas")
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    
    access_token = create_access_token(data={"sub": user.email})
    print(f"Inicio de sesión exitoso para: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/predictions/", response_model=schemas.Prediction)
def create_prediction(prediction: schemas.PredictionCreate, db: Session = Depends(get_db)):
    db_prediction = models.Prediction(**prediction.dict())
    db.add(db_prediction)
    db.commit()
    db.refresh(db_prediction)
    return db_prediction

@app.post("/reset-password/")
def reset_password(reset_data: schemas.PasswordReset, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == reset_data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    hashed_password = pwd_context.hash(reset_data.new_password)
    user.hashed_password = hashed_password
    db.commit()
    return {"message": "Contraseña actualizada"}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")
    return encoded_jwt