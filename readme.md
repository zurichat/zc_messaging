# ZC Messaging

This plugin handles messaging for both DM and Channels

## Project Structure

This project is a monolith application. You will find two folders namely:

1. backend
2. frontend

Depending on your track, you are to work in the folder that concerns you.

## Setup

### Backend

1. Fork this repository to have a copy of it in your own github account
2. Clone the forked repo to your PC, this gives you access to the repo locally
3. Install Python from <https://www.python.org/downloads/> if you haven't
4. cd into the project folder
5. cd into the backend folder
6. Ensure a virtual environment has been created and activated
7. For Linux: Run the startup.sh script to install dependencies and start up server by typing out this command on your terminal
    ```sh startup.sh```
8. For Windows: Run the startup.sh script to install dependencies and start up server by typing out this command on your console
    ```startup.sh```
9. For Windows (using git bash): Run the startup.sh script to install dependencies and start up server by typing out this command on your console
    ```source startup.sh```

10. Server can be manually started by using the following command
    ```uvicorn main:app --reload```

### Frontend

Guides for Frontend will be updated soon

## Technologies Used

1. Backend: FastApi
2. Frontend: React
