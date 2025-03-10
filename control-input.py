import pygame
import sys

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flashing Boxes")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

# Font
font = pygame.font.Font(None, 36)  # Default font, size 36

# Box dimensions
BOX_SIZE = 100

# Box positions
top_box = pygame.Rect((SCREEN_WIDTH // 2 - BOX_SIZE // 2, 50), (BOX_SIZE, BOX_SIZE))
right_box = pygame.Rect((SCREEN_WIDTH - BOX_SIZE - 50, SCREEN_HEIGHT // 2 - BOX_SIZE // 2), (BOX_SIZE, BOX_SIZE))
bottom_box = pygame.Rect((SCREEN_WIDTH // 2 - BOX_SIZE // 2, SCREEN_HEIGHT - BOX_SIZE - 50), (BOX_SIZE, BOX_SIZE))
left_box = pygame.Rect((50, SCREEN_HEIGHT // 2 - BOX_SIZE // 2), (BOX_SIZE, BOX_SIZE))

# Flashing frequencies (in Hz)
frequencies = {
    "top": 12,  # 10 Hz
    "right": 14,  # 15 Hz
    "bottom": 16,  # 20 Hz
    "left": 18  # 25 Hz
}

# Time periods (in milliseconds)
time_periods = {key: 1000 // freq for key, freq in frequencies.items()}

# Box visibility states
visible_states = {
    "top": True,
    "right": True,
    "bottom": True,
    "left": True
}

# Clock for controlling frame rate
clock = pygame.time.Clock()

# Timing variables
last_toggle_times = {key: pygame.time.get_ticks() for key in frequencies}

# Game loop
while True:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Get current time
    current_time = pygame.time.get_ticks()

    # Update visibility states based on flashing frequencies
    for key in frequencies:
        if current_time - last_toggle_times[key] >= time_periods[key]:
            visible_states[key] = not visible_states[key]
            last_toggle_times[key] = current_time

    # Clear the screen
    screen.fill(BLACK)

    # Draw boxes based on visibility states
    if visible_states["top"]:
        pygame.draw.rect(screen, GREEN, top_box)
    if visible_states["right"]:
        pygame.draw.rect(screen, GREEN, right_box)
    if visible_states["bottom"]:
        pygame.draw.rect(screen, GREEN, bottom_box)
    if visible_states["left"]:
        pygame.draw.rect(screen, GREEN, left_box)

    # Render and draw labels
    forward_text = font.render("Forward", True, WHITE)
    right_text = font.render("Right", True, WHITE)
    backward_text = font.render("Backward", True, WHITE)
    left_text = font.render("Left", True, WHITE)

    # Blit labels to the screen
    screen.blit(forward_text, (SCREEN_WIDTH // 2 - forward_text.get_width() // 2, 10))  # Label for the top box
    screen.blit(right_text, (SCREEN_WIDTH - BOX_SIZE - 50 + BOX_SIZE // 2 - right_text.get_width() // 2,
                             SCREEN_HEIGHT // 2 - BOX_SIZE // 1.2 - right_text.get_height() // 2))  # Label for the right box
    screen.blit(backward_text, (
    SCREEN_WIDTH // 2 - backward_text.get_width() // 2, SCREEN_HEIGHT - BOX_SIZE - 90))  # Label for the bottom box
    screen.blit(left_text, (50 + BOX_SIZE // 2 - left_text.get_width() // 2,
                            SCREEN_HEIGHT // 2 - BOX_SIZE // 1.2 - left_text.get_height() // 2))  # Label for the left box

    # Update the display
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

