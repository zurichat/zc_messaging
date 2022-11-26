# ZC Notifications

This repository contains the code for the Novu server used for handling notifications.

## Requirements

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/gettingstarted/)

## Setup

1. Clone the repository

```shell
git clone https://github.com/zurichat/zc_messaging
cd notifications
```

2. Setup environment variables. Modify as necessary.

```shell
cp .env.example .env
```

3. Start Novu server and dependencies with Compose.

```shell
docker compose up
```
