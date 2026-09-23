import random
from pathlib import Path

import pyglet
from pyglet import shapes

GIF_PATH = Path(__file__).parent / "ss.gif"

POWER_UP_LINES = [
    "IT'S OVER 9000!!!",
    "Kamehameha your bugs into the sun.",
    "I am Vegeta, Prince of all merge conflicts.",
    "Power level: undefined. Please initialize your variables.",
    "Fusion complete: your code and my code are now one.",
    "Senzu bean applied: -9999 stack traces.",
    "This isn't even my final commit!",
    "Warning: Ultra Instinct requires sudo.",
]

MARGIN = 16
GAP = 8
MESSAGE_HEIGHT = 44
BUTTON_WIDTH, BUTTON_HEIGHT = 200, 50

animation = pyglet.image.load_animation(str(GIF_PATH))
GIF_WIDTH, GIF_HEIGHT = animation.get_max_width(), animation.get_max_height()

WIDTH = GIF_WIDTH + 2 * MARGIN
HEIGHT = MARGIN + GIF_HEIGHT + GAP + MESSAGE_HEIGHT + GAP + BUTTON_HEIGHT + MARGIN

window = pyglet.window.Window(WIDTH, HEIGHT, caption="Dragon Ball Z Hackathon Test")
batch = pyglet.graphics.Batch()

gif_y = HEIGHT - MARGIN - GIF_HEIGHT
sprite = pyglet.sprite.Sprite(animation, x=MARGIN, y=gif_y, batch=batch)

message_top = gif_y - GAP
button_y = MARGIN
BUTTON_RECT = ((WIDTH - BUTTON_WIDTH) // 2, button_y, BUTTON_WIDTH, BUTTON_HEIGHT)

button_rect = shapes.Rectangle(*BUTTON_RECT, color=(255, 165, 0), batch=batch)
button_label = pyglet.text.Label(
    "POWER UP!",
    x=BUTTON_RECT[0] + BUTTON_RECT[2] // 2,
    y=BUTTON_RECT[1] + BUTTON_RECT[3] // 2,
    anchor_x="center",
    anchor_y="center",
    weight="bold",
    color=(0, 0, 0, 255),
    batch=batch,
)

message_label = pyglet.text.Label(
    "Press the button to power up!",
    x=WIDTH // 2,
    y=message_top,
    anchor_x="center",
    anchor_y="top",
    width=GIF_WIDTH,
    multiline=True,
    align="center",
    color=(255, 255, 255, 255),
    batch=batch,
)


@window.event
def on_draw():
    window.clear()
    batch.draw()


@window.event
def on_mouse_press(x, y, button, modifiers):
    bx, by, bw, bh = BUTTON_RECT
    if bx <= x <= bx + bw and by <= y <= by + bh:
        message_label.text = random.choice(POWER_UP_LINES)


def main():
    pyglet.app.run()


if __name__ == "__main__":
    main()
