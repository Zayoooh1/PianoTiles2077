import pygame
import math # For potential future sound generation
import array # For creating sound buffer

# Initialize Pygame
pygame.init()
pygame.mixer.init() # Initialize the mixer

# Placeholder sound creation
try:
    # Create a 1-second silent sound buffer as a placeholder
    sample_rate = pygame.mixer.get_init()[0] # Get sample rate from mixer
    if not sample_rate: # If mixer didn't init with a rate (should not happen if init() called)
        sample_rate = 44100 # Default fallback

    # Duration of 0.1 seconds for the placeholder, 16-bit stereo (2 channels * 2 bytes/sample)
    # Using a very short silent sound to avoid large buffer for a placeholder
    buffer_size = int(sample_rate * 0.1) * 2 * 2
    if buffer_size == 0: # Ensure buffer_size is not zero if sample_rate was unexpectedly low or zero
        buffer_size = 1024 # A small default buffer size

    buffer = bytearray(buffer_size)
    placeholder_sound = pygame.mixer.Sound(buffer=buffer)
    print("SOUND: Created a silent placeholder sound.")
except Exception as e:
    print(f"SOUND: Could not create placeholder sound buffer: {e}. Sound playback will be silent.")
    placeholder_sound = None # Ensure the variable exists

# Key mapping and sound setup
KEY_MAP = {
    # White keys (bottom row of letters for first octave, then K,L,; for start of second)
    pygame.K_a: 0,  # C1
    pygame.K_s: 2,  # D1
    pygame.K_d: 4,  # E1
    pygame.K_f: 5,  # F1
    pygame.K_g: 7,  # G1
    pygame.K_h: 9,  # A1
    pygame.K_j: 11, # B1
    pygame.K_k: 12, # C2
    pygame.K_l: 14, # D2
    pygame.K_SEMICOLON: 16, # E2

    # Black keys (row above letters, W,E,R,T,Y for first octave, U,I,O,P for start of second)
    pygame.K_w: 1,  # C#1
    pygame.K_e: 3,  # D#1
    pygame.K_r: 6,  # F#1
    pygame.K_t: 8,  # G#1
    pygame.K_y: 10, # A#1
    pygame.K_u: 13, # C#2
    pygame.K_i: 15, # D#2
    pygame.K_o: 18, # F#2
    pygame.K_p: 20, # G#2
}

# If placeholder_sound is None (failed to create), we should handle this.
if placeholder_sound is None:
    print("WARNING: placeholder_sound is None. Sounds will not play.")
    key_sounds = [None] * 24
else:
    key_sounds = [placeholder_sound] * 24 # All 24 keys use the same sound for now

active_pressed_keys = set() # Stores indices of currently pressed piano keys


# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)
DARK_GRAY = (100, 100, 100)
BACKGROUND_COLOR = (230, 230, 250)
PRESSED_WHITE_KEY_COLOR = (220, 220, 220)
PRESSED_BLACK_KEY_COLOR = (50, 50, 50)

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

# Piano key global indices for a 2-octave (24-key) piano
# White keys: C, D, E, F, G, A, B
# Black keys: C#, D#, F#, G#, A#
# Octave 1: C1=0, C#1=1, D1=2, D#1=3, E1=4, F1=5, F#1=6, G1=7, G#1=8, A1=9, A#1=10, B1=11
# Octave 2: C2=12, C#2=13, D2=14, D#2=15, E2=16, F2=17, F#2=18, G2=19, G#2=20, A2=21, A#2=22, B2=23
WHITE_KEY_INDICES_ON_PIANO = []
BLACK_KEY_INDICES_ON_PIANO = []
for o in range(OCTAVES):
    octave_base = o * 12
    WHITE_KEY_INDICES_ON_PIANO.extend([
        octave_base + 0, octave_base + 2, octave_base + 4,  # C, D, E
        octave_base + 5, octave_base + 7, octave_base + 9, octave_base + 11  # F, G, A, B
    ])
    BLACK_KEY_INDICES_ON_PIANO.extend([
        octave_base + 1, octave_base + 3,  # C#, D#
        octave_base + 6, octave_base + 8, octave_base + 10  # F#, G#, A#
    ])

# Function to draw white keys
def draw_white_keys(surface, active_pressed_keys):
    KEYBOARD_Y_POSITION = SCREEN_HEIGHT - KEYBOARD_HEIGHT
    for i in range(NUM_WHITE_KEYS): # i is the visual index of the white key (0 to NUM_WHITE_KEYS-1)
        current_key_global_index = WHITE_KEY_INDICES_ON_PIANO[i]
        x_position = i * WHITE_KEY_WIDTH

        color = WHITE
        if current_key_global_index in active_pressed_keys:
            color = PRESSED_WHITE_KEY_COLOR

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
        pygame.draw.rect(surface, color, key_rect)
        # Draw key border
        pygame.draw.rect(surface, BLACK, key_rect, 1)

# Function to draw black keys
def draw_black_keys(surface, active_pressed_keys):
    KEYBOARD_Y_POSITION = SCREEN_HEIGHT - KEYBOARD_HEIGHT

    # This list gives the visual white key index *after which* a black key appears.
    # This pattern repeats for each octave.
    white_indices_preceding_black_key = []
    for o in range(OCTAVES):
        # For each octave, black keys are after the 0th (C), 1st (D), 3rd (F), 4th (G), 5th (A) white key of that octave.
        # The visual index of a white key in an octave is (white_key_visual_index % 7).
        # The offset for the current octave's white keys is o * 7.
        white_indices_preceding_black_key.extend([
            (o * 7) + 0, (o * 7) + 1,  # After C, After D
            (o * 7) + 3, (o * 7) + 4, (o * 7) + 5  # After F, After G, After A
        ])

    num_black_keys_to_draw = len(BLACK_KEY_INDICES_ON_PIANO)
    for k in range(num_black_keys_to_draw): # k is the sequential index of the black key (0 to NUM_BLACK_KEYS-1)
        current_key_global_index = BLACK_KEY_INDICES_ON_PIANO[k]

        # Determine the visual white key index that this black key should be placed after.
        white_key_idx_for_placement = white_indices_preceding_black_key[k]

        # Calculate x_position based on the white key it's associated with
        x_position = (white_key_idx_for_placement + 1) * WHITE_KEY_WIDTH - (BLACK_KEY_WIDTH / 2)

        color = BLACK
        if current_key_global_index in active_pressed_keys:
            color = PRESSED_BLACK_KEY_COLOR

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
        pygame.draw.rect(surface, color, key_rect)

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
        # Add new event handlers here:
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_MAP:
                piano_key_index = KEY_MAP[event.key]
                active_pressed_keys.add(piano_key_index)
                # Play sound
                if piano_key_index < len(key_sounds) and key_sounds[piano_key_index]:
                    key_sounds[piano_key_index].play()
                else:
                    print(f"Warning: Sound not available for key index {piano_key_index}")

        if event.type == pygame.KEYUP:
            if event.key in KEY_MAP:
                piano_key_index = KEY_MAP[event.key]
                active_pressed_keys.discard(piano_key_index) # Use discard to avoid error if not found

    # Drawing
    screen.fill(BACKGROUND_COLOR)  # Fill the screen with background color
    draw_white_keys(screen, active_pressed_keys)        # Draw the white keys
    draw_black_keys(screen, active_pressed_keys)        # Draw the black keys

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
