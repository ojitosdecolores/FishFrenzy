import pygame
import random
import time

class Fish:
    def __init__(self, image, x, y):
        self.image = pygame.transform.scale(image, (14, 14))  # Scaling 16x16 to 14x14
        self.x = x
        self.y = y
        self.rect = self.image.get_rect(topleft=(x, y))  # Add rect attribute for collision detection

        # Initial movement direction (up, down, left, right)
        self.direction = random.choice(['up', 'down', 'left', 'right'])
        self.speed = 2  # Movement speed

        # Time tracking for direction change
        self.last_direction_change_time = time.time()  # Time of last direction change
        self.direction_change_interval = 0.5  # 0.5 second interval to change direction

    def move(self, screen_width, screen_height):
        """ Update fish position based on grid-like movement and periodic direction change """

        # Move fish based on current direction
        if self.direction == 'up':
            self.y -= self.speed
        elif self.direction == 'down':
            self.y += self.speed
        elif self.direction == 'left':
            self.x -= self.speed
        elif self.direction == 'right':
            self.x += self.speed

        # Update rect position
        self.rect.topleft = (self.x, self.y)

        # Check if it's time to change direction
        current_time = time.time()
        if current_time - self.last_direction_change_time >= self.direction_change_interval:
            self.last_direction_change_time = current_time  # Reset the time
            # Randomly change the direction
            self.direction = random.choice(['up', 'down', 'left', 'right'])

        # Keep fish within screen boundaries
        if self.x < 0:  # Left boundary
            self.x = 0
            self.direction = 'right'
        elif self.x > screen_width - self.rect.width:  # Right boundary
            self.x = screen_width - self.rect.width
            self.direction = 'left'

        if self.y < 0:  # Top boundary
            self.y = 0
            self.direction = 'down'
        elif self.y > screen_height - self.rect.height:  # Bottom boundary
            self.y = screen_height - self.rect.height
            self.direction = 'up'

    def draw(self, screen):
        screen.blit(self.image, (self.x, self.y))

# Function to load and split the tile sheet into individual fish
def load_fish_tiles(sheet_path, tile_size=(16, 16), rows=4, cols=4):
    try:
        sheet = pygame.image.load(sheet_path)
    except pygame.error:
        # Fallback path if the provided path doesn't work
        sheet = pygame.image.load('assets/fish.png')
    
    fish_list = []
    
    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * tile_size[0], row * tile_size[1], tile_size[0], tile_size[1])
            fish_image = sheet.subsurface(rect)
            fish_list.append(fish_image)
            
    return fish_list

# Function to create a fish safely
def create_fish(fish_list, screen_width, screen_height, cliff_rect):
    # Try to create a fish that doesn't overlap with the cliff
    for _ in range(100):  # Limit attempts to prevent infinite loop
        fish_image = random.choice(fish_list)
        x = random.randint(0, screen_width - 14)  # 14 is the scaled fish width
        y = random.randint(0, screen_height - 14)  # 14 is the scaled fish height
        fish_rect = pygame.Rect(x, y, 14, 14)
        if not fish_rect.colliderect(cliff_rect):
            return Fish(fish_image, x, y)
    
    # If we can't find a valid position after many attempts, place it in a default location
    return Fish(random.choice(fish_list), 50, 50)