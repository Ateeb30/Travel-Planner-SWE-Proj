from peewee import (
    Model, CharField, AutoField, IntegerField, ForeignKeyField, DateField
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


class Trip(BaseModel):
    trip_id = AutoField(primary_key=True)
    maxBudget = IntegerField()
    destination = CharField(max_length=100)
    startDate = DateField()
    endDate = DateField()
    user = ForeignKeyField(User, backref='trips', on_delete='CASCADE')

    class Meta:
        table_name = 'trips'

class Admin(BaseModel):
    admin_id = AutoField(primary_key=True)
    user_name = CharField(max_length=20)
    password = CharField(max_length=100, null=True)
    access_level = IntegerField()
    user = ForeignKeyField(User, backref='trips', on_delete='CASCADE')

    class Meta:
        table_name = 'admin'

if __name__ == "__main__":
    db.create_tables([User, Trip])
    print("Tables created successfully!")
    db.close()
