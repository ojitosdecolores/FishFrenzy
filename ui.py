import pygame

def draw_text(screen, text, size, x, y, color=(255, 255, 255)):
    try:
        font = pygame.font.Font('assets/pixel_font.otf', size)
    except pygame.error:
        # Fallback to default font if custom font not found
        font = pygame.font.Font(None, size)
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    text_rect.center = (x, y)
    screen.blit(text_surface, text_rect)

def draw_button(screen, text, size, x, y, width, height, inactive_color, active_color):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    
    # Check if mouse is over button
    if x < mouse[0] < x + width and y < mouse[1] < y + height:
        pygame.draw.rect(screen, active_color, (x, y, width, height))
        
        # Check for click
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, inactive_color, (x, y, width, height))
    
    # Add text to button - using the same pixel font as draw_text
    try:
        font = pygame.font.Font('assets/pixel_font.otf', size)
    except pygame.error:
        # Fallback to default font if custom font not found
        font = pygame.font.Font(None, size)
    
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect()
    text_rect.center = (x + width//2, y + height//2)
    screen.blit(text_surf, text_rect)
    
    return False

def main_menu():
    """Display the main menu with game mode selection and Exit options"""
    screen = pygame.display.get_surface()
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    button_width = 280  # Wider buttons for more text
    button_height = 50
    button_spacing = 20
    
    # Button colors
    button_color = (200, 200, 100)         # Desaturated yellow
    button_hover_color = (220, 220, 140)   # Lighter desaturated yellow
    
    # Fill with a desaturated turquoise background
    screen.fill((102, 178, 178))  # Desaturated turquoise
    
    # Draw the game title
    draw_text(screen, "Fish Frenzy", 60, screen_width // 2, screen_height // 3, (255, 255, 100))
    
    # Draw the instructions
    draw_text(screen, "Choose your mode!", 36, screen_width // 2, screen_height // 2 - 50)
    
    # Wait for user input
    waiting = True
    game_mode = None  # None = exit, "auto" = automatic shark, "player" = player-controlled shark
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return (False, None)
                
        # Draw Auto Shark button
        auto_x = screen_width//2 - button_width//2
        auto_y = screen_height//2 + 10
        if draw_button(screen, "Auto Shark (AI)", 30, auto_x, auto_y, 
                      button_width, button_height, button_color, button_hover_color):
            waiting = False
            game_mode = "auto"
            
        # Draw Player Shark button
        player_x = screen_width//2 - button_width//2
        player_y = auto_y + button_height + button_spacing
        if draw_button(screen, "Play as Shark", 30, player_x, player_y, 
                      button_width, button_height, button_color, button_hover_color):
            waiting = False
            game_mode = "player"
            
        # Draw Exit button
        exit_x = screen_width//2 - button_width//2
        exit_y = player_y + button_height + button_spacing
        if draw_button(screen, "Exit", 30, exit_x, exit_y, 
                      button_width, button_height, button_color, button_hover_color):
            return (False, None)
            
        # Update display
        pygame.display.flip()
        pygame.time.delay(10)  # Small delay to reduce CPU usage
    
    return (True, game_mode)

def pause_menu():
    """Display the pause menu with Resume, Restart and Exit options"""
    screen = pygame.display.get_surface()
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    button_width = 200
    button_height = 50
    button_spacing = 20
    
    # Button colors
    button_color = (0, 120, 200)         # Blue
    button_hover_color = (0, 150, 255)   # Lighter blue
    
    # Create a semi-transparent overlay
    overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 128))  # Black with 50% transparency
    screen.blit(overlay, (0, 0))
    
    # Draw pause text
    draw_text(screen, "PAUSED", 60, screen_width // 2, screen_height // 3)
    
    # Wait for selection
    waiting = True
    result = "resume"  # Default to resume if menu is closed another way
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
                
        # Draw Resume button
        resume_x = screen_width//2 - button_width//2
        resume_y = screen_height//2
        if draw_button(screen, "Resume", 30, resume_x, resume_y, 
                      button_width, button_height, button_color, button_hover_color):
            waiting = False
            result = "resume"
            
        # Draw Restart button
        restart_x = screen_width//2 - button_width//2
        restart_y = resume_y + button_height + button_spacing
        if draw_button(screen, "Restart", 30, restart_x, restart_y, 
                      button_width, button_height, button_color, button_hover_color):
            waiting = False
            result = "restart"
            
        # Draw Exit button
        exit_x = screen_width//2 - button_width//2
        exit_y = restart_y + button_height + button_spacing
        if draw_button(screen, "Exit", 30, exit_x, exit_y, 
                      button_width, button_height, button_color, button_hover_color):
            waiting = False
            result = "exit"
            
        # Update display
        pygame.display.flip()
        pygame.time.delay(10)  # Small delay to reduce CPU usage
    
    return result

def game_over_menu(score, game_mode):
    """Display game over screen with final score, Restart and Exit options"""
    screen = pygame.display.get_surface()
    screen_width = screen.get_width()
    screen_height = screen.get_height()
    
    button_width = 200
    button_height = 50
    button_spacing = 20
    
    # Button colors
    button_color = (0, 120, 200)         # Blue
    button_hover_color = (0, 150, 255)   # Lighter blue
    
    # Create a full screen overlay
    overlay = pygame.Surface((screen_width, screen_height))
    overlay.fill((77, 134, 134))  #turquoise
    screen.blit(overlay, (0, 0))
    
    # Draw game over text and score
    draw_text(screen, "GAME OVER", 70, screen_width // 2, screen_height // 4, (255, 100, 100))
    draw_text(screen, f"Final Score: {score}", 50, screen_width // 2, screen_height // 3 + 30)
    
    # Display game mode
    mode_text = "Mode: Player Shark" if game_mode == "player" else "Mode: AI Shark"
    draw_text(screen, mode_text, 30, screen_width // 2, screen_height // 3 + 80)
    
    # Wait for selection
    waiting = True
    result = "exit"  # Default to exit if menu is closed another way
    
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"
                
        # Draw Restart button
        restart_x = screen_width//2 - button_width//2
        restart_y = screen_height//2 + 50
        if draw_button(screen, "Play Again", 30, restart_x, restart_y, 
                      button_width, button_height, button_color, button_hover_color):
            waiting = False
            result = "restart"
            
        # Draw Exit button
        exit_x = screen_width//2 - button_width//2
        exit_y = restart_y + button_height + button_spacing
        if draw_button(screen, "Exit", 30, exit_x, exit_y, 
                      button_width, button_height, button_color, button_hover_color):
            waiting = False
            result = "exit"
            
        # Update display
        pygame.display.flip()
        pygame.time.delay(10)  # Small delay to reduce CPU usage
    
    return result

def display_controls(screen, player_controlled=False):
    """Display control information for player-controlled mode"""
    if player_controlled:
        draw_text(screen, "Controls: WASD or Arrow Keys to move", 20, 150, 45, (255, 255, 255))