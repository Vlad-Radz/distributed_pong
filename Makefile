install_pex:
	pip install pex

build_with_pex_client: install_pex
	pex . -v --disable-cache -r game/requirements.txt -e game.run -o client.pex --python=python3

build_with_pex_server: install_pex
	pex . -v --disable-cache -r game/requirements.txt -e game.run -o server.pex --python=python3

build_with_pants_client:
	./pants package game/run.py

run_with_pants_client:
	./pants run game/run.py

# ##################################

setup_rabbitmq:
	sudo docker run --rm -it -d --hostname my-rabbit --name my-rabbit -p 15672:15672 -p 5672:5672 rabbitmq:3-management

run_server:
	./dist/game/server.pex

run_client1:
	./dist/game/client1.pex

run_client2:
	./dist/game/client2.pex
