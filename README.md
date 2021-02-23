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
    - **BUG**: sometimes game starts on one host (for one player), but not on another host (another player).
    - **BUG**: my implementation has a problem, that I don't assure, that all players subscribed to the necessary topics in
    message broker and thus can miss messages --> count can differ on diff. hosts;
    - **BUG**: what if a player connects to server, and then leaves again?
    - **BUG**: if connection with one host was lost, I don't see that on other host.
    - **BUG**: problem with the ball: its trajctory is calculated on each host separately - so it can easily happen,
    that game will be not synchronized on diff. hosts --> should be calculated on one of the players, or on server.
- Environment:
    - you should run server and rabbitmq on same host, otherwise it will not work;
    - no formatter (like `black`), `linter`, `isort` and `mypy` run yet;
    - Too few docstring;
    - no tests written (I love `pytest`, and contributed to a couple of projects with it, but am not sure how to test games);
    - repo structure is bad (I actually like DDD - just fyi).
- Code smells:
    - use plain `print()` instead of proper logger (I would probably use `structlog`)
    - division of concerns is violated in some places. In general bad design of the codebase, although I fixed some issues
    (e.g. a violation of the Law of Demeter in one place).
- Security: 
    - using `pickle` is not safe, if no encrnypted network connection used, because arbitraty code can be executed while unpickling - I just wanted to implement something fast & easy (or quick & dirty?). Instead protobuf, MessagePack or something else should be used.

## Was anything achieved at all?
1. Orchestarting server works well;
2. Real-time communication over message broker (RabbitMQ) works;
3. Some design decisions might be not that bad: immutable DTOs, explicit dependency injection.
4. Synchronization of paddles works: what I do from one host, is shown on the other.
5. Also ball has same movement trajectory on both hosts.
6. Deployment is done pretty fency (although, there are some bugs).
5. Also ball has same movement trajectory on both hosts, and - with some luck - its position is 1:1 same for both players.
6. Nice waiting windows for the game (I have a good taste for design).

## Architecture of the system: current and future
1. RabbitMQ runs on a server. It will be used to send information about moves of paddles (and in the future same should be done for the ball - otherwise it doesn't work).
2. `server.py` starts listening to a socket and accepting connections.
3. `server.py` gives unique ID and starting coordinates for a paddle for each new connection
4. One connection is one instance of `run.py`, which is connecting to socket of `server.py`, getting ID and starting coordinates anf afterwards pulling the socket for new data from the server.
5. After required number of players were connected (e.g. 2), server sends full list of players (with their IDs and starting coordinates for paddles) to each connection. The role of the server finished with that (in current implementation).
6. ID given by server is used as topic in message broker (in our case - RabbitMQ). That means, that each connection (instance of `run.py`) uses own ID for sending own moves, and subscribes to topics of other connections to get moves of other players. Connection is listening for the topics in background (implemented using `threading` and `asyncio`).
7. `pygame` is being rendered on each instance.  

### Consistency
For this prototype no real consistency model was implemented. But a distributed real-time system like this needs one, so I made some thoughts on how it could work.
1. Right now changes in coordinates of the ball are done on clients' side: each client get starting position for own paddle, trajectory of the ball is calculated locally on each client following some defined (equal for all clients) rules. When own paddle changes position ("up" or "down"), this change is transmitted to other clients, and they recalculate position of that client locally. __Possible problems__: latency, caused by network or other reasons, can lead to diff. image and thus trajectory of the ball on diff. clients.
2. That's why I thought, that maybe it makes sense, if client only presses button for moving own paddle, and everything else is done on server side. A client moves own paddle, the state changes ("up" or "down") of each client are being transmitted to the server, which calculates new positions of paddles, and depending on them calculates position of the ball in each moment of time. Then it transmits positions of all objects to all clients, and they get a new rendered image. __Possible problems__: latency issues can still cause wrong state of the game, since server just consumes the events with state changes, without checking possible problems on clients' side. This issue can be solved by `event sourcing` pattern: each actor (each client and the server) has own database, where all changes for the object that this actor is responsible for (one of the paddles or the ball) are recorded, with timestamps (absolute of relative - offset). This track could be used for later recalculation of results by analyzing all moves afterwards. But this could mean, that if one the players thought that it won, it can turn out later that it actually lost, which would mean a bad user experience. Also, if there were latency issues, and it turned out, that actually a player moved its paddle to the position, where the ball was, but the server didn't get that move on the right time, that would mean that the later positions of the ball calculated originally by the server, don't make any sense. So this option is not really valid, but if we want to go for it, then the mentioned recalculation could be implemented using `numba`, for example. 
3. Then I thought, that using a time __offset__ since the start moment can be used: players send not only own moves, but also time offset since the game start, to the server. If there was no move, players still send a message - just to let server know, that it is "alive". If server doesn't get message for some time, it stops the game - other players get notification. If server gets messages from all players, but e.g. for one of them the server sees, that its latest message came with latency, it can notify other players, and game will be freezed, until all players are on same lane again.
4. After all of that I thought, that actually we generate additional latency artificially by sending to many messages to the server. So do we actually need the server to coordinate the game? Maybe players can exchange information about own moves and offset directly, P2P - and have a better __data locality__? But that would work only if the rules for calculating the trajectory of the ball are defined. Otherwise we would still need the server to calculate trajectory of the ball and send its coordinates to the players.

Also consistency depends on whether the synchronized start of the game can be enabled. This is important inependent on wether we use time offset for checking positions or not. Synchronized start can be enabled using `2-phase commit (2PC)`, which is not beloved, because it's blocking and thus slow - but in our case that can be tolerated.

### Durability

I don't know yet, if that would be needed, but we could write all moves (for all the players and the ball) to the database (implementing the `event sourcing` pattern), or databases - one for each player and server (if it is used for calculation of bal trajectory). It could be a timeseries DB, but for our case the main thing is to probably have a very leightweight DB, maybe even like `SQLite`.

### What else can be changed in the architecture?

`Actor model` could be used, since we make our system event-driven. But for this the whole code should be refactored (well, it should be done in any case), and maybe it doesn't really make sense, if our players are not on the same host.

## Deployment
To run the solution, you don't need to set up virtual environment etc. You just execute 3 PEX (Python EXecutable) files, which are already pre-built for you and are located under `dist/game/`. For better convenience, you can just execute 4 command from the `Makefile`:
1. `make setup_rabbitmq` - to set up message broker. Wait or a couple of minutes for container to be set up fully. You can check if RabbitMQ is running, manually on `localhost:15672` (user: `guest`, password: `guest`).
2. `make run_server` - to run server.
3. `make run_client2` - to run one client.
4. `make run_client2` - to run another client.

You should execute all 4 commands on same host! Otherwise it will not work (yes, it's not optimal). And there is another bug: sometimes you order is important: you cannot run `client1.pex` before `client2.pex` (yes, it's yet another bug).

### Prerequisites
Python 3.7+, pip and docker should be installed.

### Testing

Run the following command in the root of the repo: `PYTHONPATH=. pytest . -vv`

## References
For game objects and `game.py` I heavily used codebase from https://www.101computing.net/pong-tutorial-using-pygame-adding-a-scoring-system/.
Also I was inspired by socket implementation of https://github.com/techwithtim/Network-Game-Tutorial.

## Next steps
I always thought that games as learning method is lame, until this one. So I would like to continue working on this project,
and make a useful tutorial for others about distributed systems and how to build them in Python.

My plan:
- Fix the bugs;
- Decide whether all data except own moves of a player should come centralized (from a server), or P2P (also using consensus finding to determine, who starts the game);
- Check diff. modes in RabbitMQ and demonstrate pros and cons of each;
- Build abstraction from implementation of communication between players - can be P2P or via dispatcher, using message broker or another technology. Use DDD and ports & adapters design pattern, abstract base classes;
- Try diff. implementation of communication: websockets, socket.io, Pulsar, ...;
- Try to run in Docker containers: gix communication between containers & enable GUI app running inside (is not so easy). Check diff. networking possibilities.
