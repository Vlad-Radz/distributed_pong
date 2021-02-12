pex . -v --disable-cache -r game/requirements.txt -e game.run -o client.pex --python=python3

./pants package game/run.py
./pants run game/run.py
