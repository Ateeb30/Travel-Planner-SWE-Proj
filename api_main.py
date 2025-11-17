# api_main.py - FastAPI Application
from fastapi.responses import JSONResponse
from fastapi import FastAPI, HTTPException, Depends
from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date

# Import your existing modules
from auth.signup import signup
from auth.login import login
from database.database import db, User, Trip, Destination, FinalTrip
import planning
import booking
import payment

app = FastAPI(title="Travel Planner API")

# CORS Configuration - MUST BE BEFORE ROUTES
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://travel-planner-swe-proj.vercel.app",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.options("/{path:path}")
async def options_handler(path: str):
    """Handle OPTIONS requests for CORS preflight"""
    return JSONResponse(
        content={"status": "ok"},
        headers={
            "Access-Control-Allow-Origin": "https://travel-planner-swe-proj.vercel.app",
            "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true",
        },
        status_code=200
    )

# ===== PYDANTIC MODELS =====

class LoginRequest(BaseModel):
    email: str
    password: str

class SignupRequest(BaseModel):
    email: str
    username: str
    password: str
    city: str
    country: str

class CreateTripRequest(BaseModel):
    user_id: int
    max_budget: float
    start_date: str
    end_date: str
    destination_city: Optional[str] = None
    destination_country: Optional[str] = None

class FilterRequest(BaseModel):
    user_id: int
    budget: Optional[float] = None
    destination: Optional[str] = None
    category: Optional[str] = None

# ===== HEALTH CHECK (MUST BE FIRST) =====

@app.get("/")
def root():
    """API health check"""
    return {
        "message": "Travel Planner API is running",
        "version": "1.0.0"
    }

# ===== AUTH ENDPOINTS =====

@app.post("/auth/login")
def api_login(request: LoginRequest):
    """User login endpoint"""
    try:
        result = login(request.email, request.password)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/auth/signup")
def api_signup(request: SignupRequest):
    """User signup endpoint"""
    try:
        result = signup(
            email=request.email,
            username=request.username,
            password=request.password,
            city=request.city,
            country=request.country
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== PLANNING ENDPOINTS =====

@app.post("/planning/create-trip")
def api_create_trip(request: CreateTripRequest):
    """Create a new trip"""
    try:
        if db.is_closed():
            db.connect()
        
        # Find or use first destination
        dest_query = Destination.select()
        if request.destination_city:
            dest_query = dest_query.where(Destination.city.contains(request.destination_city))
        if request.destination_country:
            dest_query = dest_query.where(Destination.country.contains(request.destination_country))
        
        destination = dest_query.first()
        if not destination:
            destination = Destination.select().first()
        
        # Create trip
        trip = Trip.create(
            maxBudget=request.max_budget,
            destination=destination,
            startDate=request.start_date,
            endDate=request.end_date,
            user_id=request.user_id
        )
        
        return {
            "message": "Trip created successfully",
            "trip_id": trip.trip_id,
            "destination": {
                "city": destination.city,
                "country": destination.country
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if not db.is_closed():
            db.close()

@app.get("/planning/suggestions/{user_id}")
def api_get_suggestions(user_id: int):
    """Get random destination suggestions"""
    try:
        result = planning.show_random_suggestions(user_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/planning/filter")
def api_filter_suggestions(request: FilterRequest):
    """Filter destinations based on criteria"""
    try:
        result = planning.filter_suggestions(
            user_id=request.user_id,
            budget=request.budget,
            destination=request.destination,
            category=request.category
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== TRIP ENDPOINTS =====

@app.get("/trips/{user_id}")
def api_get_user_trips(user_id: int):
    """Get all trips for a user"""
    try:
        if db.is_closed():
            db.connect()
        
        trips = FinalTrip.select().where(FinalTrip.user_id == user_id)
        
        trips_list = []
        for trip in trips:
            trips_list.append({
                "trip_id": trip.f_trip_id,
                "destination": f"{trip.destination.city}, {trip.destination.country}",
                "totalbudget": float(trip.totalbudget),
                "startDate": str(trip.startDate),
                "endDate": str(trip.endDate)
            })
        
        return {"trips": trips_list}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if not db.is_closed():
            db.close()

# ===== BOOKING ENDPOINTS =====

@app.post("/booking/finalize/{user_id}/{filtered_suggestion_id}")
def api_finalize_booking(user_id: int, filtered_suggestion_id: int):
    """Finalize a trip booking"""
    try:
        result = booking.finalizeTrip(user_id, filtered_suggestion_id)
        if result:
            return {
                "message": "Trip finalized successfully",
                "trip_id": result.f_trip_id,
                "total_budget": float(result.totalbudget)
            }
        else:
            raise HTTPException(status_code=404, detail="Could not finalize trip")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== PAYMENT ENDPOINTS =====

@app.post("/payment/checkout/{final_trip_id}")
def api_checkout(final_trip_id: int):
    """Process payment for a trip"""
    try:
        result = payment.checkout(final_trip_id)
        if result:
            return {"message": "Payment processed successfully"}
        else:
            raise HTTPException(status_code=400, detail="Payment failed")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# For Vercel serverless deployment
app = app
# --- IGNORE ---