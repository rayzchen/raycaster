#include <raycaster/math.h>
#include <cmath>
#include <iostream>

namespace math {
    vec3::vec3() {
        x = 0.0;
        y = 0.0;
        z = 0.0;
    }

    vec3::vec3(double x, double y, double z) {
        this->x = x;
        this->y = y;
        this->z = z;
    }

    vec3 vec3::operator+(const vec3 &other) {
        return vec3(x + other.x, y + other.y, z + other.z);
    }

    vec3 vec3::operator-(const vec3 &other) {
        return vec3(x - other.x, y - other.y, z - other.z);
    }

    vec3 vec3::operator*(double other) {
        return vec3(x * other, y * other, z * other);
    }

    vec3 vec3::operator/(double other) {
        return vec3(x / other, y / other, z / other);
    }

    double vec3::dot(const vec3 &other) {
        return x * other.x + y * other.y + z * other.z;
    }

    vec3 vec3::cross(const vec3 &other) {
        double rx = y * other.z - z * other.y;
        double ry = z * other.x - x * other.z;
        double rz = x * other.y - y * other.x;
        return vec3(rx, ry, rz);
    }

    vec3 vec3::normalized() {
        double length = sqrt(pow(x, 2) + pow(y, 2) + pow(z, 2));
        return vec3(x / length, y / length, z / length);
    }

    double vec3::distance2(vec3 other) {
        double xdiff = pow(other.x - x, 2);
        double ydiff = pow(other.y - y, 2);
        double zdiff = pow(other.z - z, 2);
        return xdiff + ydiff + zdiff;
    }

    std::ostream& operator<<(std::ostream &out, const vec3 &vec) {
        out << "vec3(" << vec.x << ", " << vec.y << ", " << vec.z << ")";
        return out;
    }

    vec3 operator*(double x, vec3 y) {
        return y * x;
    }

    vec3 operator/(double x, vec3 y) {
        return vec3(x / y.x, x / y.y, x / y.z);
    }
}
