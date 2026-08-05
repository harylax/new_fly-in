*This project has been created as part of the 42 curriculum by haryandr.*

# Fly-in

**Drones are interesting.**

A multi-drone routing simulation that efficiently navigates a fleet of drones from a start hub to an end hub through a network of zones, while respecting capacity constraints, zone types, and movement costs.

## Description

Fly-in is a turn-based drone simulation system designed as part of the 42 curriculum. The goal is to move a fleet of drones from a central base (`start_hub`) to a target location (`end_hub`) in the fewest possible simulation turns.

The network is modeled as a directed graph of interconnected zones (hubs) with the following features:

- **Zone types** with different movement costs:
  - `normal` — 1 turn (default)
  - `restricted` — 2 turns (drones occupy the connection during transit)
  - `priority` — 1 turn (preferred in path ranking)
  - `blocked` — inaccessible
- **Capacity constraints**:
  - Per-zone maximum occupancy (`max_drones`)
  - Per-connection maximum concurrent drones (`max_link_capacity`)
- Special rules for the start and end hubs (unlimited capacity)
- Simultaneous multi-drone movement with conflict avoidance

The project is fully object-oriented, type-safe (mypy + flake8), and provides both a rich terminal interface and a graphical pygame animation.

## Features

- Custom map parser with strict validation and clear error messages
- Pathfinding via reverse BFS (unreachable detection) + DFS (all simple paths enumeration)
- Path ranking by total cost (priority < normal < restricted)
- Turn-based simulation engine that respects capacities and restricted-zone transit rules
- Interactive terminal menu with difficulty selection and custom map support
- Colored terminal output of the simulation
- Graphical viewer (pygame) with:
  - Scrollable city background
  - Animated drone sprites moving between hubs
  - Turn counter and pause/restart controls
- Makefile with `install`, `run`, `debug`, `clean`, `fclean`, `lint`, and `lint-strict` targets

## Algorithm Choices and Implementation Strategy

### Pathfinding Algorithms

1. **Reverse BFS** starting from the end hub marks every hub that cannot reach the goal. Blocked zones and dead-ends are eliminated early.
2. **DFS** from the start hub enumerates all simple (cycle-free) paths, pruning any branch that leads to a previously marked unreachable or blocked hub.
3. Paths are sorted by ascending total cost. The cost of a path is the sum of the individual hub costs (`priority` = 0.5, `normal` = 1, `restricted` = 2). This ordering prefers short, high-priority routes.

### Simulation Engine Strategy

The solver advances turn by turn until every drone has arrived at the end hub:

1. Drones currently in transit on restricted connections are collected and will be released at the very end of the turn, after other free drones shift, to ensure they do not move twice a turn.
2. Free drones are moved along the first fifteen ranked paths (cheapest first). For each edge of a path the engine tries to push as many eligible drones as capacity allows (both hub and link capacities are checked).
3. Capacity is freed immediately when a drone leaves a hub, allowing other drones to enter the same hub on the same turn.
4. A snapshot of every drone’s position is recorded after each turn for later visualization and textual output.

The strategy deliberately limits the number of considered paths (`paths[:15]`) to keep the per-turn complexity manageable while still exploring the most promising routes. Waiting is implicit: if no capacity is available a drone simply stays in place until a later turn.

## Visual Representation

### Terminal

- Colored ASCII banners and menus
- Step-by-step movement log following the required format (`D<id>-<zone>`)
- Colored zone highlighting

### Graphical (pygame)

- Static map layer drawn on a panoramic city skyline background
- Hubs rendered as colored circles with zone-type initials (S/G/B/N/R/P)
- Connections drawn as thin lines
- Drone sprites animated smoothly between consecutive positions
- Stacked drones on the same hub are offset for visibility
- Keyboard controls:
  - Arrow keys — pan the camera
  - Space — pause / resume
  - R — restart animation
  - Escape — quit
- Live turn counter and pause indicator

### User Experience

- Static hubs are drawn at their map coordinates with their names, labels and color to distinguish start, normal, restricted, blocked and priority zones.
- Connections are drawn between hubs, making all possible drone routes immediately visible.
- A panoramic background can be scrolled using keyboards arrows key, allowing comfortable visualization of maps larger than the window.
- Drones move smoothly along connections, making each simulation turn easy to follow.
- Drones occupying the same hub are rendered with a small positional offset so that every drone remains visible during congestion.
- The current simulation turn is permanently displayed, allowing users to monitor the progression of the solver.
- The interface displays whether the animation is currently paused or running, providing immediate visual feedback.
- The animation can be paused and resume with **Space** key, enabling detailed inspection of drone movements.
- Pressing **R** restarts the animation from the beginning without rerunning the simulation, making it easy to replay and analyze the routing strategy.
- The graphical viewer greatly improves understanding of congestion points, capacity bottlenecks, restricted-zone delays, and the overall routing strategy.

## Instructions

### Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt` (pygame, pydantic, flake8, mypy, flake8-docstrings)

### Installation

```bash
make install
```

This creates a virtual environment (`.venv`) and installs all dependencies.

### Running the simulation

```bash
make run
```

An interactive menu appears:

1. Run the default map
2. Choose a map by difficulty (easy / medium / hard / challenger)
3. Supply a custom map path
4. Quit

You can optionally launch the graphical animation.

### Debug mode

```bash
make debug
```

Runs the program under `pdb`.

### Linting

```bash
make lint          # flake8 + mypy with the required flags
make lint-strict   # same with mypy --strict
```

### Cleaning

```bash
make clean         # remove __pycache__ and .mypy_cache
make fclean        # also remove the virtual environment
```

### Map format

Custom maps can be placed anywhere and selected via the menu.
Example:
```text
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 3 0 [color=yellow]
hub: roof1 1 0 [zone=restricted color=red]
hub: roof2 2 0 [zone=normal color=blue]
hub: corridorA 1 -1 [zone=priority color=green max_drones=2]
hub: tunnelB 2 -1 [zone=normal color=red]
hub: obstacleX 1 1 [zone=blocked color=gray]
connection: hub-roof1
connection: hub-corridorA
connection: roof1-roof2
connection: roof2-goal
connection: corridorA-tunnelB [max_link_capacity=2]
connection: tunnelB-goal
```

### Output format

```bash
turn 1: D1-corridorA D2-hub-roof1
turn 2: D1-tunnelB D2-roof1 D3-corridorA
turn 3: D1-goal D2-roof2 D3-tunnelB D4-corridorA D5-hub-roof1
turn 4: D2-goal D3-goal D4-tunnelB D5-roof1
turn 5: D4-goal D5-roof2
turn 6: D5-goal
```

## Resources

### Classic references

- Pygame tutorials: https://www.youtube.com/watch?v=AY9MnQ4x3zk
- Dijkstra algorithm: https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm
- Depth-first search algorithm: https://en.wikipedia.org/wiki/Depth-first_search
- Breadth-first search algorithm: https://en.wikipedia.org/wiki/Breadth-first_search
- Pygame documentation: https://www.pygame.org/docs/tut/PygameIntro.html
- Python docs about enum, using @propriety with Enum: https://docs.python.org/3/howto/enum.html

### AI usage

AI assistants were used for the following tasks:

- Rapid prototyping of the interactive terminal menu layout and ASCII art
- Drafting of docstrings following PEP 257
- Exploration of alternative path-ranking algorithms
- Debugging of edge-case of hub capacity overflowing 
- Review of parser robustness
- Generation of the images assets (night_city_skyline background, drone)

## Project Structure

```
.
├── Makefile
├── README.md
├── default_map.txt         # Default maps for tests
├── maps.tar.gz				      # Compressed archive of maps files
├── main.py                 # Entry point
├── model.py                # Pydantic models
├── mypy.ini                # Config mypy to activate pydantic plugin
├── network.py              # Runtime graph (Hub, Connection, Drone)
├── parser.py               # Map file parser
├── pathfinder.py           # BFS + DFS path discovery & ranking
├── requirements.txt        # Dependencies needed
├── simulation.py           # Turn-based multi-drone solver
├── terminal.py             # Interactive menu & textual output
├── utils.py                # Shared helpers & ANSI colors
├── visual.py               # Pygame static map + animation
├── drone-isometric-facing-right.png
└── night_city_skyline_3600x800.png
```

## Author

- **haryandr** — 42 student
