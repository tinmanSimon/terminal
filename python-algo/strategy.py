def starter_strategy(self, game_state):
    """
    For defense we will use a spread out layout and some Scramblers early on.
    We will place destructors near locations the opponent managed to score on.
    For offense we will use long range EMPs if they place stationary units near the enemy's front.
    If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
    """
    # First, place basic defenses
    self.build_defences(game_state)
    # Now build reactive defenses based on where the enemy scored
    self.build_reactive_defense(game_state)

    # If the turn is less than 5, stall with Scramblers and wait to see enemy's base
    if game_state.turn_number < 5:
        self.stall_with_scramblers(game_state)
    else:
        # Now let's analyze the enemy base to see where their defenses are concentrated.
        # If they have many units in the front we can build a line for our EMPs to attack them at long range.
        if self.detect_enemy_unit(game_state, unit_type=None, valid_x=None, valid_y=[14, 15]) > 10:
            self.emp_line_strategy(game_state)
        else:
            # They don't have many units in the front so lets figure out their least defended area and send Pings there.

            # Only spawn Ping's every other turn
            # Sending more at once is better since attacks can only hit a single ping at a time
            if game_state.turn_number % 2 == 1:
                # To simplify we will just check sending them from back left and right
                ping_spawn_location_options = [[13, 0], [14, 0]]
                best_location = self.least_damage_spawn_location(game_state, ping_spawn_location_options)
                game_state.attempt_spawn(PING, best_location, 1000)

            # Lastly, if we have spare cores, let's build some Encryptors to boost our Pings' health.
            encryptor_locations = [[13, 2], [14, 2], [13, 3], [14, 3]]
            game_state.attempt_spawn(ENCRYPTOR, encryptor_locations)