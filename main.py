import pygame
import math # For potential future sound generation
import array # For creating sound buffer
import mido # For MIDI support
import random # For starfield
import tkinter as tk
from tkinter import filedialog

# Initialize Pygame
pygame.init()
pygame.mixer.init() # Initialize the mixer
try:
    pygame.font.init() # Ensure font module is initialized
except Exception:
    pass # Should already be covered by pygame.init()

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
BACKGROUND_COLOR = (10, 20, 40) # Dark Navy Blue
ACCENT_COLOR = (0, 255, 255) # Cyan
PRESSED_WHITE_KEY_COLOR = ACCENT_COLOR
PRESSED_BLACK_KEY_COLOR = ACCENT_COLOR

# Button parameters
BUTTON_COLOR = (100, 149, 237)  # Cornflower blue
BUTTON_TEXT_COLOR = (255, 255, 255)
BUTTON_RECT = pygame.Rect(20, 20, 150, 50) # x, y, width, height
BUTTON_TEXT = "Import MIDI"
BUTTON_FONT = pygame.font.Font(None, 30) # Default font, size 30

# Global variable for MIDI path
loaded_midi_path = None
parsed_midi_sequence = []
current_midi_playback_time = 0.0
total_midi_duration_ms = 0 # Will be updated when MIDI is parsed
midi_playing = False
midi_sequence_current_event_index = 0
playback_start_system_time = 0

# Progress Bar properties
PROGRESS_BAR_HEIGHT = 10
PROGRESS_BAR_Y = CONTROL_PANEL_RECT.top + 10 # 10px padding from top of panel
PROGRESS_BAR_WIDTH = CONTROL_PANEL_RECT.width - 40 # With some horizontal padding
PROGRESS_BAR_X = (CONTROL_PANEL_RECT.width - PROGRESS_BAR_WIDTH) // 2 # Centered horizontally
PROGRESS_BAR_RECT = pygame.Rect(PROGRESS_BAR_X, PROGRESS_BAR_Y, PROGRESS_BAR_WIDTH, PROGRESS_BAR_HEIGHT)
PROGRESS_BAR_COLOR = ACCENT_COLOR
PROGRESS_BAR_BACKGROUND_COLOR = (50, 60, 80)

# Control Panel Elements - Colors and Font
CONTROL_BUTTON_COLOR = ACCENT_COLOR
CONTROL_BUTTON_TEXT_COLOR = (10, 20, 40) # Dark Navy Blue, for contrast on Accent Color
CONTROL_BUTTON_ACTIVE_COLOR = (0, 200, 200) # Slightly dimmer cyan for active press
SLIDER_TRACK_COLOR = (70, 80, 100)
SLIDER_HANDLE_COLOR = ACCENT_COLOR
CONTROL_PANEL_FONT_SIZE = 20
# Ensure pygame.font.init() was called (it is, after pygame.init())
CONTROL_PANEL_FONT = pygame.font.Font(None, CONTROL_PANEL_FONT_SIZE)

# Control Panel Elements - Layout and Rectangles
# Button dimensions and spacing
_BUTTON_WIDTH = 80
_BUTTON_HEIGHT = 40
_BUTTON_SPACING = 15
_TOTAL_BUTTONS_WIDTH = (4 * _BUTTON_WIDTH) + (3 * _BUTTON_SPACING)

# Slider dimensions and spacing
_SLIDER_WIDTH = 150
_SLIDER_TRACK_HEIGHT = 10 # Height of the track itself
_SLIDER_HANDLE_RADIUS = 8
# _SLIDER_AREA_HEIGHT = 40 # Total vertical area for one slider with label
_SLIDER_SPACING = 30 # Between sliders

# Overall layout for controls within the panel
_BUTTONS_SECTION_WIDTH = _TOTAL_BUTTONS_WIDTH
_SLIDERS_SECTION_WIDTH = (2 * _SLIDER_WIDTH) + _SLIDER_SPACING
_SECTION_SPACING = 50 # Space between buttons section and sliders section

_TOTAL_CONTROLS_WIDTH = _BUTTONS_SECTION_WIDTH + _SECTION_SPACING + _SLIDERS_SECTION_WIDTH
_CONTROLS_START_X = (SCREEN_WIDTH - _TOTAL_CONTROLS_WIDTH) // 2

# Button Rectangles (Y position centered within the control panel)
_BUTTON_Y = CONTROL_PANEL_Y_POSITION + (CONTROL_PANEL_HEIGHT - _BUTTON_HEIGHT) // 2
_NEW_START_X_BUTTONS = _CONTROLS_START_X

START_BUTTON_RECT = pygame.Rect(_NEW_START_X_BUTTONS, _BUTTON_Y, _BUTTON_WIDTH, _BUTTON_HEIGHT)
PAUSE_BUTTON_RECT = pygame.Rect(_NEW_START_X_BUTTONS + _BUTTON_WIDTH + _BUTTON_SPACING, _BUTTON_Y, _BUTTON_WIDTH, _BUTTON_HEIGHT)
STOP_BUTTON_RECT = pygame.Rect(_NEW_START_X_BUTTONS + 2 * (_BUTTON_WIDTH + _BUTTON_SPACING), _BUTTON_Y, _BUTTON_WIDTH, _BUTTON_HEIGHT)
MODE_BUTTON_RECT = pygame.Rect(_NEW_START_X_BUTTONS + 3 * (_BUTTON_WIDTH + _BUTTON_SPACING), _BUTTON_Y, _BUTTON_WIDTH, _BUTTON_HEIGHT)

# Slider Rectangles (for tracks, handles will be derived)
_SLIDERS_GROUP_START_X = _NEW_START_X_BUTTONS + _BUTTONS_SECTION_WIDTH + _SECTION_SPACING
_SLIDER_TRACK_Y_CENTER = CONTROL_PANEL_Y_POSITION + CONTROL_PANEL_HEIGHT // 2 # Vertically centered track

TEMPO_SLIDER_TRACK_RECT = pygame.Rect(_SLIDERS_GROUP_START_X, _SLIDER_TRACK_Y_CENTER - _SLIDER_TRACK_HEIGHT // 2, _SLIDER_WIDTH, _SLIDER_TRACK_HEIGHT)
VOLUME_SLIDER_TRACK_RECT = pygame.Rect(_SLIDERS_GROUP_START_X + _SLIDER_WIDTH + _SLIDER_SPACING, _SLIDER_TRACK_Y_CENTER - _SLIDER_TRACK_HEIGHT // 2, _SLIDER_WIDTH, _SLIDER_TRACK_HEIGHT)

# Control Panel State Variables
playback_status = "stopped"  # "playing", "paused", "stopped"
current_mode = "presentation" # "presentation", "learning"
tempo_bpm = 120  # Default BPM (e.g., min 30, max 240)
global_volume = 0.8  # Default volume (0.0 to 1.0)

active_button_name = None # Stores name like "start", "pause", etc. or None
dragging_slider_name = None # Stores "tempo", "volume", or None


# Starfield parameters
NUM_STARS = 100
MIN_TEMPO_BPM = 30
MAX_TEMPO_BPM = 240
MIN_VOLUME = 0.0
MAX_VOLUME = 1.0
STAR_COLOR = (200, 200, 200) # Pale white/gray for stars
STAR_MAX_BRIGHTNESS = 150 # Max base brightness for a star
STAR_MIN_BRIGHTNESS = 20  # Min brightness in twinkle cycle
STAR_TWINKLE_SPEED = 0.001 # General speed multiplier for twinkle, individual stars vary

stars = []

# Shockwave Effect Parameters
SHOCKWAVE_MAX_RADIUS = 60
SHOCKWAVE_EXPANSION_SPEED = 1.5 # Pixels per frame
SHOCKWAVE_INITIAL_OPACITY = 255
SHOCKWAVE_FADE_RATE = 4 # Opacity decrease per frame
SHOCKWAVE_NUM_RINGS = 3
SHOCKWAVE_RING_SPACING = 10 # Spacing between rings
SHOCKWAVE_COLOR = ACCENT_COLOR

active_shockwaves = [] # List to store active shockwave animations
all_piano_key_rects = [None] * (OCTAVES * 12) # For 2 octaves, 24 keys

# Keyboard parameters
OCTAVES = 2
NUM_WHITE_KEYS = OCTAVES * 7
KEYBOARD_HEIGHT = 200 # Height of the keyboard area
# CONTROL_PANEL_HEIGHT will be defined after SCREEN_HEIGHT for proper Y calculation

# Screen dimensions
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800 # Defined earlier, good.

# Control Panel parameters
CONTROL_PANEL_HEIGHT = 60
CONTROL_PANEL_COLOR = (30, 40, 60) # Slightly different dark shade for the panel
KEYBOARD_Y_POSITION = SCREEN_HEIGHT - KEYBOARD_HEIGHT - CONTROL_PANEL_HEIGHT # Keyboard sits above control panel
CONTROL_PANEL_Y_POSITION = SCREEN_HEIGHT - CONTROL_PANEL_HEIGHT # Panel at the very bottom
CONTROL_PANEL_RECT = pygame.Rect(0, CONTROL_PANEL_Y_POSITION, SCREEN_WIDTH, CONTROL_PANEL_HEIGHT)


WHITE_KEY_WIDTH = SCREEN_WIDTH // NUM_WHITE_KEYS # Use SCREEN_WIDTH after it's defined
WHITE_KEY_HEIGHT = KEYBOARD_HEIGHT
BLACK_KEY_WIDTH = WHITE_KEY_WIDTH * 0.6
BLACK_KEY_HEIGHT = KEYBOARD_HEIGHT * 0.6
KEY_SHADOW_OFFSET = 3


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
    # KEYBOARD_Y_POSITION is now global
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
    # KEYBOARD_Y_POSITION is now global

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

# Generic function to draw a button
def draw_button(surface, rect, text, base_color, text_color, font, is_pressed=False):
    button_color = CONTROL_BUTTON_ACTIVE_COLOR if is_pressed else base_color
    pygame.draw.rect(surface, button_color, rect, border_radius=5)

    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

    pygame.draw.rect(surface, ACCENT_COLOR, rect, 1, border_radius=5) # Thin accent border

# Function to draw all control buttons
def draw_control_buttons(surface):
    # Start Button
    is_start_pressed = (active_button_name == "start")
    draw_button(surface, START_BUTTON_RECT, "Start", CONTROL_BUTTON_COLOR, CONTROL_BUTTON_TEXT_COLOR, CONTROL_PANEL_FONT, is_pressed=is_start_pressed)

    # Pause Button
    is_pause_pressed = (active_button_name == "pause")
    draw_button(surface, PAUSE_BUTTON_RECT, "Pause", CONTROL_BUTTON_COLOR, CONTROL_BUTTON_TEXT_COLOR, CONTROL_PANEL_FONT, is_pressed=is_pause_pressed)

    # Stop Button
    is_stop_pressed = (active_button_name == "stop")
    draw_button(surface, STOP_BUTTON_RECT, "Stop", CONTROL_BUTTON_COLOR, CONTROL_BUTTON_TEXT_COLOR, CONTROL_PANEL_FONT, is_pressed=is_stop_pressed)

    # Mode Toggle Button
    mode_display_text = "Present" if current_mode == "presentation" else "Learn"
    is_mode_pressed = (active_button_name == "mode")
    draw_button(surface, MODE_BUTTON_RECT, mode_display_text, CONTROL_BUTTON_COLOR, CONTROL_BUTTON_TEXT_COLOR, CONTROL_PANEL_FONT, is_pressed=is_mode_pressed)

# Function to draw control panel
def draw_control_panel(surface):
    pygame.draw.rect(surface, CONTROL_PANEL_COLOR, CONTROL_PANEL_RECT)
    pygame.draw.rect(surface, ACCENT_COLOR, CONTROL_PANEL_RECT, 1) # Border for the panel itself
    draw_control_buttons(surface) # Draw buttons on the panel
    draw_sliders(surface)

    # Draw Progress Bar
    draw_progress_bar(surface, current_midi_playback_time, total_midi_duration_ms,
                        PROGRESS_BAR_RECT, PROGRESS_BAR_COLOR, PROGRESS_BAR_BACKGROUND_COLOR)

# Function to trigger a shockwave
def trigger_shockwave(center_x, center_y):
    global active_shockwaves
    if len(active_shockwaves) < 20: # Limit concurrent shockwaves
        active_shockwaves.append({
            'center_x': float(center_x),
            'center_y': float(center_y),
            'current_radius': 0.0,
            'current_opacity': float(SHOCKWAVE_INITIAL_OPACITY)
        })

# Function to update and draw shockwaves
def update_and_draw_shockwaves(surface):
    global active_shockwaves
    new_shockwaves = []

    for wave in active_shockwaves:
        wave['current_radius'] += SHOCKWAVE_EXPANSION_SPEED
        wave['current_opacity'] -= SHOCKWAVE_FADE_RATE

        if wave['current_opacity'] > 0 and wave['current_radius'] < SHOCKWAVE_MAX_RADIUS:
            new_shockwaves.append(wave)

            brightness_ratio = wave['current_opacity'] / SHOCKWAVE_INITIAL_OPACITY
            if brightness_ratio <= 0: continue

            current_base_ring_color = (
                int(SHOCKWAVE_COLOR[0] * brightness_ratio),
                int(SHOCKWAVE_COLOR[1] * brightness_ratio),
                int(SHOCKWAVE_COLOR[2] * brightness_ratio)
            )

            for i in range(SHOCKWAVE_NUM_RINGS):
                radius = wave['current_radius'] - (i * SHOCKWAVE_RING_SPACING)
                ring_thickness = 2 # Can be a constant
                if radius > ring_thickness : # Ensure radius is large enough for a visible ring
                     pygame.draw.circle(surface, current_base_ring_color,
                                       (int(wave['center_x']), int(wave['center_y'])),
                                       int(radius), ring_thickness)

    active_shockwaves = new_shockwaves

# Generic function to draw a progress bar
def draw_progress_bar(surface, current_time_ms, total_time_ms, bar_rect, filled_color, background_color):
    pygame.draw.rect(surface, background_color, bar_rect, border_radius=3)
    if total_time_ms > 0 and current_time_ms > 0:
        progress_ratio = min(current_time_ms / total_time_ms, 1.0)
        filled_width = int(bar_rect.width * progress_ratio)
        if filled_width > 0:
            filled_rect = pygame.Rect(bar_rect.left, bar_rect.top, filled_width, bar_rect.height)
            pygame.draw.rect(surface, filled_color, filled_rect, border_radius=3)
    pygame.draw.rect(surface, ACCENT_COLOR, bar_rect, 1, border_radius=3) # Border

# Generic function to draw a slider
def draw_slider(surface, track_rect, label, current_value, min_value, max_value,
                track_color, handle_color, font, text_color, is_dragging=False):
    # Draw the label
    if label == "Tempo":
         label_text = f"{label}: {int(current_value)} BPM"
    elif label == "Volume":
         label_text = f"{label}: {int(current_value*100)}%"
    else: # Default formatting if needed for other sliders
         label_text = f"{label}: {current_value:.0f}"

    text_surf = font.render(label_text, True, text_color)
    label_rect = text_surf.get_rect(centerx=track_rect.centerx, bottom=track_rect.top - 5)
    surface.blit(text_surf, label_rect)

    # Draw the slider track
    pygame.draw.rect(surface, track_color, track_rect, border_radius=3)

    # Calculate handle position
    value_ratio = (current_value - min_value) / (max_value - min_value) if (max_value - min_value) != 0 else 0
    handle_x = track_rect.left + int(value_ratio * track_rect.width)
    # Clamp handle_x to be within the track bounds visually for the circle's center
    handle_x = max(track_rect.left, min(track_rect.right, handle_x))
    handle_y = track_rect.centery

    current_handle_color = ACCENT_COLOR if is_dragging else handle_color
    pygame.draw.circle(surface, current_handle_color, (handle_x, handle_y), _SLIDER_HANDLE_RADIUS) # Use defined global _SLIDER_HANDLE_RADIUS

# Function to draw all sliders
def draw_sliders(surface):
    # Min/max values for tempo and volume (can be global constants later)
    MIN_TEMPO_BPM = 30
    MAX_TEMPO_BPM = 240
    MIN_VOLUME = 0.0
    MAX_VOLUME = 1.0

    is_tempo_dragging = (dragging_slider_name == "tempo")
    draw_slider(surface, TEMPO_SLIDER_TRACK_RECT, "Tempo", tempo_bpm, MIN_TEMPO_BPM, MAX_TEMPO_BPM,
                SLIDER_TRACK_COLOR, SLIDER_HANDLE_COLOR, CONTROL_PANEL_FONT, ACCENT_COLOR,
                is_dragging=is_tempo_dragging)

    is_volume_dragging = (dragging_slider_name == "volume")
    draw_slider(surface, VOLUME_SLIDER_TRACK_RECT, "Volume", global_volume, MIN_VOLUME, MAX_VOLUME,
                SLIDER_TRACK_COLOR, SLIDER_HANDLE_COLOR, CONTROL_PANEL_FONT, ACCENT_COLOR,
                is_dragging=is_volume_dragging)

# Function to initialize stars
def init_stars(num_stars, screen_width, screen_height):
    global stars
    stars = []
    for _ in range(num_stars):
        x = random.randint(0, screen_width)
        y = random.randint(0, screen_height)
        base_brightness = random.randint(STAR_MIN_BRIGHTNESS + 20, STAR_MAX_BRIGHTNESS) # Star's peak brightness
        time_offset = random.uniform(0, 2 * math.pi) # Random phase for sine wave
        radius = random.uniform(0.5, 1.5)
        # Individual speed multiplier for each star's twinkle
        twinkle_speed_multiplier = random.uniform(0.5, 1.5)
        stars.append({
            'x': x, 'y': y,
            'base_brightness': base_brightness,
            'time_offset': time_offset,
            'radius': radius,
            'speed_multiplier': twinkle_speed_multiplier
        })

# Function to draw stars
def draw_stars(surface):
    current_time_ms = pygame.time.get_ticks()
    for star in stars:
        # Sine wave for twinkle: (sin(time * speed_factor + phase_offset) + 1) / 2 results in 0-1 range
        oscillation_factor = (math.sin(current_time_ms * STAR_TWINKLE_SPEED * star['speed_multiplier'] + star['time_offset']) + 1) / 2

        # Modulate brightness: STAR_MIN_BRIGHTNESS is the dimmest, star['base_brightness'] is the brightest
        dynamic_brightness = STAR_MIN_BRIGHTNESS + (star['base_brightness'] - STAR_MIN_BRIGHTNESS) * oscillation_factor
        final_brightness_component = int(max(0, min(255, dynamic_brightness))) # Clamp to 0-255

        # Modulate STAR_COLOR by the brightness component (relative to 255)
        r = int(STAR_COLOR[0] * (final_brightness_component / 255.0))
        g = int(STAR_COLOR[1] * (final_brightness_component / 255.0))
        b = int(STAR_COLOR[2] * (final_brightness_component / 255.0))
        final_star_color = (max(0,min(r,255)), max(0,min(g,255)), max(0,min(b,255))) # Ensure valid color components

        pygame.draw.circle(surface, final_star_color, (star['x'], star['y']), star['radius'])

# Function to initialize the global all_piano_key_rects list
def initialize_key_rects():
    global all_piano_key_rects

    # White keys: piano indices 0, 2, 4, 5, 7, 9, 11 for 1st octave, then +12 for 2nd, etc.
    # There are NUM_WHITE_KEYS in total (e.g., 14 for 2 octaves)
    white_key_piano_indices = []
    for o in range(OCTAVES):
        octave_base = o * 12
        white_key_piano_indices.extend([
            octave_base + 0, octave_base + 2, octave_base + 4,
            octave_base + 5, octave_base + 7, octave_base + 9, octave_base + 11
        ])

    for i, piano_idx in enumerate(white_key_piano_indices):
        # 'i' here is the visual index of the white key (0 to NUM_WHITE_KEYS-1)
        x_pos = i * WHITE_KEY_WIDTH
        if piano_idx < len(all_piano_key_rects):
             all_piano_key_rects[piano_idx] = pygame.Rect(x_pos, KEYBOARD_Y_POSITION, WHITE_KEY_WIDTH, WHITE_KEY_HEIGHT)

    # Black keys: piano indices 1, 3, 6, 8, 10 for 1st octave, then +12 for 2nd, etc.
    black_key_piano_indices = []
    # Visual indices of white keys that black keys are associated with (0-indexed)
    # C(0), D(1), E(2), F(3), G(4), A(5), B(6) for one octave
    # Black keys are after C, D, F, G, A (visual white key indices 0,1, 3,4,5)
    assoc_white_visual_indices = []
    for o in range(OCTAVES):
        octave_base_piano_idx = o * 12
        octave_base_white_visual_idx = o * 7
        black_key_piano_indices.extend([
            octave_base_piano_idx + 1, octave_base_piano_idx + 3,
            octave_base_piano_idx + 6, octave_base_piano_idx + 8, octave_base_piano_idx + 10
        ])
        assoc_white_visual_indices.extend([
            octave_base_white_visual_idx + 0, octave_base_white_visual_idx + 1,
            octave_base_white_visual_idx + 3, octave_base_white_visual_idx + 4, octave_base_white_visual_idx + 5
        ])

    for i, bk_piano_idx in enumerate(black_key_piano_indices):
        # 'i' is the index in black_key_piano_indices (0 to NUM_BLACK_KEYS-1)
        # 'bk_piano_idx' is the global piano key index (1, 3, 6, ...)
        # 'assoc_wv_idx' is the visual index of the white key that this black key is to the right of.
        assoc_wv_idx = assoc_white_visual_indices[i]

        x_pos = (assoc_wv_idx + 1) * WHITE_KEY_WIDTH - (BLACK_KEY_WIDTH / 2)
        if bk_piano_idx < len(all_piano_key_rects):
            all_piano_key_rects[bk_piano_idx] = pygame.Rect(x_pos, KEYBOARD_Y_POSITION, BLACK_KEY_WIDTH, BLACK_KEY_HEIGHT)

# Function to parse MIDI file
def parse_midi_file(filepath):
    global parsed_midi_sequence, midi_playing, current_midi_playback_time, active_pressed_keys
    global midi_sequence_current_event_index, playback_start_system_time
    global total_midi_duration_ms # Ensure total_midi_duration_ms can be modified
    try:
        mid = mido.MidiFile(filepath)
        parsed_midi_sequence = []
        absolute_time_ms = 0
        # MIDI note for C4 (middle C) is 60.
        # Our piano key 0 (C1 visual on a 2-octave C4-B5 mapping) maps to MIDI 60.
        # Our piano key 23 (B2 visual) maps to MIDI 83.
        MIDI_NOTE_OFFSET = 60 # MIDI note 60 (C4) will map to our piano key index 0

        for msg in mid: # Iterating MidiFile directly yields messages chronologically from all tracks
            absolute_time_ms += int(msg.time * 1000) # Convert delta time in seconds to absolute milliseconds

            if not msg.is_meta: # Filter out meta messages
                if msg.type == 'note_on' and msg.velocity > 0:
                    piano_key_index = msg.note - MIDI_NOTE_OFFSET
                    if 0 <= piano_key_index < (OCTAVES * 12): # Check if the note is within our N-octave range
                        parsed_midi_sequence.append({'time_ms': absolute_time_ms, 'type': 'note_on', 'key': piano_key_index, 'velocity': msg.velocity})
                elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                    piano_key_index = msg.note - MIDI_NOTE_OFFSET
                    if 0 <= piano_key_index < (OCTAVES * 12):
                        parsed_midi_sequence.append({'time_ms': absolute_time_ms, 'type': 'note_off', 'key': piano_key_index})

        # Sort by time, mido iteration should be chronological, but good practice.
        parsed_midi_sequence.sort(key=lambda x: x['time_ms'])

        if parsed_midi_sequence:
            # Sort by time to ensure the last event is truly the last chronologically
            parsed_midi_sequence.sort(key=lambda x: x['time_ms'])
            total_midi_duration_ms = parsed_midi_sequence[-1]['time_ms'] if parsed_midi_sequence else 0

            print(f"DEBUG: Parsed {len(parsed_midi_sequence)} MIDI events. Total duration: {total_midi_duration_ms} ms.")
            midi_playing = True
            current_midi_playback_time = 0.0
            midi_sequence_current_event_index = 0
            playback_start_system_time = pygame.time.get_ticks()
            active_pressed_keys.clear()
        else:
            print(f"DEBUG: No playable notes found in MIDI file or notes are outside the {OCTAVES*12}-key range (MIDI {MIDI_NOTE_OFFSET}-{MIDI_NOTE_OFFSET + OCTAVES*12 -1}). Total duration set to 0.")
            total_midi_duration_ms = 0 # Reset if no notes
            midi_playing = False
            parsed_midi_sequence = []
            midi_sequence_current_event_index = 0
            current_midi_playback_time = 0.0
        return True
    except Exception as e:
        print(f"Error parsing MIDI file {filepath}: {e}")
        parsed_midi_sequence = []
        total_midi_duration_ms = 0 # Reset on error
        midi_playing = False
        midi_sequence_current_event_index = 0
        current_midi_playback_time = 0.0
        return False

# Function to draw import button
def draw_import_button(surface):
    pygame.draw.rect(surface, BUTTON_COLOR, BUTTON_RECT)
    text_surf = BUTTON_FONT.render(BUTTON_TEXT, True, BUTTON_TEXT_COLOR)
    text_rect = text_surf.get_rect(center=BUTTON_RECT.center)
    surface.blit(text_surf, text_rect)

# Screen dimensions (SCREEN_WIDTH already defined, SCREEN_HEIGHT needed)
SCREEN_HEIGHT = 800

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

# Initialize Stars & Key Rects (after screen and layout constants are set)
init_stars(NUM_STARS, SCREEN_WIDTH, SCREEN_HEIGHT)
initialize_key_rects() # Call to pre-calculate key rects


# Set window title
pygame.display.set_caption("Piano App")

# Main game loop
running = True
while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: # Left mouse button
                # Existing Import MIDI button click check
                if BUTTON_RECT.collidepoint(event.pos):
                    print("DEBUG: Import MIDI button clicked")
                    # active_button_name = "import_midi" # Optional: for visual feedback
                    # Setup tkinter root window (it won't be shown)
                    root = tk.Tk()
                    root.withdraw() # Hide the main tkinter window
                    # Open file dialog
                    midi_file_path = filedialog.askopenfilename(
                        title="Select a MIDI file",
                        filetypes=(("MIDI files", "*.mid *.midi"), ("All files", "*.*"))
                    )
                    if midi_file_path:
                        print(f"DEBUG: Selected MIDI file: {midi_file_path}")
                        parse_midi_file(midi_file_path)
                    root.destroy()

                # New Control Panel Button Clicks
                elif START_BUTTON_RECT.collidepoint(event.pos):
                    active_button_name = "start"
                elif PAUSE_BUTTON_RECT.collidepoint(event.pos):
                    active_button_name = "pause"
                elif STOP_BUTTON_RECT.collidepoint(event.pos):
                    active_button_name = "stop"
                elif MODE_BUTTON_RECT.collidepoint(event.pos):
                    active_button_name = "mode"

                # Slider Click Detection
                # Define interactive rects for sliders (taller for easier clicking)
                tempo_slider_interactive_rect = TEMPO_SLIDER_TRACK_RECT.inflate(0, 20)
                volume_slider_interactive_rect = VOLUME_SLIDER_TRACK_RECT.inflate(0, 20)

                if not active_button_name: # Only check sliders if no button was already targeted by this click
                    if tempo_slider_interactive_rect.collidepoint(event.pos):
                        dragging_slider_name = "tempo"
                        value_ratio = (event.pos[0] - TEMPO_SLIDER_TRACK_RECT.left) / TEMPO_SLIDER_TRACK_RECT.width
                        tempo_bpm = MIN_TEMPO_BPM + value_ratio * (MAX_TEMPO_BPM - MIN_TEMPO_BPM)
                        tempo_bpm = int(max(MIN_TEMPO_BPM, min(MAX_TEMPO_BPM, tempo_bpm))) # Clamp and int
                        print(f"DEBUG: Tempo changed to {tempo_bpm} BPM")

                    elif volume_slider_interactive_rect.collidepoint(event.pos):
                        dragging_slider_name = "volume"
                        value_ratio = (event.pos[0] - VOLUME_SLIDER_TRACK_RECT.left) / VOLUME_SLIDER_TRACK_RECT.width
                        global_volume = MIN_VOLUME + value_ratio * (MAX_VOLUME - MIN_VOLUME)
                        global_volume = max(MIN_VOLUME, min(MAX_VOLUME, global_volume)) # Clamp
                        print(f"DEBUG: Volume changed to {global_volume:.2f}")

        elif event.type == pygame.MOUSEMOTION:
            if dragging_slider_name == "tempo":
                value_ratio = (event.pos[0] - TEMPO_SLIDER_TRACK_RECT.left) / TEMPO_SLIDER_TRACK_RECT.width
                tempo_bpm = MIN_TEMPO_BPM + value_ratio * (MAX_TEMPO_BPM - MIN_TEMPO_BPM)
                tempo_bpm = int(max(MIN_TEMPO_BPM, min(MAX_TEMPO_BPM, tempo_bpm))) # Clamp and int
                # print(f"DEBUG: Tempo changed to {tempo_bpm} BPM") # Optional: reduce log spam

            elif dragging_slider_name == "volume":
                value_ratio = (event.pos[0] - VOLUME_SLIDER_TRACK_RECT.left) / VOLUME_SLIDER_TRACK_RECT.width
                global_volume = MIN_VOLUME + value_ratio * (MAX_VOLUME - MIN_VOLUME)
                global_volume = max(MIN_VOLUME, min(MAX_VOLUME, global_volume)) # Clamp
                # print(f"DEBUG: Volume changed to {global_volume:.2f}") # Optional: reduce log spam

        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: # Left mouse button
                # Button release logic
                if active_button_name == "start" and START_BUTTON_RECT.collidepoint(event.pos):
                    print("DEBUG: Start button released")
                    if parsed_midi_sequence:
                        if playback_status == "stopped":
                            current_midi_playback_time = 0.0
                            midi_sequence_current_event_index = 0
                            playback_start_system_time = pygame.time.get_ticks() # Start fresh from 0
                            active_pressed_keys.clear()
                        elif playback_status == "paused":
                            # Adjust start time to seamlessly resume from current_midi_playback_time
                            playback_start_system_time = pygame.time.get_ticks() - int(current_midi_playback_time)

                        playback_status = "playing"
                        midi_playing = True # This flag enables the MIDI processing block
                    else:
                        print("DEBUG: No MIDI loaded, Start does nothing.")
                        playback_status = "stopped"
                        midi_playing = False

                elif active_button_name == "pause" and PAUSE_BUTTON_RECT.collidepoint(event.pos):
                    print("DEBUG: Pause button released")
                    if playback_status == "playing":
                        playback_status = "paused"
                        # midi_playing remains true, but the playback loop conditional on "playing" status will halt it.
                        # current_midi_playback_time will hold the time at which it was paused.


                elif active_button_name == "stop" and STOP_BUTTON_RECT.collidepoint(event.pos):
                    print("DEBUG: Stop button released")
                    playback_status = "stopped"
                    midi_playing = False
                    active_pressed_keys.clear()
                    current_midi_playback_time = 0.0 # Reset playback head
                    midi_sequence_current_event_index = 0
                    # playback_start_system_time is not critical to reset here, Start will handle it.

                elif active_button_name == "mode" and MODE_BUTTON_RECT.collidepoint(event.pos):
                    if current_mode == "presentation":
                        current_mode = "learning"
                    else:
                        current_mode = "presentation"
                    print(f"DEBUG: Mode changed to {current_mode}")

                # Reset active_button_name after all specific button checks
                if active_button_name is not None: # Check if a button was indeed active
                    active_button_name = None

                # Reset dragging_slider_name if a slider was being dragged
                if dragging_slider_name is not None:
                    # Final print on release:
                    if dragging_slider_name == "tempo": print(f"DEBUG: Tempo set to {tempo_bpm} BPM")
                    elif dragging_slider_name == "volume": print(f"DEBUG: Volume set to {global_volume:.2f}")
                    dragging_slider_name = None

        elif event.type == pygame.DROPFILE: # Event type for a dropped file
            dropped_file_path = event.file
            print(f"DEBUG: File dropped: {dropped_file_path}")
            if dropped_file_path and (dropped_file_path.lower().endswith(".mid") or dropped_file_path.lower().endswith(".midi")):
                # Call the existing MIDI parsing function
                parse_midi_file(dropped_file_path)
            else:
                print(f"DEBUG: Dropped file '{dropped_file_path}' is not a .mid or .midi file. Ignoring.")

        # Add new event handlers here:
        if event.type == pygame.KEYDOWN:
            if event.key in KEY_MAP:
                piano_key_index = KEY_MAP[event.key]
                active_pressed_keys.add(piano_key_index)

                # Play sound for manual key press
                if piano_key_index < len(key_sounds) and key_sounds[piano_key_index]:
                    key_sounds[piano_key_index].set_volume(global_volume)
                    key_sounds[piano_key_index].play()
                else:
                    print(f"Warning: Sound not available for key index {piano_key_index}")

                # Trigger shockwave in learning mode
                if current_mode == "learning":
                    if 0 <= piano_key_index < len(all_piano_key_rects) and all_piano_key_rects[piano_key_index] is not None:
                        key_rect = all_piano_key_rects[piano_key_index]
                        center_x, center_y = key_rect.centerx, key_rect.centery
                        trigger_shockwave(center_x, center_y)
                    else:
                        print(f"Warning: Rect not found for piano key index {piano_key_index} for shockwave.")

        elif event.type == pygame.KEYUP:
            if event.key in KEY_MAP:
                piano_key_index = KEY_MAP[event.key]
                active_pressed_keys.discard(piano_key_index) # Use discard to avoid error if not found

    # MIDI Playback Logic
    if midi_playing and parsed_midi_sequence:
        # Calculate elapsed time since playback started
        current_system_time = pygame.time.get_ticks()
        current_midi_playback_time = float(current_system_time - playback_start_system_time)

        # Process MIDI events up to the current playback time
        while (midi_sequence_current_event_index < len(parsed_midi_sequence) and
               parsed_midi_sequence[midi_sequence_current_event_index]['time_ms'] <= current_midi_playback_time):

            event = parsed_midi_sequence[midi_sequence_current_event_index]
            piano_key_idx = event['key']

            if event['type'] == 'note_on':
                active_pressed_keys.add(piano_key_idx)
                if 0 <= piano_key_idx < len(key_sounds) and key_sounds[piano_key_idx]:
                    key_sounds[piano_key_idx].play()
            elif event['type'] == 'note_off':
                active_pressed_keys.discard(piano_key_idx)

            midi_sequence_current_event_index += 1

        # If all events have been processed, stop playback
        if midi_sequence_current_event_index >= len(parsed_midi_sequence):
            midi_playing = False
            active_pressed_keys.clear() # Clear any lingering notes
            print("DEBUG: MIDI playback finished.")

    # Drawing
    screen.fill(BACKGROUND_COLOR)  # Fill the screen with background color
    draw_stars(screen) # Draw stars on top of the background
    draw_import_button(screen)                          # Draw the import button
    draw_white_keys(screen, active_pressed_keys)        # Draw the white keys
    draw_black_keys(screen, active_pressed_keys)        # Draw the black keys
    update_and_draw_shockwaves(screen)                  # Draw shockwaves on top of keys
    draw_control_panel(screen)                          # Draw the control panel

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
