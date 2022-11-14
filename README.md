Object-oriented design for a Single floor parking spots-DataBase-Management-System

I created a Parking spots project using Python, Postgres, and OOP, CRUD.

The Parking Lot:
1. Parking spots available for 5 types of vehicles: compact, large,  electric,  motorbike,  handicapped
2. The Parking spot has 105 available parking spaces: 
    compact, large,  electric,  motorbike,  handicapped = [50, 20, 10, 15, 10] 
3. Parking price per hour:
    compact, large,  electric,  motorbike,  handicapped = [1, 2, 2, 1, Free]
4. Parking DateTime, parking hour, ticket status
5. A window panel with 6 buttons to display the currently available parking lot and 3 other buttons: Park vehicle, Remove vehicle, and Ticket status.
6. 4 classes: class DBManager(manage the database), class Login, class ParkVehicle, class Window
7. every time park a vehicle, the specific parking spot type is 1 less available, and every time remove a vehicle, the specific parking spot type is 1 more available
8. to be continued with the payment

