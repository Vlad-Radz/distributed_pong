# Distributed pong

This project shows how a famous game Pong can be created using asynchronous & socket programming in Python.

## Prerequisites

- Crying newborn;
- max. 4 hours of sleep;
- no experience developing games;
- very good coffee without caffeine (so not really useful, but still tasty).

## Results, or why this codebase sucks
- Acceptance criteria:
    - I refused on 4 players, and concentrated on 2 (acceptance criteria not fulfilled);
    - Even with 2 players the game doesn't work: what I do from one host, is not shown on the other.
- Bugs:
    - **BUG**: my implementation has a problem, that I don't assure, that all players subscribed to the necessary topics in
    message broker and thus can miss messages --> count can differ on diff. hosts;
    - **BUG**: I worked for the 1st time with `pygame` and didn't know that ball is going to fly
    into diff. directions on diff. hosts --> so game looks actually different on 2 hosts;
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

## Deployment
1. Setup rabbitmq using docker - run on your localhost;
2. Install dependencies from requirements.txt on same host;
3. Run server.py on same host, using 2 arguments in CLI: host (your local IPV4) and port (5555);
4. Run run.py on same host, using 2 arguments in CLI: host (your local IPV4) and port (5555);
5. Run run.py on a different host, using 2 arguments in CLI: host (your local IPV4 from your 1st host) and port (5555).

## References
For game objects and `game.py` I heavily used codebase from https://www.101computing.net/pong-tutorial-using-pygame-adding-a-scoring-system/.
