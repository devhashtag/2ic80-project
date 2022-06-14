from .enums import Direction
from math import cos, sin, pi
from PyQt6.QtGui import QPainter

def draw_arrow(painter, length, rotation=0.0, origin=(0,0), direction=Direction.FORWARDS):
    """
    Draws a horizontal arrow with the given QPainter object.

    Anti-aliasing is on only if the line is not straight, because
    it does not work well on straight lines. The function can
    probably be turned into a recursive one, but I can't be
    bothered to change it.
    """
    def draw_line(x0, y0, x1, y1):
        """
        Draws a line.

        Anti-aliasing will be used only if the line is not straight.
        """
        if x0 == x1 or y0 == y1:
            painter.drawLine(x0, y0, x1, y1)
        else:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            painter.drawLine(x0, y0, x1, y1)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
    x, y = origin
    rotation = -rotation
    ltr = direction == Direction.FORWARDS or direction == Direction.BOTH
    rtl = direction == Direction.BACKWARDS or direction == Direction.BOTH

    x_end = x + length * cos(rotation)
    y_end = y + length * sin(rotation)

    draw_line(x, y, round(x_end), round(y_end))

    if ltr:
        x_bot = x_end + 7 * cos(rotation - pi*3/4)
        y_bot = y_end + 7 * sin(rotation - pi*3/4)

        x_top = x_end + 7 * cos(rotation + pi*3/4)
        y_top = y_end + 7 * sin(rotation + pi*3/4)

        draw_line(round(x_end), round(y_end), round(x_bot), round(y_bot))
        draw_line(round(x_end), round(y_end), round(x_top), round(y_top))

    if rtl:
        x_bot = x + 7 * cos(rotation - pi/4)
        y_bot = y + 7 * sin(rotation - pi/4)

        x_top = x + 7 * cos(rotation + pi/4)
        y_top = y + 7 * sin(rotation + pi/4)

        draw_line(x, y, round(x_bot), round(y_bot))
        draw_line(x, y, round(x_top), round(y_top))

def ip_to_int(ip: str):
    total = 0

    for el in ip.split('.'):
        total = total * 2**8 + int(el)

    return total