import pygame
import random
import math

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (225, 225, 225)
PLAYER_INITIAL_RADIUS = 40
PLAYER_SPEED = 5
FOOD_COUNT = 350
MAP_LIMIT = 1500  # Limite en ambos ejes para las coordenadas
FOOD_RADIUS = 7
FPS = 60
DIVIDE_COOLDOWN = 500  # Tiempo de enfriamiento en milisegundos para dividirse

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Arag.io')

# Player setup
player_circles = [{"pos": [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2], "radius": PLAYER_INITIAL_RADIUS, "vx": 0, "vy": 0, "last_divide_time": 0}]
player_speed = PLAYER_SPEED

# Food setup
food_items = [
    [
        random.randint(-MAP_LIMIT, MAP_LIMIT),
        random.randint(-MAP_LIMIT, MAP_LIMIT),
        (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
    ]
    for _ in range(FOOD_COUNT)
]

# Clock to control the frame rate
clock = pygame.time.Clock()

# Main game loop
running = True
while running:
    screen.fill(BACKGROUND_COLOR)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    # Handle movement
    keys = pygame.key.get_pressed()
    dx, dy = 0, 0
    if keys[pygame.K_w]:
        dy -= player_speed
    if keys[pygame.K_s]:
        dy += player_speed
    if keys[pygame.K_a]:
        dx -= player_speed
    if keys[pygame.K_d]:
        dx += player_speed
    
    for circle in player_circles:
        circle["pos"][0] += dx
        circle["pos"][1] += dy
        
        # Ensure the player doesn't move beyond the map limits
        circle["pos"][0] = min(max(circle["pos"][0], -MAP_LIMIT), MAP_LIMIT)
        circle["pos"][1] = min(max(circle["pos"][1], -MAP_LIMIT), MAP_LIMIT)
    
    # Divide the circle when spacebar is pressed and cooldown has passed
    if keys[pygame.K_SPACE]:
        current_time = pygame.time.get_ticks()
        if current_time - player_circles[0]["last_divide_time"] > DIVIDE_COOLDOWN:
            for circle in player_circles:
                if circle["radius"] > 20:  # Ensure the circle is large enough to divide
                    new_circle = {
                        "pos": circle["pos"][:],  # Copy the position
                        "radius": circle["radius"] // 2,
                        "vx": random.choice([1, -1]) * player_speed,
                        "vy": random.choice([1, -1]) * player_speed,
                        "last_divide_time": current_time
                    }
                    circle["radius"] //= 2
                    player_circles.append(new_circle)
                    circle["last_divide_time"] = current_time
    
    # Move the following circles
    for circle in player_circles:
        circle["pos"][0] += circle["vx"]
        circle["pos"][1] += circle["vy"]
        circle["vx"] *= 0.9  # Reduce speed over time
        circle["vy"] *= 0.9
        
        # Ensure the following circles don't move beyond the map limits
        circle["pos"][0] = min(max(circle["pos"][0], -MAP_LIMIT), MAP_LIMIT)
        circle["pos"][1] = min(max(circle["pos"][1], -MAP_LIMIT), MAP_LIMIT)
    
    # Draw food and handle collisions
    for food in food_items[:]:
        food_screen_pos = [int(food[0] - player_circles[0]["pos"][0] + SCREEN_WIDTH // 2), int(food[1] - player_circles[0]["pos"][1] + SCREEN_HEIGHT // 2)]
        pygame.draw.circle(screen, food[2], food_screen_pos, FOOD_RADIUS)
        
        # Check for collisions with player circles
        for circle in player_circles:
            distance = math.sqrt((circle["pos"][0] - food[0]) ** 2 + (circle["pos"][1] - food[1]) ** 2)
            if distance < circle["radius"] + FOOD_RADIUS:
                circle["radius"] += 1
                food_items.remove(food)
                break
    
    # Draw player circles
    for circle in player_circles:
        screen_pos = (int(circle["pos"][0] - player_circles[0]["pos"][0] + SCREEN_WIDTH // 2), int(circle["pos"][1] - player_circles[0]["pos"][1] + SCREEN_HEIGHT // 2))
        pygame.draw.circle(screen, (0, 125, 225), screen_pos, circle["radius"])
    
    # Update the screen
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

