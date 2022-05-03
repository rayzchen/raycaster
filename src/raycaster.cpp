#include <raycaster/math.h>
#include <raycaster/raycaster.h>
#include <iostream>
#include <vector>
#include <cmath>

namespace raycaster {
    Shape::~Shape() {

    }

    Shape::Shape(ShapeType type) {
        this->type = type;
    }

    Sphere::Sphere(math::vec3 center, double radius): Shape(SphereShape) {
        this->center = center;
        this->radius = radius;
    }

    Polygon::Polygon(std::vector<math::vec3> points): Shape(PolygonShape) {
        this->points = points;

        math::vec3 ab = points[1] - points[0];
        math::vec3 ac = points[2] - points[0];
        this->normal = ac.cross(ab).normalized();
    }

    bool testCrosses(math::vec3 origin, math::vec3 direction, math::vec3 a, math::vec3 b) {
        // Check if inf line from origin in direction crosses segment AB
        math::vec3 ab = b - a;
        math::vec3 ao = a - origin;

        // Coplanar
        math::vec3 perp = direction.cross(ab);

        // Parallel
        double denom = perp.dot(perp);
        if (denom == 0) {
            return false;
        }

        // s multiples of ab, t is multiples of direction
        double s = ao.cross(direction).dot(perp) / denom;
        double t = ao.cross(ab).dot(perp) / denom;
        // math::vec3 point = origin + t * direction;

        // t has no upper bound
        return (0 <= s) && (s <= 1) && (0 <= t) ? 1 : 0;
    }

    Raycast::Raycast(math::vec3 origin, math::vec3 direction) {
        this->origin = origin;
        this->direction = direction.normalized();
    }

    bool Raycast::intersects(Shape* shape, RaycastHit* hit) {
        if (shape->type == SphereShape) {
            Sphere* sphere = dynamic_cast<Sphere*>(shape);
            return this->intersects(sphere, hit);
        } else if (shape->type == PolygonShape) {
            Polygon* polygon = dynamic_cast<Polygon*>(shape);
            return this->intersects(polygon, hit);
        }
        return false;
    }

    bool Raycast::intersects(Sphere* sphere, RaycastHit* hit) {
        // Length on direction of line to nearest point
        double length = this->direction.dot(sphere->center - this->origin);
        // Only for unnormalized
        // length /= this->direction.dot(this->direction);
        // Nearest point
        math::vec3 point = this->origin + length * this->direction;
        double distance = point.distance2(sphere->center);
        if (pow(sphere->radius, 2) < distance) {
            return false;
        }

        double distSurface = std::sqrt(pow(sphere->radius, 2) - distance);
        double realDist = length - distSurface;
        math::vec3 realPoint = this->origin + realDist * this->direction;
        math::vec3 normal = (realPoint - sphere->center).normalized();

        hit->object = sphere;
        hit->distance = realDist;
        hit->point = realPoint;
        hit->normal = normal;
        return true;
    }

    bool Raycast::intersects(Polygon* polygon, RaycastHit* hit) {
        // Plane with point p0 normal n
        math::vec3 ab = polygon->points[1] - polygon->points[0];
        math::vec3 p0 = polygon->points[0];

        double denom = this->direction.dot(polygon->normal);
        if (std::abs(denom) < 1e-10) {
            // Perpendicular to plane?
            return false;
        }

        double t = (p0 - this->origin).dot(polygon->normal) / denom;
        if (t < 0) {
            // Facing other direction?
            return false;
        }

        // Point on plane in direction of line
        math::vec3 p = this->origin + this->direction * t;

        // Arbitrary direction (first side)
        math::vec3 direction = polygon->normal.cross(ab);
        unsigned int intersections = 0;
        for (unsigned int i = 0; i < polygon->points.size(); i++) {
            unsigned int n = i + 1;
            if (n == polygon->points.size()) {
                n = 0;
            }
            if (testCrosses(p, direction, polygon->points[i], polygon->points[n])) {
                intersections += 1;
            }
        }
        if (intersections % 2 == 0) {
            return false;
        }
        hit->object = polygon;
        hit->distance = t;
        hit->point = p;
        hit->normal = polygon->normal;
        return true;
    }
}
