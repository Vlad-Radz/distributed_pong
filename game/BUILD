python_requirements()

python_library(
  name='game',
  sources=[
    '*.py', 'game_objects/*.py',
    '!*_test.py', '!test_*.py', '!conftest.py'
    ],
  dependencies=[":image"]
)

resources(
    name="image",
    sources=["static/background_game_start.gif"],
)

pex_binary(
  name="client",
  entry_point="run.py",
  dependencies=[":game"]
)

pex_binary(
  name="server",
  entry_point="server.py",
)
