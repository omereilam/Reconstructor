import pygame
import sys
import numpy
import random

# This piece of code takes a jpg image file and reconstructs it line by line based on the following steps:
# 1. start from a random pixel
# 2. find its nearest neighbor within a given window size with respect to color similarity
# 3. draw a line from the old pixel to the new pixel
# 4. return to step 2.
### every second another pixel is added and the 4 step loop is executed on it as well ###

pygame.init()
pygame.display.init()

class ImageReconstructor():
    
    def __init__(self, image_surface, window):
        self.image_surface = image_surface
        self.window = window
        self.xsize = image_surface.get_width()
        self.ysize = image_surface.get_height()
        self.pixel_set = self.pixel_set()
        self.distances = dict()
        self.reconstruct()
            
    def pixel_set(self):
        pixel_set = set()
        for i in range(self.xsize):
            for j in range(self.ysize):
                pixel_set.add((i,j))
        return pixel_set
    
    def get_col(self, pixel_coords):
        return self.image_surface.get_at(pixel_coords)
    
    def get_random_pixel(self):
        return (random.randrange(self.xsize), random.randrange(self.ysize))
    
    def get_dist(self, pixel1_col, pixel2_col):
        pixel1_col_tup = (pixel1_col[0], pixel1_col[1], pixel1_col[2])
        pixel2_col_tup = (pixel2_col[0], pixel2_col[1], pixel2_col[2])
        pair = (pixel1_col_tup, pixel2_col_tup)
        if not pair in self.distances:
            dist_vec = [abs(a-b) for a,b in zip(pixel1_col_tup, pixel2_col_tup)]
            dist = numpy.linalg.norm(dist_vec,2)
            self.distances[pair] = dist
        else:
            dist = self.distances[pair]
        return dist
    
    def nearest_neighbor(self, pixel_loc):
        current_col = self.get_col(pixel_loc)
        x_coord = pixel_loc[0]
        y_coord = pixel_loc[1]
        nearest_pixel = self.get_random_pixel()
        random = True
        nearest_pixel_dist = float('Inf')
        for new_x in range(max(x_coord - self.window,0), min(self.xsize,x_coord + self.window)):
            for new_y in range(max(y_coord - self.window,0), min(self.ysize,y_coord + self.window)):
                new_coord = (new_x, new_y)
                new_col = self.get_col(new_coord)
                dist = self.get_dist(current_col, new_col)
                if (dist < nearest_pixel_dist) and new_coord in self.pixel_set:
                    nearest_pixel_dist = dist
                    nearest_pixel = new_coord
                    self.pixel_set.remove(new_coord)
                    random = False
        return [random, nearest_pixel]
            
    def reconstruct(self):
        screen_size = [self.xsize, self.ysize]
        screen = pygame.display.set_mode(screen_size)
        start_points = list()
        start_points.append(self.get_random_pixel())
        screen.fill((255, 255, 255))
        next_line_time = 10000
        
        running = True
        mouse_pressed = False
          
        while running:
            
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    mouse_pressed = True
                if event.type == pygame.QUIT:
                    running = False
                    mouse_pressed = False
                        
            while mouse_pressed:
    
                if pygame.time.get_ticks() >= next_line_time and len(start_points) < 10:
                    start_points.append(self.get_random_pixel())
                    next_line_time += next_line_time / 2
                
                # Draw on the screen a line from previous to next pixel with the color of the previous pixel
                for i, old_coord in enumerate(start_points):
                    [random, new_coord] = self.nearest_neighbor(old_coord)
                    if not random:
                        pygame.draw.line(screen, self.get_col(old_coord), old_coord, new_coord, 1)
                    start_points[i] = new_coord
                    
                # Go ahead and update the screen with what we've drawn.
                # This MUST happen after all the other drawing commands.
                pygame.display.flip()
                
        sys.exit(0)


file_shortname = 'kidA'
image_file = os.getcwd() + '/' + file_shortname + '.jpg'
image_surface = pygame.image.load(image_file)
reconstructor = ImageReconstructor(image_surface, 5)

