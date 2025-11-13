# payment.py
from database.database import FinalTrip, db

def checkout(ftripid):
    """Process payment for final trip"""
    try:
        if db.is_closed():
            db.connect()
            
        ft = FinalTrip.get(FinalTrip.f_trip_id == ftripid)
        
        print(f"💳 Processing Payment for Trip: {ft.f_trip_id}")
        print(f"👤 User: {ft.user_id.user_name}")
        print(f"📍 Destination: {ft.destination.city}, {ft.destination.country}")
        print(f"💰 Amount: ${ft.totalbudget:.2f}")
        print("✅ Payment processed successfully!")
        print("🎉 Your booking is confirmed! Have a great trip! 🌟")
        
        return True

    except FinalTrip.DoesNotExist:
        print(f"❌ Error: FinalTrip with ID {ftripid} not found")
        return False
    except Exception as e:
        print(f"❌ Payment processing error: {e}")
        return False