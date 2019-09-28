def detect_enemy_unit(self, game_state, unit_type=None, valid_x=None, valid_y=None):
    total_units = 0
    for location in game_state.game_map:
        if game_state.contains_stationary_unit(location):
            for unit in game_state.game_map[location]:
                if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (
                        valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                    total_units += 1
    return total_units


def filter_blocked_locations(self, locations, game_state):
    filtered = []
    for location in locations:
        if not game_state.contains_stationary_unit(location):
            filtered.append(location)
    return filtered