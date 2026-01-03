#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include <cstdint>     // for uintptr_t
#include <windows.h>   // for HWND, HDC, HGLRC
#include <cgame.h>  // your framework header

namespace py = pybind11;

#define CGAME_BIND_KEY(name) m.attr(#name) = cgame.name

// Assume you have a global 'cgame' with nested 'display' and methods.
// And 'display.set_mode(w,h,flags)' returns either a CGameScreen or a reference to it.

PYBIND11_MODULE(cgame, m) {
    m.doc() = "Python bindings for cgame framework";
// Event constants
    m.attr("QUIT")        = CGAME_QUIT;
    m.attr("VIDEORESIZE") = CGAME_VIDEORESIZE;
    m.attr("KEYDOWN")     = CGAME_KEYDOWN;
    m.attr("KEYUP")       = CGAME_KEYUP;

    // Display flags
    m.attr("FLAG_RESIZABLE")   = CGAME_FLAG_RESIZABLE;
    m.attr("FLAG_DPI_AWARE")   = CGAME_FLAG_DPI_AWARE;
    m.attr("FLAG_OPENGL")      = CGAME_FLAG_OPENGL;
    m.attr("FLAG_VULKAN")      = CGAME_FLAG_VULKAN;
    m.attr("FLAG_UNDECORATED") = CGAME_FLAG_UNDECORATED;
    m.attr("FLAG_MSAA_X2")     = CGAME_FLAG_MSAA_X2;
    m.attr("FLAG_MSAA_X4")     = CGAME_FLAG_MSAA_X4;
    m.attr("FLAG_MSAA_X8")     = CGAME_FLAG_MSAA_X8;
    m.attr("FLAG_MSAA_X16")    = CGAME_FLAG_MSAA_X16;

    // Bind CGameScreen
    py::class_<CGameScreen>(m, "CGameScreen")
        // Dimensions and quality settings
        .def_readonly("width", &CGameScreen::width)
        .def_readonly("height", &CGameScreen::height)
        .def_readonly("msaa_samples", &CGameScreen::msaa_samples)
        .def_readonly("ssaa_scale", &CGameScreen::ssaa_scale)
        // API flags
        .def_readonly("use_opengl", &CGameScreen::use_opengl)
        .def_readonly("use_vulkan", &CGameScreen::use_vulkan)
        // Optional: expose handles as integers if you need them in Python
        .def_property_readonly("hwnd", [](const CGameScreen& s) {
            return reinterpret_cast<std::uintptr_t>(s.hwnd);
        })
        .def_property_readonly("hdc", [](const CGameScreen& s) {
            return reinterpret_cast<std::uintptr_t>(s.hdc);
        })
        .def_property_readonly("hglrc", [](const CGameScreen& s) {
            return reinterpret_cast<std::uintptr_t>(s.hglrc);
        })
        .def_property_readonly("vk_instance", [](const CGameScreen& s) {
            return reinterpret_cast<std::uintptr_t>(s.vk_instance);
        })
        .def_property_readonly("vk_device", [](const CGameScreen& s) {
            return reinterpret_cast<std::uintptr_t>(s.vk_device);
        })
        .def_property_readonly("vk_surface", [](const CGameScreen& s) {
            return reinterpret_cast<std::uintptr_t>(s.vk_surface);
        })
        .def_property_readonly("vk_swapchain", [](const CGameScreen& s) {
            return reinterpret_cast<std::uintptr_t>(s.vk_swapchain);
        })
        .def_property_readonly("d3d12_device", [](const CGameScreen& s) {
            return reinterpret_cast<std::uintptr_t>(s.d3d12_device);
        })
        .def_property_readonly("d3d12_cmdqueue", [](const CGameScreen& s) {
            return reinterpret_cast<std::uintptr_t>(s.d3d12_cmdqueue);
        })
        .def_property_readonly("d3d12_swapchain", [](const CGameScreen& s) {
            return reinterpret_cast<std::uintptr_t>(s.d3d12_swapchain);
        });
    // --- CGameImage binding ---
    py::class_<CGameImage>(m, "CGameImage")
        .def_readonly("width", &CGameImage::width)
        .def_readonly("height", &CGameImage::height)
        .def_readonly("channels", &CGameImage::channels)
        .def_property_readonly("pixels", [](CGameImage& img) {
            // Expose pixels as Python bytes
            return py::bytes(reinterpret_cast<char*>(img.pixels),
                             img.width * img.height * img.channels);
        })
        .def_readonly("gpu_uploaded", &CGameImage::gpu_uploaded);

    py::class_<CGameFont>(m, "CGameFont")
    .def_readonly("loaded", &CGameFont::loaded)
    .def_property_readonly("name", [](const CGameFont& f) {
        // Convert WCHAR[64] to std::string
        return std::wstring(f.name).c_str();
    });


    // init/quit on the global instance
    m.def("init", []() { cgame.init(); });
    m.def("quit", []() { cgame.quit(); });

    auto display = m.def_submodule("display", "Display related functions");

        display.def("set_mode", [](int w, int h, int flags) {
            return cgame.display.set_mode(w, h, flags);
        }, py::return_value_policy::move);

        display.def("clear", [](int r, int g, int b) { cgame.display.clear(r, g, b); });
        display.def("flip", []() { cgame.display.flip(); });

        display.def("get_width", []() { return cgame.display.get_width(); });
        display.def("get_height", []() { return cgame.display.get_height(); });
        display.def("get_monitor_width", []() { return cgame.display.get_monitor_width(); });
        display.def("get_monitor_height", []() { return cgame.display.get_monitor_height(); });

        display.def("set_pos", [](int x, int y) { cgame.display.set_pos(x, y); });
        display.def("center", []() { cgame.display.center(); });
        display.def("get_posX", []() { return cgame.display.get_posX(); });
        display.def("get_posY", []() { return cgame.display.get_posY(); });

        display.def("focus", []() { cgame.display.focus(); });
        display.def("restore", []() { cgame.display.restore(); });
        display.def("minimize", []() { cgame.display.minimize(); });

        display.def("set_title", [](const std::string& title) {
            cgame.display.set_title(title.c_str());
        });

        display.def("set_icon", [](const std::string& path) {
            return cgame.display.set_icon(path.c_str());
        });

        display.def("set_icon_from_image", [](const CGameImage& img) {
            return cgame.display.set_icon_from_image(&img);
        });

    auto draw = m.def_submodule("draw", "Drawing primitives");

        draw.def("rect", [](int x, int y, int w, int h,
                            int border_width, int r, int g, int b) {
            cgame.draw.rect(x, y, w, h, border_width, r, g, b);
        });

        draw.def("rect_fill", [](int x, int y, int w, int h,
                                int r, int g, int b) {
            cgame.draw.rect_fill(x, y, w, h, r, g, b);
        });

        draw.def("rounded_rect", [](int x, int y, int w, int h,
                                    int radius, int border_width,
                                    int r, int g, int b) {
            cgame.draw.rounded_rect(x, y, w, h, radius, border_width, r, g, b);
        });

        draw.def("rounded_rect_fill", [](int x, int y, int w, int h,
                                        int radius, int r, int g, int b) {
            cgame.draw.rounded_rect_fill(x, y, w, h, radius, r, g, b);
        });

        draw.def("circle", [](int x, int y, int radius,
                            int border_width, int r, int g, int b) {
            cgame.draw.circle(x, y, radius, border_width, r, g, b);
        });

        draw.def("circle_fill", [](int x, int y, int radius,
                                int r, int g, int b) {
            cgame.draw.circle_fill(x, y, radius, r, g, b);
        });

        draw.def("line", [](int x1, int y1, int x2, int y2,
                            int border_width, int r, int g, int b) {
            cgame.draw.line(x1, y1, x2, y2, border_width, r, g, b);
        });

        // Polygon: accept Python lists for xs and ys
        draw.def("polygon", [](py::list xs, py::list ys,
                            int border_width, int r, int g, int b) {
            size_t count = xs.size();
            if (ys.size() != count)
                throw std::runtime_error("xs and ys must match length");
            std::vector<int> vx(count), vy(count);
            for (size_t i = 0; i < count; ++i) {
                vx[i] = xs[i].cast<int>();
                vy[i] = ys[i].cast<int>();
            }
            cgame.draw.polygon(vx.data(), vy.data(), count, border_width, r, g, b);
        });

        draw.def("polygon_fill", [](py::list xs, py::list ys,
                                    int r, int g, int b) {
            size_t count = xs.size();
            if (ys.size() != count)
                throw std::runtime_error("xs and ys must match length");

            std::vector<int> vx(count), vy(count);
            for (size_t i = 0; i < count; ++i) {
                vx[i] = xs[i].cast<int>();
                vy[i] = ys[i].cast<int>();
            }
            cgame.draw.polygon_fill(vx.data(), vy.data(), count, r, g, b);
        });


    auto image = m.def_submodule("image", "Image loading and drawing");

        image.def("load", [](const std::string& path) {
            return cgame.image.load(path.c_str());
        }, py::return_value_policy::move);
        image.def("load_from_memory", [](py::bytes data) {
            std::string buffer = data;  // convert Python bytes → std::string
            return cgame.image.load_from_memory(buffer.data(), buffer.size());
        }, py::return_value_policy::move);

        image.def("unload", [](CGameImage& img) {
            cgame.image.unload(&img);
        });

        image.def("draw", [](const CGameImage& img, int x, int y) {
            cgame.image.draw(&img, x, y);
        });

        image.def("draw_scaled", [](const CGameImage& img, int x, int y, int w, int h) {
            cgame.image.draw_scaled(&img, x, y, w, h);
        });

        image.def("draw_rotated", [](const CGameImage& img, int x, int y, float angle_deg) {
            cgame.image.draw_rotated(&img, x, y, angle_deg);
        });

        image.def("draw_advanced", [](const CGameImage& img,
                                    int x, int y,
                                    int imageX, int imageY,
                                    int imageW, int imageH) {
            cgame.image.draw_advanced(&img, x, y, imageX, imageY, imageW, imageH);
        });

        image.def("resize", [](const CGameImage& src, int w, int h) {
            return cgame.image.resize(&src, w, h);
        }, py::return_value_policy::move);

        image.def("rotate", [](const CGameImage& src, float angle_deg) {
            return cgame.image.rotate(&src, angle_deg);
        }, py::return_value_policy::move);

        image.def("flip_horizontal", [](const CGameImage& img) {
            return cgame.image.flip_horizontal(&img);
        }, py::return_value_policy::move);

        image.def("flip_vertical", [](const CGameImage& img) {
            return cgame.image.flip_vertical(&img);
        }, py::return_value_policy::move);

        image.def("get_width", [](const CGameImage& img) {
            return cgame.image.get_width(&img);
        });

        image.def("get_height", [](const CGameImage& img) {
            return cgame.image.get_height(&img);
        });

        image.def("get_channels", [](const CGameImage& img) {
            return cgame.image.get_channels(&img);
        });




    // In your binding code
    auto event = m.def_submodule("event", "Event related functions");
        event.def("get", []() {
            return cgame.event.get ();
    });

    auto time = m.def_submodule("time", "Timing functions");

        time.def("set_fps", [](int fps) {
            cgame.time.set_fps(fps);
        });

        time.def("get_fps", []() {
            return cgame.time.get_fps();
        });

        time.def("get_dt", []() {
            return cgame.time.get_dt();
        });

    auto text = m.def_submodule("text", "Text rendering functions");

        text.def("draw", [](const std::string& txt, int x, int y,
                            int r, int g, int b) {
            cgame.text.draw(txt.c_str(), x, y, r, g, b);
        });

        text.def("draw_complex", [](const std::string& txt, int x, int y,
                                    const CGameFont& font, float size,
                                    int r, int g, int b) {
            cgame.text.draw_complex(txt.c_str(), x, y,
                                    const_cast<CGameFont*>(&font),
                                    size, r, g, b);
        });

        text.def("load_font", [](const std::string& path) {
            return cgame.text.load_font(path.c_str());
        }, py::return_value_policy::move);

        text.def("unload_font", [](CGameFont& font) {
            cgame.text.unload_font(&font);
        });

    auto key = m.def_submodule("key", "Keyboard input");

        key.def("pressed", [](int key) {
            return cgame.key.pressed(key);
        });

        key.def("just_pressed", [](int key) {
            return cgame.key.just_pressed(key);
        });

        key.def("just_released", [](int key) {
            return cgame.key.just_released(key);
        });

        key.def("get_last", []() {
            return cgame.key.get_last();
        });

            // =========================
            // Keyboard keys (DIRECT)
            // =========================
            CGAME_BIND_KEY(K_a); CGAME_BIND_KEY(K_b); CGAME_BIND_KEY(K_c);
            CGAME_BIND_KEY(K_d); CGAME_BIND_KEY(K_e); CGAME_BIND_KEY(K_f);
            CGAME_BIND_KEY(K_g); CGAME_BIND_KEY(K_h); CGAME_BIND_KEY(K_i);
            CGAME_BIND_KEY(K_j); CGAME_BIND_KEY(K_k); CGAME_BIND_KEY(K_l);
            CGAME_BIND_KEY(K_m); CGAME_BIND_KEY(K_n); CGAME_BIND_KEY(K_o);
            CGAME_BIND_KEY(K_p); CGAME_BIND_KEY(K_q); CGAME_BIND_KEY(K_r);
            CGAME_BIND_KEY(K_s); CGAME_BIND_KEY(K_t); CGAME_BIND_KEY(K_u);
            CGAME_BIND_KEY(K_v); CGAME_BIND_KEY(K_w); CGAME_BIND_KEY(K_x);
            CGAME_BIND_KEY(K_y); CGAME_BIND_KEY(K_z);

            CGAME_BIND_KEY(K_0); CGAME_BIND_KEY(K_1); CGAME_BIND_KEY(K_2);
            CGAME_BIND_KEY(K_3); CGAME_BIND_KEY(K_4); CGAME_BIND_KEY(K_5);
            CGAME_BIND_KEY(K_6); CGAME_BIND_KEY(K_7); CGAME_BIND_KEY(K_8);
            CGAME_BIND_KEY(K_9);

            CGAME_BIND_KEY(K_SPACE);
            CGAME_BIND_KEY(K_RETURN);
            CGAME_BIND_KEY(K_ESCAPE);
            CGAME_BIND_KEY(K_LEFT);
            CGAME_BIND_KEY(K_RIGHT);
            CGAME_BIND_KEY(K_UP);
            CGAME_BIND_KEY(K_DOWN);

            CGAME_BIND_KEY(K_LSHIFT);
            CGAME_BIND_KEY(K_RSHIFT);
            CGAME_BIND_KEY(K_LCTRL);
            CGAME_BIND_KEY(K_RCTRL);

            CGAME_BIND_KEY(K_F1);  CGAME_BIND_KEY(K_F2);  CGAME_BIND_KEY(K_F3);
            CGAME_BIND_KEY(K_F4);  CGAME_BIND_KEY(K_F5);  CGAME_BIND_KEY(K_F6);
            CGAME_BIND_KEY(K_F7);  CGAME_BIND_KEY(K_F8);  CGAME_BIND_KEY(K_F9);
            CGAME_BIND_KEY(K_F10); CGAME_BIND_KEY(K_F11); CGAME_BIND_KEY(K_F12);

            CGAME_BIND_KEY(K_NUM0); CGAME_BIND_KEY(K_NUM1); CGAME_BIND_KEY(K_NUM2);
            CGAME_BIND_KEY(K_NUM3); CGAME_BIND_KEY(K_NUM4); CGAME_BIND_KEY(K_NUM5);
            CGAME_BIND_KEY(K_NUM6); CGAME_BIND_KEY(K_NUM7); CGAME_BIND_KEY(K_NUM8);
            CGAME_BIND_KEY(K_NUM9);

            CGAME_BIND_KEY(K_NUM_ADD);
            CGAME_BIND_KEY(K_NUM_SUB);
            CGAME_BIND_KEY(K_NUM_MUL);
            CGAME_BIND_KEY(K_NUM_DIV);
            CGAME_BIND_KEY(K_NUM_DECIMAL);
            CGAME_BIND_KEY(K_NUM_ENTER);



    auto mouse = m.def_submodule("mouse", "Mouse input");

        mouse.def("pressed", [](int button) {
            return cgame.mouse.pressed(button);
        });

        mouse.def("just_pressed", [](int button) {
            return cgame.mouse.just_pressed(button);
        });

        mouse.def("just_released", [](int button) {
            return cgame.mouse.just_released(button);
        });

        mouse.def("get_posX", []() {
            return cgame.mouse.get_posX();
        });

        mouse.def("get_global_posX", []() {
            return cgame.mouse.get_global_posX();
        });

        mouse.def("get_global_posY", []() {
            return cgame.mouse.get_global_posY();
        });

        mouse.def("set_pos", [](int x, int y) {
            cgame.mouse.set_pos(x, y);
        });

        mouse.def("get_wheel", []() {
            return cgame.mouse.get_wheel();
        });

    auto console = m.def_submodule("console", "console related functions");

        console.def("set_color", [](int fg, int bg) {
            cgame.console.set_color(fg, bg);
        });
        console.def("reset_color", []() {
            cgame.console.reset_color();
        });
        console.def("clear", []() {
            cgame.console.clear();
        });
            // =========================
            // Console colors
            // =========================
            m.attr("CONSOLE_COLOR_BLACK")         = CGAME_CONSOLE_COLOR_BLACK;
            m.attr("CONSOLE_COLOR_BLUE")          = CGAME_CONSOLE_COLOR_BLUE;
            m.attr("CONSOLE_COLOR_GREEN")         = CGAME_CONSOLE_COLOR_GREEN;
            m.attr("CONSOLE_COLOR_CYAN")          = CGAME_CONSOLE_COLOR_CYAN;
            m.attr("CONSOLE_COLOR_RED")           = CGAME_CONSOLE_COLOR_RED;
            m.attr("CONSOLE_COLOR_MAGENTA")       = CGAME_CONSOLE_COLOR_MAGENTA;
            m.attr("CONSOLE_COLOR_YELLOW")        = CGAME_CONSOLE_COLOR_YELLOW;
            m.attr("CONSOLE_COLOR_WHITE")         = CGAME_CONSOLE_COLOR_WHITE;
            m.attr("CONSOLE_COLOR_GRAY")          = CGAME_CONSOLE_COLOR_GRAY;
            m.attr("CONSOLE_COLOR_LIGHT_BLUE")    = CGAME_CONSOLE_COLOR_LIGHT_BLUE;
            m.attr("CONSOLE_COLOR_LIGHT_GREEN")   = CGAME_CONSOLE_COLOR_LIGHT_GREEN;
            m.attr("CONSOLE_COLOR_LIGHT_CYAN")    = CGAME_CONSOLE_COLOR_LIGHT_CYAN;
            m.attr("CONSOLE_COLOR_LIGHT_RED")     = CGAME_CONSOLE_COLOR_LIGHT_RED;
            m.attr("CONSOLE_COLOR_LIGHT_MAGENTA") = CGAME_CONSOLE_COLOR_LIGHT_MAGENTA;
            m.attr("CONSOLE_COLOR_LIGHT_YELLOW")  = CGAME_CONSOLE_COLOR_LIGHT_YELLOW;
            m.attr("CONSOLE_COLOR_BRIGHT_WHITE")  = CGAME_CONSOLE_COLOR_BRIGHT_WHITE;



    // Constants
    m.attr("QUIT")          = cgame.QUIT;
    m.attr("VIDEORESIZE")   = cgame.VIDEORESIZE;
}