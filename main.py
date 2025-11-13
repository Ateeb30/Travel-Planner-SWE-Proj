# main.py - Travel Planning System
import sys
import os
from datetime import datetime, timedelta
import random

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import all modules
from auth.signup import signup
from auth.login import login
from database.database import db, User, Destination, Trip, Food, Accommodation, Transport, Suggestion, FilteredSuggestion, FinalTrip
import planning
import booking
import payment

class TravelPlannerSystem:
    def __init__(self):
        self.current_user = None
        self.current_token = None
        self.current_trip = None
        
    def clear_screen(self):
        """Clear the console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title):
        """Print a formatted header"""
        print("\n" + "="*60)
        print(f"🚀 {title}")
        print("="*60)
    
    def wait_for_enter(self):
        """Wait for user to press Enter"""
        input("\nPress Enter to continue...")
    
    def ensure_db_connection(self):
        """Ensure database connection is open"""
        if db.is_closed():
            db.connect()
    
    def close_db_connection(self):
        """Close database connection if open"""
        if not db.is_closed():
            db.close()
    
    def authenticate_user(self):
        """Handle user authentication (login/signup)"""
        self.clear_screen()
        self.print_header("Welcome to Travel Planner System")
        
        while True:
            print("\nPlease choose an option:")
            print("1. Login")
            print("2. Sign Up")
            print("3. Exit")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                return self.handle_login()
            elif choice == "2":
                return self.handle_signup()
            elif choice == "3":
                print("Thank you for using Travel Planner System! 👋")
                return False
            else:
                print("❌ Invalid choice. Please try again.")
    
    def handle_login(self):
        """Handle user login"""
        self.clear_screen()
        self.print_header("User Login")
        
        try:
            email = input("Enter your email: ").strip()
            password = input("Enter your password: ").strip()
            
            if not email or not password:
                print("❌ Email and password are required!")
                self.wait_for_enter()
                return True  # Continue authentication
            
            result = login(email, password)
            
            if result and "user_id" in result:
                self.current_user = {
                    "user_id": result["user_id"],
                    "username": result["username"],
                    "email": email
                }
                self.current_token = result["token"]
                print(f"✅ {result['message']}")
                print(f"👋 Welcome back, {result['username']}!")
                self.wait_for_enter()
                return True
            else:
                print("❌ Login failed!")
                self.wait_for_enter()
                return True
                
        except Exception as e:
            print(f"❌ Login error: {str(e)}")
            self.wait_for_enter()
            return True
    
    def handle_signup(self):
        """Handle user registration"""
        self.clear_screen()
        self.print_header("User Sign Up")
        
        try:
            print("Please enter your details:")
            email = input("Email: ").strip()
            username = input("Username: ").strip()
            password = input("Password (min 6 characters): ").strip()
            city = input("City: ").strip()
            country = input("Country: ").strip()
            
            # Basic validation
            if len(password) < 6:
                print("❌ Password must be at least 6 characters long!")
                self.wait_for_enter()
                return True
            
            result = signup(email, username, password, city, country)
            
            if result and "user_id" in result:
                self.current_user = {
                    "user_id": result["user_id"],
                    "username": result["username"],
                    "email": email
                }
                self.current_token = result["token"]
                print(f"✅ {result['message']}")
                print(f"🎉 Welcome to Travel Planner, {result['username']}!")
                self.wait_for_enter()
                return True
            else:
                print("❌ Signup failed!")
                self.wait_for_enter()
                return True
                
        except Exception as e:
            print(f"❌ Signup error: {str(e)}")
            self.wait_for_enter()
            return True
    
    def planning_phase(self):
        """Handle trip planning with suggestions and filters"""
        self.clear_screen()
        self.print_header("Trip Planning Phase")
        
        print("Let's plan your perfect trip! 🌍")
        
        # Get trip details
        try:
            self.ensure_db_connection()
            
            max_budget = float(input("\nEnter your maximum budget ($): ").strip())
            destination_city = input("Preferred destination city (or leave blank for any): ").strip()
            destination_country = input("Preferred destination country (or leave blank for any): ").strip()
            
            # For demo, we'll use simple date inputs
            start_date = input("Start date (YYYY-MM-DD): ").strip()
            end_date = input("End date (YYYY-MM-DD): ").strip()
            
            # Find or create destination
            dest_query = Destination.select()
            if destination_city:
                dest_query = dest_query.where(Destination.city.contains(destination_city))
            if destination_country:
                dest_query = dest_query.where(Destination.country.contains(destination_country))
            
            destination = dest_query.first()
            if not destination:
                # Use a random destination if none matches
                destination = Destination.select().first()
                print(f"⚠️  Using available destination: {destination.city}, {destination.country}")
            
            # Create trip
            trip = Trip.create(
                maxBudget=max_budget,
                destination=destination,
                startDate=start_date,
                endDate=end_date,
                user_id=self.current_user["user_id"]
            )
            
            self.current_trip = trip
            print(f"✅ Trip created! Trip ID: {trip.trip_id}")
            
        except Exception as e:
            print(f"❌ Error creating trip: {str(e)}")
            self.wait_for_enter()
            return
        finally:
            self.close_db_connection()
        
        # Start the suggestion and filtering flow
        self.start_suggestion_flow()
        
        self.wait_for_enter()

    def start_suggestion_flow(self):
        """Start the suggestion and filtering flow"""
        while True:
            self.clear_screen()
            self.print_header("Find Your Perfect Destination")
            
            print("How would you like to find destinations?")
            print("1. 🎲 Show random suggestions")
            print("2. 🔍 Apply filters directly")
            print("3. 🏠 Back to Main Menu")
            
            choice = input("\nEnter your choice (1-3): ").strip()
            
            if choice == "1":
                self.show_suggestions()
                # After showing suggestions, it will ask if user wants to apply filters
                # The flow continues naturally from there
            elif choice == "2":
                self.filter_suggestions()
                break
            elif choice == "3":
                return
            else:
                print("❌ Invalid choice. Please try again.")
                self.wait_for_enter()
    
    def show_suggestions(self):
        """Show random travel suggestions"""
        self.clear_screen()
        self.print_header("Travel Suggestions")
        
        print("Here are some random travel suggestions for you: 🎯\n")
        
        try:
            result = planning.show_random_suggestions(self.current_user["user_id"])
            
            if "suggestions" in result:
                suggestions = result["suggestions"]
                
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"{i}. {suggestion['name']}, {suggestion['country']}")
                    print(f"   💰 Cost: ${suggestion['cost']:.2f}")
                    print(f"   ⭐ Rating: {suggestion['rating']}/5")
                    print(f"   🏷️  Category: {suggestion['category']}")
                    print(f"   📍 {suggestion['description']}")
                    print()
            
            print(f"📝 {result.get('message', '')}")
            
            # Ask user if they want to apply filters
            print("\n" + "="*50)
            print("What would you like to do next?")
            print("1. 🔍 Apply filters to narrow down options")
            print("2. 🏠 Back to Main Menu")
            
            choice = input("\nEnter your choice (1-2): ").strip()
            
            if choice == "1":
                return  # This will go to filter_suggestions
            elif choice == "2":
                return
            else:
                print("❌ Invalid choice. Going back to main menu...")
                self.wait_for_enter()
                
        except Exception as e:
            print(f"❌ Error showing suggestions: {str(e)}")
            self.wait_for_enter()
            
    
    def filter_suggestions(self):
        """Apply filters to suggestions - with retry on no results"""
        while True:  # Keep showing filter options until user finds results or goes back
            self.clear_screen()
            self.print_header("Filter Suggestions")
            
            print("Apply filters to find your perfect destination: 🔍\n")
            print("(Leave fields blank to skip filters)\n")
            
            try:
                # Get filter criteria
                budget_filter = None
                destination_filter = None
                category_filter = None
                
                budget_input = input("Maximum budget ($) [press Enter to skip]: ").strip()
                if budget_input:
                    try:
                        budget_filter = float(budget_input)
                    except ValueError:
                        print("❌ Invalid budget amount. Please enter a valid number.")
                        self.wait_for_enter()
                        continue
                
                destination_filter = input("Destination name [press Enter to skip]: ").strip()
                if not destination_filter:
                    destination_filter = None
                    
                category_filter = input("Category (Beach/Mountain/City/Adventure) [press Enter to skip]: ").strip()
                if not category_filter:
                    category_filter = None
                
                # Apply filters
                result = planning.filter_suggestions(
                    user_id=self.current_user["user_id"],
                    budget=budget_filter,
                    destination=destination_filter,
                    category=category_filter
                )
                
                print(f"\n🎯 {result.get('message', '')}")
                
                if "destinations" in result and result["destinations"]:
                    destinations = result["destinations"]
                    print(f"\nFound {len(destinations)} matching destinations:\n")
                    
                    for i, dest in enumerate(destinations, 1):
                        print(f"{i}. {dest['name']}, {dest['country']}")
                        print(f"   💰 Cost: ${dest['cost']:.2f}")
                        print(f"   ⭐ Rating: {dest['rating']}/5")
                        print(f"   🏷️  Category: {dest['category']}")
                        print(f"   📍 {dest['description']}")
                        print()
                    
                    # Allow user to select a destination for booking
                    self.select_destination_for_booking(destinations)
                    break  # Exit the filter loop after selection
                else:
                    # No destinations found - show options to retry or go back
                    print("\n" + "="*50)
                    print("No destinations found with current filters.")
                    print("What would you like to do?")
                    print("1. 🔄 Try different filters")
                    print("2. 📋 Show random suggestions again")
                    print("3. 🏠 Back to Main Menu")
                    
                    retry_choice = input("\nEnter your choice (1-3): ").strip()
                    
                    if retry_choice == "1":
                        continue  # Continue the while loop (show filters again)
                    elif retry_choice == "2":
                        self.show_suggestions()
                        # After showing suggestions, continue with filtering
                        continue
                    elif retry_choice == "3":
                        return  # Go back to main menu
                    else:
                        print("❌ Invalid choice. Showing filter options again...")
                        self.wait_for_enter()
                        continue
                    
            except Exception as e:
                print(f"❌ Error filtering suggestions: {str(e)}")
                self.wait_for_enter()
    
    def select_destination_for_booking(self, destinations):
        """Allow user to select a destination for booking"""
        try:
            self.ensure_db_connection()
            
            choice = input("Enter the number of destination you want to book (or 0 to skip): ").strip()
            
            if choice.isdigit() and 1 <= int(choice) <= len(destinations):
                selected_dest = destinations[int(choice) - 1]
                print(f"\n🎉 Selected: {selected_dest['name']}, {selected_dest['country']}")
                
                # Get related entities (simplified for demo)
                destination_obj = Destination.get(Destination.dest_id == selected_dest["id"])
                food_obj = Food.select().first()  # Get first available food
                transport_obj = Transport.select().first()  # Get first available transport
                accommodation_obj = Accommodation.select().first()  # Get first available accommodation
                
                # Create filtered suggestion
                filtered_suggestion = FilteredSuggestion.create(
                    trip=self.current_trip,
                    totalbudget=selected_dest["cost"],
                    dailybudget=selected_dest["cost"] / 7,  # Simple calculation
                    food=food_obj,
                    transport=transport_obj,
                    destination=destination_obj,
                    accommodation=accommodation_obj
                )
                
                print(f"✅ Created filtered suggestion ID: {filtered_suggestion.f_suggest_id}")
                
                # Proceed to booking
                self.booking_phase(filtered_suggestion.f_suggest_id)
                
            elif choice == "0":
                print("Skipping booking...")
            else:
                print("❌ Invalid selection!")
                
        except Exception as e:
            print(f"❌ Error selecting destination: {str(e)}")
        finally:
            self.close_db_connection()
    
    def booking_phase(self, filtered_suggestion_id):
        """Handle trip booking"""
        self.clear_screen()
        self.print_header("Trip Booking")
        
        print("Finalizing your trip booking... ✈️\n")
        
        try:
            # Finalize the trip
            finalized_trip = booking.finalizeTrip(
                self.current_user["user_id"], 
                filtered_suggestion_id
            )
            
            if finalized_trip:
                print(f"✅ Trip finalized successfully!")
                print(f"📋 Final Trip ID: {finalized_trip.f_trip_id}")
                print(f"💰 Total Budget: ${finalized_trip.totalbudget:.2f}")
                
                # Proceed to payment
                self.payment_phase(finalized_trip.f_trip_id)
            else:
                print("❌ Failed to finalize trip!")
                
        except Exception as e:
            print(f"❌ Booking error: {str(e)}")
        
        self.wait_for_enter()
    
    def payment_phase(self, final_trip_id):
        """Handle payment processing"""
        self.clear_screen()
        self.print_header("Payment Processing")
        
        print("Processing your payment... 💳\n")
        
        try:
            # Process payment
            payment.checkout(final_trip_id)
            
            print("✅ Payment processed successfully!")
            print("🎉 Your trip is confirmed! Have a wonderful journey! 🌟")
            
        except Exception as e:
            print(f"❌ Payment error: {str(e)}")
        
        self.wait_for_enter()
    
    def main_menu(self):
        """Display main menu after authentication"""
        while True:
            self.clear_screen()
            self.print_header(f"Main Menu - Welcome, {self.current_user['username']}!")
            
            print("Please choose an option:")
            print("1. 🗺️  Start Trip Planning")
            print("2. 🔍 View My Trips")
            print("3. 👤 View Profile")
            print("4. 🚪 Logout")
            
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == "1":
                self.planning_phase()
            elif choice == "2":
                self.view_my_trips()
            elif choice == "3":
                self.view_profile()
            elif choice == "4":
                self.current_user = None
                self.current_token = None
                self.current_trip = None
                print("✅ Logged out successfully!")
                self.wait_for_enter()
                break
            else:
                print("❌ Invalid choice. Please try again.")
                self.wait_for_enter()
    
    def view_my_trips(self):
        """View user's trip history"""
        self.clear_screen()
        self.print_header("My Trips")
        
        try:
            self.ensure_db_connection()
            
            trips = FinalTrip.select().where(FinalTrip.user_id == self.current_user["user_id"])
            
            if trips.count() > 0:
                print("Your confirmed trips:\n")
                for trip in trips:
                    print(f"📍 Trip ID: {trip.f_trip_id}")
                    print(f"🏁 Destination: {trip.destination.city}, {trip.destination.country}")
                    print(f"💰 Total Budget: ${trip.totalbudget:.2f}")
                    print(f"📅 Dates: {trip.startDate} to {trip.endDate}")
                    print("-" * 40)
            else:
                print("You don't have any confirmed trips yet.")
                print("Start planning your first trip! 🗺️")
                
        except Exception as e:
            print(f"❌ Error retrieving trips: {str(e)}")
        finally:
            self.close_db_connection()
        
        self.wait_for_enter()
    
    def view_profile(self):
        """View user profile"""
        self.clear_screen()
        self.print_header("My Profile")
        
        try:
            self.ensure_db_connection()
            
            user = User.get(User.user_id == self.current_user["user_id"])
            
            print(f"👤 Username: {user.user_name}")
            print(f"📧 Email: {user.email}")
            print(f"📍 Location: {user.city}, {user.country}")
            print(f"🆔 User ID: {user.user_id}")
            
        except Exception as e:
            print(f"❌ Error retrieving profile: {str(e)}")
        finally:
            self.close_db_connection()
        
        self.wait_for_enter()
    
    def run(self):
        """Main system loop"""
        print("Starting Travel Planner System...")
        
        try:
            while True:
                if not self.current_user:
                    if not self.authenticate_user():
                        break
                else:
                    self.main_menu()
                    
        except KeyboardInterrupt:
            print("\n\n👋 Thank you for using Travel Planner System!")
        except Exception as e:
            print(f"\n❌ System error: {str(e)}")
        finally:
            # Close database connection
            self.close_db_connection()
            print("\nSystem shutdown complete.")

# Run the system
if __name__ == "__main__":
    system = TravelPlannerSystem()
    system.run()