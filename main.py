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
midi_playing = False
midi_sequence_current_event_index = 0
playback_start_system_time = 0

# Starfield parameters
NUM_STARS = 100
STAR_COLOR = (200, 200, 200) # Pale white/gray for stars
STAR_MAX_BRIGHTNESS = 150 # Max base brightness for a star
STAR_MIN_BRIGHTNESS = 20  # Min brightness in twinkle cycle
STAR_TWINKLE_SPEED = 0.001 # General speed multiplier for twinkle, individual stars vary

stars = []

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

# Function to draw control panel
def draw_control_panel(surface):
    pygame.draw.rect(surface, CONTROL_PANEL_COLOR, CONTROL_PANEL_RECT)
    # Optional: Add a border with ACCENT_COLOR
    pygame.draw.rect(surface, ACCENT_COLOR, CONTROL_PANEL_RECT, 1) # Border width 1

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

# Function to parse MIDI file
def parse_midi_file(filepath):
    global parsed_midi_sequence, midi_playing, current_midi_playback_time, active_pressed_keys
    global midi_sequence_current_event_index, playback_start_system_time # Add new globals
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
            print(f"DEBUG: Parsed {len(parsed_midi_sequence)} MIDI events from {filepath}.")
            midi_playing = True
            current_midi_playback_time = 0.0
            midi_sequence_current_event_index = 0
            playback_start_system_time = pygame.time.get_ticks()
            active_pressed_keys.clear()
        else:
            print(f"DEBUG: No playable notes found in MIDI file or notes are outside the {OCTAVES*12}-key range (MIDI {MIDI_NOTE_OFFSET}-{MIDI_NOTE_OFFSET + OCTAVES*12 -1}).")
            midi_playing = False
            # Ensure other playback vars are reset too if no notes found
            parsed_midi_sequence = [] # Already empty if no notes, but good to be explicit
            midi_sequence_current_event_index = 0
            current_midi_playback_time = 0.0
        return True
    except Exception as e:
        print(f"Error parsing MIDI file {filepath}: {e}")
        parsed_midi_sequence = []
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

# Initialize Stars
# KEYBOARD_Y_POSITION is SCREEN_HEIGHT - KEYBOARD_HEIGHT, not strictly needed for init_stars if stars are everywhere
init_stars(NUM_STARS, SCREEN_WIDTH, SCREEN_HEIGHT)


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
                if BUTTON_RECT.collidepoint(event.pos):
                    print("DEBUG: Import MIDI button clicked")
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
                        parse_midi_file(midi_file_path) # Call the new parsing function
                        # loaded_midi_path = midi_file_path # Storing path if needed elsewhere, parse_midi_file uses it directly
                    root.destroy() # Clean up tkinter root

        elif event.type == pygame.DROPFILE: # Event type for a dropped file
            dropped_file_path = event.file # event.file contains the path
            print(f"DEBUG: File dropped: {dropped_file_path}")
            if dropped_file_path and (dropped_file_path.lower().endswith(".mid") or dropped_file_path.lower().endswith(".midi")):
                # Call the existing MIDI parsing function
                parse_midi_file(dropped_file_path)
            else:
                print(f"DEBUG: Dropped file '{dropped_file_path}' is not a .mid or .midi file. Ignoring.")

        # Add new event handlers here:
        if event.type == pygame.KEYDOWN: # Note: Changed from elif to if, to allow multiple event types per frame
            if event.key in KEY_MAP:
                piano_key_index = KEY_MAP[event.key]
                active_pressed_keys.add(piano_key_index)
                # Play sound
                if piano_key_index < len(key_sounds) and key_sounds[piano_key_index]:
                    key_sounds[piano_key_index].play()
                else:
                    print(f"Warning: Sound not available for key index {piano_key_index}")

        elif event.type == pygame.KEYUP: # Changed from if to elif, assuming keydown and keyup for same key not in same event batch
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
    # Button is drawn before keyboard and panel, so its y-pos (20) is unaffected by keyboard moving up
    draw_import_button(screen)                          # Draw the import button
    draw_white_keys(screen, active_pressed_keys)        # Draw the white keys
    draw_black_keys(screen, active_pressed_keys)        # Draw the black keys
    draw_control_panel(screen)                          # Draw the control panel

    # Update the display
    pygame.display.flip()

# Quit Pygame
pygame.quit()
