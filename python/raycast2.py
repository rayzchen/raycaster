import sys
USE_PG = sys.platform == "win32"
SOFT_SHADOWS = False

from dataclasses import dataclass
import threading
from PIL import Image
import time
import glm
import numpy as np
if USE_PG:
    import pygame
    import pygame.gfxdraw

class Shape:
    pass

@dataclass(frozen=True)
class RaycastHit:
    object: Shape
    distance: float
    point: glm.vec3
    normal: glm.vec3

@dataclass(frozen=True)
class Line:
    a: glm.vec3
    b: glm.vec3

@dataclass(frozen=True)
class InfLine:
    point: glm.vec3
    direction: glm.vec3

    def crosses(self, other):
        # Check if on same plane
        ab = other.b - other.a
        ao = other.a - self.point

        # Coplanar
        perp = glm.cross(self.direction, ab)
        # TODO: should be coplanar anyways, is this check needed?
        # Causes artifacts on edges, no idea why
        # if glm.dot(ao, perp) != 0:
        #     return False

        # Parallel
        denom = glm.dot(perp, perp)
        if denom == 0:
            return False

        # s multiples of ab, t is multiples of self.direction
        s = glm.dot(glm.cross(ao, self.direction), perp) / denom
        t = glm.dot(glm.cross(ao, ab), perp) / denom
        # point = self.point + t * self.direction

        # t has no upper bound
        return 0 <= s <= 1 and 0 <= t

@dataclass(init=False, unsafe_hash=True)
class Raycast:
    origin: glm.vec3
    direction: glm.vec3

    def __init__(self, origin, direction, norm=True):
        self.origin = origin
        if norm:
            self.direction = glm.normalize(direction)
        else:
            self.direction = direction

    def intersects(self, other):
        if isinstance(other, Polygon):
            # Plane with point p0 normal n
            ab = other.points[1] - other.points[0]
            p0 = other.points[0]

            denom = glm.dot(self.direction, other.normal)
            if abs(denom) < 1e-10:
                # Perpendicular to plane?
                return None
            t = glm.dot(p0 - self.origin, other.normal) / denom
            if t < 0:
                # Facing other direction?
                return None

            # Point on plane in direction of line
            p = self.origin + self.direction * t

            # Arbitrary direction (first side)
            direction = glm.cross(other.normal, ab)
            testLine = InfLine(p, direction)
            intersections = 0
            for line in other.lines:
                if testLine.crosses(line):
                    intersections += 1
            # Odd number of crossings means point is inside line
            if intersections % 2 == 0:
                return None
            return RaycastHit(other, t, p, other.normal)
        elif isinstance(other, Sphere):
            # Length on direction of line to nearest point
            length = glm.dot(self.direction, other.center - self.origin)
            # Only for unnormalized
            # length /= glm.dot(self.direction, self.direction)
            # Nearest point
            point = self.origin + length * self.direction
            distance = glm.distance2(point, other.center)
            if other.radius ** 2 < distance:
                return None

            distSurface = glm.sqrt(other.radius ** 2 - distance)
            realDist = length - distSurface
            realPoint = self.origin + realDist * self.direction
            normal = glm.normalize(realPoint - other.center)
            return RaycastHit(other, realDist, realPoint, normal)

@dataclass(init=False, unsafe_hash=True)
class Polygon(Shape):
    # Anticlockwise winding
    points: tuple

    def __init__(self, points):
        self.points = points

        ab = points[1] - points[0]
        ac = points[2] - points[0]
        self.normal = glm.normalize(glm.cross(ac, ab))

        self.lines = []
        for i in range(len(self.points)):
            if i == len(self.points) - 1:
                i = -1
            self.lines.append(Line(self.points[i], self.points[i + 1]))

@dataclass(frozen=True)
class Sphere(Shape):
    center: glm.vec3
    radius: float

@dataclass(unsafe_hash=True, init=False)
class Light:
    position: glm.vec3
    strength: float
    distance: float
    size: float

    def __init__(self, position, strength, distance, size):
        self.position = position
        self.strength = strength
        self.distance = distance
        self.size = size

        self.constant = 1
        # self.linear = -0.005566 + 4.833511 / distance
        self.linear = 4.690508 * distance ** -1.009712
        self.quadratic = 82.444779 * distance ** -2.019206

    def getAttenuation(self, distance):
        return 1 / (self.constant + (self.quadratic * distance +
            self.linear) * distance)

def main():
    back = Polygon((
        glm.vec3(-10, 10, 10), glm.vec3(-10, -10, 10),
        glm.vec3(10, -10, 10), glm.vec3(10, 10, 10)))
    ceiling = Polygon((
        glm.vec3(-10, 10, 10), glm.vec3(10, 10, 10),
        glm.vec3(10, 10, -10), glm.vec3(-10, 10, -10)))
    floor = Polygon((
        glm.vec3(-10, -10, 10), glm.vec3(-10, -10, -10),
        glm.vec3(10, -10, -10), glm.vec3(10, -10, 10)))
    left = Polygon((
        glm.vec3(-10, 10, 10), glm.vec3(-10, 10, -10),
        glm.vec3(-10, -10, -10), glm.vec3(-10, -10, 10)))
    right = Polygon((
        glm.vec3(10, 10, 10), glm.vec3(10, -10, 10),
        glm.vec3(10, -10, -10), glm.vec3(10, 10, -10)))

    sphere = Sphere(glm.vec3(4, -5, 8), 5)
    sphere2 = Sphere(glm.vec3(-4, -5, 5), 5)

    parts = [back, ceiling, floor, left, right, sphere, sphere2]
    colors = {
        back: np.array([255, 0, 0]),
        ceiling: np.array([0, 255, 0]),
        floor: np.array([0, 0, 255]),
        left: np.array([255, 255, 0]),
        right: np.array([0, 255, 255]),
        sphere: np.array([200, 200, 200]),
        sphere2: np.array([127, 127, 127]),
    }

    camera = glm.vec3(0, 0, -10)
    light = Light(glm.vec3(0, 7.5, 0), 1, 750, 20)
    print(light.linear, light.quadratic)
    fov = glm.radians(90)
    scale = glm.tan(fov / 2)

    def getHits(ray):
        distances = []
        for obj in parts:
            hit = ray.intersects(obj)
            if hit is not None:
                distances.append(hit)
        distances.sort(key=lambda x: x.distance)
        if len(distances) == 0:
            return None
        return distances[0]

    size = (200, 200)
    if USE_PG:
        screen = pygame.display.set_mode(size)
    start = time.perf_counter()
    img = np.zeros((*size, 3)).astype(np.uint32)
    valueBuffer = np.zeros(size)
    occlusionBuffer = np.zeros(size)
    diffuseBuffer = np.zeros(size)
    posBuffer = np.zeros((*size, 3))
    for i in range(size[0]):
        for j in range(size[1]):
            dx = ((j + 0.5) / size[1] * 2 - 1)
            dy = ((i + 0.5) / size[0] * 2 - 1)
            direction = glm.vec3(dx * scale, dy * scale, 1)
            ray = Raycast(camera, direction)
            pos = (size[0] - i - 1, j)

            hit = getHits(ray)
            if hit is None:
                continue

            ambient = 0.1
            lightDir = glm.normalize(light.position - hit.point)
            alongNormal = glm.dot(hit.normal, lightDir)
            diffuse = max(alongNormal, 0.0) * light.strength

            shadowRay = Raycast(light.position, hit.point - light.position)
            shadowHit = getHits(shadowRay)
            if shadowHit is not None and shadowHit.object is not hit.object:
                value = shadowHit.distance / hit.distance
                occlusionBuffer[pos] = value
            elif alongNormal < 0:
                # Don't add shadows on edges of underside of object
                occlusionBuffer[pos] = 0
            else:
                occlusionBuffer[pos] = 1.0

            # viewDir = glm.normalize(camera - hit.point)
            # halfwayDir = glm.normalize(lightDir + viewDir)
            # specular = max(glm.dot(hit.normal, halfwayDir), 0.0) ** 32
            specular = 0
            attenuation = light.getAttenuation(hit.distance)

            valueBuffer[pos] = (ambient + specular) * attenuation
            diffuseBuffer[pos] = diffuse
            posBuffer[pos] = np.array(hit.point)
            img[pos] = colors[hit.object]
            if USE_PG:
                pygame.gfxdraw.pixel(screen, pos[1], pos[0], colors[hit.object])

        if USE_PG:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            pygame.display.flip()

    for i in range(size[0]):
        for j in range(size[1]):
            pos = (size[0] - i - 1, j)
            if (SOFT_SHADOWS and occlusionBuffer[pos] != 1.0 and
                    diffuseBuffer[pos] > 0.1):
                broken = True
                while True:
                    # Penumbra
                    sampleSize = (1 - occlusionBuffer[pos]) * light.size
                    sampleSize /= posBuffer[pos][2]
                    # Must be odd number
                    sampleSize = int(glm.floor(sampleSize))
                    sampleSize += 1 - sampleSize % 2
                    extra = sampleSize // 2
                    if extra == 0:
                        # Not near edge of shadow
                        break

                    minX, maxX = pos[0] - extra, pos[0] + extra
                    minY, maxY = pos[1] - extra, pos[1] + extra

                    if 1 not in occlusionBuffer[minX:maxX+1, minY:maxY+1]:
                        # No nearby unshaded pixels
                        break

                    # Find nearest unshaded pixel
                    bestIndex = (0, 0)
                    bestSample = float("inf")
                    for y in range(pos[0] - extra, pos[0] + extra + 1):
                        for x in range(pos[1] - extra, pos[1] + extra + 1):
                            # Bounds check
                            if (y < 0 or y > size[0] - 1 or
                                    x < 0 or x > size[1] - 1):
                                continue
                            if occlusionBuffer[y, x] != 1.0:
                                continue

                            offset = (y - pos[0], x - pos[1])
                            sample = offset[0] ** 2 + offset[1] ** 2 # distSqrd
                            sample += (posBuffer[pos][2] - posBuffer[y, x][2]) ** 2
                            if sample < bestSample:
                                bestSample = sample
                                bestIndex = offset

                    # Convert relative to absolute
                    bestIndex = (bestIndex[0] + pos[0], bestIndex[1] + pos[1])
                    maxSample = 2 * extra ** 2
                    maxSample += (posBuffer[pos][2] - posBuffer[bestIndex][2]) ** 2
                    # 0.0 if completely in shadow, 1.0 if completely outside
                    shadow = 1 - glm.sqrt(bestSample / maxSample)
                    diffuseBuffer[pos] = 0.1 + (diffuseBuffer[pos] - 0.1) * shadow
                    broken = False
                    break
                if broken:
                    diffuseBuffer[pos] = 0.1
            elif not SOFT_SHADOWS and occlusionBuffer[pos] != 1.0:
                diffuseBuffer[pos] = min(diffuseBuffer[pos], 0.1)

            color = img[pos]
            extra = diffuseBuffer[pos] * attenuation
            fragCol = min(valueBuffer[pos] + extra, 1) * color
            img[pos] = fragCol
            if USE_PG:
                pygame.gfxdraw.pixel(screen, pos[1], pos[0], fragCol)

        if USE_PG:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    exit()
            pygame.display.flip()

    print("finished")
    print("time:", time.perf_counter() - start)
    Image.fromarray(img.astype(np.uint8)).save("out.png")

    if USE_PG:
        def show():
            Image.fromarray(img.astype(np.uint8)).show()
        t = threading.Thread(target=show)
        t.daemon = True
        # t.start()

        done = False
        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    done = True
        pygame.display.quit()

if __name__ == "__main__":
    main()
