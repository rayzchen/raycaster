#include <raycaster/raycaster.h>
#include <SDL2/SDL.h>
#include <iostream>
#include <chrono>
#include <cstdlib>
#include <cmath>
#include <ctime>

#define print(x) std::cout << x << std::endl

#define WINDOW_WIDTH 500
#define WINDOW_HEIGHT 500

class Color {
    public:
        int r;
        int g;
        int b;

        Color(int r, int g, int b) {
            this->r = r;
            this->g = g;
            this->b = b;
        }

        Color operator*(double other) {
            return Color((int)(r * other), (int)(g * other), (int)(b * other));
        }
};

class Window {
    public:
        SDL_Renderer *renderer;
        SDL_Window *window;

        Window() {
            SDL_Init(SDL_INIT_VIDEO);
            SDL_CreateWindowAndRenderer(
                WINDOW_WIDTH, WINDOW_HEIGHT, 0, &this->window, &this->renderer);
            // Clear to black
            SDL_SetRenderDrawColor(this->renderer, 0, 0, 0, 0);
            SDL_RenderClear(renderer);
        }

        void refresh() {
            SDL_Event event;
            SDL_RenderPresent(this->renderer);
            if (SDL_PollEvent(&event) && event.type == SDL_QUIT) {
                this->quit();
                exit(EXIT_SUCCESS);
            }
        }

        void pixel(int x, int y, Color color) {
            SDL_SetRenderDrawColor(this->renderer, color.r, color.g, color.b, 255);
            SDL_RenderDrawPoint(this->renderer, x, y);
        }

        void quit() {
            SDL_Surface *sshot = SDL_CreateRGBSurface(0, WINDOW_WIDTH, WINDOW_HEIGHT, 32, 0x00ff0000, 0x0000ff00, 0x000000ff, 0xff000000);
            SDL_RenderReadPixels(this->renderer, NULL, SDL_PIXELFORMAT_ARGB8888, sshot->pixels, sshot->pitch);
            SDL_SaveBMP(sshot, "out.bmp");
            SDL_FreeSurface(sshot);

            SDL_DestroyRenderer(this->renderer);
            SDL_DestroyWindow(this->window);
            SDL_Quit();
        }
};

class Light {
    public:
        math::vec3 position;
        double strength;
        double distance;
        double size;
        double constant;
        double linear;
        double quadratic;

        Light(math::vec3 position, double strength, double distance, double size) {
            this->position = position;
            this->strength = strength;
            this->distance = distance;
            this->size = size;

            this->constant = 1.0;
            this->linear = 4.690508 * std::pow(distance, -1.009712);
            this->quadratic = 82.444779 * std::pow(distance, -2.019206);
        }

        double getAttenuation(double distance) {
            return 1 / (this->constant + (this->quadratic * distance + this->linear) * distance);
        }
};

bool getHits(raycaster::Raycast ray, raycaster::RaycastHit* hit, std::vector<raycaster::Shape*> parts) {
    std::vector<raycaster::RaycastHit> hits = std::vector<raycaster::RaycastHit>();
    for (unsigned int i = 0; i < parts.size(); i++) {
        raycaster::RaycastHit hit;
        if (ray.intersects(parts[i], &hit)) {
            hits.push_back(hit);
        }
    }
    if (hits.size() == 0) {
        return false;
    }
    double bestDistance = INFINITY;
    raycaster::RaycastHit *bestHit;
    for (unsigned int i = 0; i < hits.size(); i++) {
        if (hits[i].distance < bestDistance) {
            bestDistance = hits[i].distance;
            bestHit = &hits[i];
        }
    }
    *hit = *bestHit;
    return true;
}

int main(int argc, char *argv[]) {
    raycaster::Shape *back = new raycaster::Polygon(std::vector<math::vec3>{
        math::vec3(-10, 10, 10), math::vec3(-10, -10, 10),
        math::vec3(10, -10, 10), math::vec3(10, 10, 10)
    });
    raycaster::Shape *ceiling = new raycaster::Polygon(std::vector<math::vec3>{
        math::vec3(-10, 10, 10), math::vec3(10, 10, 10),
        math::vec3(10, 10, -10), math::vec3(-10, 10, -10)
    });
    raycaster::Shape *floor = new raycaster::Polygon(std::vector<math::vec3>{
        math::vec3(-10, -10, 10), math::vec3(-10, -10, -10),
        math::vec3(10, -10, -10), math::vec3(10, -10, 10)
    });
    raycaster::Shape *left = new raycaster::Polygon(std::vector<math::vec3>{
        math::vec3(-10, 10, 10), math::vec3(-10, 10, -10),
        math::vec3(-10, -10, -10), math::vec3(-10, -10, 10)
    });
    raycaster::Shape *right = new raycaster::Polygon(std::vector<math::vec3>{
        math::vec3(10, 10, 10), math::vec3(10, -10, 10),
        math::vec3(10, -10, -10), math::vec3(10, 10, -10)
    });
    raycaster::Shape *sphere1 = new raycaster::Sphere(math::vec3(4, -5, 8), 5);
    raycaster::Shape *sphere2 = new raycaster::Sphere(math::vec3(-4, -5, 5), 5);

    std::vector<Color> colors = {
        Color(255, 0, 0),
        Color(0, 255, 0),
        Color(0, 0, 255),
        Color(255, 255, 0),
        Color(0, 255, 255),
        Color(200, 200, 200),
        Color(127, 127, 127),
    };

    std::vector<raycaster::Shape*> parts = {
        back, ceiling, floor, left, right, sphere1, sphere2
    };

    double fov = 90.0 * (M_PI / 180.0);
    double scale = tan(fov / 2);
    math::vec3 camera = math::vec3(0, 0, -10);
    Light light = Light(math::vec3(0, 7.5, 0), 1, 300, 20);

    Window *window = new Window();

    auto start = std::chrono::high_resolution_clock::now();

    raycaster::RaycastHit hit;
    for (int i = 0; i < WINDOW_HEIGHT; i++) {
        for (int j = 0; j < WINDOW_WIDTH; j++) {
            double dx = ((j + 0.5) / WINDOW_WIDTH * 2 - 1);
            double dy = ((i + 0.5) / WINDOW_WIDTH * 2 - 1);
            math::vec3 direction = math::vec3(dx * scale, dy * scale, 1);
            raycaster::Raycast ray = raycaster::Raycast(camera, direction);
            if (getHits(ray, &hit, parts)) {
                unsigned int index = -1;
                for (unsigned int i = 0; i < parts.size(); i++) {
                    if (parts[i] == hit.object) {
                        index = i;
                        break;
                    }
                }

                double ambient = 0.1;
                math::vec3 lightDir = (light.position - hit.point).normalized();
                double alongNormal = hit.normal.dot(lightDir);
                double diffuse = std::max(alongNormal, 0.0);

                double specular = 0;
                double attenuation = light.getAttenuation(hit.distance);

                raycaster::Raycast shadowRay = raycaster::Raycast(
                    light.position, hit.point - light.position);
                raycaster::RaycastHit shadowHit;
                if (getHits(shadowRay, &shadowHit, parts) && shadowHit.object != hit.object) {
                    diffuse = std::min(diffuse, 0.1);
                }

                double value = (ambient + diffuse + specular) * attenuation;
                Color color = colors[index] * std::min(value, 1.0);
                window->pixel(j, WINDOW_HEIGHT - i - 1, color);
            }
        }
        window->refresh();
    }
    auto end = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> fp_ms = end - start;
    std::cout << "Finished" << std::endl;
    std::cout << "Time taken: " << fp_ms.count() << std::endl;

    while (1) {
        window->refresh();
    }
    return EXIT_SUCCESS;
}
