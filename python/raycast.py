from dataclasses import dataclass
import math
from pyunity import Vector3
from PIL import Image

@dataclass(frozen=True)
class RaycastHit:
    distance: float
    point: float
    normal: float

@dataclass(frozen=True)
class Line:
    a: Vector3
    b: Vector3

@dataclass(frozen=True)
class InfLine:
    point: Vector3
    direction: Vector3

    def crosses(self, other):
        # Check if on same plane
        ab = other.b - other.a
        ao = other.a - self.point

        # Coplanar
        perp = self.direction.cross(ab)
        if ao.dot(perp) != 0:
            return False

        # Parallel
        if perp.getLengthSqrd() == 0:
            return False

        # s multiples of ab, t is multiples of self.direction
        s = ao.cross(self.direction).dot(perp) / perp.getLengthSqrd()
        t = ao.cross(ab).dot(perp) / perp.getLengthSqrd()
        # point = self.point + t * self.direction

        # t has no upper bound
        return 0 <= s <= 1 and 0 <= t

@dataclass(frozen=True)
class Raycast:
    origin: Vector3
    direction: Vector3

    def intersects(self, other):
        if isinstance(other, Polygon):
            # Plane with point p0 normal n
            ab = other.points[1] - other.points[0]
            ac = other.points[2] - other.points[0]
            p0 = other.points[0]
            n = ab.cross(ac).normalized()

            denom = self.direction.dot(n)
            if abs(denom) < 1e-6:
                # Perpendicular to plane?
                return None
            t = (p0 - self.origin).dot(n) / denom
            if t < 0:
                # Facing other direction?
                return None

            # Point on plane in direction of line
            p = self.origin + self.direction * t

            # Arbitrary direction (first side)
            direction = n.cross(ab)
            testLine = InfLine(p, direction)
            intersections = 0
            for line in other.lines():
                if testLine.crosses(line):
                    intersections += 1
            # Odd number of crossings means point is inside line
            if intersections % 2 == 0:
                return None
            return RaycastHit(t, p, n)
        elif isinstance(other, Sphere):
            # Length on direction of line to nearest point
            length = self.direction.dot(other.center - self.origin)
            # Nearest point
            point = self.origin + length * self.direction
            distance = point.getDistSqrd(other.center)
            if not other.radius ** 2 >= distance:
                return None

            distSurface = math.sqrt(other.radius ** 2 - distance)
            realDist = length - distSurface
            realPoint = self.origin + realDist * self.direction
            normal = realPoint - other.center
            return RaycastHit(realDist, realPoint, normal)

@dataclass(frozen=True)
class Polygon:
    # Anticlockwise winding
    points: tuple

    def lines(self):
        for i in range(len(self.points)):
            if i == len(self.points) - 1:
                i = -1
            yield Line(self.points[i], self.points[i + 1])

@dataclass(frozen=True)
class Sphere:
    center: Vector3
    radius: float

def main():
    back = Polygon((
        Vector3(-10, 10, 10), Vector3(-10, -10, 10),
        Vector3(10, -10, 10), Vector3(10, 10, 10)))
    ceiling = Polygon((
        Vector3(-10, 10, 10), Vector3(10, 10, 10),
        Vector3(10, 10, -10), Vector3(-10, 10, -10)))
    floor = Polygon((
        Vector3(-10, -10, 10), Vector3(-10, -10, -10),
        Vector3(10, -10, -10), Vector3(10, -10, 10)))
    left = Polygon((
        Vector3(-10, 10, 10), Vector3(-10, 10, -10),
        Vector3(-10, -10, -10), Vector3(-10, -10, 10)))
    right = Polygon((
        Vector3(10, 10, 10), Vector3(10, -10, 10),
        Vector3(10, -10, -10), Vector3(10, 10, -10)))

    parts = [back, ceiling, floor, left, right]
    names = {
        back: "back",
        ceiling: "ceiling",
        floor: "floor",
        left: "left",
        right: "right",
    }
    colors = {
        back: [255, 0, 0],
        ceiling: [0, 255, 0],
        floor: [0, 0, 255],
        left: [255, 255, 0],
        right: [0, 255, 255],
    }

    camera = Vector3(0, 0, -10)
    fov = math.radians(120)

    def getDist(x):
        ray = Raycast(camera, direction)
        hit = ray.intersects(x)
        if hit is not None:
            return hit.distance, x
        return None, x

    import numpy as np
    img = np.zeros((100, 100, 3)).astype(np.uint8)
    for i in range(img.shape[0]):
        print("Row", i)
        for j in range(img.shape[1]):
            dx = ((j + 0.5) / img.shape[1] * 2 - 1)
            dy = ((i + 0.5) / img.shape[0] * 2 - 1)
            direction = Vector3(dx * 10, dy * 10, 7.5)

            distances = list(map(getDist, parts))
            for n in range(len(distances) - 1, -1, -1):
                if distances[n][0] is None:
                    distances.pop(n)
            distances.sort(key=lambda x: x[0])
            if len(distances):
                # print(names[distances[0][1]], direction)
                img[i, j] = colors[distances[0][1]]

    print("finished")

    Image.fromarray(img).show()

main()
