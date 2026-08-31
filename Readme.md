*This project has been created as part of the 42 curriculum by ymouafak.*

# Fly-in — Drone Routing Simulator

## Description

Fly-in routes a fleet of autonomous drones from a shared start zone to a
shared end zone through a network of connected zones, while respecting
per-zone and per-connection capacity limits. The goal is to move every
drone from start to end in as few simulation turns as possible, without
ever letting two drones collide in the same zone or on the same
connection beyond what its capacity allows.

The project is split into four stages that mirror the pipeline in
`main.py`:

1. **Parsing** (`parsing.py`) — reads a custom map file format
   describing zones and their connections, validating every field
   against the spec (zone types, coordinates, capacities, colors).
2. **Graph construction** (`structure.py`) — builds an adjacency list
   from the parsed zones and connections.
3. **Pathfinding** (`algo.py`) — searches the graph for one or more
   distinct low-cost paths from start to end.
4. **Simulation** (`simulation.py`) — assigns each drone a path and
   steps through turns, enforcing zone and connection capacity so no
   two drones ever violate the network's limits.

## Instructions

The project ships with a `Makefile` that wraps the common tasks:

| Command | What it does |
|---|---|
| `make install` | Installs the project's Python dependencies. |
| `make run` | Runs the simulation (see below for arguments). |
| `make debug` | Runs the simulation under Python's built-in debugger (`pdb`). |
| `make lint` | Runs `flake8` and `mypy` with the required flags. |
| `make lint-strict` | Runs `flake8` and `mypy --strict`. |
| `make clean` | Removes `__pycache__` and `.mypy_cache`. |

The program takes exactly one argument: the path to a map file.

```bash
python3 main.py maps/easy/01_linear_path.txt
```

If the map is malformed, or the end zone isn't reachable from the start
zone, the program prints a clear error message and exits with a
non-zero status instead of crashing.

### Map file format

A map file declares the number of drones, a start zone, an end zone,
any number of intermediate zones (`hub`), and the connections between
them:

```
nb_drones: 2
start_hub: A 0 0 [color=green]
hub: B 1 0
hub: C 2 0 [zone=restricted color=red]
end_hub: D 3 0 [color=yellow]

connection: A-B
connection: B-C
connection: C-D [max_link_capacity=1]
```

Zone metadata (`zone`, `max_drones`, `color`) is optional and defaults
to `normal`, `1`, and `white` respectively. See `parsing.py` for the
full grammar and validation rules.

## Algorithm choices and implementation strategy

**Graph representation.** Every zone is parsed once into a `Zone`
object and reused everywhere it's referenced, so the adjacency list
built by `Graph.build_list()` maps each `Zone` directly to its neighbor
`Zone` objects rather than to names — this avoids repeated dictionary
lookups throughout pathfinding and simulation.

**Pathfinding.** `Algo.custom_dijkstra()` is a Dijkstra-style search
over a min-heap of `(cost, is_priority, insertion_order, zone)` tuples.
The cost to move into a zone comes from the zone's own type (1 turn for
`normal`/`priority`, 2 turns for `restricted`), not from the connection
used to reach it, since the spec ties movement cost to the destination
zone rather than the link. `is_priority()` acts as a tie-breaker so
that, among equally-cheap options, `priority` zones are preferred, as
required by the spec.

To find more than one distinct path (so different drones don't all
pile onto the exact same route), each zone carries a small `usage`
counter that increments slightly every time a found path passes
through it. Re-running the search afterward makes previously-used
zones marginally less attractive, nudging the algorithm toward a
different route on the next call. `get_paths()` repeats this until a
path repeats or no further path is found.

**Turn-based simulation with capacity.** `Simulation` replays every
drone's assigned path one hop per turn. Before a drone is allowed to
move, `is_movable()` checks the destination zone's remaining capacity
and the connecting link's remaining capacity for the turn(s) the move
would take. A move into a `restricted` zone takes two turns; the spec
requires that once a drone commits to that transit it cannot wait
partway through, so `is_movable()` reserves both turns atomically
before the drone is marked as mid-transit (`in_connection`), and the
drone is skipped entirely by the capacity checks until it lands. If a
move isn't currently possible, the drone simply waits one turn and
retries, which is what naturally produces different arrival times for
drones queued behind a busy zone or connection.

Drones are distributed across the collected candidate paths
round-robin, respecting each path's bottleneck capacity
(`Algo.get_max()`, the smaller of the connection's and destination
zone's limits), so drones aren't all funneled onto a single route when
alternatives exist.

## Visual representation

Simulation output is printed live, one line per turn, using
[`rich`](https://github.com/Textualize/rich) markup to color each
zone's name as it's printed. A zone's color comes from its `color`
metadata in the map file (validated and normalized to a hex code by
`webcolors` during parsing, defaulting to white for unrecognized
names). A zone with `color=rainbow` is rendered with each character of
its name in a different color from a rotating palette, cycling through
the rainbow as the name is printed.

This makes it possible to visually track, at a glance, which kind of
zone each drone is moving through turn by turn — for example, spotting
a `restricted` zone rendered in red, or a `priority` corridor rendered
in green — without cross-referencing the map file while reading the
simulation log.

## Example

Given the map shown above (`nb_drones: 2`, `A → B → C → D`, with `C`
restricted and the `C-D` connection limited to one drone at a time),
running:

```bash
python3 main.py maps/easy/01_linear_path.txt
```

produces output along these lines (colors are rendered in the actual
terminal output, shown here as plain text):

```
D1-B
D1-A-C D2-B
D1-C
D1-D D2-A-C
D2-C
D2-D
```

Drone 1 reaches `B` on turn 1, then begins its two-turn transit into
the restricted zone `C` (shown as `D1-A-C`, departing from `A`),
landing on turn 3 and reaching the end zone `D` on turn 4. Drone 2
follows one step behind, only starting its own transit into `C` once
the `C-D` connection has freed up, since its capacity is limited to a
single drone at a time.

## Resources

- [Graphs / Dijkstra's algorithm](https://youtu.be/09FIEpuNpvY?si=Cuc-ysufMTepBCEE)

### AI usage
- explanation of the custom Dijkstra algo
- fixing type hints
