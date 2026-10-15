# Rescue 911: Fire Truck Dino Rescue

A gentle platformer for Kellan (about age 4) and his dog Bernie. The bad dinos
took big sister Diana! Kellan the firefighter and Bernie jump, collect dinosaur
eggs, hose down fires and grumpy dinos, and drive the fire truck through five
places to rescue her. At the end, the fire truck raises its ladder, Diana climbs
down, and the dinos get their eggs back (they hatch!).

All the characters, art, levels and music are original. It's one self-contained
`index.html` with no build step. The only network request is the Press Start 2P
font from Google Fonts. Offline, the game uses a system font instead.

## How to play

| Action | Keyboard | Touch |
|--------|----------|-------|
| Walk | Left and Right arrows (or A and D) | ◀ ▶ |
| Jump (press again in the air for a water-jet double jump) | Space, Z or Up | JUMP |
| Spray the hose | X, C or F | SPRAY |
| Pause | P or Esc | II |
| Music and sound | M | ♪ |
| Voice | V | TALK |

- **Dino eggs.** Find enough eggs, then touch the fire truck at the end. The egg
  counter at the bottom turns green when you have enough. If you reach the
  truck too soon, Bernie barks and an arrow points to the nearest egg.
- **Fires.** Spray them with the hose or jump over them.
- **Bad dinos.** Spray them or jump on them, and they sneeze and run away.
- **Fire hydrants** bounce you up to high eggs.
- **Bones** are treats for Bernie. He barks "WOOF!"
- **Pits.** Fall in and Bernie's bubble carries you back to the last red flag.
- **Big Grumpasaur** (level 5) is too hot and grumpy. Spray him (or bounce on
  his head) until the GRUMPY meter cools down.

Each level gives up to 3 stars: one for the rescue, one for all 8 eggs, and one
for putting out every fire.

## Levels

1. Dino Meadow
2. Volcano Valley (fires and lava pits)
3. Jungle Swamp (hydrant bounces)
4. Dino Town
5. Grumpy Volcano (Big Grumpasaur, then the ladder rescue)

## Difficulty

The game always opens on EASY. Pick MEDIUM or HARD on the title screen.

| | Easy | Medium | Hard |
|---|---|---|---|
| Eggs needed per level | 4 of 8 | 6 of 8 | all 8 |
| Bumps and pits | just a little push back | lose a heart (3 hearts, then Bernie's bubble) | same as medium |
| Double jump | yes | yes | no |
| Hold JUMP to float down | yes | no | no |
| Stepping stones in pits | yes | no | no |
| Dinos | fewer and slower | more | most and fastest |
| Big Grumpasaur | cools off quickly | takes longer | takes longest, hops when he roars |

Nobody can really lose on any level. Running out of hearts just puts you back
at the last flag.

## Put it on an Android phone (works offline)

1. In this repository: Settings → Pages → Deploy from a branch → `main` → `/ (root)`.
2. On the phone, open `https://tazardous.github.io/rescue911/` in Chrome while online.
3. Wait for it to load once. Then use ⋮ → **Install app** (or **Add to Home screen**).

The app opens full screen in landscape and runs with no internet after that.

## Updating

Edit the files, change `CACHE` in `sw.js` (for example `r911-v2`), then push. The
next time the phone opens the game online, it picks up the new version.

## Making levels

Levels are in `LEVELS` near the top of `index.html`: width in tiles, pits
(`[x, width]`, 3 wide at most), platforms (`[x0, x1, row]`), eggs and bones
(`[x, row]`), dinos (`[x, 'raptor' | 'trike' | 'ptero', lowest difficulty]`),
fires, hydrants (`springs`) and checkpoint flags. The ground is row 8. Difficulty
settings are in `DIFF`.

## Testing

`tests/run.py` uses headless Chromium. It checks that every egg and bone can be
reached with HARD-mode jumping. Then it plays all 5 levels on all 3
difficulties, tests pit recovery and the finale, and runs a real-time keyboard
session. `tests/shots.py <folder>` saves a screenshot of every screen.

```
pip install playwright
python -m playwright install chromium
python tests/run.py
```
