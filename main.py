import pygame
import math # For potential future sound generation
import array # For creating sound buffer
import mido # For MIDI support
import random # For starfield
import tkinter as tk
from tkinter import filedialog

# 1. Pygame Initializations
pygame.init()
pygame.mixer.init()
try:
    pygame.font.init()
except Exception as e:
    print(f"Warning: pygame.font.init() error: {e}. Font loading might fail.")
    # pygame.init() should cover font init, this is a fallback.

# 2. Screen Setup
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Piano App")

# 3. Core Layout Constants
OCTAVES = 2
KEYBOARD_HEIGHT = 200
CONTROL_PANEL_HEIGHT = 60

# 4. Dependent Y Positions
KEYBOARD_Y_POSITION = SCREEN_HEIGHT - KEYBOARD_HEIGHT - CONTROL_PANEL_HEIGHT
CONTROL_PANEL_Y_POSITION = SCREEN_HEIGHT - CONTROL_PANEL_HEIGHT

# 5. Control Panel Rectangle
CONTROL_PANEL_RECT = pygame.Rect(0, CONTROL_PANEL_Y_POSITION, SCREEN_WIDTH, CONTROL_PANEL_HEIGHT)

# 6. Color Definitions
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200) # White key shadow
DARK_GRAY = (100, 100, 100) # Black key shadow
BACKGROUND_COLOR = (10, 20, 40) # Dark Navy Blue
ACCENT_COLOR = (0, 255, 255) # Cyan
PRESSED_WHITE_KEY_COLOR = ACCENT_COLOR
PRESSED_BLACK_KEY_COLOR = ACCENT_COLOR
CONTROL_PANEL_COLOR = (30, 40, 60) # Panel background

# Import MIDI Button Colors (distinct from control panel buttons if needed)
IMPORT_BUTTON_COLOR = (100, 149, 237)  # Cornflower blue for "Import MIDI"
IMPORT_BUTTON_TEXT_COLOR = (255, 255, 255)

# Control Panel Elements Colors
CONTROL_BUTTON_COLOR = ACCENT_COLOR # Base for Start, Pause, etc.
CONTROL_BUTTON_TEXT_COLOR = BACKGROUND_COLOR # Text color for control buttons (dark on light accent)
CONTROL_BUTTON_ACTIVE_COLOR = (0, 200, 200) # Slightly dimmer cyan for active press
SLIDER_TRACK_COLOR = (70, 80, 100)
SLIDER_HANDLE_COLOR = ACCENT_COLOR # Handle color (can be same as track or accent)

# Progress Bar Colors
PROGRESS_BAR_COLOR = ACCENT_COLOR # Filled part
PROGRESS_BAR_BACKGROUND_COLOR = (50, 60, 80) # Unfilled part

# 7. Key Dimensions
NUM_WHITE_KEYS = OCTAVES * 7
WHITE_KEY_WIDTH = SCREEN_WIDTH // NUM_WHITE_KEYS
WHITE_KEY_HEIGHT = KEYBOARD_HEIGHT
BLACK_KEY_WIDTH = WHITE_KEY_WIDTH * 0.6
BLACK_KEY_HEIGHT = KEYBOARD_HEIGHT * 0.6 # Black keys are shorter
KEY_SHADOW_OFFSET = 3

# 8. Fonts
IMPORT_BUTTON_FONT = pygame.font.Font(None, 30) # For "Import MIDI"
CONTROL_PANEL_FONT_SIZE = 20
CONTROL_PANEL_FONT = pygame.font.Font(None, CONTROL_PANEL_FONT_SIZE)

# 9. Import MIDI Button Layout
IMPORT_BUTTON_RECT = pygame.Rect(20, 20, 150, 50) # x, y, width, height
IMPORT_BUTTON_TEXT = "Import MIDI"

# 10. Control Panel Element Layout
# Button dimensions and spacing
_BUTTON_WIDTH = 80
_BUTTON_HEIGHT = 40
_BUTTON_SPACING = 15
_TOTAL_BUTTONS_WIDTH = (4 * _BUTTON_WIDTH) + (3 * _BUTTON_SPACING)

# Slider dimensions and spacing
_SLIDER_WIDTH = 150
_SLIDER_TRACK_HEIGHT = 10
_SLIDER_HANDLE_RADIUS = 8
_SLIDER_SPACING = 30

# Overall layout for controls within the panel
_BUTTONS_SECTION_WIDTH = _TOTAL_BUTTONS_WIDTH
_SLIDERS_SECTION_WIDTH = (2 * _SLIDER_WIDTH) + _SLIDER_SPACING
_SECTION_SPACING = 50

_TOTAL_CONTROLS_WIDTH = _BUTTONS_SECTION_WIDTH + _SECTION_SPACING + _SLIDERS_SECTION_WIDTH
_CONTROLS_START_X = (SCREEN_WIDTH - _TOTAL_CONTROLS_WIDTH) // 2

# Button Rectangles
_BUTTON_Y = CONTROL_PANEL_Y_POSITION + (CONTROL_PANEL_HEIGHT - _BUTTON_HEIGHT) // 2
_NEW_START_X_BUTTONS = _CONTROLS_START_X
START_BUTTON_RECT = pygame.Rect(_NEW_START_X_BUTTONS, _BUTTON_Y, _BUTTON_WIDTH, _BUTTON_HEIGHT)
PAUSE_BUTTON_RECT = pygame.Rect(_NEW_START_X_BUTTONS + _BUTTON_WIDTH + _BUTTON_SPACING, _BUTTON_Y, _BUTTON_WIDTH, _BUTTON_HEIGHT)
STOP_BUTTON_RECT = pygame.Rect(_NEW_START_X_BUTTONS + 2 * (_BUTTON_WIDTH + _BUTTON_SPACING), _BUTTON_Y, _BUTTON_WIDTH, _BUTTON_HEIGHT)
MODE_BUTTON_RECT = pygame.Rect(_NEW_START_X_BUTTONS + 3 * (_BUTTON_WIDTH + _BUTTON_SPACING), _BUTTON_Y, _BUTTON_WIDTH, _BUTTON_HEIGHT)

# Slider Track Rectangles
_SLIDERS_GROUP_START_X = _NEW_START_X_BUTTONS + _BUTTONS_SECTION_WIDTH + _SECTION_SPACING
_SLIDER_TRACK_Y_CENTER = CONTROL_PANEL_Y_POSITION + CONTROL_PANEL_HEIGHT // 2
TEMPO_SLIDER_TRACK_RECT = pygame.Rect(_SLIDERS_GROUP_START_X, _SLIDER_TRACK_Y_CENTER - _SLIDER_TRACK_HEIGHT // 2, _SLIDER_WIDTH, _SLIDER_TRACK_HEIGHT)
VOLUME_SLIDER_TRACK_RECT = pygame.Rect(_SLIDERS_GROUP_START_X + _SLIDER_WIDTH + _SLIDER_SPACING, _SLIDER_TRACK_Y_CENTER - _SLIDER_TRACK_HEIGHT // 2, _SLIDER_WIDTH, _SLIDER_TRACK_HEIGHT)

# 11. Progress Bar Layout
PROGRESS_BAR_HEIGHT = 10
PROGRESS_BAR_Y = CONTROL_PANEL_RECT.top + 8 # Adjusted padding slightly
PROGRESS_BAR_WIDTH = CONTROL_PANEL_RECT.width - 40
PROGRESS_BAR_X = (CONTROL_PANEL_RECT.width - PROGRESS_BAR_WIDTH) // 2
PROGRESS_BAR_RECT = pygame.Rect(PROGRESS_BAR_X, PROGRESS_BAR_Y, PROGRESS_BAR_WIDTH, PROGRESS_BAR_HEIGHT)

# 12. Effect Parameters
# Starfield
NUM_STARS = 100
STAR_COLOR = (200, 200, 200)
STAR_MAX_BRIGHTNESS = 150
STAR_MIN_BRIGHTNESS = 20
STAR_TWINKLE_SPEED = 0.001
# Shockwave
SHOCKWAVE_MAX_RADIUS = 60
SHOCKWAVE_EXPANSION_SPEED = 1.5
SHOCKWAVE_INITIAL_OPACITY = 255
SHOCKWAVE_FADE_RATE = 4
SHOCKWAVE_NUM_RINGS = 3
SHOCKWAVE_RING_SPACING = 10
SHOCKWAVE_COLOR = ACCENT_COLOR # Uses ACCENT_COLOR

# 13. Slider Min/Max Values
MIN_TEMPO_BPM = 30
MAX_TEMPO_BPM = 240
MIN_VOLUME = 0.0
MAX_VOLUME = 1.0

# 14. Placeholder Sound Creation
try:
    sample_rate = pygame.mixer.get_init()[0]
    if not sample_rate: sample_rate = 44100
    buffer_size = int(sample_rate * 0.1) * 2 * 2
    if buffer_size == 0: buffer_size = 1024
    buffer = bytearray(buffer_size)
    placeholder_sound = pygame.mixer.Sound(buffer=buffer)
    print("SOUND: Created a silent placeholder sound.")
except Exception as e:
    print(f"SOUND: Could not create placeholder sound buffer: {e}. Sound playback will be silent.")
    placeholder_sound = None

# 15. Key Map & Sounds List
KEY_MAP = {
    pygame.K_a: 0, pygame.K_s: 2, pygame.K_d: 4, pygame.K_f: 5, pygame.K_g: 7, pygame.K_h: 9, pygame.K_j: 11,
    pygame.K_k: 12, pygame.K_l: 14, pygame.K_SEMICOLON: 16,
    pygame.K_w: 1, pygame.K_e: 3, pygame.K_r: 6, pygame.K_t: 8, pygame.K_y: 10,
    pygame.K_u: 13, pygame.K_i: 15, pygame.K_o: 18, pygame.K_p: 20,
}
num_piano_keys = OCTAVES * 12
if placeholder_sound is None:
    print("WARNING: placeholder_sound is None. Sounds will not play for keys.")
    key_sounds = [None] * num_piano_keys
else:
    key_sounds = [placeholder_sound] * num_piano_keys

# 16. State Variables
# MIDI data and playback state
loaded_midi_path = None
parsed_midi_sequence = []
total_midi_duration_ms = 0
current_midi_playback_time = 0.0
midi_playing = False
midi_sequence_current_event_index = 0
playback_start_system_time = 0
# UI and effects state
active_pressed_keys = set()
stars = []
active_shockwaves = []
# Control Panel state
playback_status = "stopped"  # "playing", "paused", "stopped"
current_mode = "presentation" # "presentation", "learning"
tempo_bpm = 120
global_volume = 0.8
active_button_name = None
dragging_slider_name = None

# 17. Piano Key Rectangles Initialization (dependent on layout constants)
all_piano_key_rects = [None] * num_piano_keys # Initialize list

# Piano key global indices (used by initialize_key_rects and drawing functions)
WHITE_KEY_INDICES_ON_PIANO = []
BLACK_KEY_INDICES_ON_PIANO = []
for o in range(OCTAVES):
    octave_base = o * 12
    WHITE_KEY_INDICES_ON_PIANO.extend([
        octave_base + 0, octave_base + 2, octave_base + 4,
        octave_base + 5, octave_base + 7, octave_base + 9, octave_base + 11
    ])
    BLACK_KEY_INDICES_ON_PIANO.extend([
        octave_base + 1, octave_base + 3,
        octave_base + 6, octave_base + 8, octave_base + 10
    ])
# NOTE: The rest of the file (function definitions and main loop) starts from here.
# The initialize_key_rects() function definition and its call will be part of the next section.
# This overwrite block ends here.

# (Function definitions like initialize_key_rects, draw_white_keys, etc., and main loop follow)
# The existing initialize_key_rects function is fine, just ensure it's called after these constants.
# The call to initialize_key_rects() is already present after screen setup in the existing code.
# This reordering should place it correctly relative to its dependencies.

# --- End of the constants and initializations block to be overwritten ---
# The following is how the file continues, starting with initialize_key_rects definition
# (This part is NOT part of the overwrite_file_with_block, but for context)

# def initialize_key_rects(): ...
# ... (all other function definitions) ...
# init_stars(...) # This call should be after screen, before main loop
# initialize_key_rects() # This call should be after screen, before main loop

# Main game loop
# while running:
#    ...
# pygame.quit()
