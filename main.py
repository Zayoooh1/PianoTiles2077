import pygame

# Initialize Pygame
pygame.init()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BACKGROUND_COLOR = (230, 230, 250)

# Keyboard parameters
OCTAVES = 2
NUM_WHITE_KEYS = OCTAVES * 7
KEYBOARD_HEIGHT = 200
WHITE_KEY_WIDTH = 1200 // NUM_WHITE_KEYS # Assuming SCREEN_WIDTH is 1200 for now
WHITE_KEY_HEIGHT = KEYBOARD_HEIGHT
BLACK_KEY_WIDTH = WHITE_KEY_WIDTH * 0.6
BLACK_KEY_HEIGHT = KEYBOARD_HEIGHT * 0.6
KEY_SHADOW_OFFSET = 3

# Screen dimensions
SCREEN_WIDTH = 1200
# Ensure SCREEN_WIDTH is defined before WHITE_KEY_WIDTH uses it.
# Recalculate WHITE_KEY_WIDTH here if it was dependent on a default SCREEN_WIDTH before
WHITE_KEY_WIDTH = SCREEN_WIDTH // NUM_WHITE_KEYS

# Function to draw white keys
def draw_white_keys(surface):
    KEYBOARD_Y_POSITION = SCREEN_HEIGHT - KEYBOARD_HEIGHT
    for i in range(NUM_WHITE_KEYS):
        x_position = i * WHITE_KEY_WIDTH
        # Draw shadow
        shadow_rect = pygame.Rect(
            x_position + KEY_SHADOW_OFFSET,
            KEYBOARD_Y_POSITION + KEY_SHADOW_OFFSET,
            WHITE_KEY_WIDTH,
            WHITE_KEY_HEIGHT
        )
        pygame.draw.rect(surface, GRAY, shadow_rect)
        # Draw white key
        key_rect = pygame.Rect(
            x_position,
            KEYBOARD_Y_POSITION,
            WHITE_KEY_WIDTH,
            WHITE_KEY_HEIGHT
        )
        pygame.draw.rect(surface, WHITE, key_rect)
        # Draw key border
        pygame.draw.rect(surface, BLACK, key_rect, 1)

# Function to draw black keys
def draw_black_keys(surface):
    KEYBOARD_Y_POSITION = SCREEN_HEIGHT - KEYBOARD_HEIGHT
    # Pattern for black keys: white key indices that have a black key to their right
    # For 2 octaves (14 white keys), this pattern is:
    # C#, D#, F#, G#, A# (repeated for each octave)
    # Indices: 0, 1, 3, 4, 5 (first octave)
    # Then add 7 for the next octave: 7, 8, 10, 11, 12
    black_key_pattern_indices = []
    for octave in range(OCTAVES):
        offset = octave * 7
        black_key_pattern_indices.extend([
            offset + 0, offset + 1,  # C#, D#
            offset + 3, offset + 4, offset + 5  # F#, G#, A#
        ])

    for i in black_key_pattern_indices:
        # Ensure we don't try to draw a black key past the last white key
        if i >= NUM_WHITE_KEYS -1: # -1 because it's relative to the white key it's "after"
            continue

        x_position = (i + 1) * WHITE_KEY_WIDTH - (BLACK_KEY_WIDTH / 2)

        # Draw shadow
        shadow_rect = pygame.Rect(
            x_position + KEY_SHADOW_OFFSET,
            KEYBOARD_Y_POSITION + KEY_SHADOW_OFFSET,
            BLACK_KEY_WIDTH,
            BLACK_KEY_HEIGHT
        )
        pygame.draw.rect(surface, DARK_GRAY, shadow_rect)

        # Draw black key
        key_rect = pygame.Rect(
            x_position,
            KEYBOARD_Y_POSITION,
            BLACK_KEY_WIDTH,
            BLACK_KEY_HEIGHT
        )
        pygame.draw.rect(surface, BLACK, key_rect)

# Screen dimensions (SCREEN_WIDTH already defined, SCREEN_HEIGHT needed)
SCREEN_HEIGHT = 800

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Set window title
pygame.display.set_caption("Piano App")

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Drawing
    screen.fill(BACKGROUND_COLOR)  # Fill the screen with background color
    draw_white_keys(screen)        # Draw the white keys
    draw_black_keys(screen)        # Draw the black keys

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
