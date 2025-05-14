from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from game import Game, Commands

game = Game()

key_map = {
    123: Commands.ARROW_LEFT,
    124: Commands.ARROW_RIGHT,
    125: Commands.ARROW_DOWN,
    126: Commands.ARROW_UP,
    45: Commands.RESET,
    32: Commands.UNDO,
    48: Commands.TAB,
    49: Commands.SPACE,
    53: Commands.ESC,
}


def on_press(key):
    code = 0
    if isinstance(key, Key):
        code = key.value.vk
    elif isinstance(key, KeyCode):
        code = key.vk

    if code in key_map:
        game.on(key_map.get(code))


with keyboard.Listener(on_press=on_press) as listener:
    listener.join()
