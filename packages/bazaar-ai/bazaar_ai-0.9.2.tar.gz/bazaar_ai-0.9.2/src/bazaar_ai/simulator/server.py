import asyncio
import json
import websockets
import os
import time
import importlib.util
from pathlib import Path
from bazaar_ai.bazaar import BasicBazaar
from bazaar_ai.trader import Trader
from bazaar_ai.goods import GoodType
from bazaar_ai.coins import BonusType

class GameServer:
    def __init__(self, agents_folder='agents'):
        self.game = None
        self.clients = set()
        self.running = False
        self.scores_calculated = False
        self.play_speed = 1.0  # seconds between moves
        self.agents_folder = agents_folder
        self.available_agents = {}
        self.game_loaded = False
        self.build_mode = True  # Start in build mode
        self.load_available_agents()
        
    def load_available_agents(self):
        """Scan both built-in and user agents folders for available agent classes"""
        
        # First, load built-in agents from the package
        builtin_agents_path = Path(__file__).parent / 'agents'
        if builtin_agents_path.exists():
            for file in builtin_agents_path.glob('*.py'):
                if file.name.startswith('_'):
                    continue
                
                try:
                    # Load the module
                    spec = importlib.util.spec_from_file_location(file.stem, file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find Trader subclasses in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, Trader) and 
                            attr is not Trader):
                            self.available_agents[attr.__name__] = attr
                            print(f"Loaded built-in agent: {attr.__name__}")
                except Exception as e:
                    print(f"Error loading built-in agent {file.name}: {e}")
        
        # Then, load user agents from the working directory
        agents_path = Path(self.agents_folder)
        if not agents_path.exists():
            agents_path.mkdir()
            print(f"Created user agents folder at {agents_path}")
        else:
            for file in agents_path.glob('*.py'):
                if file.name.startswith('_'):
                    continue
                
                try:
                    # Load the module
                    spec = importlib.util.spec_from_file_location(file.stem, file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    # Find Trader subclasses in the module
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if (isinstance(attr, type) and 
                            issubclass(attr, Trader) and 
                            attr is not Trader):
                            self.available_agents[attr.__name__] = attr
                            print(f"Loaded user agent: {attr.__name__} from {file.name}")
                except Exception as e:
                    print(f"Error loading user agent {file.name}: {e}")
        
        if not self.available_agents:
            print("No agents found. Using default Trader class.")
            self.available_agents['DefaultTrader'] = Trader
        
    def create_game(self, trader1, trader2):
        """Create a new game instance"""
        traders = [trader1, trader2]
        seed = int(time.time() * 1000) 
        self.game = BasicBazaar(seed=seed, players=traders)
        self.scores_calculated = False
        self.game_loaded = True
        self.build_mode = False  # Switch to play mode after building
        
    def get_game_state(self):
        """Convert game state to JSON-serializable format"""
        if not self.game:
            # Return empty state when no game loaded
            return {
                'round': 0,
                'market': {},
                'marketCoins': {},
                'marketBonusCounts': {},
                'players': [
                    {
                        'name': 'Agent 1',
                        'goods': {},
                        'coins': {},
                        'bonusCoins': {},
                        'bonusCounts': {},
                        'score': 0
                    },
                    {
                        'name': 'Agent 2',
                        'goods': {},
                        'coins': {},
                        'bonusCoins': {},
                        'bonusCounts': {},
                        'score': 0
                    }
                ],
                'currentPlayer': None,
                'deckSize': 0,
                'isTerminal': False,
                'scoresCalculated': False,
                'lastAction': None,
                'hasStarted': False,
                'gameLoaded': False,
                'buildMode': self.build_mode
            }
            
        state = self.game.state
        is_terminal = self.game.terminal(state)
        
        # Convert market goods to dict
        market_goods = {}
        for good_type in GoodType:
            count = state.goods[good_type]
            if count > 0:
                market_goods[good_type.name] = count
        
        # Get player data
        players_data = []
        for player in self.game.players:
            player_goods = {}
            for good_type in GoodType:
                count = state.player_goods[player][good_type]
                if count > 0:
                    player_goods[good_type.name] = count
            
            # Get player coins
            player_coins = {}
            for good_type in GoodType:
                coins = state.player_coins[player].goods_coins[good_type]
                if coins:
                    player_coins[good_type.name] = coins
            
            # Get bonus coins - show counts, not values during game
            bonus_coins = {}
            bonus_counts = {}
            for bonus_type in BonusType:
                coins = state.player_coins[player].bonus_coins[bonus_type]
                count = len(coins)
                if count > 0:
                    bonus_counts[bonus_type.name] = count
                    if is_terminal and self.scores_calculated:
                        # Only show actual values after calculation
                        bonus_coins[bonus_type.name] = coins
                    else:
                        # Show placeholder during game
                        bonus_coins[bonus_type.name] = [bonus_type.value] * count
            
            # Calculate score - only goods coins during game
            score = sum(sum(coins) for coins in state.player_coins[player].goods_coins.values())
            if is_terminal and self.scores_calculated:
                # Add bonus coins and camel bonus only after calculation
                score += sum(sum(coins) for coins in state.player_coins[player].bonus_coins.values())
                # Add camel bonus if applicable
                other_player = self.game.state.get_non_actor() if player == self.game.state.actor else self.game.state.actor
                if state.player_goods[player][GoodType.CAMEL] > state.player_goods[other_player][GoodType.CAMEL]:
                    score += state.camel_bonus
            
            players_data.append({
                'name': player.name,
                'goods': player_goods,
                'coins': player_coins,
                'bonusCoins': bonus_coins,
                'bonusCounts': bonus_counts,
                'score': score
            })
        
        # Get market coins including bonus stacks
        market_coins = {}
        for good_type in GoodType:
            if good_type != GoodType.CAMEL:
                coins = state.coins.goods_coins[good_type]
                if coins:
                    market_coins[good_type.name] = coins
        
        # Get bonus coin counts (not values)
        market_bonus_counts = {}
        for bonus_type in BonusType:
            count = len(state.coins.bonus_coins[bonus_type])
            if count > 0:
                market_bonus_counts[bonus_type.name] = count
        
        # Get last action info
        last_action = None
        if state.action:
            action = state.action
            action_data = {
                'actor': action.actor.name,
                'type': action.trader_action_type.name
            }
            
            if hasattr(action, '_sell'):
                action_data['goodType'] = action._sell.name
                action_data['count'] = action._count
            elif hasattr(action, '_take'):
                action_data['goodType'] = action._take.name
                action_data['count'] = action._count
            else:
                # Trade action
                offered = {}
                requested = {}
                for good_type in GoodType:
                    if action.offered_goods[good_type] > 0:
                        offered[good_type.name] = action.offered_goods[good_type]
                    if action.requested_goods[good_type] > 0:
                        requested[good_type.name] = action.requested_goods[good_type]
                action_data['offered'] = offered
                action_data['requested'] = requested
            
            last_action = action_data
        
        return {
            'round': self.game.round,
            'market': market_goods,
            'marketCoins': market_coins,
            'marketBonusCounts': market_bonus_counts,
            'players': players_data,
            'currentPlayer': state.actor.name if state.actor else None,
            'deckSize': len(state.reserved_goods),
            'isTerminal': is_terminal,
            'scoresCalculated': self.scores_calculated,
            'lastAction': last_action,
            'hasStarted': self.game.round > 0,
            'gameLoaded': self.game_loaded,
            'buildMode': self.build_mode
        }
    
    async def broadcast_state(self):
        """Send current game state to all connected clients"""
        if self.clients:
            state = self.get_game_state()
            if state:
                message = json.dumps(state)
                await asyncio.gather(
                    *[client.send(message) for client in self.clients],
                    return_exceptions=True
                )
    
    async def broadcast_agents(self):
        """Send list of available agents to all connected clients"""
        if self.clients:
            message = json.dumps({
                'agents': list(self.available_agents.keys())
            })
            await asyncio.gather(
                *[client.send(message) for client in self.clients],
                return_exceptions=True
            )
    
    async def step_game(self):
        """Execute one step of the game"""
        if not self.game or self.game.terminal(self.game.state):
            return
        
        # Get current actor and their legal actions
        actor = self.game.state.actor
        legal_actions = self.game.all_actions(actor, self.game.state)
        observation = self.game.observe(actor, self.game.state)
        
        # Actor selects action
        action = actor.select_action(legal_actions, observation, self.game.simulate_action)
        
        # Save old state
        self.game.old_state = self.game.state.clone()
        # Apply action
        self.game.state = self.game.apply_action(self.game.state.clone(), action.clone())
        # Update rewards for all players
        for player in self.game.players:
            has_acted = player == self.game.old_state.actor
            old_observation = self.game.observe(player, self.game.old_state)
            current_observation = self.game.observe(player, self.game.state)
            environment_reward = self.game.calculate_reward(
                player.clone(),
                self.game.old_state.clone(),
                self.game.state.clone()
            )
            player.calculate_reward(
                old_observation.clone(),
                current_observation.clone(),
                has_acted,
                environment_reward
            )
        
        self.game.round += 1
        await self.broadcast_state()
    
    async def handle_client(self, websocket):
        """Handle a new WebSocket connection"""
        self.clients.add(websocket)
        print(f"Client connected. Total clients: {len(self.clients)}")
        
        try:
            # Send initial state and available agents
            await self.broadcast_agents()
            await self.broadcast_state()
            
            # Handle incoming messages
            async for message in websocket:
                data = json.loads(message)
                command = data.get('command')
                
                if command == 'step':
                    if not self.running:  # Only allow step when paused
                        await self.step_game()
                elif command == 'play':
                    self.running = True
                elif command == 'pause':
                    self.running = False
                elif command == 'calculate':
                    self.scores_calculated = True
                    await self.broadcast_state()
                elif command == 'setSpeed':
                    speed = data.get('speed', 1000)
                    self.play_speed = speed / 1000.0  # Convert ms to seconds
                    print(f"Speed set to {self.play_speed}s per move")
                elif command == 'getAgents':
                    await self.broadcast_agents()
                elif command == 'selectAgents':
                    agent1_name = data.get('agent1')
                    agent2_name = data.get('agent2')
                    
                    if agent1_name in self.available_agents and agent2_name in self.available_agents:
                        Agent1Class = self.available_agents[agent1_name]
                        Agent2Class = self.available_agents[agent2_name]
                        
                        # Create NEW instances with different seeds and names
                        trader1 = Agent1Class(seed=356, name=f"{agent1_name}_1")
                        trader2 = Agent2Class(seed=789, name=f"{agent2_name}_2")
                        
                        # Reset any previous game state
                        self.running = False
                        self.scores_calculated = False
                        
                        self.create_game(trader1, trader2)
                        await self.broadcast_state()
                        print(f"Game started with {agent1_name} vs {agent2_name}")
                    else:
                        print(f"Invalid agents selected: {agent1_name}, {agent2_name}")
                elif command == 'reset':
                    # Reset to empty state - no game loaded
                    self.game = None
                    self.running = False
                    self.scores_calculated = False
                    self.game_loaded = False
                    self.build_mode = True  # Back to build mode
                    await self.broadcast_state()
                    print("Game reset - waiting for agent selection")
                    
        except websockets.exceptions.ConnectionClosed:
            print("Client disconnected")
        finally:
            self.clients.remove(websocket)
    
    async def auto_play(self):
        """Automatically step through the game when playing"""
        game_was_running = False
        while True:
            if self.running and self.game and self.game_loaded and not self.game.terminal(self.game.state):
                await self.step_game()
                await asyncio.sleep(self.play_speed)
                game_was_running = True
            else:
                # Stop running if game ends - only broadcast once
                if game_was_running and self.game and self.game.terminal(self.game.state):
                    self.running = False
                    await self.broadcast_state()
                    game_was_running = False  # Only broadcast once
            await asyncio.sleep(0.1)
    
    async def start_server(self, host='localhost', port=8765):
        """Start the WebSocket server"""
        print(f"Starting server on ws://{host}:{port}")
        print(f"Available agents: {list(self.available_agents.keys())}")
        
        # Create auto-play task
        auto_play_task = asyncio.create_task(self.auto_play())
        
        # Start WebSocket server
        async with websockets.serve(self.handle_client, host, port):
            await asyncio.Future()  # Run forever


def main():
    """Main entry point"""
    # Create server
    server = GameServer(agents_folder='agents')
    
    # Don't create a default game - wait for user to load agents
    
    # Start server
    asyncio.run(server.start_server())


if __name__ == "__main__":
    main()