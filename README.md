KID_OS 

A chaotic childhood adventure on Dad's computer.

KID_OS (Kid Experience on CLI) is a short, comedic narrative game about an eight-year-old kid who gets access to his dad's computer and decides to look for free games, cheat codes, and Robux.

What could possibly go wrong?

Built with Python, KID_OS combines a retro-inspired desktop interface, interactive storytelling, absurd internet humor, and procedurally generated audio into a small standalone game.

 About the Game

Dad is leaving for ten minutes. Billy sees an opportunity.

With unrestricted access to the family computer, he begins exploring the digital world in search of free games, cheats, and virtual currency. Every action can lead to unexpected consequences, increasingly chaotic situations, and hilarious endings.

Your mission is simple: explore, click, and see how badly things can go.

 Features

- Interactive desktop interface — Explore a fictional computer environment through a custom graphical interface.
- Branching narrative — Your actions influence how Billy's story unfolds.
- Five unique endings — Discover different outcomes, including the Blue Screen, Professional Hacker, Robux Billionaire, Secret Cat, and Grounded endings.
- Retro computer aesthetics — Experience a playful desktop inspired by old-school computers and internet culture.
- Procedurally generated music — Audio tracks are synthesized directly in Python using mathematical waveforms and different musical moods.
- Dynamic visual effects — Experience digital chaos, system errors, and unexpected visual surprises.
- Standalone Windows build — A packaged executable is included in the project's distribution files.

 Built With

- Python — Core game logic and audio generation.
- Tkinter — Graphical user interface and interactive canvas.
- Python "wave" module — WAV audio generation.
- PyInstaller — Packaging the Python application into a Windows executable.

The game uses Python's standard library for its core functionality.

 Getting Started

Option 1: Run the game

Download or clone this repository and look for the packaged application in the "dist" directory.

If a compatible executable is available, run it on Windows.

«Note: Windows SmartScreen or antivirus software may occasionally flag packaged Python executables. Only run builds you trust.»

Option 2: Run from source

Requirements

- Python 3.10 or newer recommended.
- Tkinter support.
- Windows is the primary target for the packaged build.

1. Clone the repository:
   
   git clone https://github.com/FreakPuppyGameStudio/kidos-kidoncli.git

2. Navigate to the project directory:
   
   cd kidos-kidoncli

3. Run the game:
   
   python kid_os.py

If your system uses "python3" instead of "python", run:

python3 kid_os.py

No separate package installation should be necessary for the core game when Python is installed with Tkinter support.

 Project Structure

kidos-kidoncli/
├── build/
│   └── KID_OS/
├── dist/
├── kid_os.py
└── KID_OS.spec

File / Directory| Description
"kid_os.py"| Main game source code, interface, narrative, and audio generation.
"KID_OS.spec"| PyInstaller build configuration.
"build/"| Intermediate packaging files.
"dist/"| Distribution output for the packaged application.

 Procedural Audio

KID_OS generates its music programmatically instead of relying entirely on prerecorded tracks.

The audio system combines mathematical waveforms, note frequencies, chord progressions, timing, and volume envelopes to create different musical moods.

The soundtrack includes three modes:

- Calm — A slower, more relaxed atmosphere.
- Tense — Faster music to increase suspense.
- Chaos — High-energy music for the game's most chaotic moments.

The generated audio is written to WAV format using Python's built-in audio utilities.

🏁 Endings

There are five endings to discover:

1. The Blue Screen Ending — Billy's attempt to fix the computer goes exactly as expected.
2. The Professional Hacker Ending — Billy discovers his future in cybersecurity.
3. The Robux Billionaire Ending — An internet adventure becomes an absurd success story.
4. The Cat Did It — The real culprit might have paws.
5. The Grounded Ending — Dad discovers what happened.

Can you unlock all five?

 Development

KID_OS was created as a game jam project, with a focus on building a complete, playable experience under a limited development schedule.

The project explores:

- Rapid prototyping with Python.
- GUI development without a traditional game engine.
- Narrative design and multiple endings.
- Procedural sound synthesis.
- Packaging and distributing a desktop application.

 Credits

Created by Santiago Morales Itzcoatl(JaqueSorina)

Developed under Sorina Crew by DXGPANIC Studios.

This project was created for a game jam.

License

No license has been specified in this README. Please check the repository for licensing information before reusing, modifying, or redistributing the source code or assets.

---

Dad said not to touch anything important.

Billy understood the assignment.
