def build_reactive_defense(self, game_state):
    """
    This function builds reactive defenses based on where the enemy scored on us from.
    We can track where the opponent scored by looking at events in action frames
    as shown in the on_action_frame function
    """
    for location in self.scored_on_locations:
        # Build destructor one space above so that it doesn't block our own edge spawn locations
        build_location = [location[0], location[1] + 1]
        game_state.attempt_spawn(DESTRUCTOR, build_location)

def build_defences(self, game_state):
    """
    Build basic defenses using hardcoded locations.
    Remember to defend corners and avoid placing units in the front where enemy EMPs can attack them.
    """
    # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
    # More community tools available at: https://terminal.c1games.com/rules#Download

    # Place destructors that attack enemy units
    destructor_locations = [[0, 13], [27, 13], [8, 11], [19, 11], [13, 11], [14, 11]]
    # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
    game_state.attempt_spawn(DESTRUCTOR, destructor_locations)

    # Place filters in front of destructors to soak up damage for them
    filter_locations = [[8, 12], [19, 12]]
    game_state.attempt_spawn(FILTER, filter_locations)

