import array
import ctypes
import math
import os
import random
import shutil
import sys
import tempfile
import textwrap
import threading
import time
import traceback
import tkinter as tk
import tkinter.font as tkfont
import wave

DESIGN_WIDTH = 1280
DESIGN_HEIGHT = 720
TASKBAR_HEIGHT = 40
TITLE_HEIGHT = 30
FRAME_DELAY_MS = 40
SAMPLE_RATE = 16000

PALETTE = {
    "void": "#0f0f0f",
    "white": "#fcfcfc",
    "silver": "#d9d7da",
    "salmon": "#dd9b98",
    "peach": "#deb596",
    "butter": "#dedb90",
    "mint": "#98dd90",
    "sky": "#93b8de",
    "periwinkle": "#9596de",
    "lavender": "#bd93de",
    "pink": "#de93d4",
    "graphite": "#565250",
    "night": "#2f2b33",
    "plum": "#94577f",
    "clay": "#a56e6b",
    "moss": "#6fa36e",
    "teal": "#009e8a",
    "slate": "#5c7399",
    "cobalt": "#3f5e9e",
    "indigo": "#4d5fab",
    "violet": "#745eb0",
}

WALLPAPER_COLORS = ["teal", "plum", "violet", "cobalt", "clay", "moss", "indigo", "night"]
RAIN_CHARACTERS = "01ABCDEFGHIJKLMNOPQRSTUVWXYZ#$%&*+=<>?"
GARBLE_CHARACTERS = "#@%&?!01/\\|"
MENU_MESSAGES = [
    "SYSTEM: Dad is away. Probably.",
    "WARNING: Contains 0 real viruses and 100% real vibes.",
    "TIP: Never click suspicious links. (Except in this game.)",
    "Loading childhood... 99%",
    "KID_OS has not been approved by Dad.",
    "Billy's hacker rank: NOOB (confident)",
    "No real computers were harmed. Only Dad's feelings.",
    "Nothing in this game touches your real computer. Promise.",
]
BOOT_LINES = [
    "KID_OS BIOS v0.8  (Property of Dad)",
    "Checking memory... 640K ought to be enough for anybody",
    "Detecting snacks... 3 found",
    "Loading childhood... 99%",
    "Loading childhood... 99%",
    "Dad is away: [PROBABLY]",
    "Hacker mode: [NOT INSTALLED] [YET]",
    "Boot complete.",
]
TOAST_POOL_MILD = [
    "WARNING: Desktop is feeling emotional.",
    "Your mouse has been promoted to Manager.",
    "Wallpaper.exe has stopped working (it never started).",
    "Update available: an update for the update.",
    "Battery: 100%. This is a desktop. Concerning.",
    "The Recycle Bin is full of recycling.",
]
TOAST_POOL_WILD = [
    "Error 404: Dad's trust not found.",
    "Your computer is now 14% haunted.",
    "Somewhere, a developer just woke up screaming.",
    "The cloud has requested a day off.",
    "Clippy-adjacent entity detected. Do not make eye contact.",
    "WARNING: 3 icons have unionized.",
    "System32 is sending you a friend request.",
]
AD_TEXTS = [
    ("HOT SINGLE ROUTERS IN YOUR AREA", "They are lonely. They are also not real."),
    ("YOUR PC HAS 9,999 VIRUSES", "We know because we made them. Click to fix!"),
    ("YOU ARE THE 1,000,000th VISITOR", "Prize: a free prize. Terms: yes."),
    ("DOWNLOAD MORE RAM", "Now with 400% more RAM. RAM not included."),
    ("CLICK HERE TO CLOSE THIS AD", "(This is not the close button.)"),
]
BILLY_BUTTONS = ["NEXT >", "NEXT >", "NEXT >", "NEXT >", "bro...", "literally", "fr fr", "W"]

ENDINGS = {
    "blue_screen": {
        "number": 1,
        "title": "THE BLUE SCREEN ENDING",
        "lines": [
            ":(",
            "Your PC ran into a problem and needs to restart. We're just collecting some error info, and then we'll restart for you.",
            "STOP CODE: BILLY_FIXED_IT",
            "DAD: Billy... why is the screen blue?",
            "BILLY: I fixed it. It's a beautiful shade of blue now. You're welcome.",
            "DAD: ...",
            "Billy now believes he has a future in IT. Dad believes in buying a new computer.",
        ],
    },
    "hacker": {
        "number": 2,
        "title": "THE PROFESSIONAL HACKER ENDING",
        "lines": [
            "Dad stares at the screen. It is green. It is on fire. It is stuck at 99%.",
            "DAD: Billy. What. Did. You. Do.",
            "BILLY: Dad, I was conducting international cybersecurity research.",
            "DAD: On my work computer.",
            "BILLY: Pen testing, Dad. Look it up.",
            "Dad looks it up. It does not say what Billy thinks it says.",
            "Billy is now Chief Click Officer of a company that does not exist yet.",
        ],
    },
    "billionaire": {
        "number": 3,
        "title": "THE ROBUX BILLIONAIRE ENDING",
        "lines": [
            "Billy has won exactly 0 Robux.",
            "Dad's phone starts buzzing. And buzzing. And does not stop.",
            "NEWS ANCHOR: ...a local eight-year-old appears to have broken the internet. Experts say it started with PHP.",
            "Billy now has 4.2 million followers, a sponsorship from PHP Energy, and a lawyer named Gary.",
            "DAD: Billy... are we famous?",
            "BILLY: Skill issue.",
            "Robux balance: 0. Vibes: immaculate.",
        ],
    },
    "cat": {
        "number": 4,
        "title": "SECRET ENDING: THE CAT DID IT",
        "lines": [
            "DAD: The cat?",
            "BILLY: Mr. Whiskers. He walks on the keyboard. It's literally always him.",
            "Dad opens cat_photos_(2300).zip. Photo 1,337: Mr. Whiskers, typing, with a look of pure malice.",
            "The evidence is overwhelming. Mr. Whiskers is sentenced to one (1) bath.",
            "Billy walks free. The cat looks directly at you. This was the plan all along.",
            "Mr. Whiskers has a lawyer. The lawyer is also a cat.",
        ],
    },
    "grounded": {
        "number": 5,
        "title": "THE GROUNDED ENDING",
        "lines": [
            "DAD: Billy. Come here. Sit.",
            "Dad lists the damage. It takes 40 minutes. There are charts.",
            "Billy is grounded until the year 2031. No devices. No snacks. Vegetables with the lights on.",
            "BILLY: It's so over.",
            "Dad bought a new computer. Billy learned a valuable lesson. He has already forgotten it.",
        ],
    },
}
TOTAL_ENDINGS = len(ENDINGS)


def midi_to_frequency(note):
    return 440.0 * 2 ** ((note - 69) / 12.0)


def wave_value(shape, phase):
    cycle = phase % 1.0
    if shape == "square":
        return 1.0 if cycle < 0.5 else -1.0
    if shape == "pulse":
        return 1.0 if cycle < 0.25 else -1.0
    if shape == "triangle":
        return 4.0 * abs(cycle - 0.5) - 1.0
    if shape == "saw":
        return 2.0 * cycle - 1.0
    return math.sin(2.0 * math.pi * cycle)


def new_buffer(seconds):
    return [0.0] * int(seconds * SAMPLE_RATE)


def mix_note(buffer, start_seconds, frequency, duration, shape, volume, attack=0.01, release=0.05, vibrato=0.0, slide=0.0):
    start_index = int(start_seconds * SAMPLE_RATE)
    total = int(duration * SAMPLE_RATE)
    phase = 0.0
    limit = len(buffer)
    for offset in range(total):
        index = start_index + offset
        if index >= limit:
            break
        elapsed = offset / SAMPLE_RATE
        current = frequency * (1.0 + slide * elapsed)
        if vibrato:
            current *= 1.0 + 0.02 * math.sin(2.0 * math.pi * vibrato * elapsed)
        phase += max(20.0, current) / SAMPLE_RATE
        envelope = 1.0
        if elapsed < attack:
            envelope = elapsed / attack
        remaining = duration - elapsed
        if remaining < release:
            envelope *= remaining / release
        buffer[index] += wave_value(shape, phase) * volume * envelope


def mix_noise(buffer, start_seconds, duration, volume, decay=4.0, crush=1):
    start_index = int(start_seconds * SAMPLE_RATE)
    total = max(1, int(duration * SAMPLE_RATE))
    held = 0.0
    limit = len(buffer)
    for offset in range(total):
        index = start_index + offset
        if index >= limit:
            break
        if offset % crush == 0:
            held = random.uniform(-1.0, 1.0)
        buffer[index] += held * volume * math.exp(-decay * offset / total)


def save_wave(path, buffer, gain=1.0):
    samples = array.array("h")
    for value in buffer:
        clipped = max(-1.0, min(1.0, value * gain))
        samples.append(int(clipped * 30000))
    if sys.byteorder == "big":
        samples.byteswap()
    with wave.open(path, "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(SAMPLE_RATE)
        handle.writeframes(samples.tobytes())


CHORD_PROGRESSION = [
    (45, [57, 60, 64, 69]),
    (41, [53, 57, 60, 65]),
    (48, [60, 64, 67, 72]),
    (43, [55, 59, 62, 67]),
    (45, [57, 60, 64, 69]),
    (41, [53, 57, 60, 65]),
    (38, [50, 53, 57, 62]),
    (40, [52, 56, 59, 64]),
]


def build_music_track(mode):
    beats_per_minute = {"calm": 84, "tense": 122, "chaos": 158}[mode]
    beat = 60.0 / beats_per_minute
    bar = beat * 4
    buffer = new_buffer(bar * len(CHORD_PROGRESSION))
    for bar_index, (bass, arpeggio) in enumerate(CHORD_PROGRESSION):
        start = bar_index * bar
        if mode == "calm":
            mix_note(buffer, start, midi_to_frequency(bass + 12), bar * 0.98, "triangle", 0.14, attack=0.3, release=0.5)
            mix_note(buffer, start, midi_to_frequency(arpeggio[2] - 12), bar * 0.98, "sine", 0.1, attack=0.4, release=0.5)
            pattern = [0, 1, 2, 3, 2, 1, 2, 3]
            for step, tone_index in enumerate(pattern):
                if random.random() < 0.8:
                    mix_note(buffer, start + step * beat / 2, midi_to_frequency(arpeggio[tone_index]), beat * 0.45, "sine", 0.09, attack=0.01, release=0.2)
            if bar_index % 2 == 1:
                mix_note(buffer, start + beat * 3.5, midi_to_frequency(arpeggio[3] + 12), 0.08, "square", 0.04)
        elif mode == "tense":
            for step in range(8):
                mix_note(buffer, start + step * beat / 2, midi_to_frequency(bass), beat * 0.4, "square", 0.08, release=0.1)
                mix_note(buffer, start + step * beat / 2, midi_to_frequency(arpeggio[step % 4] + 12), beat * 0.3, "pulse", 0.07, release=0.1)
                mix_noise(buffer, start + step * beat / 2 + beat / 4, 0.03, 0.05, decay=5.0)
            for step in range(4):
                mix_note(buffer, start + step * beat, 120.0, 0.12, "sine", 0.22, slide=-5.0, release=0.05)
        else:
            for step in range(16):
                note = random.choice(arpeggio) + random.choice([-12, 0, 12, 1, -1, 7])
                mix_note(buffer, start + step * beat / 4, midi_to_frequency(note), beat * 0.22, "saw", 0.07, vibrato=9.0, release=0.04)
            for step in range(8):
                mix_note(buffer, start + step * beat / 2, midi_to_frequency(bass - 12), beat * 0.4, "square", 0.1, slide=random.uniform(-0.5, 0.5), release=0.05)
            for step in range(4):
                mix_note(buffer, start + step * beat, 130.0, 0.14, "sine", 0.26, slide=-6.0, release=0.05)
            for step in range(8):
                mix_noise(buffer, start + step * beat / 2 + beat / 4, 0.04, 0.1, decay=3.0, crush=random.choice([1, 3, 6]))
    return buffer


def build_effect(name):
    if name == "click":
        buffer = new_buffer(0.07)
        mix_note(buffer, 0.0, 1400, 0.05, "square", 0.35, attack=0.002, release=0.02)
    elif name == "open":
        buffer = new_buffer(0.2)
        mix_note(buffer, 0.0, 660, 0.06, "square", 0.3, release=0.02)
        mix_note(buffer, 0.06, 990, 0.1, "square", 0.3, release=0.04)
    elif name == "close":
        buffer = new_buffer(0.2)
        mix_note(buffer, 0.0, 880, 0.06, "square", 0.3, release=0.02)
        mix_note(buffer, 0.06, 440, 0.1, "square", 0.3, release=0.04)
    elif name == "error":
        buffer = new_buffer(0.45)
        mix_note(buffer, 0.0, 220, 0.14, "square", 0.4, release=0.03)
        mix_note(buffer, 0.16, 165, 0.25, "saw", 0.4, release=0.08)
    elif name == "notify":
        buffer = new_buffer(0.4)
        mix_note(buffer, 0.0, 988, 0.1, "sine", 0.4, release=0.04)
        mix_note(buffer, 0.1, 1319, 0.28, "sine", 0.4, release=0.15)
    elif name == "crash":
        buffer = new_buffer(1.3)
        mix_noise(buffer, 0.0, 1.2, 0.6, decay=3.0, crush=3)
        mix_note(buffer, 0.0, 300, 1.1, "saw", 0.4, release=0.4, slide=-0.9)
    elif name == "glitch":
        buffer = new_buffer(0.4)
        for index in range(5):
            mix_noise(buffer, index * 0.07, 0.05, 0.5, decay=2.0, crush=random.choice([2, 5, 9]))
            mix_note(buffer, index * 0.07, random.uniform(200, 1800), 0.04, "pulse", 0.25, release=0.01)
    elif name == "fanfare":
        buffer = new_buffer(1.6)
        for index, note in enumerate([72, 76, 79, 84]):
            mix_note(buffer, index * 0.12, midi_to_frequency(note), 0.14, "square", 0.25, release=0.04)
        for note in [72, 76, 79, 84]:
            mix_note(buffer, 0.5, midi_to_frequency(note), 1.0, "triangle", 0.18, release=0.5)
    elif name == "sad":
        buffer = new_buffer(2.4)
        mix_note(buffer, 0.0, midi_to_frequency(67), 0.4, "saw", 0.28, release=0.1, vibrato=6.0)
        mix_note(buffer, 0.45, midi_to_frequency(66), 0.4, "saw", 0.28, release=0.1, vibrato=6.0)
        mix_note(buffer, 0.9, midi_to_frequency(65), 0.4, "saw", 0.28, release=0.1, vibrato=6.0)
        mix_note(buffer, 1.35, midi_to_frequency(64), 1.0, "saw", 0.28, release=0.4, vibrato=7.0)
    elif name == "coin":
        buffer = new_buffer(0.4)
        mix_note(buffer, 0.0, 988, 0.07, "square", 0.3, release=0.02)
        mix_note(buffer, 0.07, 1319, 0.28, "square", 0.3, release=0.15)
    elif name == "keys":
        buffer = new_buffer(0.8)
        for index in range(10):
            mix_note(buffer, index * 0.06 + random.uniform(0, 0.03), random.uniform(2000, 3600), 0.08, "sine", 0.25, release=0.06)
    else:
        buffer = new_buffer(0.8)
        mix_note(buffer, 0.0, 880, 0.7, "sine", 0.4, release=0.1)
    return buffer


EFFECT_NAMES = ["click", "open", "close", "error", "notify", "crash", "glitch", "fanfare", "sad", "coin", "keys", "beep"]


def send_mci(command):
    try:
        text_buffer = ctypes.create_unicode_buffer(256)
        error_code = ctypes.windll.winmm.mciSendStringW(command, text_buffer, 255, 0)
        return error_code == 0, text_buffer.value
    except Exception:
        return False, ""


class AudioEngine:
    def __init__(self, script_folder):
        self.available = sys.platform.startswith("win")
        self.muted = False
        self.unlocked = False
        self.folder = None
        self.effect_paths = {}
        self.track_paths = {}
        self.effect_states = {}
        self.current_key = None
        self.wanted_key = "calm"
        self.last_check = 0.0
        self.silent_until = 0.0
        self.user_track = self.find_user_track(script_folder)
        if self.available:
            self.folder = tempfile.mkdtemp(prefix="kid_os_audio_")
            threading.Thread(target=self.generate_all, daemon=True).start()

    def find_user_track(self, script_folder):
        allowed = ["mp3", "wav", "wma", "m4a", "aac", "mp4", "ogg", "flac"]
        try:
            for file_name in sorted(os.listdir(script_folder)):
                base, dot, extension = file_name.rpartition(".")
                if dot and base.lower() == "kid" and extension.lower() in allowed:
                    return os.path.join(script_folder, file_name)
        except Exception:
            return None
        return None

    def generate_all(self):
        try:
            for name in EFFECT_NAMES:
                path = os.path.join(self.folder, name + ".wav")
                save_wave(path, build_effect(name))
                self.effect_paths[name] = path
            for mode in ("calm", "tense", "chaos"):
                path = os.path.join(self.folder, "music_" + mode + ".wav")
                save_wave(path, build_music_track(mode), gain=0.7)
                self.track_paths[mode] = path
        except Exception:
            traceback.print_exc()

    def play_effect(self, name):
        if not self.available or not self.unlocked or self.muted:
            return
        path = self.effect_paths.get(name)
        if path is None:
            return
        alias = "fx_" + name
        if name not in self.effect_states:
            opened, _ = send_mci('open "' + path + '" type waveaudio alias ' + alias)
            self.effect_states[name] = opened
        if self.effect_states[name]:
            send_mci("play " + alias + " from 0")

    def start_music(self, key):
        path = self.user_track if key == "user" else self.track_paths.get(key)
        if path is None:
            return
        self.stop_music()
        lowered = path.lower()
        if lowered.endswith(".mp3"):
            device = " type mpegvideo"
        elif lowered.endswith(".wav"):
            device = " type waveaudio"
        else:
            device = ""
        opened, _ = send_mci('open "' + path + '"' + device + " alias bgm")
        if not opened and device:
            opened, _ = send_mci('open "' + path + '" alias bgm')
        if not opened:
            if key == "user":
                self.user_track = None
            return
        send_mci("setaudio bgm volume to 700")
        send_mci("play bgm from 0")
        self.current_key = key

    def stop_music(self):
        if self.current_key is not None:
            send_mci("stop bgm")
            send_mci("close bgm")
        self.current_key = None

    def want(self, key):
        self.wanted_key = key

    def tick(self):
        if not self.available or not self.unlocked:
            return
        now = time.time()
        if now - self.last_check < 0.5:
            return
        self.last_check = now
        if now < self.silent_until:
            return
        if self.muted:
            if self.current_key is not None:
                self.stop_music()
            return
        key = "user" if self.user_track else self.wanted_key
        if key != self.current_key:
            self.start_music(key)
            return
        ok, state = send_mci("status bgm mode")
        if ok and state == "stopped":
            send_mci("play bgm from 0")

    def silence(self, seconds):
        self.silent_until = time.time() + seconds
        if self.available:
            self.stop_music()

    def toggle_mute(self):
        self.muted = not self.muted
        if self.muted:
            self.stop_music()
        self.last_check = 0.0

    def shutdown(self):
        if self.available:
            send_mci("close all")
            if self.folder:
                shutil.rmtree(self.folder, ignore_errors=True)


class GameWindow:
    def __init__(self, title, elements, width, x, y, closable, modal, kind, icon, on_close):
        self.title = title
        self.elements = elements
        self.width = width
        self.x = x
        self.y = y
        self.height = 100
        self.closable = closable
        self.modal = modal
        self.kind = kind
        self.icon = icon
        self.on_close = on_close


class KidOS:
    def __init__(self, root):
        self.root = root
        root.title("KID_OS: Kid Experience on CLI")
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        start_scale = min(1.0, (screen_width - 60) / DESIGN_WIDTH, (screen_height - 140) / DESIGN_HEIGHT)
        start_width = int(DESIGN_WIDTH * start_scale)
        start_height = int(DESIGN_HEIGHT * start_scale)
        root.geometry(str(start_width) + "x" + str(start_height))
        root.minsize(640, 360)
        root.configure(bg=PALETTE["void"])
        self.canvas = tk.Canvas(root, width=start_width, height=start_height, bg=PALETTE["void"], highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.scale = start_scale
        self.offset_x = 0.0
        self.offset_y = 0.0
        self.shake_x = 0.0
        self.shake_y = 0.0
        self.shake_until = 0.0
        self.pointer = (-1.0, -1.0)
        self.hotspots = []
        self.drag_state = None
        self.tint_cache = {}
        self.matrix_on = False
        self.comic = False
        self.session = 0
        self.screen = "boot"
        self.boot_start = time.time()
        self.menu_start = time.time()
        self.ending = None
        self.card = None
        self.bsod = None
        self.found_endings = set()
        script_folder = os.path.dirname(os.path.abspath(__file__))
        self.audio = AudioEngine(script_folder)
        self.setup_fonts()
        self.setup_rain()
        self.reset_state()
        self.windows = []
        self.toasts = []
        canvas = self.canvas
        canvas.bind("<Configure>", self.on_resize)
        canvas.bind("<Button-1>", self.on_press)
        canvas.bind("<B1-Motion>", self.on_drag)
        canvas.bind("<ButtonRelease-1>", self.on_release)
        canvas.bind("<Motion>", self.on_motion)
        root.bind("<KeyPress-m>", lambda event: self.toggle_mute())
        root.bind("<KeyPress-M>", lambda event: self.toggle_mute())
        root.bind("<F11>", self.toggle_fullscreen)
        root.bind("<Escape>", self.leave_fullscreen)
        root.protocol("WM_DELETE_WINDOW", self.quit_game)
        self.rebuild_scanlines()
        self.frame()

    def setup_fonts(self):
        families = set(tkfont.families())
        self.mono_family = "Courier New"
        for candidate in ("Consolas", "Lucida Console", "Courier New", "Courier"):
            if candidate in families:
                self.mono_family = candidate
                break
        self.comic_family = "Comic Sans MS" if "Comic Sans MS" in families else self.mono_family
        self.font_specs = {
            "small": (11, False),
            "body": (13, False),
            "bold": (13, True),
            "label": (12, False),
            "mid": (20, True),
            "big": (36, True),
            "huge": (88, True),
            "rain": (14, True),
            "icon": (11, True),
        }
        self.fonts = {}
        for key, (pixels, bold) in self.font_specs.items():
            self.fonts[key] = tkfont.Font(family=self.mono_family, size=-pixels, weight="bold" if bold else "normal")
        probe = tkfont.Font(family=self.mono_family, size=-100)
        self.char_ratio = max(0.4, probe.measure("M") / 100.0)
        self.update_fonts()

    def update_fonts(self):
        family = self.comic_family if self.comic else self.mono_family
        for key, (pixels, bold) in self.font_specs.items():
            self.fonts[key].configure(family=family, size=-max(6, int(round(pixels * self.scale))), weight="bold" if bold else "normal")

    def char_width(self, font_key):
        return self.font_specs[font_key][0] * self.char_ratio * (1.08 if self.comic else 1.0)

    def line_height(self, font_key):
        return max(1.0, self.fonts[font_key].metrics("linespace") / max(0.1, self.scale))

    def reset_state(self):
        self.stage = 0
        self.chaos = 0.0
        self.suspicion = 0.0
        self.stability = 100.0
        self.robux_progress = 0.0
        self.fame = 0.0
        self.hacker_points = 0
        self.flags = set()
        self.tweaks_used = set()
        self.problems_used = set()
        self.explored = set()
        self.hinted = False
        self.pulse_ids = set()
        self.wallpaper = "teal"
        self.wallpaper_override = None
        self.matrix_on = False
        self.comic = False
        self.objective = ""
        self.icon_offsets = {}
        self.next_chaos_event = 0.0
        self.game_start = time.time()
        self.generator_log = []
        self.amount_label = "1,000 R$"
        self.dad_arrival = 0.0
        self.card = None
        self.bsod = None
        self.ending = None

    def setup_rain(self):
        self.rain_columns = []
        for index in range(DESIGN_WIDTH // 20):
            self.rain_columns.append({
                "x": index * 20 + 10,
                "head": random.uniform(-720, 0),
                "speed": random.uniform(7, 20),
                "length": random.randint(8, 16),
                "chars": [random.choice(RAIN_CHARACTERS) for _ in range(16)],
            })

    def on_resize(self, event):
        width = max(320, event.width)
        height = max(180, event.height)
        self.scale = min(width / DESIGN_WIDTH, height / DESIGN_HEIGHT)
        self.offset_x = (width - DESIGN_WIDTH * self.scale) / 2.0
        self.offset_y = (height - DESIGN_HEIGHT * self.scale) / 2.0
        self.update_fonts()
        self.rebuild_scanlines()

    def rebuild_scanlines(self):
        self.canvas.delete("scan")
        width = int(self.canvas.winfo_width() or DESIGN_WIDTH)
        height = int(self.canvas.winfo_height() or DESIGN_HEIGHT)
        step = max(3, int(round(3 * self.scale)))
        for y in range(0, height, step):
            self.canvas.create_rectangle(0, y, width, y + 1, fill="#000000", outline="", stipple="gray25", tags="scan")

    def toggle_fullscreen(self, event=None):
        current = bool(self.root.attributes("-fullscreen"))
        self.root.attributes("-fullscreen", not current)

    def leave_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

    def quit_game(self):
        self.audio.shutdown()
        self.root.destroy()

    def toggle_mute(self):
        self.audio.toggle_mute()
        if not self.audio.muted:
            self.play("click")

    def play(self, name):
        self.audio.play_effect(name)

    def later(self, milliseconds, function):
        session = self.session

        def run():
            if session == self.session:
                function()

        self.root.after(int(milliseconds), run)

    def to_design(self, pixel_x, pixel_y):
        return (pixel_x - self.offset_x) / self.scale, (pixel_y - self.offset_y) / self.scale

    def design_x(self, value):
        return self.offset_x + self.shake_x + value * self.scale

    def design_y(self, value):
        return self.offset_y + self.shake_y + value * self.scale

    def tint(self, color):
        hex_color = PALETTE.get(color, color)
        if not self.matrix_on:
            return hex_color
        cached = self.tint_cache.get(hex_color)
        if cached is None:
            red = int(hex_color[1:3], 16)
            green = int(hex_color[3:5], 16)
            blue = int(hex_color[5:7], 16)
            luminance = (0.299 * red + 0.587 * green + 0.114 * blue) / 255.0
            cached = "#%02x%02x%02x" % (int(10 * luminance), int(18 + 225 * luminance), int(24 * luminance))
            self.tint_cache[hex_color] = cached
        return cached

    def draw_rect(self, x0, y0, x1, y1, fill=None, outline=None, width=1, stipple=None):
        options = {"tags": "frame", "fill": self.tint(fill) if fill else "", "outline": self.tint(outline) if outline else ""}
        if outline:
            options["width"] = max(1, int(width * self.scale))
        if stipple:
            options["stipple"] = stipple
        return self.canvas.create_rectangle(self.design_x(x0), self.design_y(y0), self.design_x(x1), self.design_y(y1), **options)

    def draw_oval(self, x0, y0, x1, y1, fill=None, outline=None, width=1):
        options = {"tags": "frame", "fill": self.tint(fill) if fill else "", "outline": self.tint(outline) if outline else ""}
        if outline:
            options["width"] = max(1, int(width * self.scale))
        return self.canvas.create_oval(self.design_x(x0), self.design_y(y0), self.design_x(x1), self.design_y(y1), **options)

    def draw_polygon(self, points, fill=None, outline=None):
        flat = []
        for point_x, point_y in points:
            flat.append(self.design_x(point_x))
            flat.append(self.design_y(point_y))
        return self.canvas.create_polygon(*flat, tags="frame", fill=self.tint(fill) if fill else "", outline=self.tint(outline) if outline else "")

    def draw_line(self, points, color, width=2):
        flat = []
        for point_x, point_y in points:
            flat.append(self.design_x(point_x))
            flat.append(self.design_y(point_y))
        return self.canvas.create_line(*flat, tags="frame", fill=self.tint(color), width=max(1, int(width * self.scale)))

    def draw_text(self, x, y, text, color, font_key="body", anchor="nw", width=None, justify="left"):
        options = {"text": text, "fill": self.tint(color), "font": self.fonts[font_key], "anchor": anchor, "tags": "frame", "justify": justify}
        if width:
            options["width"] = max(10, int(width * self.scale))
        return self.canvas.create_text(self.design_x(x), self.design_y(y), **options)

    def add_hotspot(self, x0, y0, x1, y1, callback, kind="button"):
        self.hotspots.append((x0, y0, x1, y1, callback, kind))

    def is_hover(self, x0, y0, x1, y1):
        return x0 <= self.pointer[0] <= x1 and y0 <= self.pointer[1] <= y1

    def garble(self, text):
        level = self.glitch_level()
        if level < 0.35 or random.random() > level * 0.25:
            return text
        characters = list(text)
        for index in range(len(characters)):
            if characters[index] != " " and random.random() < 0.12:
                characters[index] = random.choice(GARBLE_CHARACTERS)
        return "".join(characters)

    def glitch_level(self):
        if self.screen != "game":
            return 0.0
        return min(1.0, 0.65 * self.chaos / 100.0 + 0.35 * (100.0 - self.stability) / 100.0)

    def adjust(self, chaos=0, suspicion=0, stability=0, robux=0, fame=0, hacker=0):
        self.chaos = max(0.0, min(100.0, self.chaos + chaos))
        self.suspicion = max(0.0, min(100.0, self.suspicion + suspicion))
        self.stability = max(0.0, min(100.0, self.stability + stability))
        self.robux_progress = max(0.0, min(100.0, self.robux_progress + robux))
        self.fame = max(0.0, self.fame + fame)
        self.hacker_points += hacker
        if self.chaos < 30:
            self.audio.want("calm")
        elif self.chaos < 65:
            self.audio.want("tense")
        else:
            self.audio.want("chaos")

    def hacker_rank(self):
        if self.hacker_points <= 0:
            return "NOOB (confident)"
        if self.hacker_points <= 2:
            return "SCRIPT KIDDIE"
        if self.hacker_points <= 4:
            return "ELITE HAXOR"
        return "LEGENDARY (self-declared)"

    def draw_icon(self, kind, x, y, size):
        s = size
        if kind == "folder":
            self.draw_rect(x + 0.05 * s, y + 0.18 * s, x + 0.42 * s, y + 0.36 * s, fill="butter", outline="void")
            self.draw_rect(x + 0.05 * s, y + 0.3 * s, x + 0.95 * s, y + 0.86 * s, fill="butter", outline="void")
            self.draw_rect(x + 0.08 * s, y + 0.45 * s, x + 0.92 * s, y + 0.83 * s, fill="peach")
        elif kind == "exe":
            self.draw_rect(x + 0.1 * s, y + 0.12 * s, x + 0.9 * s, y + 0.88 * s, fill="white", outline="void")
            self.draw_rect(x + 0.1 * s, y + 0.12 * s, x + 0.9 * s, y + 0.32 * s, fill="cobalt", outline="void")
            self.draw_text(x + 0.5 * s, y + 0.62 * s, "EXE", "cobalt", "icon", anchor="center")
        elif kind == "robux":
            self.draw_oval(x + 0.08 * s, y + 0.08 * s, x + 0.92 * s, y + 0.92 * s, fill="butter", outline="void", width=2)
            self.draw_oval(x + 0.2 * s, y + 0.2 * s, x + 0.8 * s, y + 0.8 * s, outline="peach", width=2)
            self.draw_text(x + 0.5 * s, y + 0.5 * s, "R$", "void", "icon", anchor="center")
        elif kind == "text":
            self.draw_polygon([(x + 0.15 * s, y + 0.08 * s), (x + 0.65 * s, y + 0.08 * s), (x + 0.85 * s, y + 0.28 * s), (x + 0.85 * s, y + 0.92 * s), (x + 0.15 * s, y + 0.92 * s)], fill="white", outline="void")
            for row in range(4):
                line_y = y + (0.4 + row * 0.12) * s
                self.draw_line([(x + 0.25 * s, line_y), (x + 0.75 * s, line_y)], "graphite", 1)
        elif kind == "zip":
            self.draw_rect(x + 0.15 * s, y + 0.08 * s, x + 0.85 * s, y + 0.92 * s, fill="silver", outline="void")
            for row in range(6):
                self.draw_rect(x + 0.44 * s, y + (0.1 + row * 0.1) * s, x + 0.56 * s, y + (0.16 + row * 0.1) * s, fill="plum" if row % 2 == 0 else "white")
            self.draw_rect(x + 0.4 * s, y + 0.68 * s, x + 0.6 * s, y + 0.82 * s, fill="plum", outline="void")
        elif kind == "gear":
            self.draw_rect(x + 0.42 * s, y + 0.04 * s, x + 0.58 * s, y + 0.96 * s, fill="teal", outline="void")
            self.draw_rect(x + 0.04 * s, y + 0.42 * s, x + 0.96 * s, y + 0.58 * s, fill="teal", outline="void")
            self.draw_oval(x + 0.18 * s, y + 0.18 * s, x + 0.82 * s, y + 0.82 * s, fill="teal", outline="void", width=2)
            self.draw_oval(x + 0.38 * s, y + 0.38 * s, x + 0.62 * s, y + 0.62 * s, fill="night", outline="void")
        elif kind == "floppy":
            self.draw_rect(x + 0.1 * s, y + 0.1 * s, x + 0.9 * s, y + 0.9 * s, fill="cobalt", outline="void")
            self.draw_rect(x + 0.3 * s, y + 0.1 * s, x + 0.7 * s, y + 0.38 * s, fill="silver", outline="void")
            self.draw_rect(x + 0.2 * s, y + 0.5 * s, x + 0.8 * s, y + 0.9 * s, fill="white", outline="void")
            self.draw_rect(x + 0.32 * s, y + 0.58 * s, x + 0.4 * s, y + 0.72 * s, fill="void")
            self.draw_rect(x + 0.6 * s, y + 0.58 * s, x + 0.68 * s, y + 0.72 * s, fill="void")
            self.draw_line([(x + 0.36 * s, y + 0.8 * s), (x + 0.5 * s, y + 0.84 * s), (x + 0.64 * s, y + 0.8 * s)], "void", 2)
        elif kind == "error":
            self.draw_oval(x + 0.06 * s, y + 0.06 * s, x + 0.94 * s, y + 0.94 * s, fill="plum", outline="void", width=2)
            self.draw_line([(x + 0.3 * s, y + 0.3 * s), (x + 0.7 * s, y + 0.7 * s)], "white", 4)
            self.draw_line([(x + 0.7 * s, y + 0.3 * s), (x + 0.3 * s, y + 0.7 * s)], "white", 4)
        elif kind == "warn":
            self.draw_polygon([(x + 0.5 * s, y + 0.06 * s), (x + 0.96 * s, y + 0.9 * s), (x + 0.04 * s, y + 0.9 * s)], fill="butter", outline="void")
            self.draw_text(x + 0.5 * s, y + 0.66 * s, "!", "void", "mid", anchor="center")
        elif kind == "info":
            self.draw_oval(x + 0.06 * s, y + 0.06 * s, x + 0.94 * s, y + 0.94 * s, fill="sky", outline="void", width=2)
            self.draw_text(x + 0.5 * s, y + 0.5 * s, "i", "void", "mid", anchor="center")
        elif kind == "game":
            self.draw_rect(x + 0.04 * s, y + 0.28 * s, x + 0.96 * s, y + 0.76 * s, fill="lavender", outline="void")
            self.draw_rect(x + 0.18 * s, y + 0.44 * s, x + 0.4 * s, y + 0.52 * s, fill="white")
            self.draw_rect(x + 0.25 * s, y + 0.37 * s, x + 0.33 * s, y + 0.6 * s, fill="white")
            self.draw_oval(x + 0.6 * s, y + 0.4 * s, x + 0.7 * s, y + 0.52 * s, fill="salmon", outline="void")
            self.draw_oval(x + 0.74 * s, y + 0.5 * s, x + 0.84 * s, y + 0.62 * s, fill="mint", outline="void")
        elif kind == "cat":
            self.draw_polygon([(x + 0.15 * s, y + 0.08 * s), (x + 0.15 * s, y + 0.45 * s), (x + 0.42 * s, y + 0.3 * s)], fill="peach", outline="void")
            self.draw_polygon([(x + 0.85 * s, y + 0.08 * s), (x + 0.85 * s, y + 0.45 * s), (x + 0.58 * s, y + 0.3 * s)], fill="peach", outline="void")
            self.draw_rect(x + 0.15 * s, y + 0.3 * s, x + 0.85 * s, y + 0.88 * s, fill="peach", outline="void")
            self.draw_rect(x + 0.28 * s, y + 0.45 * s, x + 0.38 * s, y + 0.58 * s, fill="mint", outline="void")
            self.draw_rect(x + 0.62 * s, y + 0.45 * s, x + 0.72 * s, y + 0.58 * s, fill="mint", outline="void")
            self.draw_rect(x + 0.46 * s, y + 0.62 * s, x + 0.54 * s, y + 0.68 * s, fill="pink")
        elif kind == "ad":
            self.draw_rect(x + 0.05 * s, y + 0.2 * s, x + 0.95 * s, y + 0.8 * s, fill="pink", outline="void")
            self.draw_text(x + 0.5 * s, y + 0.5 * s, "AD!!", "void", "icon", anchor="center")
        else:
            self.draw_rect(x + 0.15 * s, y + 0.1 * s, x + 0.85 * s, y + 0.92 * s, fill="peach", outline="void")
            self.draw_rect(x + 0.15 * s, y + 0.05 * s, x + 0.85 * s, y + 0.3 * s, fill="clay", outline="void")
            if kind == "billy_smug":
                self.draw_rect(x + 0.22 * s, y + 0.42 * s, x + 0.78 * s, y + 0.56 * s, fill="void")
                self.draw_line([(x + 0.32 * s, y + 0.72 * s), (x + 0.5 * s, y + 0.8 * s), (x + 0.7 * s, y + 0.68 * s)], "void", 2)
            elif kind == "billy_panic":
                self.draw_rect(x + 0.28 * s, y + 0.42 * s, x + 0.4 * s, y + 0.58 * s, fill="white", outline="void")
                self.draw_rect(x + 0.6 * s, y + 0.42 * s, x + 0.72 * s, y + 0.58 * s, fill="white", outline="void")
                self.draw_oval(x + 0.42 * s, y + 0.68 * s, x + 0.58 * s, y + 0.86 * s, fill="void")
                self.draw_polygon([(x + 0.86 * s, y + 0.3 * s), (x + 0.94 * s, y + 0.46 * s), (x + 0.78 * s, y + 0.46 * s)], fill="sky")
            else:
                self.draw_rect(x + 0.3 * s, y + 0.44 * s, x + 0.4 * s, y + 0.58 * s, fill="void")
                self.draw_rect(x + 0.6 * s, y + 0.44 * s, x + 0.7 * s, y + 0.58 * s, fill="void")
                self.draw_line([(x + 0.34 * s, y + 0.72 * s), (x + 0.5 * s, y + 0.78 * s), (x + 0.66 * s, y + 0.72 * s)], "void", 2)

    def draw_button(self, x, y, width, height, label, callback, enabled=True, accent=None, font_key="body"):
        hovered = enabled and self.is_hover(x, y, x + width, y + height)
        face = accent or "silver"
        if hovered:
            face = "butter"
        self.draw_rect(x, y, x + width, y + height, fill=face, outline="void")
        self.draw_line([(x + 1, y + height - 2), (x + 1, y + 1), (x + width - 2, y + 1)], "white", 2)
        self.draw_line([(x + 1, y + height - 1), (x + width - 1, y + height - 1), (x + width - 1, y + 1)], "graphite", 2)
        self.draw_text(x + width / 2.0, y + height / 2.0, label, "void" if enabled else "graphite", font_key, anchor="center", width=width - 8, justify="center")
        if enabled:
            self.add_hotspot(x, y, x + width, y + height, callback, "button")

    def wrap_text(self, text, width, font_key):
        columns = max(6, int(width / self.char_width(font_key)))
        lines = []
        for paragraph in text.split("\n"):
            lines.extend(textwrap.wrap(paragraph, columns) or [""])
        return "\n".join(lines), len(lines)

    def button_height(self, label, width):
        columns = max(4, int((width - 16) / self.char_width("body")))
        lines = max(1, len(textwrap.wrap(label, columns)))
        return 14 + lines * self.line_height("body")

    def layout_window(self, window):
        elements = window.elements() if callable(window.elements) else window.elements
        padding = 14
        inner = window.width - padding * 2
        text_x = padding
        text_width = inner
        icon_bottom = 0
        if window.icon:
            text_x = padding + 64
            text_width = inner - 64
            icon_bottom = padding + 56
        y = padding
        placed = []
        for element in elements:
            kind = element[0]
            if kind == "text":
                content = element[1]() if callable(element[1]) else element[1]
                color = element[2] if len(element) > 2 else "void"
                font_key = element[3] if len(element) > 3 else "body"
                joined, count = self.wrap_text(content, text_width, font_key)
                placed.append(("text", text_x, y, text_width, joined, color, font_key))
                y += count * self.line_height(font_key) + 6
            elif kind == "gap":
                y += element[1]
            elif kind == "button":
                y = max(y, icon_bottom)
                label = element[1]
                enabled = element[3] if len(element) > 3 else True
                accent = element[4] if len(element) > 4 else None
                height = self.button_height(label, inner)
                placed.append(("button", padding, y, inner, height, label, element[2], enabled, accent))
                y += height + 8
            elif kind == "row":
                y = max(y, icon_bottom)
                entries = element[1]
                each = (inner - 8 * (len(entries) - 1)) / len(entries)
                height = max(self.button_height(entry[0], each) for entry in entries)
                for index, entry in enumerate(entries):
                    enabled = entry[2] if len(entry) > 2 else True
                    placed.append(("button", padding + index * (each + 8), y, each, height, entry[0], entry[1], enabled, None))
                y += height + 8
            elif kind == "file":
                y = max(y, icon_bottom)
                placed.append(("file", padding, y, inner, 38, element[1], element[2], element[3]))
                y += 40
            elif kind == "bar":
                y = max(y, icon_bottom)
                placed.append(("bar", padding, y, inner, 22, element[1]))
                y += 30
            elif kind == "console":
                y = max(y, icon_bottom)
                placed.append(("console", padding, y, inner, element[2], element[1]))
                y += element[2] + 8
        y = max(y, icon_bottom)
        return y + 6, placed

    def open_window(self, title, elements, width=460, x=None, y=None, closable=True, modal=False, kind="info", icon=None, on_close=None):
        window = GameWindow(title, elements, width, 0, 0, closable, modal, kind, icon, on_close)
        content_height, _ = self.layout_window(window)
        window.height = TITLE_HEIGHT + content_height
        available = DESIGN_HEIGHT - TASKBAR_HEIGHT
        if x is None:
            if modal:
                x = (DESIGN_WIDTH - width) / 2.0 + random.randint(-30, 30)
            else:
                x = 330 + random.randint(0, 280)
        if y is None:
            y = (available - window.height) / 2.0 + random.randint(-30, 30)
        window.x = max(0, min(DESIGN_WIDTH - width, x))
        window.y = max(0, min(available - window.height, y))
        self.windows.append(window)
        self.play("error" if kind == "error" else "open")
        return window

    def close_window(self, window):
        if window in self.windows:
            self.windows.remove(window)
            self.play("close")
            if window.on_close:
                window.on_close()

    def find_window(self, title):
        for window in self.windows:
            if window.title == title:
                return window
        return None

    def raise_window(self, window):
        if window in self.windows:
            self.windows.remove(window)
            self.windows.append(window)

    def begin_drag(self, window):
        self.raise_window(window)
        self.drag_state = (window, self.pointer[0] - window.x, self.pointer[1] - window.y)

    def draw_window(self, window):
        content_height, placed = self.layout_window(window)
        window.height = TITLE_HEIGHT + content_height
        available = DESIGN_HEIGHT - TASKBAR_HEIGHT
        window.x = max(0, min(DESIGN_WIDTH - window.width, window.x))
        window.y = max(0, min(available - window.height, window.y))
        x = window.x
        y = window.y
        width = window.width
        height = window.height
        self.draw_rect(x + 6, y + 6, x + width + 6, y + height + 6, fill="void", stipple="gray50")
        self.draw_rect(x, y, x + width, y + height, fill="silver", outline="void")
        self.draw_line([(x + 1, y + height - 2), (x + 1, y + 1), (x + width - 2, y + 1)], "white", 2)
        self.draw_line([(x + 1, y + height - 1), (x + width - 1, y + height - 1), (x + width - 1, y + 1)], "graphite", 2)
        self.add_hotspot(x, y, x + width, y + height, lambda target=window: self.raise_window(target), "window")
        bar_colors = {"info": ("cobalt", "white"), "billy": ("indigo", "white"), "error": ("plum", "white"), "warn": ("butter", "void"), "system": ("teal", "white")}
        bar_color, text_color = bar_colors.get(window.kind, ("cobalt", "white"))
        self.draw_rect(x + 4, y + 4, x + width - 4, y + TITLE_HEIGHT - 4, fill=bar_color)
        self.draw_text(x + 10, y + TITLE_HEIGHT / 2.0, self.garble(window.title), text_color, "bold", anchor="w", width=width - 60)
        self.add_hotspot(x + 4, y + 4, x + width - 30, y + TITLE_HEIGHT - 4, lambda target=window: self.begin_drag(target), "drag")
        if window.closable:
            self.draw_button(x + width - 28, y + 5, 22, 20, "X", lambda target=window: self.close_window(target), font_key="small")
        body_y = y + TITLE_HEIGHT
        if window.icon:
            self.draw_icon(window.icon, x + 14, body_y + 12, 48)
        for item in placed:
            kind = item[0]
            if kind == "text":
                self.draw_text(x + item[1], body_y + item[2], item[4], item[5], item[6], width=item[3])
            elif kind == "button":
                self.draw_button(x + item[1], body_y + item[2], item[3], item[4], item[5], item[6], item[7], item[8])
            elif kind == "file":
                fx = x + item[1]
                fy = body_y + item[2]
                hovered = self.is_hover(fx, fy, fx + item[3], fy + item[4])
                if hovered:
                    self.draw_rect(fx, fy, fx + item[3], fy + item[4], fill="butter", outline="void")
                self.draw_icon(item[6], fx + 6, fy + 5, 28)
                self.draw_text(fx + 44, fy + item[4] / 2.0, self.garble(item[5]), "void", "body", anchor="w", width=item[3] - 50)
                self.add_hotspot(fx, fy, fx + item[3], fy + item[4], item[7], "button")
            elif kind == "bar":
                value = max(0.0, min(1.0, item[5]()))
                bx = x + item[1]
                by = body_y + item[2]
                self.draw_rect(bx, by, bx + item[3], by + item[4], fill="white", outline="void")
                self.draw_rect(bx + 2, by + 2, bx + 2 + (item[3] - 4) * value, by + item[4] - 2, fill="teal")
                self.draw_text(bx + item[3] / 2.0, by + item[4] / 2.0, str(int(value * 100)) + "%", "void", "small", anchor="center")
            elif kind == "console":
                cx = x + item[1]
                cy = body_y + item[2]
                self.draw_rect(cx, cy, cx + item[3], cy + item[4], fill="void", outline="graphite")
                content = item[5]()
                joined, count = self.wrap_text(content, item[3] - 12, "small")
                lines = joined.split("\n")
                visible = max(1, int((item[4] - 10) / self.line_height("small")))
                self.draw_text(cx + 6, cy + 5, "\n".join(lines[-visible:]), "mint", "small", width=item[3] - 12)

    def draw_windows(self):
        for window in self.windows:
            if not window.modal:
                self.draw_window(window)
        for window in self.windows:
            if window.modal:
                self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill="void", stipple="gray25")
                self.add_hotspot(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, None, "blocker")
                self.draw_window(window)

    def show_dialog(self, title, text, options, icon=None, kind="info", width=460, extra=None):
        holder = []

        def make_handler(callback):
            def handler():
                self.close_window(holder[0])
                self.play("click")
                callback()

            return handler

        elements = [("text", text)]
        if extra:
            elements.extend(extra)
        for option in options:
            enabled = option[2] if len(option) > 2 else True
            elements.append(("button", option[0], make_handler(option[1]), enabled))
        window = self.open_window(title, elements, width=width, closable=False, modal=True, kind=kind, icon=icon)
        holder.append(window)
        return window

    def toast(self, text, kind="warn"):
        self.toasts.append({"text": text, "born": time.time(), "life": 5.5, "kind": kind})
        self.toasts = self.toasts[-5:]
        self.play("error" if kind == "error" else "notify")

    def draw_toasts(self):
        now = time.time()
        self.toasts = [item for item in self.toasts if now - item["born"] < item["life"]]
        for index, item in enumerate(reversed(self.toasts[-4:])):
            width = 330
            height = 62
            x = DESIGN_WIDTH - width - 10
            y = DESIGN_HEIGHT - TASKBAR_HEIGHT - 10 - (index + 1) * (height + 6) + 6
            self.draw_rect(x + 4, y + 4, x + width + 4, y + height + 4, fill="void", stipple="gray50")
            self.draw_rect(x, y, x + width, y + height, fill="silver", outline="void")
            self.draw_line([(x + 1, y + height - 2), (x + 1, y + 1), (x + width - 2, y + 1)], "white", 2)
            self.draw_rect(x, y, x + 6, y + height, fill="plum" if item["kind"] == "error" else "butter")
            self.draw_icon("error" if item["kind"] == "error" else "warn", x + 12, y + 14, 34)
            self.draw_text(x + 54, y + height / 2.0, self.garble(item["text"]), "void", "small", anchor="w", width=width - 64)
            self.add_hotspot(x, y, x + width, y + height, lambda target=item: self.dismiss_toast(target), "button")

    def dismiss_toast(self, item):
        if item in self.toasts:
            self.toasts.remove(item)

    def draw_rain(self, trail_color, head_color, always_visible=True):
        for column in self.rain_columns:
            column["head"] += column["speed"]
            if column["head"] - column["length"] * 17 > DESIGN_HEIGHT:
                column["head"] = random.uniform(-250, -20)
                column["speed"] = random.uniform(7, 20)
                column["length"] = random.randint(8, 16)
            if random.random() < 0.4:
                column["chars"][random.randrange(16)] = random.choice(RAIN_CHARACTERS)
            letters = column["chars"][:column["length"]]
            self.draw_text(column["x"], column["head"], "\n".join(letters), trail_color, "rain", anchor="s", justify="center")
            self.draw_text(column["x"], column["head"], letters[-1], head_color, "rain", anchor="s")

    def draw_boot(self):
        self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill="void")
        elapsed = time.time() - self.boot_start
        shown = min(len(BOOT_LINES), int(elapsed / 0.45) + 1)
        for index in range(shown):
            self.draw_text(60, 60 + index * 30, BOOT_LINES[index], "mint", "body")
        if shown >= len(BOOT_LINES):
            if int(elapsed * 2) % 2 == 0:
                self.draw_text(DESIGN_WIDTH / 2.0, 520, "CLICK ANYWHERE TO BOOT KID_OS", "butter", "mid", anchor="center")
            self.draw_text(DESIGN_WIDTH / 2.0, 560, "(sound starts after your first click)", "slate", "small", anchor="center")
        self.add_hotspot(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, self.finish_boot, "button")

    def finish_boot(self):
        self.audio.unlocked = True
        self.audio.want("calm")
        self.play("open")
        self.screen = "menu"
        self.menu_start = time.time()

    def draw_menu(self):
        self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill="void")
        self.draw_rain("night", "slate")
        now = time.time()
        jitter = 3 if random.random() < 0.04 else 0
        center = DESIGN_WIDTH / 2.0
        self.draw_text(center + 5 + jitter, 90 + 5, "KID_OS", "plum", "huge", anchor="n")
        self.draw_text(center - 3, 90, "KID_OS", "sky", "huge", anchor="n")
        self.draw_text(center + 3, 90, "KID_OS", "pink", "huge", anchor="n")
        self.draw_text(center, 90, "KID_OS", "white", "huge", anchor="n")
        self.draw_text(center, 205, "KID EXPERIENCE ON CLI", "butter", "mid", anchor="n")
        self.draw_icon("billy", center - 330, 290, 90)
        self.draw_icon("billy_smug", center + 240, 290, 90)
        for index, (label, callback) in enumerate([("PLAY", self.new_game), ("CREDITS", self.open_credits), ("EXIT", self.ask_exit)]):
            self.draw_button(center - 160, 280 + index * 76, 320, 56, label, callback, font_key="mid")
        message = MENU_MESSAGES[int((now - self.menu_start) / 2.6) % len(MENU_MESSAGES)]
        self.draw_rect(0, DESIGN_HEIGHT - 44, DESIGN_WIDTH, DESIGN_HEIGHT, fill="night")
        self.draw_text(20, DESIGN_HEIGHT - 22, "> " + message + ("_" if int(now * 2) % 2 == 0 else " "), "mint", "body", anchor="w")
        self.draw_text(DESIGN_WIDTH - 20, DESIGN_HEIGHT - 22, "endings found: " + str(len(self.found_endings)) + "/" + str(TOTAL_ENDINGS), "periwinkle", "small", anchor="e")

    def open_credits(self):
        self.play("open")
        self.screen = "credits"

    def draw_credits(self):
        self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill="void")
        self.draw_rain("night", "slate")
        center = DESIGN_WIDTH / 2.0
        self.draw_rect(center - 330, 70, center + 330, 640, fill="silver", outline="void")
        self.draw_rect(center - 326, 74, center + 326, 100, fill="cobalt")
        self.draw_text(center - 316, 87, "CREDITS.txt", "white", "bold", anchor="w")
        self.draw_text(center, 140, "KID_OS", "cobalt", "big", anchor="n")
        self.draw_text(center, 215, "Game Developer:", "graphite", "body", anchor="n")
        self.draw_text(center, 242, "Santiago Morales Itzcoatl", "void", "mid", anchor="n")
        self.draw_text(center, 320, "Studio:", "graphite", "body", anchor="n")
        self.draw_text(center, 347, "SorinaCrew by DXGPANIC Studios", "void", "mid", anchor="n")
        self.draw_text(center, 440, "Thank you for playing.\nNo real computers were harmed.\nOnly Dad's feelings.", "plum", "body", anchor="n", justify="center")
        self.draw_button(center - 140, 550, 280, 50, "BACK TO MENU", self.go_menu)

    def ask_exit(self):
        self.show_dialog("EXIT", "Nice try.\nYour dad's computer is still running.\n\nDo you really want to close KID_OS?", [("No, keep playing", lambda: None), ("Yes, close the game", self.quit_game)], icon="warn", kind="warn")

    def go_menu(self):
        self.session += 1
        self.windows = []
        self.toasts = []
        self.reset_state()
        self.tint_cache = {}
        self.update_fonts()
        self.screen = "menu"
        self.menu_start = time.time()
        self.audio.want("calm")
        self.play("click")

    def confirm_menu(self):
        if any(window.title == "BACK TO MENU?" for window in self.windows):
            return
        self.show_dialog("BACK TO MENU?", "Return to the main menu?\nBilly's progress will be lost.\n(Dad will not notice.)", [("No, keep hacking", lambda: None), ("Yes, main menu", self.go_menu)], icon="warn", kind="warn")

    def draw_desktop(self):
        if self.matrix_on:
            self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill="void")
            self.draw_rain("teal", "white")
        elif self.wallpaper == "cursed":
            base = self.wallpaper_override or "pink"
            self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill=base)
            self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill="plum", stipple="gray25")
            self.draw_rect(500, 140, 900, 460, fill="butter", outline="void", width=4)
            self.draw_rect(580, 220, 650, 290, fill="void")
            self.draw_rect(750, 220, 820, 290, fill="void")
            self.draw_rect(580, 360, 820, 390, fill="void")
            self.draw_text(700, 500, "sunset_but_wrong.bmp", "void", "mid", anchor="n")
        else:
            base = self.wallpaper_override or "teal"
            self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill=base)
            self.draw_text(DESIGN_WIDTH - 30, DESIGN_HEIGHT - 80, "DAD-OS 1.0\nProperty of Dad. Do not touch.", "moss" if base == "teal" else "silver", "body", anchor="se", justify="right")
        icons = [
            ("games", "GAMES", "folder"),
            ("dad_work", "DAD_WORK", "folder"),
            ("robux", "free_robux_FINAL_REAL.exe", "robux"),
            ("help", "HELP.exe", "floppy"),
            ("tweak", "SYS_TWEAK.exe", "gear"),
        ]
        now = time.time()
        for index, (icon_id, label, icon_kind) in enumerate(icons):
            offset_x, offset_y = self.icon_offsets.get(icon_id, (0, 0))
            x = 20 + offset_x
            y = 22 + index * 110 + offset_y
            x = max(0, min(DESIGN_WIDTH - 110, x))
            y = max(0, min(DESIGN_HEIGHT - TASKBAR_HEIGHT - 100, y))
            hovered = self.is_hover(x, y, x + 110, y + 100)
            if hovered:
                self.draw_rect(x, y, x + 110, y + 100, fill="white", stipple="gray25")
            if icon_id in self.pulse_ids and int(now * 3) % 2 == 0:
                self.draw_rect(x + 2, y + 2, x + 108, y + 98, outline="butter", width=3)
            self.draw_icon(icon_kind, x + 27, y + 4, 56)
            shown_label = self.garble(label)
            self.draw_text(x + 56, y + 65, shown_label, "void", "label", anchor="n", width=106, justify="center")
            self.draw_text(x + 55, y + 64, shown_label, "white", "label", anchor="n", width=106, justify="center")
            self.add_hotspot(x, y, x + 110, y + 100, lambda target=icon_id: self.on_desktop_icon(target), "button")

    def clock_text(self):
        minutes = 15 * 60 + 47 + int((time.time() - self.game_start) / 6.5)
        if self.glitch_level() > 0.6 and random.random() < 0.25:
            return random.choice(["??:?? PM", "99:99 AM", "4:20 PM", "0:00 ??"])
        hour = (minutes // 60) % 12 or 12
        return "%d:%02d PM" % (hour, minutes % 60)

    def draw_meter(self, x, y, label, value, color):
        self.draw_text(x, y + 10, label, "void", "small", anchor="w")
        self.draw_rect(x + 40, y + 3, x + 100, y + 17, fill="white", outline="void")
        self.draw_rect(x + 41, y + 4, x + 41 + 58 * (value / 100.0), y + 16, fill=color)

    def draw_taskbar(self):
        top = DESIGN_HEIGHT - TASKBAR_HEIGHT
        self.draw_rect(0, top, DESIGN_WIDTH, DESIGN_HEIGHT, fill="silver", outline="void")
        self.draw_line([(0, top + 1), (DESIGN_WIDTH, top + 1)], "white", 2)
        self.draw_button(4, top + 5, 90, 30, "KID_OS", self.confirm_menu, font_key="bold")
        self.draw_text(106, top + 20, "OBJECTIVE: " + self.objective, "void", "small", anchor="w", width=520)
        meters_x = 640
        self.draw_meter(meters_x, top + 10, "CHAOS", self.chaos, "salmon")
        self.draw_meter(meters_x + 112, top + 10, "STAB", self.stability, "mint")
        self.draw_meter(meters_x + 224, top + 10, "DAD?", self.suspicion, "butter")
        self.draw_meter(meters_x + 336, top + 10, "R$", self.robux_progress, "teal")
        self.draw_button(DESIGN_WIDTH - 176, top + 5, 76, 30, "SND OFF" if self.audio.muted else "SND ON", self.toggle_mute, font_key="small")
        self.draw_text(DESIGN_WIDTH - 12, top + 20, self.clock_text(), "void", "body", anchor="e")

    def draw_floating_mute(self):
        self.draw_button(DESIGN_WIDTH - 96, 10, 86, 28, "SND OFF" if self.audio.muted else "SND ON", self.toggle_mute, font_key="small")

    def draw_effects(self):
        level = self.glitch_level()
        now = time.time()
        if now < self.shake_until:
            self.shake_x = random.uniform(-7, 7) * self.scale
            self.shake_y = random.uniform(-5, 5) * self.scale
        else:
            self.shake_x = 0.0
            self.shake_y = 0.0
        if random.random() < 0.012 + 0.03 * level:
            self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill="white", stipple="gray12")
        if level > 0.0 and random.random() < 0.01 + level * 0.3:
            for _ in range(random.randint(1, 3 + int(level * 4))):
                bar_y = random.uniform(0, DESIGN_HEIGHT)
                self.draw_rect(0, bar_y, DESIGN_WIDTH, bar_y + random.uniform(3, 8 + 30 * level), fill=random.choice(["pink", "sky", "mint", "void", "butter"]), stipple="gray50")
        if level > 0.55:
            for _ in range(int(level * 30)):
                speck_x = random.uniform(0, DESIGN_WIDTH)
                speck_y = random.uniform(0, DESIGN_HEIGHT)
                self.draw_rect(speck_x, speck_y, speck_x + random.uniform(2, 14), speck_y + 2, fill=random.choice(["white", "pink", "sky"]))
        if level > 0.3 and random.random() < level * 0.012:
            self.shake_until = now + 0.25
            self.play("glitch")

    def chaos_event(self):
        now = time.time()
        if self.stage < 3 or self.stage > 5 or self.ending or self.card or self.bsod:
            return
        if now < self.next_chaos_event:
            return
        self.next_chaos_event = now + max(2.0, 6.0 - self.chaos / 25.0) + random.uniform(0, 2.0)
        roll = random.random()
        if roll < 0.35:
            pool = TOAST_POOL_WILD if self.chaos > 55 else TOAST_POOL_MILD
            self.toast(random.choice(pool), "error" if self.chaos > 70 else "warn")
        elif roll < 0.6:
            movable = [window for window in self.windows if not window.modal]
            if movable:
                target = random.choice(movable)
                target.x = random.randint(320, DESIGN_WIDTH - target.width)
                target.y = random.randint(10, 300)
                self.play("glitch")
        elif roll < 0.85:
            icon_id = random.choice(["games", "dad_work", "robux", "help", "tweak"])
            self.icon_offsets[icon_id] = (random.randint(0, 40) + (random.randint(0, 600) if self.chaos > 50 else 0), random.randint(-20, 40))
            self.play("glitch")
        else:
            if not self.matrix_on:
                self.wallpaper_override = random.choice(WALLPAPER_COLORS)
            self.shake_until = now + 0.3
            self.play("glitch")

    def draw_stage_card(self):
        card = self.card
        elapsed = time.time() - card["start"]
        self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill=card["color"])
        center = DESIGN_WIDTH / 2.0
        typed = int(elapsed * 40)
        self.draw_text(center, 270, card["title"], "butter", "mid", anchor="n")
        self.draw_text(center, 320, card["subtitle"][:typed], "white", "big", anchor="n")
        if elapsed > 0.6:
            self.draw_text(center, 420, card["footer"], "slate", "small", anchor="n")
        self.add_hotspot(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, self.skip_card, "blocker")
        if elapsed >= card["duration"]:
            self.skip_card()

    def show_card(self, title, subtitle, then, color="void", duration=2.6, footer="(click to skip)"):
        self.card = {"title": title, "subtitle": subtitle, "then": then, "start": time.time(), "color": color, "duration": duration, "footer": footer, "session": self.session}
        self.play("open")

    def skip_card(self):
        card = self.card
        if card is None or time.time() - card["start"] < 0.7:
            return
        self.card = None
        if card["session"] == self.session and card["then"]:
            card["then"]()

    def draw_bsod(self):
        data = self.bsod
        elapsed = time.time() - data["start"]
        self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill="cobalt")
        self.draw_text(120, 90, ":(", "white", "huge")
        percent = min(100, int(elapsed / data["duration"] * 100))
        self.draw_text(120, 250, "KID_OS ran into a problem and needs to restart.\nWe're just collecting some error info,\nand then we'll restart for you.", "white", "mid", width=900)
        self.draw_text(120, 390, str(percent) + "% complete", "white", "mid")
        generator = random.Random(11)
        for row in range(9):
            for column in range(9):
                if generator.random() < 0.5:
                    self.draw_rect(120 + column * 12, 450 + row * 12, 132 + column * 12, 462 + row * 12, fill="white")
        self.draw_text(250, 452, "Stop code: BILLY_CLICKED_THE_THING\nWhat failed: robux.sys\nSomewhere, a developer winced.", "white", "body")
        self.add_hotspot(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, self.skip_bsod, "blocker")
        if elapsed >= data["duration"]:
            self.skip_bsod(force=True)

    def show_bsod(self, then, duration=3.6):
        self.bsod = {"start": time.time(), "duration": duration, "then": then, "session": self.session}
        self.play("crash")
        self.shake_until = time.time() + 0.4

    def skip_bsod(self, force=False):
        data = self.bsod
        if data is None:
            return
        if not force and time.time() - data["start"] < 1.4:
            return
        self.bsod = None
        if data["session"] == self.session and data["then"]:
            data["then"]()

    def show_ending(self, key):
        self.windows = []
        self.toasts = []
        self.found_endings.add(key)
        self.ending = {"key": key, "start": time.time()}
        self.audio.silence(6.5)
        if key == "blue_screen":
            self.play("crash")
            self.later(1500, lambda: self.play("beep"))
        elif key == "grounded":
            self.play("sad")
        else:
            self.play("fanfare")
        self.audio.want("calm")

    def draw_ending(self):
        data = ENDINGS[self.ending["key"]]
        elapsed = time.time() - self.ending["start"]
        blue = self.ending["key"] == "blue_screen"
        self.draw_rect(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, fill="cobalt" if blue else "night")
        text_color = "white"
        left = 90
        if blue:
            self.draw_text(left, 40, ":(", "white", "huge")
            top = 170
        else:
            self.draw_text(left, 40, "ENDING " + str(data["number"]) + " OF " + str(TOTAL_ENDINGS), "periwinkle", "body")
            self.draw_text(left, 70, data["title"], "butter", "big", width=1100)
            top = 160
        joined = "\n\n".join(data["lines"][1:] if blue else data["lines"])
        typed = int(elapsed * 55)
        self.draw_text(left, top, joined[:typed], text_color, "body", width=1100)
        finished = typed >= len(joined)
        if finished:
            stats = "FINAL STATS   Chaos: %d%%   Stability: %d%%   Dad's suspicion: %d%%   Robux: 0   Endings found: %d/%d" % (self.chaos, self.stability, self.suspicion, len(self.found_endings), TOTAL_ENDINGS)
            self.draw_text(left, 560, stats, "mint" if not blue else "white", "small", width=1100)
            self.draw_button(left, 600, 260, 52, "PLAY AGAIN", self.new_game, font_key="bold")
            self.draw_button(left + 280, 600, 260, 52, "MAIN MENU", self.go_menu, font_key="bold")
        self.add_hotspot(0, 0, DESIGN_WIDTH, DESIGN_HEIGHT, self.skip_ending_typing, "blocker")

    def skip_ending_typing(self):
        if self.ending:
            self.ending["start"] -= 20.0

    def frame(self):
        try:
            self.canvas.delete("frame")
            self.hotspots = []
            self.audio.tick()
            if self.screen == "boot":
                self.draw_boot()
                self.draw_effects()
            elif self.screen == "menu":
                self.draw_menu()
                self.draw_windows()
                self.draw_floating_mute()
            elif self.screen == "credits":
                self.draw_credits()
                self.draw_floating_mute()
            else:
                self.chaos_event()
                self.draw_desktop()
                self.draw_windows()
                self.draw_toasts()
                self.draw_taskbar()
                self.draw_effects()
                if self.card:
                    self.draw_stage_card()
                    self.draw_floating_mute()
                if self.bsod:
                    self.draw_bsod()
                    self.draw_floating_mute()
                if self.ending:
                    self.draw_ending()
                    self.draw_floating_mute()
            self.canvas.tag_raise("scan")
        except Exception:
            traceback.print_exc()
        self.root.after(FRAME_DELAY_MS, self.frame)

    def on_motion(self, event):
        self.pointer = self.to_design(event.x, event.y)
        over_button = False
        for x0, y0, x1, y1, callback, kind in reversed(self.hotspots):
            if x0 <= self.pointer[0] <= x1 and y0 <= self.pointer[1] <= y1:
                over_button = callback is not None and kind == "button"
                break
        self.canvas.configure(cursor="hand2" if over_button else "arrow")

    def on_press(self, event):
        self.pointer = self.to_design(event.x, event.y)
        self.audio.unlocked = True
        for x0, y0, x1, y1, callback, kind in reversed(self.hotspots):
            if x0 <= self.pointer[0] <= x1 and y0 <= self.pointer[1] <= y1:
                if callback is not None:
                    if kind == "button":
                        self.play("click")
                    callback()
                return

    def on_drag(self, event):
        self.pointer = self.to_design(event.x, event.y)
        if self.drag_state:
            window, grab_x, grab_y = self.drag_state
            window.x = self.pointer[0] - grab_x
            window.y = self.pointer[1] - grab_y

    def on_release(self, event):
        self.drag_state = None

    def run_steps(self, steps, final=None):
        session = self.session

        def advance(index):
            if session != self.session:
                return
            if index >= len(steps):
                if final:
                    final()
                return
            steps[index](lambda: advance(index + 1))

        advance(0)

    def sys_step(self, title, text, button="OK", kind="info", icon=None):
        def run(done):
            self.show_dialog(title, text, [(button, done)], icon=icon or ("error" if kind == "error" else ("warn" if kind == "warn" else "info")), kind=kind)

        return run

    def billy_step(self, text, face="billy", button=None):
        def run(done):
            self.show_dialog("BILLY", text, [(button or random.choice(BILLY_BUTTONS), done)], icon=face, kind="billy")

        return run

    def do_step(self, function):
        def run(done):
            function()
            done()

        return run

    def wait_step(self, milliseconds):
        def run(done):
            self.later(milliseconds, done)

        return run

    def toast_step(self, text, kind="warn", wait=0):
        def run(done):
            self.toast(text, kind)
            self.later(max(1, wait), done)

        return run

    def progress_step(self, title, text, seconds, kind="system", stall=0.99):
        def run(done):
            holder = {"value": 0.0}
            started = time.time()
            window = self.open_window(title, [("text", text), ("bar", lambda: holder["value"])], width=460, closable=False, modal=True, kind=kind)

            def tick():
                if window not in self.windows:
                    return
                elapsed = time.time() - started
                holder["value"] = min(stall, elapsed / seconds)
                if elapsed >= seconds:
                    holder["value"] = 1.0
                    self.close_window(window)
                    done()
                    return
                self.later(60, tick)

            tick()

        return run

    def bsod_step(self, duration=3.6):
        def run(done):
            self.show_bsod(done, duration)

        return run

    def new_game(self):
        self.session += 1
        self.windows = []
        self.toasts = []
        self.reset_state()
        self.tint_cache = {}
        self.update_fonts()
        self.screen = "game"
        self.audio.want("calm")
        self.objective = "..."
        self.show_card("STAGE 1", "DAD'S COMPUTER", self.stage_one_intro)

    def stage_one_intro(self):
        self.stage = 1
        self.objective = "Find free games, cheat codes and FREE ROBUX. Nothing important. Promise."
        steps = [
            self.sys_step("DAD (from the hallway)", "Billy! I'm stepping out for ten minutes.\nDo NOT touch anything important!", button="Okay Dad!", kind="warn"),
            self.billy_step("Ten minutes? Bro, that's a whole speedrun."),
            self.billy_step("Dad's computer. No password. This is literally a gift from the universe."),
            self.billy_step("Mission: free games, cheat codes, and FREE ROBUX. Let's get it.", face="billy_smug", button="LET'S GO"),
        ]
        self.run_steps(steps)

    def on_desktop_icon(self, icon_id):
        if self.card or self.bsod or self.ending:
            return
        if icon_id == "games":
            self.open_folder("C:\\GAMES", [
                ("solitaire.exe", "game", lambda: self.run_file("solitaire")),
                ("minecraft_but_free.zip", "zip", lambda: self.run_file("minecraft")),
                ("Totally_Legit_Installer_v2.exe", "exe", lambda: self.run_file("installer")),
                ("README_PLEASE.txt", "text", lambda: self.run_file("readme")),
            ])
        elif icon_id == "dad_work":
            self.open_folder("C:\\DAD_WORK (DO NOT TOUCH)", [
                ("QUARTERLY_REPORT_FINAL_v7_REAL.xlsx", "text", lambda: self.run_file("report")),
                ("do_not_delete.txt", "text", lambda: self.run_file("note")),
                ("cat_photos_(2300).zip", "cat", lambda: self.run_file("cats")),
                ("salary_negotiation_strategy.docx", "text", lambda: self.run_file("salary")),
            ])
        elif icon_id == "robux":
            self.click_robux()
        elif icon_id == "help":
            self.click_help()
        elif icon_id == "tweak":
            self.open_tweaker()

    def open_folder(self, title, entries):
        existing = self.find_window(title)
        if existing:
            self.raise_window(existing)
            return
        elements = [("text", "Click a file to open it. (Kids love clicking.)", "graphite", "small")]
        for label, icon, callback in entries:
            elements.append(("file", label, icon, callback))
        self.open_window(title, elements, width=470, closable=True)

    FILE_SCRIPTS = {
        "solitaire": {"effects": {}, "script": [("sys", "SOLITAIRE.EXE", "52 cards loaded.\nNo Robux found in any of them."), ("billy", "Cards? Bro. Zero Robux. Disrespectful.")]},
        "minecraft": {"effects": {"chaos": 2}, "script": [("sys", "minecraft_but_free.zip", "File size: 0 KB\nContents: vibes"), ("billy", "0 KB?? That's how you know it's optimized.")]},
        "installer": {"effects": {"chaos": 3}, "script": [("warn", "Totally_Legit_Installer_v2.exe", "This installer wants to install 4 other installers.\nThose installers want to install 16 more."), ("billy", "Inception but for games. I respect it.")]},
        "readme": {"effects": {}, "script": [("sys", "README_PLEASE.txt", "Free games are never free. They cost your time, your soul, and 12 browser toolbars.\n\n- Dad, 2011"), ("billy", "Dad is just jealous of my gaming potential.")]},
        "report": {"effects": {"suspicion": 4}, "script": [("sys", "QUARTERLY_REPORT_FINAL_v7_REAL.xlsx", "Loading 4,000,000 cells...\nEvery single cell says TBD."), ("billy", "Dad works so hard. At nothing. But so hard.")]},
        "note": {"effects": {"suspicion": 6}, "script": [("sys", "do_not_delete.txt", "Billy do NOT touch anything.\nLove, Dad.\nP.S. The Wi-Fi password is on the fridge."), ("billy", "He wrote a P.S. That's basically an invitation.")]},
        "cats": {"effects": {"suspicion": 2}, "flag": "cat_evidence", "script": [("sys", "PHOTO VIEWER", "Photo 1,337 of 2,300:\nMr. Whiskers on the keyboard. Again.\n\nThe cat has used this computer more than Dad."), ("billy", "That cat is a menace. Noted.")]},
        "salary": {"effects": {"suspicion": 4}, "script": [("sys", "salary_negotiation_strategy.docx", "Page 1 of 1:\n\nAsk for more."), ("billy", "Wow. Dad is a strategist.")]},
    }

    def run_file(self, key):
        data = self.FILE_SCRIPTS[key]
        steps = []
        effects = data["effects"]
        flag = data.get("flag")

        def apply_effects():
            self.adjust(**effects)
            if flag:
                self.flags.add(flag)

        steps.append(self.do_step(apply_effects))
        for entry in data["script"]:
            if entry[0] == "billy":
                steps.append(self.billy_step(entry[1]))
            else:
                steps.append(self.sys_step(entry[1], entry[2], kind="warn" if entry[0] == "warn" else "info"))
        self.run_steps(steps, lambda: self.after_explore(key))

    def after_explore(self, key):
        self.explored.add(key)
        if self.stage == 1 and len(self.explored) >= 3 and not self.hinted:
            self.hinted = True
            self.pulse_ids.add("tweak")
            self.toast("SYS_TWEAK.exe keeps blinking at you.", "warn")

    def click_robux(self):
        if self.stage == 4:
            self.launch_installer()
            return
        if self.stage >= 5:
            self.run_steps([self.sys_step("free_robux_FINAL_REAL.exe", "File size: 0 KB\nIt has done enough.", kind="warn"), self.billy_step("I'm never touching that again. (I'm touching it again.)")])
            return
        lines = {
            1: "Hacker mode?? So it EXISTS. ...that weird gear thing has been staring at me.",
            2: "Not yet. I need hacker upgrades first. Patience, bro.",
            3: "First I gotta fix the desktop. THEN riches.",
        }
        stage = self.stage

        def after():
            if stage == 1:
                self.pulse_ids.add("tweak")
            self.after_explore("robux_denied")

        self.run_steps([
            self.sys_step("ACCESS DENIED", "free_robux_FINAL_REAL.exe requires HACKER MODE.\n\nHacker mode: NOT INSTALLED.", kind="error"),
            self.billy_step(lines.get(stage, lines[1])),
        ], after)

    def click_help(self):
        if self.stage in (1, 2):
            def teach():
                self.pulse_ids.add("tweak")
                self.run_steps([
                    self.sys_step("BITSY THE HELPFUL FLOPPY", "Step one: click the thing.\nStep two: profit.\n\nPro tip: the thing is the gear thing.", icon="floppy"),
                    self.billy_step("Genius. Absolutely genius.", face="billy_smug"),
                ], lambda: self.after_explore("bitsy"))

            def decline():
                self.run_steps([
                    self.sys_step("BITSY THE HELPFUL FLOPPY", "Respect. You'll go far.\n(Statistically, to a courtroom.)", icon="floppy"),
                    self.billy_step("Facts."),
                ], lambda: self.after_explore("bitsy"))

            self.show_dialog("BITSY THE HELPFUL FLOPPY", "Hi! I'm Bitsy!\nIt looks like you're trying to become a hacker.\n\nWould you like help with that?", [("Yes, make me a hacker", teach), ("No, I'm already a hacker", decline)], icon="floppy", kind="system")
        else:
            lines = [
                "Bitsy: I've seen things. Mostly folders.",
                "Bitsy: I told you so. (I didn't. But I feel like I did.)",
                "Bitsy: I'm a floppy disk. I have 1.44 MB of patience left.",
            ]
            self.run_steps([self.sys_step("BITSY THE HELPFUL FLOPPY", random.choice(lines), icon="floppy")])

    def open_tweaker(self):
        if self.stage == 1:
            self.stage = 2
            self.pulse_ids.discard("tweak")
            self.show_card("STAGE 2", "THE HACKER ARC", self.stage_two_intro)
        elif self.stage == 2:
            self.show_tweaker_window()
        elif self.stage >= 3:
            self.run_steps([
                self.sys_step("SYS_TWEAK 9000", "SYS_TWEAK has stopped responding.\n(It has stopped responding to reality.)", kind="error"),
                self.billy_step("Okay that one's on the tweaker, not me."),
            ])

    def stage_two_intro(self):
        self.objective = "Customize your destiny with SYS_TWEAK. Two upgrades should do it."
        self.run_steps([
            self.sys_step("SYS_TWEAK 9000", "Welcome to SYS_TWEAK 9000!\nCustomize your computer, your desktop and your destiny.\n\n(Dad: please do not.)", icon="gear"),
            self.billy_step("...Bro. This is the hacker menu. I'm in.", face="billy_smug"),
        ], self.show_tweaker_window)

    def show_tweaker_window(self):
        existing = self.find_window("SYS_TWEAK 9000")
        if existing:
            self.raise_window(existing)
            return

        def elements():
            rows = [("text", lambda: "HACKER RANK: " + self.hacker_rank(), "plum", "bold"), ("text", "Pick two upgrades. Each one is 100% safe.*\n*Not safe.", "graphite", "small"), ("gap", 4)]
            options = [("matrix", "[ MATRIX MODE ]"), ("wallpaper", "[ CHANGE WALLPAPER ]"), ("secret", "[ UNLOCK SECRET GAME ]")]
            for key, label in options:
                done = key in self.tweaks_used
                rows.append(("button", ("[DONE] " + label[2:-2].title()) if done else label, lambda target=key: self.use_tweak(target), not done))
            return rows

        self.open_window("SYS_TWEAK 9000", elements, width=440, closable=True, kind="system", icon="gear")

    def use_tweak(self, key):
        if key in self.tweaks_used or self.stage != 2:
            return
        self.tweaks_used.add(key)
        if key == "matrix":
            def apply():
                self.matrix_on = True
                self.adjust(chaos=14, stability=-8, hacker=2)

            steps = [
                self.do_step(apply),
                self.sys_step("MATRIX MODE: ENABLED", "The screen is now green.\nNobody asked it to be.", kind="system", icon="gear"),
                self.billy_step("I have successfully hacked the color green.", face="billy_smug"),
            ]
        elif key == "wallpaper":
            def apply():
                self.wallpaper = "cursed"
                self.adjust(chaos=10, stability=-6, hacker=1)

            steps = [
                self.do_step(apply),
                self.sys_step("WALLPAPER CHANGED", "New wallpaper: sunset_but_wrong.bmp\n\nThe sun is a rectangle now.", kind="system", icon="gear"),
                self.billy_step("Anonymous would be proud.", face="billy_smug"),
            ]
        else:
            def apply():
                self.adjust(chaos=10, suspicion=8, hacker=2)
                self.flags.add("secret_game")

            steps = [
                self.progress_step("SECRET_GAME.exe", "LOADING... 99%\nLOADING... 99%\nLOADING... 99%", 3.0),
                self.do_step(apply),
                self.sys_step("SECRET GAME UNLOCKED", "'Press F To Pay Respects To Your Computer'\n\nGameplay: press F.\nObjective: F.", kind="system", icon="game"),
                self.billy_step("10/10 no notes. Step one: click the thing. Step two: profit.", face="billy_smug"),
            ]
        self.run_steps(steps, self.after_tweak)

    def after_tweak(self):
        if self.stage == 2 and len(self.tweaks_used) >= 2:
            self.run_steps([
                self.billy_step("Bro, I am literally him.", face="billy_smug"),
                self.sys_step("WARNING", "Display driver is feeling things.\n\nPlease do not make eye contact with the driver.", kind="warn"),
                self.billy_step("That's normal. That's normal, right?", face="billy_panic"),
            ], self.begin_stage_three)

    def begin_stage_three(self):
        tweaker = self.find_window("SYS_TWEAK 9000")
        if tweaker:
            self.windows.remove(tweaker)
        self.stage = 3
        self.show_card("STAGE 3", "THE CONSEQUENCES", self.stage_three_intro)

    def stage_three_intro(self):
        self.objective = "Fix the desktop. Billy says it's fine."
        self.next_chaos_event = time.time() + 3.0
        self.toast("WARNING: Desktop is feeling emotional.", "warn")
        self.run_steps([
            self.billy_step("Okay. Small problem. The desktop is doing a little dance.", face="billy_panic"),
            self.billy_step("No worries. I'm basically IT support. Let me fix it.", face="billy_smug"),
        ], self.show_problem_menu)

    def show_problem_menu(self):
        labels = {
            "restore": "Restore default settings",
            "optimizer": "Install TURBO_OPTIMIZER_PRO (FREE!!!)",
            "bitsy": "Ask Bitsy for advice",
            "repair": "Press AUTOMATIC REPAIR",
        }
        options = []
        handlers = {"restore": self.problem_restore, "optimizer": self.problem_optimizer, "bitsy": self.problem_bitsy, "repair": self.problem_repair}
        for key in ("restore", "optimizer", "bitsy", "repair"):
            done = key in self.problems_used
            options.append((("[DONE] " if done else "") + labels[key], handlers[key], not done))
        text = lambda: "Computer stability: %d%%\nChaos level: %d%%\n\nBilly says everything is fine.\nBilly is wrong. Pick TWO fixes." % (self.stability, self.chaos)
        self.show_dialog("SOMETHING IS WRONG", text, options, icon="billy_panic", kind="billy", width=480)

    def after_problem(self, key):
        self.problems_used.add(key)
        if len(self.problems_used) >= 2:
            self.run_steps([
                self.billy_step("Okay. Desktop is fixed.*\n\n*Not fixed. But I have bigger plans.", face="billy_smug"),
            ], self.begin_stage_four)
        else:
            self.run_steps([self.billy_step("See? Fixed. Probably. One more should do it.")], self.show_problem_menu)

    def problem_restore(self):
        def apply():
            self.matrix_on = False
            self.wallpaper = "teal"
            self.wallpaper_override = None
            self.comic = True
            self.update_fonts()
            self.adjust(chaos=4, stability=-8, suspicion=-4)

        self.run_steps([
            self.billy_step("Easy. Restore defaults. Everyone knows that button fixes everything."),
            self.progress_step("RESTORING DEFAULTS", "Restoring factory settings...", 2.6),
            self.do_step(apply),
            self.sys_step("DEFAULTS RESTORED", "Default theme: COMIC_SANS_FOREVER\nDefault volume: 3%\nDefault Dad: still angry", kind="warn"),
            self.billy_step("This isn't what I remember but it's FINE. It's fine.", face="billy_panic"),
        ], lambda: self.after_problem("restore"))

    def problem_optimizer(self):
        def apply():
            self.adjust(chaos=16, stability=-14, suspicion=8)
            self.flags.add("optimizer")
            self.spawn_clutter(3)

        self.run_steps([
            self.billy_step("TURBO_OPTIMIZER_PRO. It says it makes computers 400% faster. Four hundred percent. That's like four computers.", face="billy_smug"),
            self.progress_step("INSTALLING TURBO_OPTIMIZER_PRO", "Installing 14 toolbars...\nInstalling 3 more toolbars...\nWhy.", 2.8),
            self.do_step(apply),
            self.sys_step("TURBO_OPTIMIZER_PRO", "Your computer is now 400% faster at displaying ads.", kind="error"),
            self.billy_step("...That's technically still faster.", face="billy_panic"),
        ], lambda: self.after_problem("optimizer"))

    def spawn_clutter(self, count):
        for _ in range(count):
            title, text = random.choice(AD_TEXTS)
            self.open_window(title, [("text", text, "void", "body"), ("button", "CLOSE (probably)", lambda: None)], width=360, closable=True, kind="warn", icon="ad", x=random.randint(380, 860), y=random.randint(20, 380))

    def problem_bitsy(self):
        def delete_system():
            def apply():
                self.adjust(chaos=24, stability=-26, suspicion=12)
                self.flags.add("system32_deleted")

            self.run_steps([
                self.progress_step("DELETING System32", "Deleting 2,411 files...\nWait, why is it so fast?", 2.8),
                self.do_step(apply),
                self.sys_step("System32", "System32 has been deleted.\nSystem32 has left the chat.", kind="error"),
                self.billy_step("Wow. It's SO fast now. I can't even open stuff. That's what fast means.", face="billy_panic"),
            ], lambda: self.after_problem("bitsy"))

        def ignore():
            self.adjust(chaos=2)
            self.flags.add("bitsy_angry")
            self.run_steps([
                self.sys_step("BITSY THE HELPFUL FLOPPY", "Rude.\nI'm telling the Recycle Bin.", icon="floppy"),
                self.billy_step("I don't take advice from 1.44 MB."),
            ], lambda: self.after_problem("bitsy"))

        def ask_robux():
            self.adjust(chaos=3, robux=10)
            self.flags.add("bitsy_robux")
            self.run_steps([
                self.sys_step("BITSY THE HELPFUL FLOPPY", "Great question!\nRun free_robux_FINAL_REAL.exe.\nIt's definitely safe.\n\n(Bitsy is a floppy disk and has never been outside.)", icon="floppy"),
                self.billy_step("Bro. BITSY. You're my favorite floppy.", face="billy_smug"),
            ], lambda: self.after_problem("bitsy"))

        self.show_dialog("BITSY THE HELPFUL FLOPPY", "Hi! Have you tried turning it off and on again?\n\nOr, even better: deleting System32! It's the folder that makes your computer slow.\n\n(Source: trust me.)", [
            ("Delete System32 (Bitsy says it's fine)", delete_system),
            ("Ignore Bitsy", ignore),
            ("Ask: how do I get free Robux?", ask_robux),
        ], icon="floppy", kind="system", width=500)

    def problem_repair(self):
        def apply():
            self.adjust(chaos=12, stability=-10)
            self.scramble_desktop()

        self.run_steps([
            self.billy_step("AUTOMATIC REPAIR. It's literally in the name. It's automatic."),
            self.progress_step("AUTOMATIC REPAIR", "Scanning for problems...\nRepairing... repairing...\nStill repairing...", 3.4),
            self.do_step(apply),
            self.sys_step("REPAIR COMPLETE", "Repair found 4,096 problems.\nFixed: 0\nCreated: 4,097", kind="error"),
            self.billy_step("That's one more than before. We are winning.", face="billy_panic"),
        ], lambda: self.after_problem("repair"))

    def scramble_desktop(self):
        for icon_id in ("games", "dad_work", "robux", "help", "tweak"):
            self.icon_offsets[icon_id] = (random.randint(0, 500), random.randint(-30, 60))
        self.shake_until = time.time() + 0.5
        self.play("glitch")

    def begin_stage_four(self):
        self.stage = 4
        self.show_card("STAGE 4", "FREE ROBUX", self.stage_four_intro)

    def stage_four_intro(self):
        self.objective = "Run free_robux_FINAL_REAL.exe. Become rich."
        self.adjust(robux=20)
        self.pulse_ids.add("robux")
        self.run_steps([
            self.billy_step("Okay. The real mission. Free. Robux."),
            self.toast_step("free_robux_FINAL_REAL.exe is now UNLOCKED. (Nobody knows why.)", "warn", 500),
            self.billy_step("Hacker mode: unlocked. Dad's computer: cooked. Me: LOCKED IN.", face="billy_smug", button="LOCK IN"),
        ])

    def launch_installer(self):
        if self.find_window("ROBUX_GENERATOR_9000 SETUP") or any(window.modal for window in self.windows):
            return
        self.pulse_ids.discard("robux")
        self.amount_label = "1,000 R$"
        steps = [
            self.billy_step("This is it. The legendary file. Don't blink.", face="billy_smug"),
            self.installer_welcome_step(),
            self.installer_permission_step(),
            self.installer_amount_step(),
        ]
        steps.extend(self.generator_steps())
        self.run_steps(steps, self.begin_stage_five)

    def installer_welcome_step(self):
        def run(done):
            def show():
                self.show_dialog("ROBUX_GENERATOR_9000 SETUP", "Welcome!\n\nGenerate UNLIMITED Robux with ONE click*.\n\n*Not Robux. Not unlimited. Not one click.", [("NEXT >", done), ("Read terms and conditions", read_terms)], icon="robux", kind="warn")

            def read_terms():
                self.adjust(chaos=2)
                self.run_steps([
                    self.sys_step("TERMS (page 1 of 4,800)", "By clicking NEXT you grant us access to your files, your camera, your dad's browsing history and one (1) kidney.", kind="warn"),
                    self.billy_step("Kidney's fine. I have two. Also I'm not reading 4,800 pages."),
                ], show)

            show()

        return run

    def installer_permission_step(self):
        def run(done):
            def allow(message):
                def handler():
                    self.adjust(chaos=10, suspicion=10, stability=-10, robux=8)
                    self.run_steps([self.sys_step("PERMISSIONS", message, kind="warn"), self.billy_step("Wait, what's PHP? ...Doesn't matter. Free Robux.")], done)

                return handler

            self.show_dialog("ROBUX_GENERATOR_9000 SETUP", "ROBUX_GENERATOR wants permission to:\n\n- Access ALL files\n- Use the camera\n- Control PHP (???)\n- Rename Dad", [
                ("ALLOW EVERYTHING (recommended)", allow("Allowed: everything.\nThanks for your trust!")),
                ("Allow only some things", allow("We ignored your selection.\nAllowed: everything.\nThanks for your trust!")),
            ], icon="robux", kind="warn", width=500)

        return run

    def installer_amount_step(self):
        def run(done):
            def choose(label, fame, chaos, reply):
                def handler():
                    self.amount_label = label
                    self.adjust(fame=fame, chaos=chaos, robux=10)
                    self.run_steps([self.billy_step(reply, face="billy_smug")], done)

                return handler

            self.show_dialog("HOW MANY ROBUX?", "Select your desired amount of free Robux:", [
                ("1,000 R$ (humble)", choose("1,000 R$", 15, 10, "Humble. Respectable. Boring.")),
                ("100,000 R$ (hacker budget)", choose("100,000 R$", 35, 15, "Hacker budget. Okay okay okay.")),
                ("1,000,000 R$ (Billy goes pro)", choose("1,000,000 R$", 55, 22, "Billy goes pro. Say less.")),
                ("ALL OF THEM", choose("ALL OF THEM", 75, 30, "There are no more Robux left in the world and that's on me.")),
            ], icon="robux", kind="warn", width=500)

        return run

    def log_line(self, text):
        self.generator_log.append(text)
        self.generator_log = self.generator_log[-30:]

    def log_step(self, text, delay, sound=None, shake=False, **changes):
        def run(done):
            def fire():
                self.log_line(text)
                self.adjust(**changes)
                if sound:
                    self.play(sound)
                if shake:
                    self.shake_until = time.time() + 0.4
                done()

            self.later(delay, fire)

        return run

    def open_generator_step(self):
        def run(done):
            self.generator_log = []
            self.open_window("ROBUX_GENERATOR_9000.exe", [
                ("text", lambda: "Target: " + self.amount_label + "   |   Status: RUNNING", "plum", "bold"),
                ("console", lambda: "\n".join(self.generator_log) or "Booting...", 190),
                ("bar", lambda: self.robux_progress / 100.0),
            ], width=560, closable=False, modal=True, kind="error", icon="robux")
            done()

        return run

    def close_generator_step(self):
        def run(done):
            window = self.find_window("ROBUX_GENERATOR_9000.exe")
            if window:
                self.close_window(window)
            done()

        return run

    def internet_decision_step(self):
        def run(done):
            def result(steps, **changes):
                def handler():
                    self.adjust(**changes)
                    self.run_steps(steps, done)

                return handler

            def clutter():
                self.spawn_clutter(3)

            self.show_dialog("THE INTERNET IS ON FIRE", "Billy has about four seconds to make a decision.\n\nWhat does Billy do?", [
                ("Click CANCEL", result([self.sys_step("CANCEL", "The Cancel button is on a break.\nBack in 5 years.", kind="warn"), self.billy_step("Union rules?? In THIS economy?", face="billy_panic")], chaos=3)),
                ("Unplug the router", result([self.sys_step("ROUTER", "You walk to the router.\nIt is unplugged. It has been unplugged since 2019.\nThe internet is coming from somewhere else.", kind="error"), self.billy_step("Bro that is so spooky.", face="billy_panic")], chaos=4)),
                ("Close the window", result([self.do_step(clutter), self.sys_step("WINDOWS", "You closed the window.\n3 more windows opened.\nThat's how windows work.", kind="warn"), self.billy_step("Unfair.", face="billy_panic")], chaos=6)),
                ("Livestream this on TikToob", result([self.do_step(lambda: self.flags.add("livestreamed")), self.sys_step("LIVE", "You're live!\nViewers: 1... 14... 38,000\nChat: PHP??? LMAOOO", kind="info"), self.billy_step("Chat, we're so back.", face="billy_smug")], chaos=5, fame=20)),
            ], icon="error", kind="error", width=500)

        return run

    def generator_steps(self):
        return [
            self.open_generator_step(),
            self.log_step("Connecting to robux.totally-real.biz ...", 900, "click", robux=6, chaos=2),
            self.log_step("Connected to PHP SERVER #1. It sounds nervous.", 1000, "glitch", chaos=4, stability=-4),
            self.log_step("PHP SERVER #1 invited 400 other PHP servers.", 1000, "glitch", True, chaos=4, robux=8),
            self.toast_step("PHP HAS LEFT THE CHAT.", "error", 900),
            self.log_step("Installing toolbar 15... 16... 17... why.", 800, "click", robux=6, chaos=2),
            self.sys_step("GLOBAL INTERNET INCIDENT DETECTED", "Severity: yes.\nAffected: the internet.\nCause: Billy.", kind="error"),
            self.billy_step("Why is it saying 'internet'?? I just wanted my Robux!", face="billy_panic"),
            self.do_step(lambda: self.adjust(chaos=6, stability=-8, suspicion=8)),
            self.sys_step("ERROR 418", "Error 418: Billy is a teapot.\n\nThe server refuses to brew coffee because Billy is, in fact, a teapot.", kind="error"),
            self.billy_step("I am literally not a teapot.", face="billy_panic"),
            self.bsod_step(3.6),
            self.toast_step("System restarted successfully. (It did not.)", "warn", 900),
            self.toast_step("Somewhere, a developer just woke up screaming.", "error", 1300),
            self.toast_step("Your dad's computer is now wanted in 37 countries.", "error", 1300),
            self.log_step("Global incident level: RIDICULOUS", 500, "glitch", True, chaos=6, robux=10),
            self.internet_decision_step(),
            self.do_step(lambda: self.adjust(robux=100)),
            self.log_step("Generating Robux... done.", 900, "coin"),
            self.sys_step("CONGRATULATIONS!", "YOU HAVE WON 0 ROBUX.", kind="warn", icon="robux"),
            self.billy_step("ZERO?? ...ZERO??? I did all of this for ZERO?", face="billy_panic"),
            self.close_generator_step(),
            self.do_step(self.announce_fame),
            self.wait_step(1500),
        ]

    def announce_fame(self):
        self.play("fanfare")
        if self.fame >= 60:
            self.toast("TRENDING #1: #BillyBrokeTheInternet", "warn")
        else:
            self.toast("TRENDING #73: #SomebodyBrokeTheInternet", "warn")

    def begin_stage_five(self):
        self.stage = 5
        self.show_card("STAGE 5", "DAD IS HOME", self.stage_five_intro)

    def stage_five_intro(self):
        self.objective = "DAD IS HOME. THINK FAST."
        self.dad_arrival = time.time() + 30.0
        self.audio.want("chaos")
        self.play("keys")
        self.run_steps([
            self.sys_step("NOTIFICATION", "Front door unlocked.\nKeys jingling.\nA familiar voice hums in the hallway.", kind="warn"),
            self.billy_step("Wait. WAIT. Those are the KEYS. Dad's keys. It's been like ten minutes??", face="billy_panic"),
            self.billy_step("Okay. Okay okay okay. I'm cooked. But I'm a genius. I can fix this.", face="billy_panic"),
        ], self.show_final_choice)

    def final_status_text(self):
        parts = []
        if self.matrix_on:
            parts.append("The screen is still Matrix green.")
        if "system32_deleted" in self.flags:
            parts.append("System32 is gone and does not seem sad about it.")
        if "optimizer" in self.flags:
            parts.append("There are 14 toolbars on the desktop.")
        if self.comic:
            parts.append("Everything is in Comic Sans.")
        if self.chaos > 80:
            parts.append("The desktop looks like it was dropped from a building.")
        if not parts:
            parts.append("The computer looks... suspiciously fine?")
        remaining = max(0, int(self.dad_arrival - time.time()))
        countdown = "DAD ARRIVES IN 0:%02d" % remaining if remaining > 0 else "DAD IS IN THE ROOM."
        return countdown + "\n\n" + " ".join(parts) + "\n\nWhat does Billy do?"

    def show_final_choice(self):
        self.show_dialog("DAD IS HOME", self.final_status_text, [
            ("Attempt to repair everything", self.final_repair),
            ("Pretend nothing happened", self.final_pretend),
            ("Blame the cat", self.final_cat),
            ("Turn off the monitor and hope nobody notices", self.final_monitor),
        ], icon="billy_panic", kind="error", width=520)

    def final_repair(self):
        self.run_steps([
            self.billy_step("I'm just gonna fix it. How hard can it be. I'm basically IT.", face="billy_smug"),
            self.progress_step("REPAIRING EVERYTHING", "Repairing the desktop...\nRepairing the internet...\nRepairing Dad's trust...", 3.2),
            self.sys_step("REPAIR TOOL", "Repair complete!\n\nFixed: 0\nBroken: everything\nBlue: new", kind="error"),
        ], lambda: self.show_ending("blue_screen"))

    def final_pretend(self):
        steps = [
            self.billy_step("Nothing happened. I was never here. Nobody was.", face="billy_panic", button="act natural"),
            self.sys_step("DAD", "Billy? Why is the desktop on fire?", kind="warn", icon="warn"),
        ]
        if self.suspicion >= 45:
            steps.append(self.sys_step("DAD", "Billy. Look at me.\nWhat. Did. You. Do.\n\n(Billy is sweating through his shirt.)", kind="error"))
            self.run_steps(steps, lambda: self.show_ending("grounded"))
        else:
            steps.append(self.billy_step("Dad. I was conducting international cybersecurity research.", face="billy_smug", button="research"))
            steps.append(self.sys_step("DAD", "...On my work computer.", kind="warn", icon="warn"))
            self.run_steps(steps, lambda: self.show_ending("hacker"))

    def final_cat(self):
        if "cat_evidence" in self.flags:
            self.run_steps([
                self.billy_step("It was Mr. Whiskers. He sits on the keyboard. Literally always.", face="billy_smug"),
                self.sys_step("DAD", "The cat?\n\n...Hm. Let me check cat_photos_(2300).zip.", kind="warn", icon="cat"),
            ], lambda: self.show_ending("cat"))
        else:
            self.run_steps([
                self.billy_step("It was the cat.", face="billy_smug"),
                self.sys_step("DAD", "We don't have a cat.", kind="error"),
                self.billy_step("...The goldfish?", face="billy_panic", button="please"),
            ], lambda: self.show_ending("grounded"))

    def final_monitor(self):
        def after_blackout():
            if self.fame >= 60:
                self.play("notify")
                self.run_steps([
                    self.sys_step("DAD'S PHONE", "4,821 notifications.\n\n'Your son just broke the internet.'", kind="warn", icon="warn"),
                    self.billy_step("...Wait, what?", face="billy_panic"),
                ], lambda: self.show_ending("billionaire"))
            else:
                self.run_steps([
                    self.sys_step("DAD", "Why is the monitor off?\n\n(Dad turns the monitor on.)", kind="warn", icon="warn"),
                ], lambda: self.show_ending("blue_screen"))

        self.show_card("...", "(the monitor is off)", after_blackout, color="void", duration=2.6, footer="Billy holds his breath.")


def main():
    root = tk.Tk()
    KidOS(root)
    root.mainloop()


if __name__ == "__main__":
    main()
