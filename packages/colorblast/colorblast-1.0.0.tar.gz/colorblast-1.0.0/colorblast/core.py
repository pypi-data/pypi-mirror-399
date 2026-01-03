import sys
import time
import random

class ColorBlast:
    COLORS = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "reset": "\033[0m"
    }

    STYLES = {
        "bold": "\033[1m",
        "italic": "\033[3m",
        "underline": "\033[4m",
        "blink": "\033[5m",
        "reverse": "\033[7m"
    }

    LOG_LEVELS = {
        "INFO": "blue",
        "WARNING": "yellow",
        "ERROR": "red",
        "SUCCESS": "green"
    }

    EMOJIS = {
        "info": "ℹ️",
        "warning": "⚠️",
        "error": "❌",
        "success": "✅",
        "star": "⭐",
        "fire": "🔥",
        "confetti": "🎉"
    }

    @staticmethod
    def _style_text(text, color=None, style=None):
        final_text = text
        if color in ColorBlast.COLORS:
            final_text = ColorBlast.COLORS[color] + final_text + ColorBlast.COLORS["reset"]
        if style in ColorBlast.STYLES:
            final_text = ColorBlast.STYLES[style] + final_text + ColorBlast.COLORS["reset"]
        return final_text

    @staticmethod
    def print(text, color=None, style=None, typing_speed=0, emoji=None, gradient=False):
        if emoji in ColorBlast.EMOJIS:
            text = f"{ColorBlast.EMOJIS[emoji]} {text}"

        if gradient:
            gradient_colors = ["red", "yellow", "green", "cyan", "blue", "magenta"]
            colored_text = ""
            for i, char in enumerate(text):
                colored_text += ColorBlast.COLORS[gradient_colors[i % len(gradient_colors)]] + char
            text = colored_text + ColorBlast.COLORS["reset"]

        final_text = ColorBlast._style_text(text, color, style) if not gradient else text

        if typing_speed > 0:
            for char in final_text:
                print(char, end="")
                sys.stdout.flush()
                time.sleep(typing_speed)
            print()
        else:
            print(final_text)

    @staticmethod
    def framed(text, border_char="*", padding=1, color=None, style=None):
        lines = text.split("\n")
        width = max(len(line) for line in lines) + padding*2
        border_line = border_char * (width + 2)
        print(ColorBlast._style_text(border_line, color, style))
        for line in lines:
            print(ColorBlast._style_text(f"{border_char}{' '*padding}{line}{' '*(width - len(line) - padding)}{border_char}", color, style))
        print(ColorBlast._style_text(border_line, color, style))

    @staticmethod
    def log(text, level="INFO", typing_speed=0):
        color = ColorBlast.LOG_LEVELS.get(level.upper(), "white")
        ColorBlast.print(f"[{level.upper()}] {text}", color=color, style="bold", typing_speed=typing_speed, emoji=level.lower())

    @staticmethod
    def animated(text, duration=2, style=None, color=None):
        end_time = time.time() + duration
        while time.time() < end_time:
            chars = ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*") for _ in range(len(text)))
            print(ColorBlast._style_text(chars, color, style), end="\r")
            time.sleep(0.05)
        print(ColorBlast._style_text(text, color, style))

    @staticmethod
    def confetti(text, count=50, duration=2):
        symbols = ["🎉", "✨", "⭐", "🔥", "💥"]
        end_time = time.time() + duration
        print(text)
        while time.time() < end_time:
            line = ''.join(random.choice(symbols + [" "]*5) for _ in range(60))
            print(line)
            time.sleep(0.05)

    @staticmethod
    def fireworks(text, duration=2):
        symbols = ["*", "+", "x", "o", "O"]
        end_time = time.time() + duration
        for _ in range(int(duration*10)):
            line = ''.join(random.choice(symbols + [" "] * 10) for _ in range(60))
            print(line)
            time.sleep(0.1)
        print(text)
