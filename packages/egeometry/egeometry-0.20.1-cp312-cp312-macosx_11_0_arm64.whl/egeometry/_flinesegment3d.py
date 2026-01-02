# generated from codegen/templates/_linesegment3d.py

from __future__ import annotations

__all__ = ["FLineSegment3d"]

from emath import FVector3


class FLineSegment3d:
    __slots__ = ["_a", "_b"]

    def __init__(self, a: FVector3, b: FVector3):
        if a == b:
            raise ValueError("line segment points must be different")
        self._a = a
        self._b = b

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, FLineSegment3d):
            return False
        return self._a == other._a and self._b == other._b

    def __repr__(self) -> str:
        return f"<LineSegment3d a={self._a} b={self._b}>"

    @property
    def a(self) -> FVector3:
        return self._a

    @property
    def b(self) -> FVector3:
        return self._b

    @property
    def points(self) -> tuple[FVector3, FVector3]:
        return (self._a, self._b)

    @property
    def length(self) -> float:
        return (self._b - self._a).magnitude
