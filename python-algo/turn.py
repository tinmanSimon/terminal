def on_turn(self, turn_state):
    """
    This function is called every turn with the game state wrapper as
    an argument. The wrapper stores the state of the arena and has methods
    for querying its state, allocating your current resources as planned
    unit deployments, and transmitting your intended deployments to the
    game engine.
    """
    game_state = gamelib.GameState(self.config, turn_state)
    gamelib.debug_write('Performing turn {} of your custom algo strategy'.format(game_state.turn_number))
    game_state.suppress_warnings(True)  # Comment or remove this line to enable warnings.

    self.starter_strategy(game_state)

    game_state.submit_turn()