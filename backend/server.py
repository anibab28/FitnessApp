from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone
from enum import Enum

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Enums
class ExerciseType(str, Enum):
    ABDOMINAL = "abdominal"
    PECTORAL = "pectoral"
    CARDIO = "cardio"
    FULL_BODY = "full_body"

class ExerciseLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

# Models
class Exercise(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str
    video_url: str
    exercise_type: ExerciseType
    level: ExerciseLevel
    default_duration: int  # seconds
    default_rest: int  # seconds
    default_repetitions: Optional[int] = None
    instructions: List[str]
    muscle_groups: List[str]
    equipment: List[str] = []
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class WorkoutSession(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date: str  # ISO date string
    exercises_completed: List[Dict[str, Any]]
    total_duration: int  # seconds
    difficulty_rating: Optional[int] = None  # 1-5
    energy_level: Optional[int] = None  # 1-5
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    height: Optional[float] = None  # cm
    weight: Optional[float] = None  # kg
    age: Optional[int] = None
    gender: Optional[str] = None
    fitness_level: Optional[ExerciseLevel] = None
    goals: List[str] = []
    available_equipment: List[str] = []
    preferred_duration: Optional[int] = None  # minutes
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class AbdominalMeasurement(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    measurement: float  # cm
    date: str  # ISO date string
    notes: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

# Helper function to prepare data for MongoDB
def prepare_for_mongo(data):
    if isinstance(data, dict):
        prepared = {}
        for key, value in data.items():
            if isinstance(value, datetime):
                prepared[key] = value.isoformat()
            elif isinstance(value, list):
                prepared[key] = [prepare_for_mongo(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, dict):
                prepared[key] = prepare_for_mongo(value)
            else:
                prepared[key] = value
        return prepared
    return data

# Initialize default exercises
async def initialize_exercises():
    existing_count = await db.exercises.count_documents({})
    if existing_count == 0:
        default_exercises = [
            {
                "name": "Push-up",
                "description": "Ejercicio clásico para fortalecer pectorales, tríceps y core",
                "video_url": "https://www.youtube.com/watch?v=IODxDxX7oi4",
                "exercise_type": "pectoral",
                "level": "beginner",
                "default_duration": 30,
                "default_rest": 30,
                "default_repetitions": 10,
                "instructions": [
                    "Colócate en posición de plancha con las manos separadas al ancho de los hombros",
                    "Mantén el cuerpo recto desde la cabeza hasta los talones",
                    "Baja el pecho hacia el suelo doblando los codos",
                    "Empuja hacia arriba hasta la posición inicial"
                ],
                "muscle_groups": ["Pectorales", "Tríceps", "Core"],
                "equipment": ["Colchoneta"]
            },
            {
                "name": "Russian Twist",
                "description": "Ejercicio rotacional para fortalecer oblicuos y core",
                "video_url": "https://www.youtube.com/watch?v=wkD8rjkodUI",
                "exercise_type": "abdominal",
                "level": "intermediate",
                "default_duration": 45,
                "default_rest": 25,
                "default_repetitions": 20,
                "instructions": [
                    "Siéntate en el suelo con las rodillas dobladas",
                    "Inclínate ligeramente hacia atrás manteniendo la espalda recta",
                    "Levanta los pies del suelo (opcional para mayor dificultad)",
                    "Rota el torso de lado a lado tocando el suelo con las manos"
                ],
                "muscle_groups": ["Oblicuos", "Core", "Abdominales"],
                "equipment": ["Colchoneta"]
            },
            {
                "name": "Mountain Climber",
                "description": "Ejercicio cardiovascular que fortalece core y mejora resistencia",
                "video_url": "https://www.youtube.com/watch?v=nmwgirgXLYM",
                "exercise_type": "cardio",
                "level": "intermediate",
                "default_duration": 40,
                "default_rest": 30,
                "instructions": [
                    "Comienza en posición de plancha con brazos extendidos",
                    "Lleva una rodilla hacia el pecho rápidamente",
                    "Regresa la pierna a la posición inicial",
                    "Alterna las piernas de forma rápida y continua"
                ],
                "muscle_groups": ["Core", "Hombros", "Piernas"],
                "equipment": ["Colchoneta"]
            },
            {
                "name": "Elevación de piernas y crunch abdominal",
                "description": "Combinación de ejercicios para abdomen bajo y alto",
                "video_url": "https://www.youtube.com/watch?v=JB2oyawG9KI",
                "exercise_type": "abdominal",
                "level": "beginner",
                "default_duration": 35,
                "default_rest": 25,
                "default_repetitions": 15,
                "instructions": [
                    "Acuéstate boca arriba con las manos detrás de la cabeza",
                    "Eleva las piernas rectas hacia arriba",
                    "Realiza un crunch llevando el torso hacia las piernas",
                    "Baja controladamente a la posición inicial"
                ],
                "muscle_groups": ["Abdomen alto", "Abdomen bajo", "Core"],
                "equipment": ["Colchoneta"]
            },
            {
                "name": "Peso muerto con mancuernas",
                "description": "Ejercicio compound para fortalecer espalda baja, glúteos y piernas",
                "video_url": "https://www.youtube.com/watch?v=ytGaGIn3SjE",
                "exercise_type": "full_body",
                "level": "intermediate",
                "default_duration": 45,
                "default_rest": 40,
                "default_repetitions": 12,
                "instructions": [
                    "Mantente de pie con pies separados al ancho de caderas",
                    "Sostén las mancuernas frente a los muslos",
                    "Inclínate hacia adelante desde las caderas manteniendo espalda recta",
                    "Regresa a la posición inicial activando glúteos y isquiotibiales"
                ],
                "muscle_groups": ["Espalda baja", "Glúteos", "Isquiotibiales", "Core"],
                "equipment": ["Mancuernas"]
            }
        ]
        
        for exercise_data in default_exercises:
            exercise = Exercise(**exercise_data)
            await db.exercises.insert_one(prepare_for_mongo(exercise.dict()))
        
        logging.info(f"Initialized {len(default_exercises)} default exercises")

# Routes
@api_router.get("/")
async def root():
    return {"message": "Fitness App API - ¡Entrena con éxito!"}

# Exercise routes
@api_router.get("/exercises", response_model=List[Exercise])
async def get_exercises(exercise_type: Optional[str] = None, level: Optional[str] = None):
    filter_query = {}
    if exercise_type:
        filter_query["exercise_type"] = exercise_type
    if level:
        filter_query["level"] = level
    
    exercises = await db.exercises.find(filter_query).to_list(length=None)
    return [Exercise(**exercise) for exercise in exercises]

@api_router.get("/exercises/{exercise_id}", response_model=Exercise)
async def get_exercise(exercise_id: str):
    exercise = await db.exercises.find_one({"id": exercise_id})
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return Exercise(**exercise)

# Workout session routes
@api_router.post("/workouts", response_model=WorkoutSession)
async def create_workout_session(workout: WorkoutSession):
    workout_dict = prepare_for_mongo(workout.dict())
    await db.workout_sessions.insert_one(workout_dict)
    return workout

@api_router.get("/workouts", response_model=List[WorkoutSession])
async def get_workout_sessions(limit: int = 50):
    sessions = await db.workout_sessions.find().sort("created_at", -1).limit(limit).to_list(length=None)
    return [WorkoutSession(**session) for session in sessions]

@api_router.get("/workouts/stats")
async def get_workout_stats():
    total_sessions = await db.workout_sessions.count_documents({})
    
    # Get sessions from last 30 days
    from datetime import timedelta
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    recent_sessions = await db.workout_sessions.count_documents({
        "created_at": {"$gte": thirty_days_ago.isoformat()}
    })
    
    # Calculate total workout time
    pipeline = [
        {"$group": {"_id": None, "total_time": {"$sum": "$total_duration"}}}
    ]
    total_time_result = await db.workout_sessions.aggregate(pipeline).to_list(length=1)
    total_time = total_time_result[0]["total_time"] if total_time_result else 0
    
    return {
        "total_sessions": total_sessions,
        "recent_sessions": recent_sessions,
        "total_workout_time": total_time,
        "average_session_time": total_time // total_sessions if total_sessions > 0 else 0
    }

# User profile routes
@api_router.post("/profile", response_model=UserProfile)
async def create_or_update_profile(profile: UserProfile):
    # For simplicity, we'll use a single profile. In real app, you'd use user authentication
    existing_profile = await db.user_profiles.find_one({})
    
    if existing_profile:
        profile.id = existing_profile["id"]
        profile.created_at = datetime.fromisoformat(existing_profile["created_at"])
        profile.updated_at = datetime.now(timezone.utc)
        
        await db.user_profiles.replace_one(
            {"id": profile.id}, 
            prepare_for_mongo(profile.dict())
        )
    else:
        await db.user_profiles.insert_one(prepare_for_mongo(profile.dict()))
    
    return profile

@api_router.get("/profile", response_model=Optional[UserProfile])
async def get_profile():
    profile = await db.user_profiles.find_one({})
    return UserProfile(**profile) if profile else None

# Measurements routes
@api_router.post("/measurements", response_model=AbdominalMeasurement)
async def add_measurement(measurement: AbdominalMeasurement):
    measurement_dict = prepare_for_mongo(measurement.dict())
    await db.measurements.insert_one(measurement_dict)
    return measurement

@api_router.get("/measurements", response_model=List[AbdominalMeasurement])
async def get_measurements(limit: int = 50):
    measurements = await db.measurements.find().sort("created_at", -1).limit(limit).to_list(length=None)
    return [AbdominalMeasurement(**measurement) for measurement in measurements]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await initialize_exercises()
    logger.info("Fitness App started successfully!")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
