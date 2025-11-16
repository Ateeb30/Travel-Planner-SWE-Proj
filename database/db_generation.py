from faker import Faker
from database import (
    db, User, Destination, Trip, Food, Accommodation, 
    Transport, Suggestion, FilteredSuggestion, Admin, FinalTrip
)
from datetime import datetime, timedelta
import random

fake = Faker()

def generate_users(n=200):
    """Generate fake users"""
    users = []
    print(f"Generating {n} users...")
    for i in range(n):
        if i % 50 == 0:
            print(f"  Progress: {i}/{n} users created")
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


def generate_destinations(n=500):
    """Generate fake destinations"""
    destinations = []
    print(f"Generating {n} destinations...")
    for i in range(n):
        if i % 100 == 0:
            print(f"  Progress: {i}/{n} destinations created")
        destination = Destination.create(
            city=fake.city()[:20],
            country=fake.country()[:100],
            description=fake.text(max_nb_chars=500)
        )
        destinations.append(destination)
    print(f"✅ Created {n} destinations")
    return destinations


def generate_food(destinations, n=1000):
    """Generate fake food/restaurant data"""
    cuisines = ['Italian', 'Chinese', 'Mexican', 'Japanese', 'Indian', 
                'French', 'Thai', 'Mediterranean', 'Korean', 'Vietnamese',
                'American', 'Greek', 'Turkish', 'Spanish', 'Lebanese']
    foods = []
    print(f"Generating {n} food entries...")
    for i in range(n):
        if i % 200 == 0:
            print(f"  Progress: {i}/{n} food entries created")
        food = Food.create(
            name=f"{random.choice(cuisines)} {fake.company()}"[:100],
            location=fake.address()[:200],
            rating=round(random.uniform(3.0, 5.0), 1),
            destination=random.choice(destinations)
        )
        foods.append(food)
    print(f"✅ Created {n} food entries")
    return foods


def generate_accommodations(destinations, n=800):
    """Generate fake accommodations"""
    types = [1, 2, 3, 4, 5]  # Hotel, Hostel, Apartment, Resort, B&B
    accommodation_types = ['Hotel', 'Inn', 'Lodge', 'Resort', 'Hostel', 
                          'Villa', 'Apartment', 'Guesthouse']
    accommodations = []
    print(f"Generating {n} accommodations...")
    for i in range(n):
        if i % 200 == 0:
            print(f"  Progress: {i}/{n} accommodations created")
        accommodation = Accommodation.create(
            name=f"{fake.company()} {random.choice(accommodation_types)}"[:100],
            type=random.choice(types),
            rating=round(random.uniform(3.0, 5.0), 1),
            destination=random.choice(destinations)
        )
        accommodations.append(accommodation)
    print(f"✅ Created {n} accommodations")
    return accommodations


def generate_transports(n=300):
    """Generate fake transport options"""
    transport_types = [1, 2, 3, 4, 5]  # Flight, Train, Bus, Car, Ferry
    transports = []
    print(f"Generating {n} transport options...")
    for i in range(n):
        if i % 100 == 0:
            print(f"  Progress: {i}/{n} transports created")
        transport = Transport.create(
            originCity=fake.city()[:100],
            originCountry=fake.country()[:100],
            destCity=fake.city()[:100],
            destCountry=fake.country()[:100],
            transportType=random.choice(transport_types),
            cost=round(random.uniform(50, 2000), 2),
            time=fake.time()
        )
        transports.append(transport)
    print(f"✅ Created {n} transport options")
    return transports


def generate_trips(users, destinations, n=400):
    """Generate fake trips for users"""
    trips = []
    print(f"Generating {n} trips...")
    for i in range(n):
        if i % 100 == 0:
            print(f"  Progress: {i}/{n} trips created")
        start_date = fake.date_between(start_date='-1y', end_date='+6m')
        end_date = start_date + timedelta(days=random.randint(3, 21))
        
        trip = Trip.create(
            maxBudget=random.randint(500, 10000),
            destination=random.choice(destinations),
            startDate=start_date,
            endDate=end_date,
            user=random.choice(users)
        )
        trips.append(trip)
    print(f"✅ Created {n} trips")
    return trips


def generate_suggestions(trips, foods, transports, destinations, accommodations, n=600):
    """Generate fake suggestions"""
    suggestions = []
    print(f"Generating {n} suggestions...")
    for i in range(n):
        if i % 100 == 0:
            print(f"  Progress: {i}/{n} suggestions created")
        suggestion = Suggestion.create(
            trip=random.choice(trips),
            dailybudget=round(random.uniform(50, 500), 2),
            food=random.choice(foods),
            transport=random.choice(transports),
            destination=random.choice(destinations),
            accommodation=random.choice(accommodations)
        )
        suggestions.append(suggestion)
    print(f"✅ Created {n} suggestions")
    return suggestions


def generate_filtered_suggestions(trips, foods, transports, destinations, accommodations, n=300):
    """Generate fake filtered suggestions"""
    filtered = []
    print(f"Generating {n} filtered suggestions...")
    for i in range(n):
        if i % 100 == 0:
            print(f"  Progress: {i}/{n} filtered suggestions created")
        daily = round(random.uniform(50, 500), 2)
        duration = random.randint(3, 14)
        
        filtered_suggestion = FilteredSuggestion.create(
            trip=random.choice(trips),
            totalbudget=round(daily * duration, 2),
            dailybudget=daily,
            food=random.choice(foods),
            transport=random.choice(transports),
            destination=random.choice(destinations),
            accommodation=random.choice(accommodations)
        )
        filtered.append(filtered_suggestion)
    print(f"✅ Created {n} filtered suggestions")
    return filtered


def generate_final_trips(users, filtered_suggestions, destinations, transports, accommodations, foods, n=150):
    """Generate fake final trips"""
    final_trips = []
    print(f"Generating {n} final trips...")
    for i in range(n):
        if i % 50 == 0:
            print(f"  Progress: {i}/{n} final trips created")
        filtered_sugg = random.choice(filtered_suggestions)
        start_date = fake.date_between(start_date='-1y', end_date='+6m')
        end_date = start_date + timedelta(days=random.randint(3, 21))
        
        final_trip = FinalTrip.create(
            f_suggest=filtered_sugg,
            destination=random.choice(destinations),
            transport=random.choice(transports),
            accommodation=random.choice(accommodations),
            food=random.choice(foods),
            user_id=random.choice(users),
            totalbudget=round(random.uniform(1000, 10000), 2),
            startDate=start_date,
            endDate=end_date
        )
        final_trips.append(final_trip)
    print(f"✅ Created {n} final trips")
    return final_trips


def generate_admins(n=5):
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
    FinalTrip.delete().execute()
    FilteredSuggestion.delete().execute()
    Suggestion.delete().execute()
    Trip.delete().execute()
    Transport.delete().execute()
    Accommodation.delete().execute()
    Food.delete().execute()
    Destination.delete().execute()
    User.delete().execute()
    Admin.delete().execute()
    print("✅ All data cleared!")


if __name__ == "__main__":
    try:
        # Optional: Clear existing data first
        print("\n⚠️  This will delete ALL existing data and create new data.")
        response = input("Continue? (yes/no): ").lower()
        if response != 'yes':
            print("Cancelled.")
            exit()
        
        clear_all_data()
        
        print("\n🚀 Starting LARGE data generation...")
        print("This may take a few minutes...\n")
        
        # Generate data in order (respecting foreign key dependencies)
        users = generate_users(200)          # 200 users
        destinations = generate_destinations(500)  # 500 destinations
        foods = generate_food(destinations, 1000)  # 1000 restaurants
        accommodations = generate_accommodations(destinations, 800)  # 800 accommodations
        transports = generate_transports(300)  # 300 transport options
        trips = generate_trips(users, destinations, 400)  # 400 trips
        suggestions = generate_suggestions(trips, foods, transports, destinations, accommodations, 600)  # 600 suggestions
        filtered_suggestions = generate_filtered_suggestions(trips, foods, transports, destinations, accommodations, 300)  # 300 filtered
        final_trips = generate_final_trips(users, filtered_suggestions, destinations, transports, accommodations, foods, 150)  # 150 final trips
        admins = generate_admins(5)  # 5 admins
        
        print("\n" + "="*60)
        print("🎉 ALL FAKE DATA GENERATED SUCCESSFULLY!")
        print("="*60)
        print(f"""
        📊 FINAL SUMMARY:
        ─────────────────
        👥 Users:                  {len(users):,}
        📍 Destinations:            {len(destinations):,}
        🍽️  Food/Restaurants:       {len(foods):,}
        🏨 Accommodations:          {len(accommodations):,}
        🚗 Transport Options:       {len(transports):,}
        ✈️  Trips:                   {len(trips):,}
        💡 Suggestions:             {len(suggestions):,}
        🔍 Filtered Suggestions:    {len(filtered_suggestions):,}
        ✅ Final Trips:             {len(final_trips):,}
        👨‍💼 Admins:                  {len(admins):,}
        ─────────────────
        📦 TOTAL RECORDS:          {len(users) + len(destinations) + len(foods) + len(accommodations) + len(transports) + len(trips) + len(suggestions) + len(filtered_suggestions) + len(final_trips) + len(admins):,}
        """)
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ Error generating data: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()
        print("\n🔌 Database connection closed.")