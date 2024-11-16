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
PLAYER_SPEED = 0.5
FOOD_COUNT = 350
MAP_LIMIT = 1500  # Limite en ambos ejes para las coordenadas
FOOD_RADIUS = 7
FPS = 60
DIVIDE_COOLDOWN = 500  # Tiempo de enfriamiento en milisegundos para dividirse
MAX_SPEED = 5
FRICTION = 0.9  # Coeficiente de fricción para desacelerar
SEPARATION_DISTANCE = 50  # Distancia mínima de separación entre clones

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Arag.io')

# Player setup
player_circles = [{"pos": [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2], "radius": PLAYER_INITIAL_RADIUS, "vx": 0, "vy": 0, "last_divide_time": 0, "is_main": True}]
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

def limit_speed(circle):
    # Limit the speed
    speed = math.sqrt(circle["vx"] ** 2 + circle["vy"] ** 2)
    if speed > MAX_SPEED:
        scale = MAX_SPEED / speed
        circle["vx"] *= scale
        circle["vy"] *= scale

def move_circle(circle, dx, dy):
    circle["vx"] += dx
    circle["vy"] += dy
    limit_speed(circle)
    circle["pos"][0] += circle["vx"]
    circle["pos"][1] += circle["vy"]
    circle["vx"] *= FRICTION
    circle["vy"] *= FRICTION

def apply_separation(circle, others):
    separation_force_x = 0
    separation_force_y = 0
    for other in others:
        if other != circle:
            distance = math.sqrt((circle["pos"][0] - other["pos"][0]) ** 2 + (circle["pos"][1] - other["pos"][1]) ** 2)
            if distance < SEPARATION_DISTANCE:
                angle = math.atan2(circle["pos"][1] - other["pos"][1], circle["pos"][0] - other["pos"][0])
                separation_force_x += math.cos(angle) * (SEPARATION_DISTANCE - distance)
                separation_force_y += math.sin(angle) * (SEPARATION_DISTANCE - distance)
    circle["vx"] += separation_force_x * 0.1
    circle["vy"] += separation_force_y * 0.1

def fuse_circles():
    main_circle = player_circles[0]
    total_area = math.pi * main_circle["radius"] ** 2
    
    for circle in player_circles[1:]:
        total_area += math.pi * circle["radius"] ** 2
    
    new_radius = math.sqrt(total_area / math.pi)
    player_circles[:] = [{"pos": main_circle["pos"], "radius": new_radius, "vx": 0, "vy": 0, "last_divide_time": main_circle["last_divide_time"], "is_main": True}]

# Main game loop
running = True
while running:
    screen.fill(BACKGROUND_COLOR)
    
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                fuse_circles()
    
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
    
    # Move the main circle
    main_circle = player_circles[0]
    move_circle(main_circle, dx, dy)
    
    # Ensure the player doesn't move beyond the map limits
    main_circle["pos"][0] = min(max(main_circle["pos"][0], -MAP_LIMIT), MAP_LIMIT)
    main_circle["pos"][1] = min(max(main_circle["pos"][1], -MAP_LIMIT), MAP_LIMIT)
    
    # Divide the circle when spacebar is pressed and cooldown has passed
    if keys[pygame.K_SPACE]:
        current_time = pygame.time.get_ticks()
        if current_time - main_circle["last_divide_time"] > DIVIDE_COOLDOWN:
            for circle in player_circles:
                if circle["radius"] > 20:  # Ensure the circle is large enough to divide
                    new_circle = {
                        "pos": circle["pos"][:],  # Copy the position
                        "radius": circle["radius"] // 2,
                        "vx": random.choice([1, -1]) * player_speed,
                        "vy": random.choice([1, -1]) * player_speed,
                        "last_divide_time": current_time,
                        "is_main": False
                    }
                    circle["radius"] //= 2
                    player_circles.append(new_circle)
                    circle["last_divide_time"] = current_time
    
    # Move and apply separation to the following circles
    for circle in player_circles[1:]:
        # Move towards the main circle but maintain separation
        angle = math.atan2(main_circle["pos"][1] - circle["pos"][1], main_circle["pos"][0] - circle["pos"][0])
        distance = math.sqrt((main_circle["pos"][0] - circle["pos"][0]) ** 2 + (main_circle["pos"][1] - circle["pos"][1]) ** 2)
        if distance > SEPARATION_DISTANCE:  # Maintain a distance from the main circle
            circle["vx"] += math.cos(angle) * player_speed * 0.5
            circle["vy"] += math.sin(angle) * player_speed * 0.5
        
        # Apply separation force
        apply_separation(circle, player_circles)
        
        limit_speed(circle)
        circle["pos"][0] += circle["vx"]
        circle["pos"][1] += circle["vy"]
        circle["vx"] *= FRICTION
        circle["vy"] *= FRICTION
        
        # Ensure the following circles don't move beyond the map limits
        circle["pos"][0] = min(max(circle["pos"][0], -MAP_LIMIT), MAP_LIMIT)
        circle["pos"][1] = min(max(circle["pos"][1], -MAP_LIMIT), MAP_LIMIT)
    
    # Draw food and handle collisions
    for food in food_items[:]:
        food_screen_pos = [int(food[0] - main_circle["pos"][0] + SCREEN_WIDTH // 2), int(food[1] - main_circle["pos"][1] + SCREEN_HEIGHT // 2)]
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
        screen_pos = (int(circle["pos"][0] - main_circle["pos"][0] + SCREEN_WIDTH // 2), int(circle["pos"][1] - main_circle["pos"][1] + SCREEN_HEIGHT // 2))
        pygame.draw.circle(screen, (0, 125, 225), screen_pos, circle["radius"])
    
    # Update the screen
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

