from peewee import (
    Model, CharField, AutoField, IntegerField, ForeignKeyField, DateField, FloatField, TimeField
)
from playhouse.pool import PooledPostgresqlDatabase
import os
from dotenv import load_dotenv

load_dotenv()

try:
    db = PooledPostgresqlDatabase(
        os.getenv('DB_NAME', 'travel_planner_swe'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST', 'localhost'),
        port=int(os.getenv('DB_PORT', 5432))
    )
    db.connect()
    print("Connected to PostgreSQL successfully!")

except Exception as e:
    print("Connection failed:")
    print(e)


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = AutoField(primary_key=True)
    user_name = CharField(max_length=20)
    password = CharField(max_length=100, null=True)
    email = CharField(max_length=50, unique=True)
    city = CharField(max_length=50)
    country = CharField(max_length=50)

    class Meta:
        table_name = 'users'


class Destination(BaseModel):
    dest_id = AutoField(primary_key=True)
    city = CharField(max_length=20)
    country = CharField(max_length=100)
    description = CharField(max_length=500)
    
    class Meta:
        table_name = 'destinations'


class Trip(BaseModel):
    trip_id = AutoField(primary_key=True)
    maxBudget = IntegerField()
    destination = ForeignKeyField(Destination, backref='trips', on_delete='CASCADE')
    startDate = DateField()
    endDate = DateField()
    user = ForeignKeyField(User, backref='trips', on_delete='CASCADE')

    class Meta:
        table_name = 'trips'


class Food(BaseModel):
    cuisine_id = AutoField(primary_key=True)
    name = CharField(max_length=100)
    location = CharField(max_length=200)
    rating = FloatField()
    destination = ForeignKeyField(Destination, backref='foods', on_delete='CASCADE')
    class Meta:
        table_name = 'food'


class Accommodation(BaseModel):
    acco_id = AutoField(primary_key=True)
    name = CharField(max_length=100)
    type = IntegerField()  # Could be enum: hotel, hostel, apartment, etc.
    rating = FloatField()
    destination = ForeignKeyField(Destination, backref='foods', on_delete='CASCADE')
    class Meta:
        table_name = 'accommodations'


class Transport(BaseModel):
    transport_id = AutoField(primary_key=True)
    originCity = CharField(max_length=100)
    originCountry = CharField(max_length=100)
    destCity = CharField(max_length=100)
    destCountry = CharField(max_length=100)
    transportType = IntegerField()  # Could be enum: flight, train, bus, etc.
    cost = FloatField()
    time = TimeField()
    
    class Meta:
        table_name = 'transport'


class Suggestion(BaseModel):
    suggest_id = AutoField(primary_key=True)
    trip = ForeignKeyField(Trip, backref='filtered_suggestions', on_delete='CASCADE')
    dailybudget = FloatField()
    food = ForeignKeyField(Food, backref='suggestions', on_delete='CASCADE')
    transport = ForeignKeyField(Transport, backref='suggestions', on_delete='CASCADE')
    destination = ForeignKeyField(Destination, backref='suggestions', on_delete='CASCADE')
    accommodation = ForeignKeyField(Accommodation, backref='suggestions', on_delete='CASCADE')
    class Meta:
        table_name = 'suggestions'


class FilteredSuggestion(BaseModel):
    f_suggest_id = AutoField(primary_key=True)
    trip = ForeignKeyField(Trip, backref='filtered_suggestions', on_delete='CASCADE')
    totalbudget = FloatField()
    dailybudget = FloatField()
    food = ForeignKeyField(Food, backref='filtered_suggestions', on_delete='CASCADE')
    transport = ForeignKeyField(Transport, backref='filtered_suggestions', on_delete='CASCADE')
    destination = ForeignKeyField(Destination, backref='filtered_suggestions', on_delete='CASCADE')
    accommodation = ForeignKeyField(Accommodation, backref='filtered_suggestions', on_delete='CASCADE')
    class Meta:
        table_name = 'filtered_suggestions'


class Admin(BaseModel):
    admin_id = AutoField(primary_key=True)
    username = CharField(max_length=50)
    password = CharField(max_length=100)
    access_level = IntegerField()
    
    class Meta:
        table_name = 'admins'

class FinalTrip(BaseModel):
    f_trip_id = AutoField(primary_key=True)
    f_suggest = ForeignKeyField(FilteredSuggestion, backref='final_trips', on_delete='CASCADE')
    destination = ForeignKeyField(Destination, backref='final_trips', on_delete='CASCADE')
    transport = ForeignKeyField(Transport, backref='final_trips', on_delete='CASCADE')
    accommodation = ForeignKeyField(Accommodation, backref='final_trips', on_delete='CASCADE')
    food = ForeignKeyField(Food, backref='final_trips', on_delete='CASCADE')
    user_id = ForeignKeyField(User, backref='final_trips', on_delete='CASCADE')
    totalbudget = FloatField()
    startDate = DateField()
    endDate = DateField()

    class Meta:
        table_name = 'final_trips'

if __name__ == "__main__":
    # Create tables
    db.create_tables([
        User, 
        Destination, 
        Trip, 
        Food, 
        Accommodation, 
        Transport, 
        Suggestion, 
        FilteredSuggestion, 
        Admin,
        FinalTrip
    ], safe=True)  
    print("All tables created successfully!")
    db.close()