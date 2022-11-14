Object-oriented design for a Single floor parking spots-DataBase-Management-System

I created a Parking spots project using Python, Postgres, and OOP, CRUD.

The Parking Lot:
1. Parking spots are available for 5 types of vehicles: compact, large,  electric,  motorbike,  handicapped
2.The Parking spot has 105 available parking spaces:
    compact, large,  electric,  motorbike,  handicapped = [50, 20, 10, 15, 10]
3. Parking price per hour:
    compact, large,  electric,  motorbike,  handicapped = [1, 2, 2, 1, Free]
4. Park a vehicle will automatically generate a ticket number , regenerate the current DateTime, and enter a spot type, License plate, and parking hours
5. Remove a vehicle will need to provide the ticket number to do so
6. Every time park a vehicle, the specific parking spot type is 1 less available, and every time remove a vehicle, the specific parking spot type is 1 more available
7. There are 4 classes: class DBManager(manage the PostgreSQL database, ), class Login(), class ParkVehicle(), class Window(manage the UI)
8. A window panel with 5 buttons to display the currently available parking spots and 3 other buttons: Park vehicle, Remove vehicle, and Ticket status.



