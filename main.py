import pygame
import random
import time
import threading
import queue
import os

# Local imports
from fish import load_fish_tiles, create_fish, Fish
from collision_handler import CollisionHandler
from ui import main_menu, pause_menu, game_over_menu, display_controls
from shark import load_shark_image, spawn_shark, Shark
from area_calculator import AreaCalculator
from sound import init_music, play_music, set_music_volume, pause_music, unpause_music, stop_music

def main():
    # Initialize Pygame
    pygame.init()
    
    # Initialize audio system right at the beginning
    init_music()
    
    # Start background music immediately with looping
    try:
        # The loop parameter -1 means infinite looping
        play_music("assets/sofiathefirst_instrumental.mp3", loop=-1)
        set_music_volume(0.5)  # Set to 50% volume
    except pygame.error as e:
        print(f"Error playing music: {e}")
    
    # Set up display
    # Each tile is 16x16 pixels, and we have 63x50 tiles
    # Real-world dimensions: 630cm x 500cm
    screen_width, screen_height = 1008, 800
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Fish Frenzy")  # Updated to match UI title
    clock = pygame.time.Clock()
    
    # Main game loop with restart functionality
    game_active = True
    game_mode = "auto"  # Default game mode
    
    while game_active:
        result, game_mode = run_game(screen, screen_width, screen_height, clock, game_mode)
        game_active = result

    # Clean up before exit
    pygame.quit()

# Define font 
def get_font(size=24):
    try:
        return pygame.font.Font('assets/pixel_font.otf', size)
    except pygame.error:
        return pygame.font.Font(None, size)  # Use default font if pixel font not found

def run_game(screen, screen_width, screen_height, clock, current_game_mode="auto"):
    # Initialize the collision handler
    collision_handler = CollisionHandler()
    
    # Game state variables
    running = True
    paused = False
    score = 0
    
    # Display the main menu and get game mode
    menu_result, game_mode = main_menu()
    if not menu_result:
        return False, None  # Exit the game if user selects Exit from main menu
    
    # If no game mode was selected but we got here, use previous mode
    if game_mode is None:
        game_mode = current_game_mode
    
    # Load sound effects
    try:
        scream_sounds = [
            pygame.mixer.Sound('assets/scream1.mp3'),
            pygame.mixer.Sound('assets/scream2.mp3')
        ]
    except pygame.error as e:
        print(f"Error loading sound effects: {e}")
        scream_sounds = []
    
    # Load and split the fish tiles
    try:
        fish_list = load_fish_tiles("assets/fish_tiles.png")
    except Exception:
        # Fallback to assets/fish.png if the other path fails
        fish_list = load_fish_tiles("assets/fish.png")
    
    # Load the cliff image and get its rectangle
    try:
        cliff_image = pygame.image.load('assets/cliff.png')
    except pygame.error:
        # Create a placeholder if cliff image can't be loaded
        cliff_image = pygame.Surface((440, 150))
        cliff_image.fill((139, 69, 19))  # Brown color
    
    cliff_rect = pygame.Rect(230, 490, 440, 150)  # Top left corner (x, y, width, height)
    
    # Initialize the area calculator with real-world dimensions
    area_calculator = AreaCalculator(screen_width, screen_height, cliff_rect)
    
    # Initialize area calculation variables
    last_calculation_time = 0
    calculation_interval = 5000  # 5 seconds in milliseconds
    area_results = None

    # Load and scale the map
    try:
        map_image = pygame.image.load("assets/seamap.png")
        map_image = pygame.transform.scale(map_image, (screen_width, screen_height))
    except pygame.error:
        # Create a basic blue background if map can't be loaded
        map_image = pygame.Surface((screen_width, screen_height))
        map_image.fill((0, 120, 215))  # Ocean blue
    
    # Load the shark image and spawn one shark
    shark_image = load_shark_image("assets/shark.png")
    player_controlled = (game_mode == "player")
    shark = spawn_shark(shark_image, screen_width, screen_height, player_controlled)
    
    # Initialize fish list
    fish_objects = []
    
    # Fish counter for unique IDs
    fish_counter = 0
    
    # Initial fish population
    for i in range(10):
        new_fish = create_fish(fish_list, screen_width, screen_height, cliff_rect)
        new_fish.id = fish_counter  # Add a unique ID to each fish
        fish_counter += 1
        fish_objects.append(new_fish)
        print(f"Initial fish #{new_fish.id} created at position ({new_fish.x:.1f}, {new_fish.y:.1f})")
    
    # Set up thread-safe communication for fish generation
    fish_queue = queue.Queue(maxsize=20)
    stop_event = threading.Event()
    
    # Modified fish_generator function for threading
    def fish_generator_thread():
        nonlocal fish_counter
        thread_name = threading.current_thread().name
        thread_id = threading.get_ident()
        print(f"Fish generator thread started: {thread_name} (ID: {thread_id})")
        
        while not stop_event.is_set():
            try:
                # Create a new fish
                new_fish = create_fish(fish_list, screen_width, screen_height, cliff_rect)
                new_fish.id = fish_counter  # Add a unique ID to each fish
                fish_counter += 1
                
                # Try to add it to the queue
                try:
                    fish_queue.put(new_fish, block=False)
                    print(f"Fish #{new_fish.id} created by thread {thread_name} at position ({new_fish.x:.1f}, {new_fish.y:.1f})")
                except queue.Full:
                    print(f"Queue full, skipping fish #{new_fish.id}")
                    pass  # Queue is full, skip this fish
                
                # Sleep for a bit before creating the next fish
                time.sleep(1)
            except Exception as e:
                print(f"Error in fish generation: {e}")
                time.sleep(1)  # Sleep to prevent spamming errors
    
    # Start fish generator thread
    fish_gen_thread = threading.Thread(target=fish_generator_thread, name="FishGenerator")
    fish_gen_thread.daemon = True  # Thread will terminate when main program exits
    fish_gen_thread.start()
    print(f"Main thread ID: {threading.get_ident()}")
    
    # Get the fonts - regular for score and smaller for area calculations
    font = get_font(24)
    small_font = get_font(18)
    
    # Main game loop
    while running:
        current_time = pygame.time.get_ticks()
        
        # Calculate areas and cleaning time every 5 seconds
        if current_time - last_calculation_time > calculation_interval:
            # Calculate areas concurrently
            areas, computation_time = area_calculator.calculate_all_areas_concurrent()
            total_area = sum(areas.values())
            cleaning_time = area_calculator.calculate_cleaning_time(total_area)
            
            # Store results for display
            area_results = {
                'areas': areas,
                'total_area': total_area,
                'cleaning_time': cleaning_time,
                'computation_time': computation_time
            }
            
            last_calculation_time = current_time
        
        # Get keyboard state for player control
        keys = pygame.key.get_pressed()
        
        # Process events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                stop_music()  # Stop music when quitting
                return False, game_mode  # Exit the game completely
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p or event.key == pygame.K_ESCAPE:
                    paused = True
                    pause_music()  # Pause the music
                    pause_result = pause_menu()
                    if pause_result == "resume":
                        paused = False
                        unpause_music()  # Resume the music
                    elif pause_result == "restart":
                        stop_event.set()  # Signal fish generator to stop
                        return True, game_mode  # Restart the game
                    elif pause_result == "exit":
                        running = False
                        stop_music()  # Stop music when exiting
                        return False, game_mode  # Exit the game
            # Add an event for music end
            elif event.type == pygame.USEREVENT:
                # This is the music end event, but we're using -1 for infinite looping so this shouldn't trigger
                print("Music end event detected")
        
        if not paused:
            # Check for new fish in the queue
            try:
                while not fish_queue.empty():
                    new_fish = fish_queue.get_nowait()
                    fish_objects.append(new_fish)
                    print(f"Fish #{new_fish.id} added to game from queue. Total fish: {len(fish_objects)}")
            except queue.Empty:
                pass  # No new fish, continue with game
            
            # Fill the screen
            screen.blit(map_image, (0, 0))
            
            # Draw the cliff
            screen.blit(cliff_image, cliff_rect)
            
            # Update shark position based on game mode
            if player_controlled:
                shark.handle_player_control(keys)
                shark.keep_in_bounds(screen_width, screen_height)
            else:
                shark.move_towards_fish(fish_objects)
            
            # Check for collision between shark and cliff
            if collision_handler.check_collision(shark, cliff_rect):
                # Use shark's custom method instead of the general collision handler
                shark.handle_cliff_collision()
                print("Shark collided with cliff!")
                
            # Draw shark
            shark.draw(screen)
            
            # Track which fish to remove (eaten by shark)
            fish_to_remove = []
            
            # Update fish movement
            for fish in fish_objects:
                fish.move(screen_width, screen_height)
                
                # Check for collision with the cliff
                if collision_handler.check_collision(fish, cliff_rect):
                    collision_handler.handle_collision(fish)
                    
                # Check for collision with shark
                if shark.check_collision(fish):
                    fish_to_remove.append(fish)
                    score += 1
                    if scream_sounds:
                        # Randomly choose between the scream sounds
                        random.choice(scream_sounds).play()
                
                # Draw fish
                fish.draw(screen)
            
            # Remove fish that were eaten by the shark
            for fish in fish_to_remove:
                if fish in fish_objects:
                    fish_objects.remove(fish)
                    print(f"Fish #{fish.id} eaten by shark. Remaining fish: {len(fish_objects)}")
            
            # Draw score
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            screen.blit(score_text, (10, 10))
            
            # Display controls for player mode
            if player_controlled:
                display_controls(screen, True)
            
            # Display area calculation results if available
            if area_results:
                area_calculator.display_results(
                    screen, small_font, 
                    area_results['areas'],
                    area_results['total_area'],
                    area_results['cleaning_time'],
                    area_results['computation_time']
                )
            
            # Update display
            pygame.display.flip()
            
            # Control the frame rate
            clock.tick(60)
            
            # Check for game over conditions (can be expanded)
            if len(fish_objects) <= 0 and fish_queue.empty():
                # Handle game over
                stop_music()  # Stop music for game over
                game_over_result = game_over_menu(score, game_mode)
                if game_over_result == "restart":
                    stop_event.set()  # Signal fish generator to stop
                    # Restart the music for the new game
                    try:
                        play_music("assets/sofiathefirst_instrumental.mp3", loop=-1)
                        set_music_volume(0.5)
                    except pygame.error as e:
                        print(f"Error restarting music: {e}")
                    return True, game_mode  # Restart the game
                else:  # Exit
                    running = False
                    return False, game_mode  # Exit the game
    
    # Clean up before exit
    stop_event.set()  # Signal fish generator to stop
    print("Stopping fish generator thread...")
    return False, game_mode  # Exit the game

if __name__ == "__main__":
    main()