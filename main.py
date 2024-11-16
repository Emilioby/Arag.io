import pygame
import random

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
BACKGROUND_COLOR = (225, 225, 225)
PLAYER_INITIAL_RADIUS = 40
PLAYER_SPEED = 5
FOOD_COUNT = 100
MAP_WIDTH = 2000
MAP_HEIGHT = 2000
FOOD_RADIUS = 5
FPS = 60

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Arag.io')

# Player setup
player_circles = [{"pos": [SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2], "radius": PLAYER_INITIAL_RADIUS, "following": False}]
player_speed = PLAYER_SPEED

# Food setup
food_items = [
    [
        random.randint(-MAP_WIDTH // 2, MAP_WIDTH // 2),
        random.randint(-MAP_HEIGHT // 2, MAP_HEIGHT // 2),
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
    if keys[pygame.K_w]:
        player_circles[0]["pos"][1] -= player_speed
    if keys[pygame.K_s]:
        player_circles[0]["pos"][1] += player_speed
    if keys[pygame.K_a]:
        player_circles[0]["pos"][0] -= player_speed
    if keys[pygame.K_d]:
        player_circles[0]["pos"][0] += player_speed
    
    # Divide the circle when spacebar is pressed
    if keys[pygame.K_SPACE] and len(player_circles) == 1:
        original_circle = player_circles[0]
        if original_circle["radius"] > 20:  # Ensure the circle is large enough to divide
            new_circle = {
                "pos": original_circle["pos"][:],  # Copy the position
                "radius": original_circle["radius"] // 2,
                "following": True
            }
            original_circle["radius"] //= 2
            player_circles.append(new_circle)
    
    # Move the following circle to follow the main circle
    for circle in player_circles[1:]:
        if circle["following"]:
            circle["pos"] = player_circles[0]["pos"][:]
    
    # Draw food and handle collisions
    for food in food_items[:]:
        food_screen_pos = [int(food[0] - player_circles[0]["pos"][0] + SCREEN_WIDTH // 2), int(food[1] - player_circles[0]["pos"][1] + SCREEN_HEIGHT // 2)]
        pygame.draw.circle(screen, food[2], food_screen_pos, FOOD_RADIUS)
        
        # Check for collisions with player circles
        for circle in player_circles:
            distance = ((circle["pos"][0] - food[0]) ** 2 + (circle["pos"][1] - food[1]) ** 2) ** 0.5
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
