from peewee import (
    Model, CharField, AutoField
)
from playhouse.pool import PooledPostgresqlDatabase

try:
    db = PooledPostgresqlDatabase(
        'travel_planner_swe',   
        user='postgres',      
        password='Minato12!',        
        host='localhost',
        port=5432
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


if __name__ == "__main__":
    db.create_tables([User])
    print("✅ Table 'users' created successfully!")
    db.close()
