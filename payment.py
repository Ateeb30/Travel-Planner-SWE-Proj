def checkout(ftripid)
    ft=FinalTrip.get(Finaltrip.f_trip_id==ftripid)

    print(f"Proccessing Paymnet for Trip : {ft.f_trip_id} for User : {ft.user_id}")

    
