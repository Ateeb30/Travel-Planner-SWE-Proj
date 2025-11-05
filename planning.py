from fastapi import HTTPException
from database import Destination, db
from typing import Optional, Dict, Any
import random

# --- Helper to structure the destination data ---

def format_destination(dest: Destination) -> Dict[str, Any]:
    """Extracts required destination attributes for the API response"""
    # NOTE: Destination model only has city, country, description 
    # Cost, rating, category are simulated for now as they are not in the Destination table.
    return {
        "id": dest.dest_id,
        "name": dest.city, # Using city as the primary name
        "country": dest.country,
        "city": dest.city,
        "description": dest.description,
        # SIMULATED ATTRIBUTES (Need to be calculated from Food/Accommodation/Transport tables later)
        "cost": random.uniform(50, 200),
        "rating": round(random.uniform(3.5, 5.0), 1),
        "category": random.choice(["Beach", "Mountain", "City", "Adventure"]),
        "image": "placeholder_url",
    }

# --- Main Logic Functions ---

def show_random_suggestions(user_id: int):
    """Queries DB, randomly picks 5 destinations, and returns them"""
    
    db.connect()
    try:
        # 1. Queries database to get all destinations (Peewee SELECT query)
        all_dests = list(Destination.select())

        if not all_dests:
            return {"error": "No destinations exist in the database."}

        # 2. Randomly picks 5 destinations
        num_suggestions = min(5, len(all_dests))
        random_suggestions = random.sample(all_dests, num_suggestions)

        # 3. Extracts details and returns list
        suggestions_list = [format_destination(dest) for dest in random_suggestions]

        return {
            "suggestions": suggestions_list,
            "message": f"Showing {num_suggestions} random suggestions."
        }
    finally:
        db.close()


def filter_suggestions(user_id: int, budget: Optional[float] = None, destination: Optional[str] = None, 
                       category: Optional[str] = None):
    """Receives filter parameters and returns destinations matching ALL filters"""
    
    db.connect()
    try:
        # Start with a base query
        query = Destination.select() 
        applied_filters = {}

        # 1. Apply filters one by one
        
        # Filter by Destination name (search in city/country)
        if destination:
            # Peewee query using __contains for LIKE search on City or Country [cite: 44-45]
            query = query.where(
                (Destination.city.contains(destination)) | 
                (Destination.country.contains(destination))
            )
            applied_filters["destination"] = destination
        
        # NOTE: Budget and Category filters require joining with other tables 
        # (Food, Accommodation, Transport) or adding fields to Destination, 
        # which is not possible with the current simple Destination model.
        # We process the remaining attributes from the simulated data:
        if budget is not None:
             applied_filters["budget"] = f"Cost <= ${budget}"
        if category:
             applied_filters["category"] = category
        
        # 2. Execute filtered query
        filtered_results = list(query)
        
        # 3. Apply simulated cost/category filters in Python (since DB doesn't support it)
        final_list = []
        for dest in filtered_results:
            formatted = format_destination(dest)
            
            # cost filter
            if budget is not None and formatted['cost'] > budget:
                continue
            
            # category filter
            if category and formatted['category'].lower() != category.lower():
                continue
            
            final_list.append(formatted)

        # 4. Returns list of destinations matching ALL filters
        if not final_list:
            message = "No destinations match the applied filters."
        else:
            message = f"Found {len(final_list)} destinations matching your criteria."
            
        return {
            "message": message,
            "filters_applied": applied_filters,
            "destinations": final_list
        }
    finally:
        db.close()