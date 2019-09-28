import gamelib
import random
import math
import warnings
from sys import maxsize
import json


"""
Most of the algo code you write will be in this file unless you create new
modules yourself. Start by modifying the 'on_turn' function.

Advanced strategy tips: 

  - You can analyze action frames by modifying on_action_frame function

  - The GameState.map object can be manually manipulated to create hypothetical 
  board states. Though, we recommended making a copy of the map to preserve 
  the actual current map state.
"""

class AlgoStrategy(gamelib.AlgoCore):
    def __init__(self):
        super().__init__()
        seed = random.randrange(maxsize)
        random.seed(seed)
        gamelib.debug_write('Random seed: {}'.format(seed))

    def on_game_start(self, config):
        """
        Read in config and perform any initial setup here
        """
        gamelib.debug_write('Configuring your custom algo strategy...')
        self.config = config
        global FILTER, ENCRYPTOR, DESTRUCTOR, PING, EMP, SCRAMBLER
        FILTER = config["unitInformation"][0]["shorthand"]
        ENCRYPTOR = config["unitInformation"][1]["shorthand"]
        DESTRUCTOR = config["unitInformation"][2]["shorthand"]
        PING = config["unitInformation"][3]["shorthand"]
        EMP = config["unitInformation"][4]["shorthand"]
        SCRAMBLER = config["unitInformation"][5]["shorthand"]
        # This is a good place to do initial setup
        self.scored_on_locations = []
        self.fortify_destructor_locations=[]
        self.fortify_filter_locations=[]
        self.attack_right=True
        self.transition=False
        self.attack=False



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
        game_state.suppress_warnings(True)  #Comment or remove this line to enable warnings.

        if game_state.turn_number%10 <=4:
            self.attack_right=False
        else:
            self.attack_right=True

        if game_state.turn_number%10==0 or game_state.turn_number%10==5:
            self.transition=True
        else:
            self.transition=False

        if game_state.turn_number%2==0:
            self.attack=True
        else:
            self.attack=False

        self.starter_strategy(game_state)

        game_state.submit_turn()



    """
    NOTE: All the methods after this point are part of the sample starter-algo
    strategy and can safely be replaced for your custom algo.
    """


    def starter_strategy(self, game_state):
        """
        For defense we will use a spread out layout and some Scramblers early on.
        We will place destructors near locations the opponent managed to score on.
        For offense we will use long range EMPs if they place stationary units near the enemy's front.
        If there are no stationary units to attack in the front, we will send Pings to try and score quickly.
        """
        # Defend

        # First, place basic defenses
        self.build_defences(game_state)
        # Now build reactive defenses based on where the enemy scored
        self.build_reactive_defense(game_state)

        # Attack
        self.ping_rush(game_state)

    def build_defences(self, game_state):
        """
        Build basic defenses using hardcoded locations.
        Remember to defend corners and avoid placing units in the front where enemy EMPs can attack them.
        """
        # Useful tool for setting up your base locations: https://www.kevinbai.design/terminal-map-maker
        # More community tools available at: https://terminal.c1games.com/rules#Download

        # Place destructors that attack enemy units
        initial_destructor_locations = [[3, 12], [6, 12], [9, 12], [12, 12], [15, 12], [18, 12], [21, 12], [24, 12]]

        # attempt_spawn will try to spawn units if we have resources, and will check if a blocking unit is already there
        game_state.attempt_spawn(DESTRUCTOR, initial_destructor_locations)

        # Place filters in front of destructors to soak up damage for them

        # Place encryptors
        initial_encrypter_locations = [[11, 5], [12, 5], [11, 4], [12, 4], [9, 7], [10, 7], [9, 6], [10, 6],
                                       [15, 5], [15, 4], [16, 5], [16, 4], [12, 8], [12, 7], [13, 8], [13, 7],
                                       [14, 8], [14, 7], [15, 8], [15, 7], [15, 5], [15, 4], [16, 5], [16, 4],
                                       [17, 7], [17, 6], [18, 7], [18, 6], [11, 2], [12, 2], [12, 1], [13, 2], [13, 1]]
        game_state.attempt_spawn(ENCRYPTOR, initial_encrypter_locations)


    def ping_rush(self, game_state):
        '''
        We simply spawn a bunch of pings on a route that passes through encryptors
        '''
        if self.attack_right and not self.transition:
            rush_location = [10, 3]
        elif self.attack_right:
            rush_location = [17, 3]
        elif self.transition:
            rush_location = [10, 3]
        else:
            rush_location = [17,3]

        if self.attack:
            while game_state.can_spawn(PING, rush_location):
                game_state.attempt_spawn(PING, rush_location)

    def build_reactive_defense(self, game_state):
        """
        This function builds reactive defenses based on where the enemy scored on us from.
        We can track where the opponent scored by looking at events in action frames
        as shown in the on_action_frame function
        """

        # Get breech locations
        for location in self.scored_on_locations:
            # Build destructor one space above so that it doesn't block our own edge spawn locations
            self.fortify_destructor_locations.append([location[0], location[1]])
            self.fortify_destructor_locations.append([location[0]-1, location[1]])
            self.fortify_destructor_locations.append([location[0]+1, location[1]])
            self.fortify_filter_locations.append([location[0], location[1] + 1])
            self.fortify_filter_locations.append([location[0]-1, location[1] + 1])
            self.fortify_filter_locations.append([location[0]+1, location[1] + 1])

        # Spawn destructors
        for location in self.fortify_destructor_locations:
            if game_state.can_spawn(DESTRUCTOR, location):
                game_state.attempt_spawn(DESTRUCTOR, location)
                self.fortify_destructor_locations.remove(location)

        # Spawn filters
        for location in self.fortify_filter_locations:
            if game_state.can_spawn(FILTER, location):
                game_state.attempt_spawn(FILTER, location)
                self.fortify_filter_locations.remove(location)

        # Define encryptor spawn locations for either attack direction
        attack_right_encryptor_locations = [[14, 3], [10, 4], [10, 5], [13, 6], [12, 6], [15, 9], [16, 9], [16, 10],
                                            [17, 10],
                                            [17, 11], [18, 11], [18, 8], [19, 8],
                                            [19, 9], [20, 9], [20, 10], [21, 10], [14, 2], [15, 3]]
        attack_left_encryptor_locations = [[13, 3], [17, 4], [17, 5], [14, 6], [15, 6], [12, 9], [11, 9], [11, 10],
                                            [10, 10],
                                            [10, 11], [9, 11], [9, 8], [8, 8],
                                            [8, 9], [7, 9], [7, 10], [6, 10], [13, 2], [12, 3]]

        # Spawn encryptors
        if self.attack_right:
            if not self.transition:
                game_state.attempt_spawn(ENCRYPTOR, attack_right_encryptor_locations)
            game_state.attempt_remove(attack_left_encryptor_locations)
        else:
            if not self.transition:
                game_state.attempt_spawn(ENCRYPTOR, attack_left_encryptor_locations)
            game_state.attempt_remove(attack_right_encryptor_locations)


    def stall_with_scramblers(self, game_state):
        """
        Send out Scramblers at random locations to defend our base from enemy moving units.
        """
        # We can spawn moving units on our edges so a list of all our edge locations
        friendly_edges = game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_LEFT) + game_state.game_map.get_edge_locations(game_state.game_map.BOTTOM_RIGHT)

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
                damage += len(game_state.get_attackers(path_location, 0)) * gamelib.GameUnit(DESTRUCTOR, game_state.config).damage
            damages.append(damage)

        # Now just return the location that takes the least damage
        return location_options[damages.index(min(damages))]

    def detect_enemy_unit(self, game_state, unit_type=None, valid_x = None, valid_y = None):
        total_units = 0
        for location in game_state.game_map:
            if game_state.contains_stationary_unit(location):
                for unit in game_state.game_map[location]:
                    if unit.player_index == 1 and (unit_type is None or unit.unit_type == unit_type) and (valid_x is None or location[0] in valid_x) and (valid_y is None or location[1] in valid_y):
                        total_units += 1
        return total_units

    def filter_blocked_locations(self, locations, game_state):
        filtered = []
        for location in locations:
            if not game_state.contains_stationary_unit(location):
                filtered.append(location)
        return filtered

    def on_action_frame(self, turn_string):
        """
        This is the action frame of the game. This function could be called
        hundreds of times per turn and could slow the algo down so avoid putting slow code here.
        Processing the action frames is complicated so we only suggest it if you have time and experience.
        Full doc on format of a game frame at: https://docs.c1games.com/json-docs.html
        """
        # Let's record at what position we get scored on
        state = json.loads(turn_string)
        events = state["events"]
        breaches = events["breach"]
        for breach in breaches:
            location = breach[0]
            unit_owner_self = True if breach[4] == 1 else False
            # When parsing the frame data directly,
            # 1 is integer for yourself, 2 is opponent (StarterKit code uses 0, 1 as player_index instead)
            if not unit_owner_self:
                gamelib.debug_write("Got scored on at: {}".format(location))
                self.scored_on_locations.append(location)
                gamelib.debug_write("All locations: {}".format(self.scored_on_locations))


if __name__ == "__main__":
    algo = AlgoStrategy()
    algo.start()
