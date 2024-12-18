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

# Function to get player name
def get_player_name():
    font = pygame.font.SysFont(None, 48)
    input_box = pygame.Rect(300, 250, 200, 50)
    color_inactive = pygame.Color('gray')
    color_active = pygame.Color('dodgerblue2')
    color = color_inactive
    active = False
    text = ''
    done = False

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Toggle the active variable.
                if input_box.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_inactive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((30, 30, 30))
        txt_surface = font.render(text, True, color)
        width = max(200, txt_surface.get_width() + 10)
        input_box.w = width
        screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, color, input_box, 2)
        pygame.display.flip()

# Get player name before starting the game
player_name = get_player_name()

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

# Bots setup
bot_names = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta", "Iota", "Kappa"]
bot_circles = [
    {
        "pos": [random.randint(-MAP_LIMIT, MAP_LIMIT), random.randint(-MAP_LIMIT, MAP_LIMIT)], 
        "radius": random.randint(20, 40), 
        "vx": random.uniform(-2, 2), 
        "vy": random.uniform(-2, 2), 
        "name": bot_names[i], 
        "color": (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))  # Color aleatorio para cada bot
    }
    for i in range(len(bot_names))
]
font = pygame.font.SysFont(None, 24)
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

def move_bots():
    for bot in bot_circles:
        # Movimiento aleatorio
        bot["vx"] += random.uniform(-0.5, 0.5)
        bot["vy"] += random.uniform(-0.5, 0.5)
        limit_speed(bot)
        bot["pos"][0] += bot["vx"]
        bot["pos"][1] += bot["vy"]
        bot["vx"] *= FRICTION
        bot["vy"] *= FRICTION

        # Asegurarse de que los bots no salgan del mapa
        bot["pos"][0] = min(max(bot["pos"][0], -MAP_LIMIT), MAP_LIMIT)
        bot["pos"][1] = min(max(bot["pos"][1], -MAP_LIMIT), MAP_LIMIT)

        # Buscar comida y "comerla"
        for food in food_items[:]:
            distance = math.sqrt((bot["pos"][0] - food[0]) ** 2 + (bot["pos"][1] - food[1]) ** 2)
            if distance < bot["radius"] + FOOD_RADIUS:
                bot["radius"] += 1
                food_items.remove(food)
                break

def draw_controls(): 
    font = pygame.font.Font(None, 20) 
    controls_text = [ 
        "[W] [A] [S] [D] para moverse", 
        "[ESPACIO] para separarse", 
        "[ENTER] para juntarse" 
    ] 
    x = SCREEN_WIDTH - 200
    y = 10 
    menu_width = 190 
    menu_height = 100 

    # Draw transparent background 
    s = pygame.Surface((menu_width, menu_height)) # the size of your rect 
    s.set_alpha(150) # alpha level 
    s.fill((0, 0, 0)) # this fills the entire surface 
    screen.blit(s, (x, y)) 
    
    # Draw text 
    for line in controls_text: 
        text_surface = font.render(line, True, (255, 255, 255)) 
        screen.blit(text_surface, (x + 10, y + 10)) 
        y += 30

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
     # Draw the player's name above the main circle
    for circle in player_circles:
        if circle["is_main"]:
            screen_pos = (int(circle["pos"][0] - player_circles[0]["pos"][0] + SCREEN_WIDTH // 2), int(circle["pos"][1] - player_circles[0]["pos"][1] + SCREEN_HEIGHT // 2))
            pygame.draw.circle(screen, (0, 125, 225), screen_pos, int(circle["radius"]))
            name_surface = font.render(player_name, True, (0, 0, 0))
            screen.blit(name_surface, (screen_pos[0] - name_surface.get_width() // 2, screen_pos[1] - circle["radius"] - 20))
                
    
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
    
    # Move bots
    move_bots()

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
    
      # Draw bots
    for bot in bot_circles:
        bot_screen_pos = [int(bot["pos"][0] - main_circle["pos"][0] + SCREEN_WIDTH // 2),
                          int(bot["pos"][1] - main_circle["pos"][1] + SCREEN_HEIGHT // 2)]
        pygame.draw.circle(screen, bot["color"], bot_screen_pos, int(bot["radius"]))
        
        # Draw bot name
        bot_name_surface = font.render(bot["name"], True, (0, 0, 0))
        screen.blit(bot_name_surface, (bot_screen_pos[0] - bot_name_surface.get_width() // 2, bot_screen_pos[1] - bot["radius"] - 10))
    
    # Draw player circles
    for circle in player_circles:
        screen_pos = (int(circle["pos"][0] - main_circle["pos"][0] + SCREEN_WIDTH // 2), int(circle["pos"][1] - main_circle["pos"][1] + SCREEN_HEIGHT // 2))
        pygame.draw.circle(screen, (0, 125, 225), screen_pos, int(circle["radius"]))
    
# Check collisions between bots and players
    for bot in bot_circles[:]:
        for circle in player_circles:
            distance = math.sqrt((bot["pos"][0] - circle["pos"][0]) ** 2 + (bot["pos"][1] - circle["pos"][1]) ** 2)
            if distance < bot["radius"] + circle["radius"]:
                if bot["radius"] > circle["radius"]:  # Bot eats player
                    bot["radius"] += circle["radius"] // 2
                    player_circles.remove(circle)
                    if not player_circles:
                        running = False  # End game if no player circles remain
                else:  # Player eats bot
                    circle["radius"] += bot["radius"] // 2
                    bot_circles.remove(bot)
                break

    #draw controls
    draw_controls()
    
    # Update the screen
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
