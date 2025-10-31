from faker import Faker
from database import (
    db, User, Destination, Trip, Food, Accommodation, 
    Transport, Suggestion, FilteredSuggestion, Admin
)
from datetime import datetime, timedelta
import random

fake = Faker()

def generate_users(n=20):
    """Generate fake users"""
    users = []
    for _ in range(n):
        user = User.create(
            user_name=fake.user_name()[:20],
            password=fake.password(),
            email=fake.unique.email(),
            city=fake.city(),
            country=fake.country()
        )
        users.append(user)
    print(f"✅ Created {n} users")
    return users


def generate_destinations(n=15):
    """Generate fake destinations"""
    destinations = []
    for _ in range(n):
        destination = Destination.create(
            city=fake.city()[:20],
            country=fake.country()[:100],
            description=fake.text(max_nb_chars=500)
        )
        destinations.append(destination)
    print(f"✅ Created {n} destinations")
    return destinations


def generate_food(n=30):
    """Generate fake food/restaurant data"""
    cuisines = ['Italian', 'Chinese', 'Mexican', 'Japanese', 'Indian', 
                'French', 'Thai', 'Mediterranean', 'Korean', 'Vietnamese']
    foods = []
    for _ in range(n):
        food = Food.create(
            name=f"{random.choice(cuisines)} {fake.company()}"[:100],
            location=fake.address()[:200],
            rating=round(random.uniform(3.0, 5.0), 1)
        )
        foods.append(food)
    print(f"✅ Created {n} food entries")
    return foods


def generate_accommodations(n=25):
    """Generate fake accommodations"""
    types = [1, 2, 3, 4, 5]  # Hotel, Hostel, Apartment, Resort, B&B
    accommodations = []
    for _ in range(n):
        accommodation = Accommodation.create(
            name=f"{fake.company()} {random.choice(['Hotel', 'Inn', 'Lodge', 'Resort'])}"[:100],
            type=random.choice(types),
            rating=round(random.uniform(3.0, 5.0), 1)
        )
        accommodations.append(accommodation)
    print(f"✅ Created {n} accommodations")
    return accommodations


def generate_transports(n=40):
    """Generate fake transport options"""
    transport_types = [1, 2, 3, 4, 5]  # Flight, Train, Bus, Car, Ferry
    transports = []
    for _ in range(n):
        transport = Transport.create(
            originCity=fake.city()[:100],
            originCountry=fake.country()[:100],
            destCity=fake.city()[:100],
            destCountry=fake.country()[:100],
            transportType=random.choice(transport_types),
            cost=round(random.uniform(50, 1000), 2),
            time=fake.time()
        )
        transports.append(transport)
    print(f"✅ Created {n} transport options")
    return transports


def generate_trips(users, destinations, n=30):
    """Generate fake trips for users"""
    trips = []
    for _ in range(n):
        start_date = fake.date_between(start_date='-1y', end_date='+6m')
        end_date = start_date + timedelta(days=random.randint(3, 21))
        
        trip = Trip.create(
            maxBudget=random.randint(500, 5000),
            destination=random.choice(destinations),
            startDate=start_date,
            endDate=end_date,
            user=random.choice(users)
        )
        trips.append(trip)
    print(f"✅ Created {n} trips")
    return trips


def generate_suggestions(foods, transports, destinations, n=20):
    """Generate fake suggestions"""
    suggestions = []
    for _ in range(n):
        suggestion = Suggestion.create(
            dailybudget=round(random.uniform(50, 300), 2),
            food=random.choice(foods),
            transport=random.choice(transports),
            destination=random.choice(destinations)
        )
        suggestions.append(suggestion)
    print(f"✅ Created {n} suggestions")
    return suggestions


def generate_filtered_suggestions(foods, transports, destinations, n=15):
    """Generate fake filtered suggestions"""
    filtered = []
    for _ in range(n):
        daily = round(random.uniform(50, 300), 2)
        duration = random.randint(3, 14)
        
        filtered_suggestion = FilteredSuggestion.create(
            totalbudget=round(daily * duration, 2),
            dailybudget=daily,
            food=random.choice(foods),
            transport=random.choice(transports),
            destination=random.choice(destinations)
        )
        filtered.append(filtered_suggestion)
    print(f"✅ Created {n} filtered suggestions")
    return filtered


def generate_admins(n=3):
    """Generate fake admin users"""
    admins = []
    for i in range(n):
        admin = Admin.create(
            username=f"admin{i+1}",
            password=fake.password(),
            access_level=random.randint(1, 3)
        )
        admins.append(admin)
    print(f"✅ Created {n} admins")
    return admins


def clear_all_data():
    """Clear all existing data from tables"""
    print("🗑️  Clearing existing data...")
    FilteredSuggestion.delete().execute()
    Suggestion.delete().execute()
    Trip.delete().execute()
    Transport.delete().execute()
    Accommodation.delete().execute()
    Food.delete().execute()
    Destination.delete().execute()
    User.delete().execute()
    Admin.delete().execute()
    print(" All data cleared!")


if __name__ == "__main__":
    try:
        # Optional: Clear existing data first
        # clear_all_data()
        
        print("\n Starting data generation...\n")
        
        # Generate data in order (respecting foreign key dependencies)
        users = generate_users(20)
        destinations = generate_destinations(15)
        foods = generate_food(30)
        accommodations = generate_accommodations(25)
        transports = generate_transports(40)
        trips = generate_trips(users, destinations, 30)
        suggestions = generate_suggestions(foods, transports, destinations, 20)
        filtered_suggestions = generate_filtered_suggestions(foods, transports, destinations, 15)
        admins = generate_admins(3)
        
        print("\n All fake data generated successfully!")
        print(f"""
        Summary:
        --------
        Users: {len(users)}
        Destinations: {len(destinations)}
        Food: {len(foods)}
        Accommodations: {len(accommodations)}
        Transports: {len(transports)}
        Trips: {len(trips)}
        Suggestions: {len(suggestions)}
        Filtered Suggestions: {len(filtered_suggestions)}
        Admins: {len(admins)}
        """)
        
    except Exception as e:
        print(f"Error generating data: {e}")
    
    finally:
        db.close()
        print("Database connection closed.")