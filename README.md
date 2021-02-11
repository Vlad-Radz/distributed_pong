# Distributed pong

This project shows how a famous game Pong can be created using asynchronous & socket programming in Python.

## Prerequisites for the project

- Crying newborn;
- max. 4 hours of sleep;
- no experience developing games;
- very good coffee without caffeine (so not really useful, but still tasty).

## Results, or why does this codebase suck
- Acceptance criteria:
    - I refused on 4 players, and concentrated on 2 (acceptance criteria not fulfilled);
- Bugs:
    - **BUG**: my implementation has a problem, that I don't assure, that all players subscribed to the necessary topics in
    message broker and thus can miss messages --> count can differ on diff. hosts;
    - **BUG**: what if a player connects to server, and then leaves again?
    - **BUG**: if connection with one host was lost, I don't see that on other host.
- Environment:
    - no proper deployment; I tried to do it with Docker, but lacked time for this. My attempts are in a separate branch.
    For now you need to do manual setup.
    - No automated dependency management.
    - no formatter (like `black`), `linter`, `isort` and `mypy` run;
    - Too few docstring;
    - no tests written (I love `pytest`, and contributed to a couple of projects with it, but am not sure how to test games);
    - repo structure is bad (I actually like DDD - just fyi).
- Code smells:
    - use plain `print()` instead of proper logger (I would probably use `structlog`)
    - division of concerns is violated in some places.

## Was anything achieved at all?
1. Orchestarting server works well;
2. Real-time communication over message broker (RabbitMQ) worked;
3. Some design decisions might be not that bad.
4. Synchronization of paddles works: what I do from one host, is shown on the other.
5. Also ball has same movement trajectory on both hosts.

## Architecture of the system
1. RabbitMQ runs on a server. It will be used to send information about moves of paddles (and in the future same should
be done for the ball - otherwise it doesn't work).
2. `server.py` starts listening to a socket and accepting connections.
3. `server.py` gives unique ID and starting coordinates for a paddle for each new connection
4. One connection is one instance of `run.py`, which is connecting to socket of `server.py`, getting ID and
starting coordinates anf afterwards pulling the socket for new data from the server.
5. After required number of players were connected (e.g. 2), server sends full list of players (with their IDs and
starting coordinates for paddles) to each connection. The role of the server finished with that
(in current implementation).
6. ID given by server is used as topic in message broker (in our case - RabbitMQ). That means, that each connection
(instance of `run.py`) uses own ID for sending own moves, and subscribes to topics of other connections to get moves of
other players. Connection is listening for the topics in background (implemented using `threading` and `asyncio`).
7. `pygame` is being rendered on each instance.  

## Deployment
1. Setup rabbitmq using docker - run on your localhost.
    - Using following docker command:
        - Windows: `docker run --rm -it -d --hostname my-rabbit --name my-rabbit -p 15672:15672 -p 5672:5672 rabbitmq:3-management`
        - Linux (Ubuntu): `sudo docker run --rm -it -d --hostname my-rabbit --name my-rabbit -p 15672:15672 -p 5672:5672 rabbitmq:3-management`
    - Afterwards you can check the RabbitMQ dashboard under `localhost:15672`, login with user `guest`, password: `guest`.
2. Install dependencies from requirements.txt on same host;
3. Run server.py on same host, using 2 arguments in CLI: host (your local IPV4) and port (5555);
4. Run run.py on same host, using 2 arguments in CLI: host (your local IPV4) and port (5555);
5. Run run.py on a different host, using 2 arguments in CLI: host (your local IPV4 from your 1st host) and port (5555).

## References
For game objects and `game.py` I heavily used codebase from https://www.101computing.net/pong-tutorial-using-pygame-adding-a-scoring-system/.
Also I was inspired by socket implementation of https://github.com/techwithtim/Network-Game-Tutorial.

## Next steps
I always thought that games as learning method is lame, until this one. So I would like to continue working on this project,
and make a useful tutorial for others about distributed systems and how to build them in Python.

My plan:
- Fix the bugs - make the game run;
- Decide whether all data except own moves of a player should come centralized (from a server), or P2P 
(also using consensus finding to determine, who starts the game);
- Check diff. modes in RabbitMQ and demonstrate pros and cons of each;
- Build abstraction from implementation of communication between players - can be P2P or via dispatcher, using
message broker or another technology. Use DDD and ports & adapters design pattern;
- Try diff. implementation of communication: websockets, socket.io, ...;
- Fix communication between containers & enable GUI app running inside. Check diff. networking possibilities.
