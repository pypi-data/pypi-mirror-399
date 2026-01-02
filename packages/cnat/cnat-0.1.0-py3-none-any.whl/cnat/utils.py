from tuikit.textools import transmit, style_text, wrap_text


def warning(msg: str) -> None:
    prefix = "[cnat] "
    print(style_text(prefix, "cyan"), end="")
    msg = wrap_text(msg, 7, inline=True, order=prefix)
    transmit(msg, speed=0.01, hold=0.025, hue="red")
