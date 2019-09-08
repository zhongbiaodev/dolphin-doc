"Base classes for geometrics related operations"
from typing import Generic, TypeVar

T = TypeVar('T')


class Rect(Generic[T]):
    '''Class to represent a rectangle.
    X-axis direction: from left to right.
    Y-axis direction: from top to bottom.

    T should be int or float.
    When T is int: right and bottom are inside the Rect.
    When T is float: right and bottom are on the edge.
    '''
    _x: T
    _y: T
    _w: T
    _h: T

    def __init__(self, x: T, y: T, w: T, h: T):
        if w <= 0:
            raise ValueError("|w| should be positive, got {}".format(w))
        if h <= 0:
            raise ValueError("|h| should be positive, got {}".format(h))
        self._x = x
        self._y = y
        self._w = w
        self._h = h

    def left(self) -> T:
        "Return left."
        return self._x

    def right(self) -> T:
        "Return right."
        if isinstance(self._x, int):
            return self._x+self._w-1
        return self._x+self._w

    def top(self) -> T:
        "Return top."
        return self._y

    def bottom(self) -> T:
        "Return bottom."
        if isinstance(self._x, int):
            return self._y+self._h-1
        return self._y+self._h

    def width(self) -> T:
        "Return width."
        return self._w

    def height(self) -> T:
        "Return height."
        return self._h

    def area(self) -> T:
        "Return the area."
        return self._w * self._h

    def contains(self, other: 'Rect[T]') -> bool:
        "Return whether a rect is inside the current rect."
        return self.left() <= other.left() \
            and self.right() >= other.right() \
            and self.top() <= other.top() \
            and self.bottom() >= other.bottom()

    def contains_point(self, x: T, y: T) -> bool:
        "Return whether a point is inside the current rect."
        return self.left() <= x <= self.right() \
            and self.top() <= y <= self.bottom()
