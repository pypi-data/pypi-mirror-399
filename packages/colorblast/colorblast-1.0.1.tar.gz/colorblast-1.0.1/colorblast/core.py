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
        "confetti": "🎉",
        "sparkle": "✨"
    }

    @staticmethod
    def _style_text(text, color=None, style=None):
        final = text
        if color in ColorBlast.COLORS:
            final = ColorBlast.COLORS[color] + final + ColorBlast.COLORS["reset"]
        if style in ColorBlast.STYLES:
            final = ColorBlast.STYLES[style] + final + ColorBlast.COLORS["reset"]
        return final

    @staticmethod
    def print(text, color=None, style=None, typing_speed=0, emoji=None, gradient=False, blink=False, reverse=False):
        if emoji in ColorBlast.EMOJIS:
            text = f"{ColorBlast.EMOJIS[emoji]} {text}"
        if gradient:
            gradient_colors = ["red","yellow","green","cyan","blue","magenta"]
            colored = ""
            for i, char in enumerate(text):
                colored += ColorBlast.COLORS[gradient_colors[i % len(gradient_colors)]] + char
            text = colored + ColorBlast.COLORS["reset"]
        if blink: style="blink"
        if reverse: style="reverse"
        final_text = ColorBlast._style_text(text, color, style) if not gradient else text
        if typing_speed>0:
            for c in final_text:
                print(c, end="")
                sys.stdout.flush()
                time.sleep(typing_speed)
            print()
        else:
            print(final_text)

    @staticmethod
    def framed(text, border_char="*", padding=1, color=None, style=None):
        lines = text.split("\n")
        width = max(len(l) for l in lines)+padding*2
        border = border_char*(width+2)
        print(ColorBlast._style_text(border,color,style))
        for l in lines:
            print(ColorBlast._style_text(f"{border_char}{' '*padding}{l}{' '*(width-len(l)-padding)}{border_char}",color,style))
        print(ColorBlast._style_text(border,color,style))

    @staticmethod
    def log(text, level="INFO", typing_speed=0):
        color = ColorBlast.LOG_LEVELS.get(level.upper(),"white")
        ColorBlast.print(f"[{level.upper()}] {text}", color=color, style="bold", typing_speed=typing_speed, emoji=level.lower())

    @staticmethod
    def animated(text, duration=2, style=None, color=None):
        end = time.time()+duration
        while time.time()<end:
            scramble = ''.join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*") for _ in range(len(text)))
            print(ColorBlast._style_text(scramble,color,style), end="\r")
            time.sleep(0.05)
        print(ColorBlast._style_text(text,color,style))

    @staticmethod
    def confetti(text, duration=2):
        symbols=["🎉","✨","⭐","🔥","💥"]
        end=time.time()+duration
        print(text)
        while time.time()<end:
            line = ''.join(random.choice(symbols+[" "]*5) for _ in range(60))
            print(line)
            time.sleep(0.05)

    @staticmethod
    def fireworks(text, duration=2):
        symbols=["*","+","x","o","O"]
        end=time.time()+duration
        for _ in range(int(duration*10)):
            line = ''.join(random.choice(symbols+[" "]*10) for _ in range(60))
            print(line)
            time.sleep(0.1)
        print(text)

    @staticmethod
    def marquee(text, width=50, speed=0.1, repeat=1):
        display = " "*width + text + " "*width
        for _ in range(repeat):
            for i in range(len(display)-width):
                print(display[i:i+width], end="\r")
                time.sleep(speed)
        print()

    @staticmethod
    def countdown(seconds, color=None, style=None):
        for i in range(seconds,0,-1):
            print(ColorBlast._style_text(str(i),color,style), end="\r")
            time.sleep(1)
        print("0")

    @staticmethod
    def sparkle(text, duration=2):
        symbols=["*","+","✦","✨","❇"]
        end=time.time()+duration
        for _ in range(int(duration*20)):
            line=''.join(random.choice(symbols+[" "]*5) for _ in range(len(text)+10))
            print(line, end="\r")
            time.sleep(0.05)
        print(text)

    @staticmethod
    def rainbow(text, speed=0.05, repeat=1):
        colors=["red","yellow","green","cyan","blue","magenta"]
        for _ in range(repeat):
            for i in range(len(text)):
                c=color=colors[i % len(colors)]
                ColorBlast.print(text[i], color=c, end="")
                time.sleep(speed)
            print()

    @staticmethod
    def progress_bar(total=20, duration=5, color="green"):
        for i in range(total+1):
            bar = "█"*i + "-"*(total-i)
            ColorBlast.print(f"[{bar}]", color=color, end="\r")
            time.sleep(duration/total)
        print()
