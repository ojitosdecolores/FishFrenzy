import pygame
import concurrent.futures
import time

class AreaCalculator:
    def __init__(self, screen_width, screen_height, cliff_rect):
        # Store original pixel dimensions
        self.screen_width_px = screen_width
        self.screen_height_px = screen_height
        self.cliff_rect = cliff_rect
        
        # Conversion factors (derived from 1008px = 630cm, 800px = 500cm)
        self.px_to_cm_x = 630 / 1008  # approximately 0.625 cm per pixel on x-axis
        self.px_to_cm_y = 500 / 800   # approximately 0.625 cm per pixel on y-axis
        
        # Real-world dimensions in cm
        self.screen_width = screen_width * self.px_to_cm_x
        self.screen_height = screen_height * self.px_to_cm_y
        
        # Cleaning rate (cm²/second)
        self.cleaning_rate = 1000
        
        # Define zones based on pixel dimensions, conversion happens in calculation
        self.zones = self._define_zones()
        
    def _define_zones(self):
        """Define the zones in the game area (in pixel coordinates)."""
        # Zone 1: Top-left area
        # Zone 2: Top-right area
        # Zone 3: Bottom-left area (excluding cliff)
        # Zone 4: Bottom-right area (excluding cliff)
        # Zone 5: Cliff area
        
        cliff_x = self.cliff_rect.x
        cliff_y = self.cliff_rect.y
        cliff_width = self.cliff_rect.width
        cliff_height = self.cliff_rect.height
        
        zones = [
            {"name": "Top-left", "x": 0, "y": 0, "width": cliff_x, "height": cliff_y},
            {"name": "Top-right", "x": cliff_x + cliff_width, "y": 0, 
             "width": self.screen_width_px - (cliff_x + cliff_width), "height": cliff_y},
            {"name": "Bottom-left", "x": 0, "y": cliff_y + cliff_height, 
             "width": cliff_x, "height": self.screen_height_px - (cliff_y + cliff_height)},
            {"name": "Bottom-right", "x": cliff_x + cliff_width, "y": cliff_y + cliff_height,
             "width": self.screen_width_px - (cliff_x + cliff_width), 
             "height": self.screen_height_px - (cliff_y + cliff_height)},
            {"name": "Cliff", "x": cliff_x, "y": cliff_y, "width": cliff_width, "height": cliff_height}
        ]
        return zones
    
    def calculate_area_px(self, length_px, width_px):
        """Calculate area in pixels by multiplying length and width."""
        return length_px * width_px
    
    def calculate_area_cm(self, length_px, width_px):
        """Calculate area in square centimeters from pixel dimensions."""
        length_cm = length_px * self.px_to_cm_x
        width_cm = width_px * self.px_to_cm_y
        return length_cm * width_cm
    
    def calculate_zone_area(self, zone):
        """Calculate the area of a zone in square centimeters."""
        # First get pixel area
        pixel_area = self.calculate_area_px(zone["width"], zone["height"])
        
        # Convert to square centimeters
        cm_area = self.calculate_area_cm(zone["width"], zone["height"])
        
        return cm_area
    
    def calculate_all_areas_concurrent(self):
        """Use concurrent.futures to calculate all zone areas in parallel."""
        start_time = time.time()
        areas = {}
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit all zone calculations
            future_to_zone = {
                executor.submit(self.calculate_zone_area, zone): zone 
                for zone in self.zones
            }
            
            # Collect results as they complete
            for future in concurrent.futures.as_completed(future_to_zone):
                zone = future_to_zone[future]
                try:
                    area = future.result()
                    areas[zone["name"]] = area
                except Exception as e:
                    print(f"Error calculating area for {zone['name']}: {e}")
                    areas[zone["name"]] = 0
        
        computation_time = time.time() - start_time
        return areas, computation_time
    
    def calculate_cleaning_time(self, total_area):
        """Calculate cleaning time based on total area and cleaning rate."""
        return total_area / self.cleaning_rate
    
    def display_results(self, screen, font, areas, total_area, cleaning_time, computation_time):
        """Display the results on the screen."""

        small_font = font if font.get_height() <= 20 else pygame.font.Font(None, 20)
        y_offset = 50
        
        # Display each zone area
        for i, (zone_name, area) in enumerate(areas.items()):
            text = small_font.render(f"Área de {zone_name}: {area:.2f} cm²", True, (255, 255, 255))
            screen.blit(text, (10, y_offset + i * 25))
        
        # Display total area and cleaning time
        y_offset += len(areas) * 25 + 10
        total_text = small_font.render(f"Superficie Total: {total_area:.2f} cm²", True, (255, 255, 0))
        screen.blit(total_text, (10, y_offset))
        
        time_text = small_font.render(f"Tiempo de Limpieza: {cleaning_time:.2f} segundos", True, (255, 255, 0))
        screen.blit(time_text, (10, y_offset + 25))
        
        comp_text = small_font.render(f"Tiempo de Cálculo: {computation_time*1000:.2f} ms", True, (255, 255, 0))
        screen.blit(comp_text, (10, y_offset + 50))