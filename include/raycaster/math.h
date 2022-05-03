#ifndef MATH_H
#define MATH_H

#include <iostream>

namespace math {
    class vec3 {
        public:
            double x;
            double y;
            double z;
            vec3();
            vec3(double x, double y, double z);
            vec3 operator+(const vec3 &other);
            vec3 operator-(const vec3 &other);
            vec3 operator*(double other);
            vec3 operator/(double other);
            double dot(const vec3 &other);
            vec3 cross(const vec3 &other);
            vec3 normalized();
            double distance2(vec3 other);
    };

    std::ostream& operator<<(std::ostream &out, const vec3 &vec);
    vec3 operator*(double x, vec3 y);
    vec3 operator/(double x, vec3 y);
}

#endif // math.h