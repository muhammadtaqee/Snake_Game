import pygame
import random
import time
import sys
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Game variables
clock = pygame.time.Clock()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Snake Game")

# Load sounds
try:
    eat_sound = mixer.Sound("eat.wav")  # Create this file or remove this line
    game_over_sound = mixer.Sound("game_over.wav")  # Create this file or remove this line
except:
    print("Sound files not found. Continuing without sound.")

# Snake skins
SKINS = {
    "classic": GREEN,
    "rainbow": [(255, 0, 0), (255, 165, 0), (255, 255, 0), (0, 255, 0), 
               (0, 0, 255), (75, 0, 130), (238, 130, 238)],
    "blue": BLUE,
    "gold": (255, 215, 0)
}

# Levels
LEVELS = [
    {"speed": 10, "description": "Easy - Slow speed, no obstacles"},
    {"speed": 15, "description": "Medium - Faster speed, some walls"},
    {"speed": 20, "description": "Hard - Fast speed, maze walls"},
    {"speed": 25, "description": "Expert - Very fast, complex maze"}
]

class Snake:
    def __init__(self, skin="classic"):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.length = 1
        self.score = 0
        self.level = 0
        self.skin = skin
        self.color_index = 0
        self.obstacles = []
        self.grow_to = 1
        
    def get_head_position(self):
        return self.positions[0]
    
    def get_color(self, index):
        if self.skin == "rainbow":
            return SKINS["rainbow"][index % len(SKINS["rainbow"])]
        return SKINS.get(self.skin, GREEN)
    
    def update(self):
        head = self.get_head_position()
        x, y = self.direction
        new_head = ((head[0] + x) % GRID_WIDTH, (head[1] + y) % GRID_HEIGHT)
        
        # Check for collision with self
        if new_head in self.positions[1:]:
            return True  # Game over
        
        # Check for collision with obstacles
        if new_head in self.obstacles:
            return True  # Game over
        
        self.positions.insert(0, new_head)
        if len(self.positions) > self.grow_to:
            self.positions.pop()
        else:
            self.grow_to = self.length
        
        return False  # Continue game
    
    def grow(self):
        self.length += 1
        self.grow_to = self.length
        self.score += 10 * (self.level + 1)
    
    def change_direction(self, direction):
        # Prevent 180-degree turns
        if (direction[0] * -1, direction[1] * -1) != self.direction:
            self.direction = direction
    
    def draw(self, surface):
        for i, p in enumerate(self.positions):
            color = self.get_color(i)
            rect = pygame.Rect((p[0] * GRID_SIZE, p[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)
    
    def reset(self):
        self.positions = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = (1, 0)
        self.length = 1
        self.grow_to = 1
        self.score = 0
        self.obstacles = []
        self.generate_obstacles()
    
    def generate_obstacles(self):
        self.obstacles = []
        
        # Level-based obstacles
        if self.level >= 1:  # Medium level
            # Border walls
            for x in range(GRID_WIDTH):
                self.obstacles.append((x, 0))
                self.obstacles.append((x, GRID_HEIGHT - 1))
            for y in range(GRID_HEIGHT):
                self.obstacles.append((0, y))
                self.obstacles.append((GRID_WIDTH - 1, y))
        
        if self.level >= 2:  # Hard level
            # Some random walls
            for _ in range(5):
                wall_x = random.randint(5, GRID_WIDTH - 5)
                wall_y = random.randint(5, GRID_HEIGHT - 5)
                length = random.randint(3, 8)
                horizontal = random.choice([True, False])
                
                for i in range(length):
                    if horizontal:
                        self.obstacles.append((wall_x + i, wall_y))
                    else:
                        self.obstacles.append((wall_x, wall_y + i))
        
        if self.level >= 3:  # Expert level
            # Complex maze pattern
            for x in range(5, GRID_WIDTH - 5, 2):
                self.obstacles.append((x, 5))
                self.obstacles.append((x, GRID_HEIGHT - 5))
            for y in range(5, GRID_HEIGHT - 5, 2):
                self.obstacles.append((5, y))
                self.obstacles.append((GRID_WIDTH - 5, y))
    
    def draw_obstacles(self, surface):
        for obstacle in self.obstacles:
            rect = pygame.Rect((obstacle[0] * GRID_SIZE, obstacle[1] * GRID_SIZE), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, PURPLE, rect)
            pygame.draw.rect(surface, BLACK, rect, 1)

class Food:
    def __init__(self, snake):
        self.position = (0, 0)
        self.color = RED
        self.randomize_position(snake)
        self.special = False
        self.special_timer = 0
        self.spawn_time = time.time()
    
    def randomize_position(self, snake):
        self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        while self.position in snake.positions or self.position in snake.obstacles:
            self.position = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
        
        # 20% chance to be special food
        self.special = random.random() < 0.2
        self.spawn_time = time.time()
    
    def draw(self, surface):
        size = GRID_SIZE
        if self.special:
            # Blinking effect for special food
            if int(time.time() * 2) % 2 == 0:
                color = YELLOW
            else:
                color = (255, 165, 0)  # Orange
            size = GRID_SIZE * 1.2
        else:
            color = self.color
        
        rect = pygame.Rect((self.position[0] * GRID_SIZE, self.position[1] * GRID_SIZE), (size, size))
        pygame.draw.rect(surface, color, rect)
        pygame.draw.rect(surface, BLACK, rect, 1)

def draw_grid(surface):
    for y in range(0, HEIGHT, GRID_SIZE):
        for x in range(0, WIDTH, GRID_SIZE):
            rect = pygame.Rect((x, y), (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(surface, (40, 40, 40), rect, 1)

def show_menu():
    selected_skin = "classic"
    selected_level = 0
    
    while True:
        screen.fill(BLACK)
        
        # Title
        title_font = pygame.font.SysFont("arial", 50)
        title_text = title_font.render("SNAKE GAME", True, GREEN)
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, 50))
        
        # Skin selection
        skin_font = pygame.font.SysFont("arial", 30)
        skin_text = skin_font.render("Select Skin:", True, WHITE)
        screen.blit(skin_text, (WIDTH // 2 - skin_text.get_width() // 2, 150))
        
        skin_y = 200
        for i, (skin_name, _) in enumerate(SKINS.items()):
            color = YELLOW if skin_name == selected_skin else WHITE
            skin_option = skin_font.render(skin_name.capitalize(), True, color)
            screen.blit(skin_option, (WIDTH // 2 - skin_option.get_width() // 2, skin_y))
            skin_y += 40
        
        # Level selection
        level_font = pygame.font.SysFont("arial", 30)
        level_text = level_font.render("Select Level:", True, WHITE)
        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, skin_y + 30))
        
        level_y = skin_y + 80
        for i, level in enumerate(LEVELS):
            color = YELLOW if i == selected_level else WHITE
            level_option = level_font.render(f"Level {i+1}: {level['description']}", True, color)
            screen.blit(level_option, (WIDTH // 2 - level_option.get_width() // 2, level_y))
            level_y += 40
        
        # Start instruction
        start_font = pygame.font.SysFont("arial", 25)
        start_text = start_font.render("Press SPACE to start or ESC to quit", True, WHITE)
        screen.blit(start_text, (WIDTH // 2 - start_text.get_width() // 2, HEIGHT - 50))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    selected_skin = list(SKINS.keys())[(list(SKINS.keys()).index(selected_skin) - 1) % len(SKINS)]
                elif event.key == pygame.K_DOWN:
                    selected_skin = list(SKINS.keys())[(list(SKINS.keys()).index(selected_skin) + 1) % len(SKINS)]
                elif event.key == pygame.K_LEFT:
                    selected_level = (selected_level - 1) % len(LEVELS)
                elif event.key == pygame.K_RIGHT:
                    selected_level = (selected_level + 1) % len(LEVELS)
                elif event.key == pygame.K_SPACE:
                    return selected_skin, selected_level
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

def show_game_over(score):
    while True:
        screen.fill(BLACK)
        
        # Game over text
        font = pygame.font.SysFont("arial", 50)
        text = font.render("GAME OVER", True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))
        
        # Score
        score_font = pygame.font.SysFont("arial", 30)
        score_text = score_font.render(f"Final Score: {score}", True, WHITE)
        screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, HEIGHT // 2))
        
        # Instructions
        restart_font = pygame.font.SysFont("arial", 25)
        restart_text = restart_font.render("Press SPACE to restart or ESC to quit", True, WHITE)
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 100))
        
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True  # Restart
                elif event.key == pygame.K_ESCAPE:
                    return False  # Quit

def main():
    while True:
        # Show menu and get selections
        skin, level = show_menu()
        
        # Initialize game
        snake = Snake(skin)
        snake.level = level
        snake.generate_obstacles()
        food = Food(snake)
        fps = LEVELS[level]["speed"]
        
        running = True
        game_over = False
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        snake.change_direction((0, -1))
                    elif event.key == pygame.K_DOWN:
                        snake.change_direction((0, 1))
                    elif event.key == pygame.K_LEFT:
                        snake.change_direction((-1, 0))
                    elif event.key == pygame.K_RIGHT:
                        snake.change_direction((1, 0))
                    elif event.key == pygame.K_ESCAPE:
                        running = False
            
            if not game_over:
                # Update snake
                game_over = snake.update()
                
                # Check if snake ate food
                if snake.get_head_position() == food.position:
                    try:
                        mixer.Sound.play(eat_sound)
                    except:
                        pass
                    
                    if food.special:
                        snake.score += 50 * (snake.level + 1)
                        snake.grow()
                        snake.grow()  # Extra growth for special food
                    else:
                        snake.grow()
                    
                    food = Food(snake)
                
                # Check if special food expired (5 seconds)
                if food.special and time.time() - food.spawn_time > 5:
                    food.special = False
            
            # Draw everything
            screen.fill(BLACK)
            draw_grid(screen)
            snake.draw_obstacles(screen)
            food.draw(screen)
            snake.draw(screen)
            
            # Display score and level
            font = pygame.font.SysFont("arial", 20)
            score_text = font.render(f"Score: {snake.score}", True, WHITE)
            level_text = font.render(f"Level: {level + 1}", True, WHITE)
            screen.blit(score_text, (5, 5))
            screen.blit(level_text, (5, 30))
            
            if game_over:
                try:
                    mixer.Sound.play(game_over_sound)
                except:
                    pass
                
                # Dark overlay
                overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                overlay.fill((0, 0, 0, 180))
                screen.blit(overlay, (0, 0))
                
                # Game over text
                font = pygame.font.SysFont("arial", 50)
                text = font.render("PAUSED - Press any key", True, RED)
                screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2))
            
            pygame.display.update()
            clock.tick(fps)
            
            if game_over:
                pygame.time.wait(1000)  # Short delay before showing game over screen
                if show_game_over(snake.score):
                    break  # Restart game
                else:
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    main()
