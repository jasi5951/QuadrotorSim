# Quadrotor Landing Game

A 2D drone landing game built with Python and Pygame.

## How to Play
- Use `Left` and `Right` arrows to control tilt.
- Use `W` and `S` to adjust thrust.
- The **top left** of the screen shows real-time game stats:
  - If the stats are **red**, then a landing on the pad **will not be safe**.
  - The **current difficulty** (`Normal` or `Hard`) is also shown here.
- The **bottom left** shows the **active control inputs** such as `Left`, `Right`, `W`, and `S`.

## Objective

The drone's goal is to **land safely on the red landing pad**.

A landing is considered **safe** only if the following conditions are met at the moment of contact:

- **Tilt angle** is within ±3 degrees.
- **Landing speed**, calculated as  
  $\sqrt{v_x^2 + v_y^2}$,  
  is **less than 15**.

If either of these conditions is not satisfied, the landing is **unsafe**, and the stats in the top left will be shown in **red**.

## Install
Make sure you have Python 3. Then run:
```bash
pip install -r requirements.txt
```

## Run Game
```bash
python3 main.py
```
Run the game 20 times. A `logs` folder will be created with game logs. **Do not** modify anything in this folder.

## Submit Your Logs
1. After playing the game 20 times, locate the `logs` folder.
2. Zip the `logs` folder.
3. Email the zipped file to Jasdeep at: [jasi5951@colorado.edu](mailto:jasi5951@colorado.edu).


