def stall_with_scramblers(self, game_state):
    """
    Send out Scramblers at random locations to defend our base from enemy moving units.
    """
    # We can spawn moving units on our edges so a list of all our edge locations
    friendly_edges = game_state.game_map.get_edge_locations(
        game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

    # Remove locations that are blocked by our own firewalls
    # since we can't deploy units there.
    deploy_locations = self.filter_blocked_locations(friendly_edges, game_state)

    # While we have remaining bits to spend lets send out scramblers randomly.
    while game_state.get_resource(game_state.BITS) >= game_state.type_cost(SCRAMBLER) and len(deploy_locations) > 0:
        # Choose a random deploy location.
        deploy_index = random.randint(0, len(deploy_locations) - 1)
        deploy_location = deploy_locations[deploy_index]

        game_state.attempt_spawn(SCRAMBLER, deploy_location)
        """
        We don't have to remove the location since multiple information 
        units can occupy the same space.
        """


def emp_line_strategy(self, game_state):
    """
    Build a line of the cheapest stationary unit so our EMP's can attack from long range.
    """
    # First let's figure out the cheapest unit
    # We could just check the game rules, but this demonstrates how to use the GameUnit class
    stationary_units = [FILTER, DESTRUCTOR, ENCRYPTOR]
    cheapest_unit = FILTER
    for unit in stationary_units:
        unit_class = gamelib.GameUnit(unit, game_state.config)
        if unit_class.cost < gamelib.GameUnit(cheapest_unit, game_state.config).cost:
            cheapest_unit = unit

    # Now let's build out a line of stationary units. This will prevent our EMPs from running into the enemy base.
    # Instead they will stay at the perfect distance to attack the front two rows of the enemy base.
    for x in range(27, 5, -1):
        game_state.attempt_spawn(cheapest_unit, [x, 11])

    # Now spawn EMPs next to the line
    # By asking attempt_spawn to spawn 1000 units, it will essentially spawn as many as we have resources for
    game_state.attempt_spawn(EMP, [24, 10], 1000)


def least_damage_spawn_location(self, game_state, location_options):
    """
    This function will help us guess which location is the safest to spawn moving units from.
    It gets the path the unit will take then checks locations on that path to
    estimate the path's damage risk.
    """
    damages = []
    # Get the damage estimate each path will take
    for location in location_options:
        path = game_state.find_path_to_edge(location)
        damage = 0
        for path_location in path:
            # Get number of enemy destructors that can attack the final location and multiply by destructor damage
            damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR,
                                                                                         game_state.config).damage
        damages.append(damage)

    # Now just return the location that takes the least damage
    return location_options[damages.index(min(damages))]