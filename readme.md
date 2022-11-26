# ZC Messaging

This plugin handles messaging for both DM and Channels

## Project Structure

This project is a monolith application. You will find three folders namely:

1. backend
2. frontend
3. notifications

Depending on your track, you are to work in the folder that concerns you.

## Setup

### Backend

- Fork this repository to have a copy of it in your own github account
- Clone the forked repo to your PC, this gives you access to the repo locally
- Install Python from <https://www.python.org/downloads/> if you haven't
- cd into the project folder
- cd into the backend folder
- Ensure a virtual environment has been created and activated by either using

  - For pipenv

    ```bash
    pipenv shell #creates and activates a virtual environment
    ```

  - For venv

    ```bash
    python -m venv venv # to create a virtualenv
    source venv/bin/activate # activate for linux
    venv\Scripts\activate # activate for windows
    ```

- Run the startup.sh script to install dependencies and start up server by typing out this command on your terminal(Linux, Mac) or Git bash (Windows)

  ```bash
  sh startup.sh venv # starts script to use virtualenv
  sh startup.sh pipenv # starts script to use pipenv
  ```

- Server can also be manually started by using the following command

  ```bash
  uvicorn main:app --reload
  ```

### Frontend

- Fork this repository to have a copy of it in your own github account
- Clone the forked repo to your PC, this gives you access to the repo locally
- Install Node from <https://nodejs.org/> if you haven't
- cd into the project folder
- cd into the frontend folder
- `yarn install`
- `yarn setup` to setup app
- `yarn setup:root` to setup SPA
- `yarn setup:messaging` to setup React App
- `yarn dev` to run apps simultaneously
- `yarn dev:root` to run SPA
- `yarn dev:messaging` to run React App
- `yarn build` to build apps simultaneously
- `yarn build:root` to build SPA
- `yarn build:messaging` ro build React App
- `yarn lint` to lint App
- `yarn prettify` to run prettier

### Notifications

See [setup instructions](/notifications/README.md)

## Technologies Used

1. Backend: FastApi
2. Frontend: React
3. Notifications: Novu
