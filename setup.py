from setuptools import setup                                                                                                                                                              

setup(
    name='distributed_pong',
    version='0.1',
    packages=["game", "game/game_objects"],
    package_data={'game': ['static/background_game_start.gif']},
    include_package_data=True
)