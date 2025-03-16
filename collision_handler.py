import pygame

class CollisionHandler:
    def __init__(self):
        # Initialize any needed variables
        pass
        
    def check_collision(self, obj1, obj2):
        """Check if two objects collide using their rect attributes."""
        if hasattr(obj2, 'rect'):
            return obj1.rect.colliderect(obj2.rect)
        else:
            # If obj2 is a pygame.Rect
            return obj1.rect.colliderect(obj2)
            
    def handle_collision(self, fish):
        """Handle collision between fish and cliff (or other objects)."""
        # Reverse the fish direction when it hits something
        if fish.direction == 'up':
            fish.direction = 'down'
        elif fish.direction == 'down':
            fish.direction = 'up'
        elif fish.direction == 'left':
            fish.direction = 'right'
        elif fish.direction == 'right':
            fish.direction = 'left'
            
        # Add a small nudge to prevent the fish from getting stuck
        if fish.direction == 'up':
            fish.y -= 3
        elif fish.direction == 'down':
            fish.y += 3
        elif fish.direction == 'left':
            fish.x -= 3
        elif fish.direction == 'right':
            fish.x += 3