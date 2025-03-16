import pygame
import math
import random

class Shark:
    def __init__(self, image, x, y, player_controlled=False):
        self.original_image = pygame.transform.scale(image, (30, 30))  # Slightly larger than fish
        self.image = self.original_image
        self.flipped_image = pygame.transform.flip(self.original_image, True, False)  # Flip horizontally
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = 2
        self.player_speed = 4  # Higher speed for player control
        self.target_fish = None
        self.facing_right = True  # Track which direction shark is facing
        self.player_controlled = player_controlled  # New flag for player control
        
        # Add attributes needed for collision handling
        self.direction = random.uniform(0, 2 * math.pi)  # Random angle in radians
        self.dx = 0  # Velocity in x direction
        self.dy = 0  # Velocity in y direction
        
        # Add attributes for collision response
        self.collision_recovery = 0  # Counter for frames to follow collision direction
        self.collision_recovery_time = 30  # Number of frames to respect collision direction

    def update(self, fish_list, keys=None):
        """Update shark position based on AI or player control"""
        if self.player_controlled:
            self.handle_player_control(keys)
        else:
            self.move_towards_fish(fish_list)
    
    def handle_player_control(self, keys):
        """Handle player keyboard input for shark movement"""
        if keys is None:
            return
            
        # Reset velocity
        dx, dy = 0, 0
        
        # Check for key presses
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
            if self.facing_right:
                self.image = self.flipped_image
                self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
            if not self.facing_right:
                self.image = self.original_image
                self.facing_right = True
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
            
        # If we're in collision recovery mode, reduce the counter but allow player control
        if self.collision_recovery > 0:
            self.collision_recovery -= 1
            
        # Normalize diagonal movement to maintain consistent speed
        if dx != 0 and dy != 0:
            magnitude = math.sqrt(dx*dx + dy*dy)
            dx /= magnitude
            dy /= magnitude
            
        # Store velocity components for collision handling
        self.dx = dx * self.player_speed
        self.dy = dy * self.player_speed
            
        # Update position
        self.x += self.dx
        self.y += self.dy
        
        # Update rectangle position
        self.rect.topleft = (self.x, self.y)
        
        # Update direction for collision handling
        if dx != 0 or dy != 0:
            self.direction = math.atan2(dy, dx)

    def move_towards_fish(self, fish_list):
        if not fish_list:
            return  # No fish to chase
        
        # If we're in collision recovery mode, move in the current direction
        if self.collision_recovery > 0:
            self.collision_recovery -= 1
            
            # Move based on current direction
            self.x += self.speed * math.cos(self.direction)
            self.y += self.speed * math.sin(self.direction)
            
            # Update rectangle position
            self.rect.topleft = (self.x, self.y)
            
            # Update facing direction based on current movement
            if math.cos(self.direction) < 0:  # Moving left
                if self.facing_right:
                    self.image = self.flipped_image
                    self.facing_right = False
            elif math.cos(self.direction) > 0:  # Moving right
                if not self.facing_right:
                    self.image = self.original_image
                    self.facing_right = True
                    
            # Store velocity components for collision handling
            self.dx = self.speed * math.cos(self.direction)
            self.dy = self.speed * math.sin(self.direction)
            
            return
            
        # Normal target-seeking behavior
        # Find closest fish if we don't have a target or our target was removed
        if self.target_fish is None or self.target_fish not in fish_list:
            closest_fish = None
            min_distance = float('inf')
            
            for fish in fish_list:
                # Calculate distance to this fish
                dx = fish.x - self.x
                dy = fish.y - self.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                if distance < min_distance:
                    min_distance = distance
                    closest_fish = fish
                    
            self.target_fish = closest_fish
        
        if self.target_fish:
            # Calculate direction to target fish
            dx = self.target_fish.x - self.x
            dy = self.target_fish.y - self.y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # Avoid division by zero
            if distance > 0:
                # Normalize direction vector
                dx /= distance
                dy /= distance
                
                # Store the velocity components for collision handling
                self.dx = dx * self.speed
                self.dy = dy * self.speed
                
                # Update direction angle for collision handling
                self.direction = math.atan2(dy, dx)
                
                # Check direction and flip image if needed
                if dx < 0:  # Moving left
                    if self.facing_right:
                        self.image = self.flipped_image
                        self.facing_right = False
                elif dx > 0:  # Moving right
                    if not self.facing_right:
                        self.image = self.original_image
                        self.facing_right = True
                
                # Move towards target
                self.x += self.dx
                self.y += self.dy
                
                # Update rectangle position
                self.rect.topleft = (self.x, self.y)

    def draw(self, screen):
        screen.blit(self.image, self.rect.topleft)
        
    def check_collision(self, fish):
        return self.rect.colliderect(fish.rect)
        
    def handle_cliff_collision(self):
        # This method is called when the shark collides with the cliff
        # Start the collision recovery period
        self.collision_recovery = self.collision_recovery_time
        
        # If player controlled, just bounce back a bit
        if self.player_controlled:
            # Move in the opposite direction of current movement
            self.x -= self.dx * 2
            self.y -= self.dy * 2
            self.rect.topleft = (self.x, self.y)
            return
            
        # For AI control, adjust direction to bounce away (roughly opposite of current direction)
        # Add some randomness to prevent getting stuck
        self.direction = self.direction + math.pi + random.uniform(-0.5, 0.5)
        
        # Keep direction in [0, 2π] range
        self.direction = self.direction % (2 * math.pi)
    
    def keep_in_bounds(self, screen_width, screen_height):
        """Keep the shark within screen bounds"""
        # Clamp position to screen boundaries
        self.x = max(0, min(self.x, screen_width - self.rect.width))
        self.y = max(0, min(self.y, screen_height - self.rect.height))
        self.rect.topleft = (self.x, self.y)

def load_shark_image(path):
    try:
        return pygame.image.load(path)
    except pygame.error:
        # Create a simple shark shape if image can't be loaded
        surf = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.polygon(surf, (75, 75, 75), [(15, 0), (30, 15), (15, 30), (0, 15)])
        return surf

def spawn_shark(shark_image, screen_width, screen_height, player_controlled=False):
    # Spawn shark at a random edge position
    edge = random.choice(['top', 'right', 'bottom', 'left'])
    
    if edge == 'top':
        x = random.randint(0, screen_width - 30)
        y = 0
    elif edge == 'right':
        x = screen_width - 30
        y = random.randint(0, screen_height - 30)
    elif edge == 'bottom':
        x = random.randint(0, screen_width - 30)
        y = screen_height - 30
    else:  # left
        x = 0
        y = random.randint(0, screen_height - 30)
        
    return Shark(shark_image, x, y, player_controlled)