#ifndef RAYCASTER_H
#define RAYCASTER_H

#include <raycaster/math.h>
#include <vector>

namespace raycaster {
    enum ShapeType {PolygonShape, SphereShape};

    class Shape {
        public:
            ShapeType type;
            Shape(ShapeType type);
            virtual ~Shape();
    };

    typedef struct RaycastHit {
        Shape *object;
        double distance;
        math::vec3 point;
        math::vec3 normal;
    } RaycastHit;

    class Sphere: public Shape {
        public:
            math::vec3 center;
            double radius;
            Sphere(math::vec3 center, double radius);
    };

    class Polygon: public Shape {
        public:
            std::vector<math::vec3> points;
            math::vec3 normal;
            Polygon(std::vector<math::vec3> points);
    };

    bool testCrosses(math::vec3 origin, math::vec3 direction, math::vec3 a, math::vec3 b);

    class Raycast {
        public:
            math::vec3 origin;
            math::vec3 direction;
            Raycast(math::vec3 origin, math::vec3 direction);
            bool intersects(Shape* shape, RaycastHit* hit);
            bool intersects(Sphere* sphere, RaycastHit* hit);
            bool intersects(Polygon* polygon, RaycastHit* hit);
    };
}

#endif // raycaster.h