def finalizeTrip(userid, fsuggestid)
    try:
        user=User.get(User.user_ID==userid)
        fs=FilteredSuggestion.get(FilteredSuggestion.f_suggest_id==fsuggestid)
        trip=fs.trip

        ftrip = FinalTrip.create(
            f_suggest=fs,
            destination=fs.destination,
            transport=fs.transport,
            accommodation=fs.accommodation,
            food=fs.food,
            user_id=user,
            totalbudget=fs.totalbudget,
            startDate=trip.startDate,
            endDate=trip.endDate
        )
        print(f"Trip finalize successfully! Trip ID: {ftrip.f_trip_id}")
        return ftrip    

    except User.DoesNotExist:
        print(f"Error: User with ID {userid} not found")
        return None
    except FilteredSuggestion.DoesNotExist:
        print(f"Error: FilteredSuggestion with ID {fsuggestid} not found")
        return None
    except Exception as e:
        print(f"Error creating final trip: {e}")
        return None