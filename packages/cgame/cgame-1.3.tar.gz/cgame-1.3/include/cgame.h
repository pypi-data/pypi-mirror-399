
// |===========================================================================|
// |===========================================================================|
// |                     [][]  [][]   [][]  []    [] [][][]                    |
// |                    []    []     []  [] [][][][] []                        |
// |                    []    []     [][][] [] [] [] [][][]                    |
// |                    []    []  [] []  [] []    [] []                        |
// |                     [][]  [][]  []  [] []    [] [][][]                    |
// |===========================================================================|
// |===========================================================================|
// | []  [] [][][] [][][]   [][] [][][]  [][]  []  []         [][]      [][][] |
// | []  [] []     []  [] []       []   []  [] [][ [] []        []          [] |
// | []  [] [][][] [][]   [][][]   []   []  [] [][][]    [][]   []      [][][] |
// |  [][]  []     []  []     []   []   []  [] [] ][] []        []          [] |
// |   []   [][][] []  [] [][]   [][][]  [][]  []  []         [][][] [] [][][] |
// |===========================================================================|
// |                             BY : M.HASSNAIN.K                             |
// |===========================================================================|

#ifndef CGAME_H
#define CGAME_H

#define CGAME_VERSION_MAJOR 1
#define CGAME_VERSION_MINOR 3
#define CGAME_VERSION_PATCH 0

#ifndef M_PI
#define M_PI 3.14159265358979323846
#endif

#include <stdbool.h>
#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <math.h>
#include <string>

#if defined(_WIN32) || defined(_WIN64)
// |---------------------------------------------------------------------------|
//     []   []    [] [][][] []  [] [][]    [][]  []    []   [][]
//      []  []    []   []   [][ [] []  [] []  [] []    [] []
// [][][][] [] [] []   []   [][][] []  [] []  [] [] [] [] [][][]
//      []  [][][][]   []   [] ][] []  [] []  [] [][][][]     []
//     []   []    [] [][][] []  [] [][]    [][]  []    [] [][]
// |---------------------------------------------------------------------------|
    #if defined(_MSC_VER)
        #pragma comment(lib, "opengl32.lib")
        #pragma comment(lib, "gdiplus.lib")
        #pragma comment(lib, "gdi32.lib")
        #pragma comment(lib, "ws2_32.lib")
        #pragma comment(lib, "msimg32.lib")
        #pragma comment(lib, "winmm.lib")
        #pragma comment(lib, "ole32.lib")
    #elif defined(__GNUC__)
        // MinGW/GCC users: link with
        //   -lopengl32 -lgdi32 -lgdiplus -lws2_32 -lmsimg32 -lwinmm -municode
    #endif

    #define  WIN32_LEAN_AND_MEAN
    #include <windows.h>
    #include <mmsystem.h>
    #include <windowsx.h>
    #include <objidl.h>
    #include <gdiplus.h>
    #include <stdlib.h>
    

    // -------------------------
    // GDI+ helper globals
    // -------------------------
    static ULONG_PTR _cgame_gdiplusToken = 0;
    static bool _cgame_gdiplus_inited = false;

    // =========================
    // Events
    // =========================
    #define CGAME_QUIT         1
    #define CGAME_VIDEORESIZE  2
    #define CGAME_KEYDOWN      3
    #define CGAME_KEYUP        4

    // =========================
    // Display flags
    // =========================
    #define CGAME_FLAG_RESIZABLE   0x01
    #define CGAME_FLAG_DPI_AWARE   0x02
    #define CGAME_FLAG_OPENGL      0x04
    #define CGAME_FLAG_VULKAN      0x08
    #define CGAME_FLAG_D3D12       0x10 
    #define CGAME_FLAG_UNDECORATED 0x20
    #define CGAME_FLAG_MSAA_X2     0x40
    #define CGAME_FLAG_MSAA_X4     0x80
    #define CGAME_FLAG_MSAA_X8     0x100
    #define CGAME_FLAG_MSAA_X16    0x200


    // =========================
    // Console colors (Windows standard 16-color palette)
    // =========================
    #define CGAME_CONSOLE_COLOR_BLACK         0
    #define CGAME_CONSOLE_COLOR_BLUE          1
    #define CGAME_CONSOLE_COLOR_GREEN         2
    #define CGAME_CONSOLE_COLOR_CYAN          3
    #define CGAME_CONSOLE_COLOR_RED           4
    #define CGAME_CONSOLE_COLOR_MAGENTA       5
    #define CGAME_CONSOLE_COLOR_YELLOW        6
    #define CGAME_CONSOLE_COLOR_WHITE         7
    #define CGAME_CONSOLE_COLOR_GRAY          8
    #define CGAME_CONSOLE_COLOR_LIGHT_BLUE    9
    #define CGAME_CONSOLE_COLOR_LIGHT_GREEN   10
    #define CGAME_CONSOLE_COLOR_LIGHT_CYAN    11
    #define CGAME_CONSOLE_COLOR_LIGHT_RED     12
    #define CGAME_CONSOLE_COLOR_LIGHT_MAGENTA 13
    #define CGAME_CONSOLE_COLOR_LIGHT_YELLOW  14
    #define CGAME_CONSOLE_COLOR_BRIGHT_WHITE  15

    // =========================
    // Message box types
    // =========================
    #define CGAME_MSGBOX_ICONINFO             MB_ICONINFORMATION
    #define CGAME_MSGBOX_ICONWARNING          MB_ICONWARNING
    #define CGAME_MSGBOX_ICONERROR            MB_ICONERROR

    // =========================
    // Message box options
    // =========================
    #define CGAME_MSGBOX_OPTION_OK            MB_OK
    #define CGAME_MSGBOX_OPTION_OK_CANCEL     MB_OKCANCEL
    #define CGAME_MSGBOX_OPTION_YES_NO        MB_YESNO

    // =========================
    // Message box results
    // =========================
    #define CGAME_MSGBOX_RESULT_OK            1
    #define CGAME_MSGBOX_RESULT_CANCEL        2
    #define CGAME_MSGBOX_RESULT_YES           3
    #define CGAME_MSGBOX_RESULT_NO            4

    // =========================
    // Screen struct
    // =========================
    typedef struct 
    {
        HWND hwnd;
        HDC hdc;
        HGLRC hglrc;
        int width;
        int height;

        int msaa_samples;   // 1,2,4,8,16 -> used by GPU backends
        int ssaa_scale;     // 1,2,4,8,16 -> CPU supersample scale (render target multiplier)


        // API OPTIONS
        bool use_opengl;
        bool use_vulkan;
        bool use_d3d12;

        // Vulkan handles
        HMODULE vk_lib;
        void*   vk_instance;
        void*   vk_device;
        void*   vk_surface;
        void*   vk_swapchain;

        // Direct3D 12 handles
        HMODULE        d3d12_lib;
        void*          d3d12_device;
        void*          d3d12_cmdqueue;
        void*          d3d12_swapchain;
    } CGameScreen;
    // =========================
    // Image subsystem
    // =========================
    typedef struct 
    {
        int width;
        int height;
        int channels;
        unsigned char* pixels;
        Gdiplus::Bitmap* gdi_bitmap;
        bool gpu_uploaded;
    } CGameImage;

    // =========================
    // Font subsystem
    // =========================
    typedef struct CGameFont
    {
        Gdiplus::PrivateFontCollection* collection;
        Gdiplus::FontFamily* family;
        WCHAR name[64];
        bool loaded;
    } CGameFont;




    // =========================
    // Key Constants
    // =========================
    enum {
        CGAME_K_UNKNOWN = 0,

        CGAME_K_a = 'A', CGAME_K_b = 'B', CGAME_K_c = 'C',
        CGAME_K_d = 'D', CGAME_K_e = 'E', CGAME_K_f = 'F',
        CGAME_K_g = 'G', CGAME_K_h = 'H', CGAME_K_i = 'I',
        CGAME_K_j = 'J', CGAME_K_k = 'K', CGAME_K_l = 'L',
        CGAME_K_m = 'M', CGAME_K_n = 'N', CGAME_K_o = 'O',
        CGAME_K_p = 'P', CGAME_K_q = 'Q', CGAME_K_r = 'R',
        CGAME_K_s = 'S', CGAME_K_t = 'T', CGAME_K_u = 'U',
        CGAME_K_v = 'V', CGAME_K_w = 'W', CGAME_K_x = 'X',
        CGAME_K_y = 'Y', CGAME_K_z = 'Z',

        CGAME_K_0 = '0', CGAME_K_1 = '1', CGAME_K_2 = '2',
        CGAME_K_3 = '3', CGAME_K_4 = '4', CGAME_K_5 = '5',
        CGAME_K_6 = '6', CGAME_K_7 = '7', CGAME_K_8 = '8',
        CGAME_K_9 = '9',

        CGAME_K_SPACE   = VK_SPACE,
        CGAME_K_RETURN  = VK_RETURN,
        CGAME_K_ESCAPE  = VK_ESCAPE,
        CGAME_K_LEFT    = VK_LEFT,
        CGAME_K_RIGHT   = VK_RIGHT,
        CGAME_K_UP      = VK_UP,
        CGAME_K_DOWN    = VK_DOWN,

        // NEW KEYS
        CGAME_K_LSHIFT  = VK_LSHIFT,
        CGAME_K_RSHIFT  = VK_RSHIFT,
        CGAME_K_LCTRL   = VK_LCONTROL,
        CGAME_K_RCTRL   = VK_RCONTROL,

        // ── Function keys ── NEW
        CGAME_K_F1      = VK_F1,  CGAME_K_F2  = VK_F2,  CGAME_K_F3  = VK_F3,
        CGAME_K_F4      = VK_F4,  CGAME_K_F5  = VK_F5,  CGAME_K_F6  = VK_F6,
        CGAME_K_F7      = VK_F7,  CGAME_K_F8  = VK_F8,  CGAME_K_F9  = VK_F9,
        CGAME_K_F10     = VK_F10, CGAME_K_F11 = VK_F11, CGAME_K_F12 = VK_F12,

        // ── Numpad keys ──   NEW
        CGAME_K_NUM0        = VK_NUMPAD0,
        CGAME_K_NUM1        = VK_NUMPAD1,
        CGAME_K_NUM2        = VK_NUMPAD2,
        CGAME_K_NUM3        = VK_NUMPAD3,
        CGAME_K_NUM4        = VK_NUMPAD4,
        CGAME_K_NUM5        = VK_NUMPAD5,
        CGAME_K_NUM6        = VK_NUMPAD6,
        CGAME_K_NUM7        = VK_NUMPAD7,
        CGAME_K_NUM8        = VK_NUMPAD8,
        CGAME_K_NUM9        = VK_NUMPAD9,
        CGAME_K_NUM_ADD     = VK_ADD,
        CGAME_K_NUM_SUB     = VK_SUBTRACT,
        CGAME_K_NUM_MUL     = VK_MULTIPLY,
        CGAME_K_NUM_DIV     = VK_DIVIDE,
        CGAME_K_NUM_DECIMAL = VK_DECIMAL,
        CGAME_K_NUM_ENTER   = VK_RETURN
    };

    // =========================
    // Mouse Constants
    // =========================
    #define CGameMouseButtonLeft        1
    #define CGameMouseButtonRight       2
    #define CGameMouseButtonMiddle      3
    #define CGameMouseButtonX1          4
    #define CGameMouseButtonX2          5

    #define CGAME_MOUSEBUTTONDOWN       5
    #define CGAME_MOUSEBUTTONUP         6
    #define CGAME_MOUSEMOTION           7
    #define CGAME_MOUSEWHEEL            8


    // =========================
    // Internal globals
    // =========================
    static HINSTANCE    _cgame_hInstance            = NULL;
    static bool         _cgame_running              = true;
    static int          _cgame_event                = 0;
    static CGameScreen  _cgame_screen               = { 0 };
    static int          _cgame_display_flags        = 0;


    static COLORREF     _cgame_bgcolor              = RGB (0,0,0);
    static HDC          _cgame_memdc                = NULL;
    static HBITMAP      _cgame_membmp               = NULL;
    static HGDIOBJ      _cgame_oldbmp               = NULL;

    static WPARAM       _cgame_last_key             = 0;
    static bool         _cgame_key_state      [512] = { false };
    static bool         _cgame_key_prev_state [512] = { false };

    static bool         _cgame_mouse_state      [6] = { false }; // left,right,middle,X1,X2
    static bool         _cgame_mouse_prev       [6] = { false };
    static int          _cgame_mouse_x              = 0;
    static int          _cgame_mouse_y              = 0;
    static int          _cgame_mouse_wheel          = 0;

    // font 
    static Gdiplus::PrivateFontCollection _cgame_font_collection;

    // =========================
    // Forward declarations
    // =========================
    static inline void _cgame_make_backbuffer                  (int w, int h);
    static inline void _cgame_free_backbuffer                  (void);
    static inline int  _cgame_get_backbuffer_scale             (void);
    static inline void _cgame_key_poll_impl                    (void);
    static inline void _cgame_time_init_impl                   (void);
    static inline void _cgame_time_update_impl                 (void);
    static inline void _cgame_image_update_pixels_from_gdiplus (const Gdiplus::Bitmap* bmp, CGameImage* out);
    /* OPENGL THE GOAT :) */
    static inline bool _cgame_init_opengl      (HWND hwnd, HDC* hdc, HGLRC* hglrc);
    static inline void _cgame_cleanup_opengl   (HDC hdc, HGLRC hglrc);


    /* Vulkan stubs / runtime detection (lightweight) */
    static inline bool _cgame_init_vulkan      (HWND hwnd, HMODULE* vk_lib_out);
    static inline void _cgame_cleanup_vulkan   (HMODULE vk_lib);

    /* DIRECT X 12 */
    static inline bool _cgame_init_d3d12       (HWND hwnd, HMODULE* d3d12_lib_out);
    static inline void _cgame_cleanup_d3d12    (HMODULE d3d12_lib);


    /* small helper to centralize FillRect usage */
    static inline void _cgame_fill_dc          (HDC dc, int w, int h, COLORREF color);

    static WCHAR _cgame_window_title [256] = L"CGame Window";
    static HICON _cgame_window_icon        = NULL;

    // Simple box-filter downsample from src (rt_w x rt_h) to dst (w x h).
    // src and dst are tightly packed RGBA (4 bytes per pixel).
    static inline void _cgame_downsample_box_rgba_internal         (const unsigned char* src, int rt_w, int rt_h, unsigned char* dst, int w, int h, int scale)
    {
        if (!src || !dst || scale <= 1) return;

        const int sx = scale;
        const int sy = scale;
        const int area = sx * sy;

        for (int y = 0; y < h; ++y)
        {
            for (int x = 0; x < w; ++x)
            {
                uint32_t r = 0, g = 0, b = 0, a = 0;
                int baseY  = y * sy;
                int baseX  = x * sx;

                for (int yy = 0; yy < sy; ++yy)
                {
                    const unsigned char* row = src + ((size_t)(baseY + yy) * rt_w + baseX) * 4;
                    for (int xx = 0; xx < sx; ++xx)
                    {
                        b += row [xx * 4 + 0];
                        g += row [xx * 4 + 1];
                        r += row [xx * 4 + 2];
                        a += row [xx * 4 + 3];
                    }
                }

                unsigned char* out = dst + ((size_t)y * w + x) * 4;
                out[0] = (unsigned char)(b / area);
                out[1] = (unsigned char)(g / area);
                out[2] = (unsigned char)(r / area);
                out[3] = (unsigned char)(a / area);
            }
        }
    }
    static inline void _cgame_present_backbuffer_to_hdc            (HDC wnddc)
    {
        if (!wnddc) return;

        if (!_cgame_memdc || !_cgame_membmp)
        {
            _cgame_fill_dc (wnddc, _cgame_screen.width, _cgame_screen.height, _cgame_bgcolor);
            return;
        }

        BITMAP bm = { 0 };
        if (GetObject (_cgame_membmp, sizeof(BITMAP), &bm) == 0)
        {
            // Fallback to simple BitBlt if we can't query the DIB
            BitBlt (wnddc, 0, 0, _cgame_screen.width, _cgame_screen.height, _cgame_memdc, 0, 0, SRCCOPY);
            return;
        }

        int rt_w  = bm.bmWidth;
        int rt_h  = (bm.bmHeight < 0) ? -bm.bmHeight : bm.bmHeight;
        int dst_w = _cgame_screen.width;
        int dst_h = _cgame_screen.height;

        if (rt_w <= 0 || rt_h <= 0 || dst_w <= 0 || dst_h <= 0)
        {
            _cgame_fill_dc (wnddc, dst_w, dst_h, _cgame_bgcolor);
            return;
        }

        int scale = _cgame_get_backbuffer_scale ();
        if (scale <= 1)
        {
            // Direct blit is simplest and fastest
            if (!BitBlt        (wnddc, 0, 0, dst_w, dst_h, _cgame_memdc, 0, 0, SRCCOPY))
            {
                // If BitBlt fails, fill with background
                _cgame_fill_dc (wnddc, dst_w, dst_h, _cgame_bgcolor);
            }
            return;
        }

        BITMAPINFO bmi              = {};
        bmi.bmiHeader.biSize        = sizeof(BITMAPINFOHEADER);
        bmi.bmiHeader.biWidth       = rt_w;
        bmi.bmiHeader.biHeight      = -rt_h; 
        bmi.bmiHeader.biPlanes      = 1;
        bmi.bmiHeader.biBitCount    = 32;
        bmi.bmiHeader.biCompression = BI_RGB;

        size_t src_size = (size_t)rt_w * (size_t)rt_h * 4;
        unsigned char* src_pixels = (unsigned char*)malloc (src_size);
        if (!src_pixels)
        {
            BitBlt (wnddc, 0, 0, dst_w, dst_h, _cgame_memdc, 0, 0, SRCCOPY);
            return;
        }

        HBITMAP currentSelected = (HBITMAP)SelectObject (_cgame_memdc, _cgame_membmp);
        int got = GetDIBits (_cgame_memdc, _cgame_membmp, 0, rt_h, src_pixels, &bmi, DIB_RGB_COLORS);
        SelectObject        (_cgame_memdc, currentSelected);

        if (got == 0)
        {
            free   (src_pixels);
            BitBlt (wnddc, 0, 0, dst_w, dst_h, _cgame_memdc, 0, 0, SRCCOPY);
            return;
        }

        // Convert BGRA -> RGBA for downsample
        for (int i = 0; i < rt_w * rt_h; ++i)
        {
            unsigned char b        = src_pixels [i * 4 + 0];
            unsigned char g        = src_pixels [i * 4 + 1];
            unsigned char r        = src_pixels [i * 4 + 2];
            unsigned char a        = src_pixels [i * 4 + 3];
            src_pixels [i * 4 + 0] = r;
            src_pixels [i * 4 + 1] = g;
            src_pixels [i * 4 + 2] = b;
            src_pixels [i * 4 + 3] = a;
        }

        // Allocate dst and downsample
        size_t dst_size           = (size_t)dst_w * (size_t)dst_h * 4;
        unsigned char* dst_pixels = (unsigned char*)malloc (dst_size);
        if (!dst_pixels)
        {
            free   (src_pixels);
            BitBlt (wnddc, 0, 0, dst_w, dst_h, _cgame_memdc, 0, 0, SRCCOPY);
            return;
        }

        // Perform box downsample (re-using your internal function)
        _cgame_downsample_box_rgba_internal (src_pixels, rt_w, rt_h, dst_pixels, dst_w, dst_h, scale);

        // Convert back RGBA -> BGRA
        for (int i = 0; i < dst_w * dst_h; ++i)
        {
            unsigned char r        = dst_pixels [i * 4 + 0];
            unsigned char g        = dst_pixels [i * 4 + 1];
            unsigned char b        = dst_pixels [i * 4 + 2];
            unsigned char a        = dst_pixels [i * 4 + 3];
            dst_pixels [i * 4 + 0] = b;
            dst_pixels [i * 4 + 1] = g;
            dst_pixels [i * 4 + 2] = r;
            dst_pixels [i * 4 + 3] = a;
        }

        // Prepare BITMAPINFO for output (top-down)
        BITMAPINFO out_bmi              = {};
        out_bmi.bmiHeader.biSize        = sizeof (BITMAPINFOHEADER);
        out_bmi.bmiHeader.biWidth       =  dst_w;
        out_bmi.bmiHeader.biHeight      = -dst_h;
        out_bmi.bmiHeader.biPlanes      = 1;
        out_bmi.bmiHeader.biBitCount    = 32;
        out_bmi.bmiHeader.biCompression = BI_RGB;

        // SetDIBitsToDevice returns number of scan lines set; check it
        int lines = SetDIBitsToDevice (wnddc, 0, 0, dst_w, dst_h, 0, 0, 0, dst_h, dst_pixels, &out_bmi, DIB_RGB_COLORS);
        if (lines == 0)
        {
            // If SetDIBitsToDevice fails, fallback to BitBlt of the original memdc
            BitBlt (wnddc, 0, 0, dst_w, dst_h, _cgame_memdc, 0, 0, SRCCOPY);
        }

        free (src_pixels);
        free (dst_pixels);
    }

    // =========================
    // Win32 window procedure
    // =========================
    static inline LRESULT CALLBACK _cgame_WndProc (HWND hwnd, UINT msg, WPARAM wParam, LPARAM lParam) 
    {
        switch (msg) 
        {
            case WM_CLOSE      :
            {
                _cgame_running = false;
                DestroyWindow (hwnd);
                return 0;
            }
            case WM_DESTROY    :
            {
                _cgame_event   = CGAME_QUIT;
                PostQuitMessage (0);
                return 0;
            }
            case WM_SIZE       : 
            {
                int nw = LOWORD (lParam);
                int nh = HIWORD (lParam);

                // Only update if we have valid dimensions
                if (nw > 0 && nh > 0) {
                    _cgame_screen.width  = nw;
                    _cgame_screen.height = nh;
                    _cgame_event         = CGAME_VIDEORESIZE;

                    if (!_cgame_screen.use_opengl && !_cgame_screen.use_vulkan) 
                    {
                        _cgame_free_backbuffer ();
                        _cgame_make_backbuffer (nw, nh);
                    } else 
                    {
                        /* GPU-backed (OpenGL/Vulkan) — user should handle swapchain/viewport resizing */
                    }
                }
                return 0;
            }
            case WM_PAINT:
            {
                if (!_cgame_screen.use_opengl && !_cgame_screen.use_vulkan && !_cgame_screen.use_d3d12)
                {
                    PAINTSTRUCT ps;
                    HDC hdc = BeginPaint(hwnd, &ps);

                    if (_cgame_memdc && _cgame_membmp)
                    {
                        _cgame_present_backbuffer_to_hdc(hdc); // use BeginPaint HDC
                    }
                    else
                    {
                        HBRUSH brush = CreateSolidBrush(_cgame_bgcolor);
                        FillRect(hdc, &ps.rcPaint, brush);
                        DeleteObject(brush);
                    }

                    EndPaint(hwnd, &ps);
                }
                else
                {
                    // GPU path unchanged
                }
                break;
            }


            case WM_KEYDOWN    :
            {
                if (wParam < 512)
                {
                    _cgame_key_state [wParam] = true;
                    _cgame_last_key = wParam;
                }
                break;
            }
            case WM_KEYUP      :
            {
                if (wParam < 512) 
                {
                    _cgame_key_state [wParam] = false;
                }
                break;
            }
            case WM_LBUTTONDOWN:
            {
                _cgame_event = CGAME_MOUSEBUTTONDOWN;
                _cgame_mouse_state [CGameMouseButtonLeft] = true;
                return 0;
            }
            case WM_LBUTTONUP  :
            {
                _cgame_event = CGAME_MOUSEBUTTONUP;
                _cgame_mouse_state [CGameMouseButtonLeft] = false;
                return 0;
            }
            case WM_RBUTTONDOWN:
            {
                _cgame_event = CGAME_MOUSEBUTTONDOWN;
                _cgame_mouse_state [CGameMouseButtonRight] = true;
                return 0;
            }
            case WM_RBUTTONUP  :
            {
                _cgame_event = CGAME_MOUSEBUTTONUP;
                _cgame_mouse_state [CGameMouseButtonRight] = false;
                return 0;
            }
            case WM_MBUTTONDOWN:
            {
                _cgame_event = CGAME_MOUSEBUTTONDOWN;
                _cgame_mouse_state [CGameMouseButtonMiddle] = true;
                return 0;
            }
            case WM_MBUTTONUP:
            {
                _cgame_event = CGAME_MOUSEBUTTONUP;
                _cgame_mouse_state [CGameMouseButtonMiddle] = false;
                return 0;
            }
            case WM_XBUTTONDOWN:
            {
                int xbtn = HIWORD(wParam);
                if (xbtn == XBUTTON1) _cgame_mouse_state [CGameMouseButtonX1] = true;
                if (xbtn == XBUTTON2) _cgame_mouse_state [CGameMouseButtonX2] = true;
                _cgame_event = CGAME_MOUSEBUTTONDOWN;
                return 0;
            }
            case WM_XBUTTONUP:
            {
                int xbtn = HIWORD(wParam);
                if (xbtn == XBUTTON1) _cgame_mouse_state [CGameMouseButtonX1] = false;
                if (xbtn == XBUTTON2) _cgame_mouse_state [CGameMouseButtonX2] = false;
                _cgame_event = CGAME_MOUSEBUTTONUP;
                return 0;
            }
            case WM_MOUSEMOVE:
            {
                _cgame_event   = CGAME_MOUSEMOTION;
                _cgame_mouse_x = GET_X_LPARAM (lParam);
                _cgame_mouse_y = GET_Y_LPARAM (lParam);
                return 0;
            }
            case WM_MOUSEWHEEL:
            {
                _cgame_event       = CGAME_MOUSEWHEEL;
                _cgame_mouse_wheel = GET_WHEEL_DELTA_WPARAM(wParam) / WHEEL_DELTA;
                return 0;

            }
        }
        return DefWindowProc (hwnd, msg, wParam, lParam);
    }

    // =========================
    // Backbuffer helpers
    // =========================
    static inline void _cgame_fill_dc              (HDC dc, int w, int h, COLORREF color)
    {
        if (!dc || w <= 0 || h <= 0) return;
        HBRUSH brush = CreateSolidBrush (color);
        if (!brush) return;
        RECT rc = { 0, 0, w, h };
        FillRect     (dc, &rc, brush);
        DeleteObject (brush);
    }
    static inline int  _cgame_get_backbuffer_scale (void)
    {
        if (!_cgame_membmp || _cgame_screen.width <= 0 || _cgame_screen.height <= 0) return 1;

        BITMAP bm = { 0 };
        if (GetObject (_cgame_membmp, sizeof (BITMAP), &bm) == 0) return 1;

        int bb_w  = bm.bmWidth;
        int bb_h  = (bm.bmHeight <  0) ? -bm.bmHeight : bm.bmHeight;
        if (bb_w <= 0 ||    bb_h <= 0) return 1;

        int sx = bb_w / _cgame_screen.width;
        int sy = bb_h / _cgame_screen.height;
        if (sx < 1) sx = 1;
        if (sy < 1) sy = 1;
        return (sx < sy) ? sx : sy;
    }
    static inline void _cgame_make_backbuffer      (int w, int h)
    {
        if (!_cgame_screen.hwnd || w <= 0 || h <= 0) return;

        HDC wnddc = GetDC(_cgame_screen.hwnd);
        if (!wnddc) return;

        int scale = (_cgame_screen.ssaa_scale > 1) ? _cgame_screen.ssaa_scale : 1;
        int bb_w  = w * scale;
        int bb_h  = h * scale;
        if (bb_w <= 0 || bb_h <= 0) { ReleaseDC (_cgame_screen.hwnd, wnddc); return; }

        _cgame_free_backbuffer();

        _cgame_memdc = CreateCompatibleDC(wnddc);
        if (!_cgame_memdc) { ReleaseDC(_cgame_screen.hwnd, wnddc); return; }

        BITMAPINFO bmi              = {};
        bmi.bmiHeader.biSize        = sizeof(BITMAPINFOHEADER);
        bmi.bmiHeader.biWidth       = bb_w;
        bmi.bmiHeader.biHeight      = -bb_h; // top-down DIB
        bmi.bmiHeader.biPlanes      = 1;
        bmi.bmiHeader.biBitCount    = 32;
        bmi.bmiHeader.biCompression = BI_RGB;

        void* bits    = NULL;
        _cgame_membmp = CreateDIBSection (wnddc, &bmi, DIB_RGB_COLORS, &bits, NULL, 0);
        if (!_cgame_membmp)
        {
            DeleteDC  (_cgame_memdc);
            _cgame_memdc = NULL;
            ReleaseDC (_cgame_screen.hwnd, wnddc);
            return;
        }

        HGDIOBJ prev = SelectObject(_cgame_memdc, _cgame_membmp);
        if (!_cgame_oldbmp) _cgame_oldbmp = prev;
        COLORREF bg  = _cgame_bgcolor;
        HBRUSH brush = CreateSolidBrush (RGB (GetRValue (bg), GetGValue (bg), GetBValue (bg)));
        if (brush)
        {
            RECT rc = { 0, 0, bb_w, bb_h };
            FillRect     (_cgame_memdc, &rc, brush);
            DeleteObject (brush);
        }

        ReleaseDC (_cgame_screen.hwnd, wnddc);
    }
    static inline void _cgame_free_backbuffer      (void)
    {
        if (!_cgame_memdc) return;

        if (_cgame_oldbmp)
        {
            SelectObject (_cgame_memdc, _cgame_oldbmp);
            _cgame_oldbmp = NULL;
        }

        if (_cgame_membmp)
        {
            DeleteObject (_cgame_membmp);
            _cgame_membmp = NULL;
        }

        DeleteDC (_cgame_memdc);
        _cgame_memdc = NULL;
    }

    // =========================
    // OpenGL helpers
    // =========================
    static inline bool _cgame_init_opengl         (HWND hwnd, HDC* hdc, HGLRC* hglrc)
    {
        if (!hwnd || !hdc || !hglrc) return false;

        PIXELFORMATDESCRIPTOR pfd =
        {
            sizeof (PIXELFORMATDESCRIPTOR),
            1,
            PFD_DRAW_TO_WINDOW | PFD_SUPPORT_OPENGL | PFD_DOUBLEBUFFER,
            PFD_TYPE_RGBA,
            32, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            24, 8, 0,
            PFD_MAIN_PLANE,
            0, 0, 0, 0
        };

        *hdc            = GetDC (hwnd);
        if (!*hdc) return false;
        int pixelFormat = ChoosePixelFormat (*hdc, &pfd);
        if (!pixelFormat)
        {
            ReleaseDC(hwnd, *hdc);
            *hdc = NULL;
            return false;
        }
        if (!SetPixelFormat (*hdc, pixelFormat, &pfd))
        {
            ReleaseDC (hwnd, *hdc);
            *hdc = NULL;
            return false;
        }
        *hglrc = wglCreateContext (*hdc);
        if (!*hglrc)
        {
            ReleaseDC (hwnd, *hdc);
            *hdc = NULL;
            return false;
        }
        if (!wglMakeCurrent (*hdc, *hglrc))
        {
            wglDeleteContext (*hglrc);
            *hglrc = NULL;
            ReleaseDC (hwnd, *hdc);
            *hdc = NULL;
            return false;
        }
        return true;
    }
    static inline void _cgame_cleanup_opengl      (HDC hdc, HGLRC hglrc)
    {
        if (hglrc)
        {
            wglMakeCurrent   (NULL, NULL);
            wglDeleteContext (hglrc);
        }
        if (hdc && _cgame_screen.hwnd)
        {
            ReleaseDC (_cgame_screen.hwnd, hdc);
        }
    }

    // =========================
    // Vulkan helpers (lightweight runtime detection)
    //  - This does not implement a full Vulkan setup. It attempts to
    //    load the Vulkan runtime (vulkan-1.dll) so the host has Vulkan
    //    available. Full instance/device/swapchain creation is left to
    //    the user or later extension code.
    // =========================
    static inline bool _cgame_init_vulkan         (HWND hwnd, HMODULE* vk_lib_out)
     {
        if (!vk_lib_out) return false;
        *vk_lib_out = LoadLibraryA("vulkan-1.dll");
        if (!*vk_lib_out)
        {
            MessageBoxW (hwnd,
                        L"Vulkan runtime (vulkan-1.dll) not found.\nInstall Vulkan runtime/SDK or remove CGAME_VULKAN flag.",
                        L"CGame Vulkan Error",
                        MB_OK | MB_ICONERROR);
            return false;
        }
        /* We don't create a Vulkan instance here — this is a safe runtime detection
           scaffold so user code (or a later extension) can link Vulkan functions
           and create instance/device/swapchain as desired. */
        return true;
    }
    static inline void _cgame_cleanup_vulkan      (HMODULE vk_lib) 
    {
        if (vk_lib) 
        {
            FreeLibrary(vk_lib);
        }
    }
    // =========================
    // DIRECT X [12] 3D helpers
    // =========================
    static inline bool _cgame_init_d3d12          (HWND hwnd, HMODULE* d3d12_lib_out) 
    {
        *d3d12_lib_out = LoadLibraryA ("d3d12.dll");
        if (!*d3d12_lib_out) 
        {
            MessageBoxW (hwnd,
                L"Direct3D 12 runtime (d3d12.dll) not found.\nInstall latest DirectX runtime or remove CGAME_D3D12 flag.",
                L"CGame D3D12 Error",
                MB_OK | MB_ICONERROR);
            return false;
        }

        /* Full D3D12 setup (device, swapchain, command queue) left to user.
        We only load the runtime dynamically and provide placeholders. */
        return true;
    }
    static inline void _cgame_cleanup_d3d12       (HMODULE d3d12_lib)
    {
        if (d3d12_lib) FreeLibrary(d3d12_lib);
    }

    // =========================
    // SAFETY CHECK HELPERS
    // =========================
    static inline bool _cgame_safe_to_draw              () 
    {
        return (_cgame_memdc && _cgame_screen.hwnd && IsWindow (_cgame_screen.hwnd));
    }
    static inline bool _cgame_image_from_gdiplus_bitmap        (Gdiplus::Bitmap* bmp, CGameImage* out)
    {
        if (!bmp || !out) return false;

        UINT w            = bmp -> GetWidth  ();
        UINT h            = bmp -> GetHeight ();
        out -> width      = (int)w;
        out -> height     = (int)h;
        out -> channels   = 4;
        out -> gdi_bitmap = NULL;
        out -> pixels     = NULL;

        // Allocate pixel buffer (RGBA)
        size_t total      = (size_t)w * (size_t)h * 4;
        out -> pixels     = (unsigned char*) malloc (total);
        if (!out -> pixels) return false;

        // Lock the GDI+ bitmap and read pixels
        Gdiplus::Rect rect (0, 0, w, h);
        Gdiplus::BitmapData bd;
        if (bmp -> LockBits (&rect, Gdiplus::ImageLockModeRead, PixelFormat32bppPARGB, &bd) != Gdiplus::Ok)
        {
            free (out -> pixels);
            out -> pixels = NULL;
            return false;
        }

        for (UINT y = 0; y < h; ++y)
        {
            unsigned char* dstRow = out -> pixels + (size_t)y * w * 4;
            unsigned char* srcRow = (unsigned char*) bd.Scan0 + (size_t)y * bd.Stride;

            for (UINT x = 0; x < w; ++x)
            {
                unsigned char b  = srcRow [x*4 + 0];
                unsigned char g  = srcRow [x*4 + 1];
                unsigned char r  = srcRow [x*4 + 2];
                unsigned char a  = srcRow [x*4 + 3];

                dstRow [x*4 + 0] = r;
                dstRow [x*4 + 1] = g;
                dstRow [x*4 + 2] = b;
                dstRow [x*4 + 3] = a;
            }
        }

        bmp -> UnlockBits (&bd);

        // Clone the bitmap for GDI+ use
        out -> gdi_bitmap = bmp -> Clone (0, 0, w, h, PixelFormat32bppPARGB);
        return (out -> gdi_bitmap != NULL);
    }
    static inline void _cgame_image_update_pixels_from_gdiplus (const Gdiplus::Bitmap* bmp, CGameImage* out)
    {
        if (!bmp || !out) return;

        // Cast away const because GDI+ APIs are non-const even for read operations
        Gdiplus::Bitmap* nonConstBmp = const_cast <Gdiplus::Bitmap*> (bmp);

        out -> width                 = nonConstBmp -> GetWidth();
        out -> height                = nonConstBmp -> GetHeight();

        Gdiplus::Rect rect      (0, 0, out -> width, out -> height);
        Gdiplus::BitmapData bmpData;
        nonConstBmp -> LockBits (&rect, Gdiplus::ImageLockModeRead, PixelFormat32bppPARGB, &bmpData);

        int stride = bmpData.Stride;
        int w      = out -> width;
        int h      = out -> height;

        // Free any previous pixel buffer if reusing 'out'
        if (out -> pixels) free (out -> pixels);

        // Allocate new buffer (tightly packed RGBA)
        size_t size   = (size_t)w * (size_t)h * 4;
        out -> pixels = (unsigned char*)malloc (size);
        if (!out -> pixels)
        {
            nonConstBmp -> UnlockBits (&bmpData);
            return;
        }
        unsigned char* src = (unsigned char*)bmpData.Scan0;
        unsigned char* dst = out -> pixels;

        for (int y = 0; y < h; ++y)
        {
            unsigned char* srow = src + y * stride;
            unsigned char* drow = dst + y * w * 4;

            for (int x = 0; x < w; ++x)
            {
                unsigned char b = srow[x * 4 + 0];
                unsigned char g = srow[x * 4 + 1];
                unsigned char r = srow[x * 4 + 2];
                unsigned char a = srow[x * 4 + 3];
                drow[x * 4 + 0] = r;
                drow[x * 4 + 1] = g;
                drow[x * 4 + 2] = b;
                drow[x * 4 + 3] = a;
            }
        }

        nonConstBmp -> UnlockBits(&bmpData);
    }
    // =========================
    // IMAGE SYSTEM
    // =========================
    static inline CGameImage _cgame_image_load_impl                   (const char * path)
    {
        CGameImage img = {0, 0, 0, NULL, NULL};
        if (!path) return img;

        // Ensure GDI+ is initialized
        if (!_cgame_gdiplus_inited) 
        {
            Gdiplus::GdiplusStartupInput input;
            Gdiplus::GdiplusStartup (&_cgame_gdiplusToken, &input, NULL);
            _cgame_gdiplus_inited = true;
        }

        // Convert UTF-8 → wide
        int len = MultiByteToWideChar (CP_UTF8, 0, path, -1, NULL, 0);
        if                            (len <= 0) return img;

        wchar_t* wpath = (wchar_t*)malloc (len * sizeof  (wchar_t));
        if               (!wpath) return img;

        MultiByteToWideChar           (CP_UTF8, 0, path, -1, wpath, len);

        // Load GDI+ Bitmap
        Gdiplus::Bitmap* bmp = Gdiplus::Bitmap::FromFile (wpath, FALSE);
        free (wpath);

        if (!bmp || bmp -> GetLastStatus() != Gdiplus::Ok) 
        {
            if (bmp) delete bmp;
            return img;
        }

        // Fill struct
        img.width      = bmp -> GetWidth  ();
        img.height     = bmp -> GetHeight ();
        img.channels   = 4;
        img.gdi_bitmap = bmp;

        // Extract tightly packed RGBA pixel data
        _cgame_image_update_pixels_from_gdiplus (bmp, &img);
        return img;
    }
    static inline CGameImage _cgame_image_load_from_memory_impl       (const void* data, size_t size)
    {
        CGameImage img = {0, 0, 0, NULL, NULL};
        if (!data || size == 0) { return img; }

        // Ensure GDI+ is initialized
        if (!_cgame_gdiplus_inited)
        {
            Gdiplus::GdiplusStartupInput input;
            Gdiplus::GdiplusStartup (&_cgame_gdiplusToken, &input, NULL);
            _cgame_gdiplus_inited = true;
        }

        // Create IStream over memory buffer
        HGLOBAL hMem    = GlobalAlloc (GMEM_MOVEABLE, size);
        if (!hMem) return img;
        void* pMem      = GlobalLock (hMem);
        memcpy                  (pMem, data, size);
        GlobalUnlock            (hMem);
        IStream* stream = NULL;
        if (CreateStreamOnHGlobal (hMem, TRUE, &stream) != S_OK) 
        {
            GlobalFree (hMem);
            return img;
        }

        // Load GDI+ Bitmap from stream
        Gdiplus::Bitmap* bmp = Gdiplus::Bitmap::FromStream (stream, FALSE);
        stream->Release(); // stream owns hMem now (TRUE flag)

        if (!bmp || bmp->GetLastStatus () != Gdiplus::Ok) 
        {
            if (bmp) delete bmp;
            return img;
        }

        // Fill struct
        img.width      = bmp->GetWidth  ();
        img.height     = bmp->GetHeight ();
        img.channels   = 4;
        img.gdi_bitmap = bmp;

        // Extract tightly packed RGBA pixel data
        _cgame_image_update_pixels_from_gdiplus (bmp, &img);
        return img;
    }

    // Free image
    static inline void _cgame_image_free_impl                  (CGameImage* img)
    {
        if (!img) return;

        // 1. Delete bitmap first
        if (img -> gdi_bitmap) 
        {
            delete img -> gdi_bitmap;
            img -> gdi_bitmap = NULL;
        }

        // 2. Only free pixels if not GPU uploaded
        if (img -> pixels && !img -> gpu_uploaded) 
        {
            free (img -> pixels);
            img -> pixels = NULL;
        }

        // 3. Reset metadata
        img -> width = img -> height = img -> channels = 0;
        img -> gpu_uploaded = false;
    }
    static inline void _cgame_image_unload_impl                (CGameImage* img)
    {
        if (!img) return;

        // If the texture was uploaded to GPU, make sure OpenGL side is cleaned first.
        // The caller should already call glDeleteTextures() before this.
        _cgame_image_free_impl (img);
    }
    // Create nearest-neighbour resized copy
    static inline CGameImage _cgame_image_resize_nearest_impl  (const CGameImage* img, int new_w, int new_h)
    {
        CGameImage out = {0, 0, 0, NULL, NULL};
        if (!img || (!img -> pixels && !img -> gdi_bitmap)) return out;

        out.width    = new_w;
        out.height   = new_h;
        out.channels = 4;

        // --------------- GDI+ PATH (for CPU drawing) ---------------
        if (img -> gdi_bitmap) {
            Gdiplus::Bitmap* target = new Gdiplus::Bitmap(new_w, new_h, PixelFormat32bppPARGB);
            Gdiplus::Graphics g(target);
            g.SetInterpolationMode(Gdiplus::InterpolationModeNearestNeighbor);
            g.SetCompositingMode(Gdiplus::CompositingModeSourceOver);
            g.Clear(Gdiplus::Color(0, 0, 0, 0));
            g.DrawImage(img -> gdi_bitmap, 0, 0, new_w, new_h);
            out.gdi_bitmap = target;
        }

        // --------------- PIXEL PATH (for GPU) ---------------
        if (img -> pixels) {
            size_t total = (size_t)new_w * (size_t)new_h * 4;
            out.pixels = (unsigned char*)malloc(total);
            if (out.pixels) {
                for (int y = 0; y < new_h; ++y) {
                    int sy = y * img -> height / new_h;
                    for (int x = 0; x < new_w; ++x) {
                        int sx = x * img -> width / new_w;
                        const unsigned char* sp = img -> pixels + ((size_t)sy * img -> width + sx) * 4;
                        unsigned char* dp = out.pixels + ((size_t)y * new_w + x) * 4;
                        memcpy(dp, sp, 4);
                    }
                }
            }
        }

        return out;
    }
    // Flip horizontal (in-place)
    static inline CGameImage _cgame_image_flip_horizontal_impl (const CGameImage* img)
    {
        CGameImage out = { 0, 0, 0, NULL, NULL };
        if (!img || (!img -> pixels && !img -> gdi_bitmap)) return out;

        int w        = img -> width;
        int h        = img -> height;
        out.width    = w;
        out.height   = h;
        out.channels = 4;

        // --- GDI+ path ---
        if (img -> gdi_bitmap) 
        {
            Gdiplus::Bitmap*  target = new Gdiplus::Bitmap(w, h, PixelFormat32bppPARGB);
            Gdiplus::Graphics g (target);
            Gdiplus::Matrix   m;
            m.Scale          (-1.f, 1.f);
            m.Translate      ((Gdiplus::REAL)-w, 0.f);
            g.SetTransform   (&m);
            g.DrawImage      (img -> gdi_bitmap, 0, 0, w, h);
            g.ResetTransform ();
            out.gdi_bitmap = target;
        }

        // --- Pixel path ---
        if (img -> pixels) 
        {
            size_t total = (size_t)w * (size_t)h * 4;
            out.pixels   = (unsigned char*)malloc (total);
            if (!out.pixels) return out;  // <-- guard added

            for (int y = 0; y < h; ++y) 
            {
                const unsigned char* imgRow = img -> pixels + (size_t)y * w * 4;
                unsigned char* dstRow       = out.pixels    + (size_t)y * w * 4;

                for (int x = 0; x < w; ++x) 
                {
                    const unsigned char* sp = imgRow + (size_t)(w - 1 - x) * 4;
                    unsigned char* dp       = dstRow + (size_t)x * 4;

                    if ((size_t)(y * w * 4 + x * 4 + 4) <= total) memcpy(dp, sp, 4);
                }
            }
        }
        return out;
    }
    static inline CGameImage _cgame_image_flip_vertical_impl   (const CGameImage* img)
    {
        CGameImage out = {0, 0, 0, NULL, NULL};
        if (!img || (!img -> pixels && !img -> gdi_bitmap)) return out;

        int w        = img -> width;
        int h        = img -> height;
        out.width    = w;
        out.height   = h;
        out.channels = 4;

        // --- GDI+ path for CPU ---
        if (img -> gdi_bitmap) 
        {
            Gdiplus::Bitmap*  target = new Gdiplus::Bitmap (w, h, PixelFormat32bppPARGB);
            Gdiplus::Graphics g(target);
            Gdiplus::Matrix   m;
            m.Scale          (1.f, -1.f);
            m.Translate      (0.f, (Gdiplus::REAL)-h);
            g.SetTransform   (&m);
            g.DrawImage      (img -> gdi_bitmap, 0, 0, w, h);
            g.ResetTransform ();
            out.gdi_bitmap = target;
        }

        // --- Pixel path for GPU ---
        // --- Pixel path for GPU ---
        if (img -> pixels) 
        {
            size_t total = (size_t)w * (size_t)h * 4;
            out.pixels   = (unsigned char*)malloc(total);
            if (!out.pixels) return out;  // <-- ssssaafeguard for analyzer and runtime

            for (int y = 0; y < h; ++y) 
            {
                const unsigned char* srow = img -> pixels + (size_t)(h - 1 - y) * w * 4;
                unsigned char* drow       = out.pixels    + (size_t)y * w * 4;
                memcpy                         (drow, srow, (size_t)w * 4);
            }
        }
        return out;
    }
    // Draw image at (x,y). If image has HBITMAP, use AlphaBlend with compatible DC.
    static inline void _cgame_image_draw_impl(const CGameImage* img, int x, int y)
    {
        if (!img || !img->gdi_bitmap || !_cgame_memdc) return;

        int offset = 1;

        // Skip drawing if image is completely outside the screen
        if (x + img->width           + offset < 0) return;                
        if (y + img->height          + offset < 0) return;               
        if (x > _cgame_screen.width  + offset    ) return;            
        if (y > _cgame_screen.height + offset    ) return;            

        Gdiplus::Graphics g    (_cgame_memdc);
        g.SetCompositingMode   (Gdiplus::CompositingModeSourceOver);
        g.SetInterpolationMode (Gdiplus::InterpolationModeNearestNeighbor);
        g.SetSmoothingMode     (Gdiplus::SmoothingModeHighQuality);

        g.DrawImage(img->gdi_bitmap, (Gdiplus::REAL)x, (Gdiplus::REAL)y, (Gdiplus::REAL)img->width, (Gdiplus::REAL)img->height);
    }
   // Draw a specific portion of an image (sprite-sheet frame)
    static inline void _cgame_image_draw_advanced_impl         (const CGameImage* img, int x, int y, int xImage, int yImage, int wImage, int hImage)
    {
        if (!img || !img -> gdi_bitmap || !_cgame_memdc) return;
        int offset = 1;

        // Skip drawing if image is completely outside the screen
        if (x + img->width           + offset < 0) return;                
        if (y + img->height          + offset < 0) return;               
        if (x > _cgame_screen.width  + offset    ) return;            
        if (y > _cgame_screen.height + offset    ) return;
        Gdiplus::Graphics     g(_cgame_memdc);
        g.SetCompositingMode   (Gdiplus::CompositingModeSourceOver);
        g.SetInterpolationMode (Gdiplus::InterpolationModeNearestNeighbor);
        g.SetSmoothingMode     (Gdiplus::SmoothingModeNone);

        // Source rectangle defines which part of the image to draw
        Gdiplus::Rect srcRect (xImage, yImage, wImage, hImage);

        // Destination rectangle defines where and how large it appears on screen
        Gdiplus::Rect destRect (x, y, wImage, hImage);

        g.DrawImage (img -> gdi_bitmap,
                    destRect,
                    srcRect.X, srcRect.Y, srcRect.Width, srcRect.Height,
                    Gdiplus::UnitPixel);
    }
    static inline void _cgame_image_draw_rotated_impl          (const CGameImage* img, int x, int y, float angle_deg)
    {
        if (!img || !img -> gdi_bitmap || !_cgame_memdc) return;

        const int src_w = img -> width;
        const int src_h = img -> height;

        // --- Compute expanded bounding box ---
        double radians = angle_deg * 3.14159265358979323846 / 180.0;
        double cosA    = fabs (cos (radians));
        double sinA    = fabs (sin (radians));

        int new_w      = int (src_w * cosA + src_h * sinA + 0.5);
        int new_h      = int (src_w * sinA + src_h * cosA + 0.5);

        // --- Create an offscreen ARGB bitmap big enough for the rotated image ---
        Gdiplus::Bitmap target       (new_w, new_h, PixelFormat32bppPARGB);
        Gdiplus::Graphics g          (&target);
        g.SetCompositingMode         (Gdiplus::CompositingModeSourceOver);
        g.SetInterpolationMode       (Gdiplus::InterpolationModeHighQualityBicubic);
        g.SetSmoothingMode           (Gdiplus::SmoothingModeHighQuality);
        g.Clear                      (Gdiplus::Color(0, 0, 0, 0));

        // --- Rotate around center of the new canvas ---
        g.TranslateTransform         ((Gdiplus::REAL)new_w / 2.0f, (Gdiplus::REAL)new_h / 2.0f);
        g.RotateTransform            ((Gdiplus::REAL)angle_deg);
        g.TranslateTransform         (-(Gdiplus::REAL)src_w / 2.0f, -(Gdiplus::REAL)src_h / 2.0f);
        g.DrawImage                  (img -> gdi_bitmap, 0, 0, src_w, src_h);
        g.ResetTransform             ();

        // --- Now blend this rotated result directly to the main memory DC ---
        Gdiplus::Graphics gscreen    (_cgame_memdc);
        gscreen.SetCompositingMode   (Gdiplus::CompositingModeSourceOver);
        gscreen.SetInterpolationMode (Gdiplus::InterpolationModeHighQualityBicubic);
        gscreen.DrawImage            (&target, x - new_w / 2, y - new_h / 2, new_w, new_h);
    }
    static inline CGameImage _cgame_image_rotate_impl          (const CGameImage* img, float angle) 
    {
        CGameImage out = {0, 0, 0, NULL, NULL};
        if (!img || !img -> gdi_bitmap) return out;

        double radians = angle * M_PI / 180.0;
        double cosA    = fabs (cos (radians));
        double sinA    = fabs (sin (radians));
        int new_w      = int(img -> width * cosA + img -> height * sinA + 0.5);
        int new_h      = int(img -> width * sinA + img -> height * cosA + 0.5);

        Gdiplus::Bitmap target (new_w, new_h, PixelFormat32bppPARGB);
        Gdiplus::Graphics g    (&target);
        g.SetCompositingMode   (Gdiplus::CompositingModeSourceOver);
        g.SetInterpolationMode (Gdiplus::InterpolationModeHighQualityBicubic);
        g.SetSmoothingMode     (Gdiplus::SmoothingModeHighQuality);
        g.Clear                (Gdiplus::Color(0, 0, 0, 0));

        g.TranslateTransform   ((Gdiplus::REAL)new_w / 2.0f, (Gdiplus::REAL)new_h / 2.0f);
        g.RotateTransform      ((Gdiplus::REAL)angle);
        g.TranslateTransform   (-(Gdiplus::REAL)img -> width / 2.0f, -(Gdiplus::REAL)img -> height / 2.0f);
        g.DrawImage            (img -> gdi_bitmap, 0, 0, img -> width, img -> height);
        g.ResetTransform       ();

        _cgame_image_from_gdiplus_bitmap (&target, &out);
        return out;
    }
    // Draw scaled (new_w,new_h)
    static inline void _cgame_image_draw_scaled_impl           (const CGameImage* img, int x, int y, int new_w, int new_h) 
    {
        if (!img || !img -> pixels) return;
        // create nearest-resized temp and draw
        CGameImage tmp = _cgame_image_resize_nearest_impl (img, new_w, new_h);
        _cgame_image_draw_impl                            (&tmp, x, y);
        _cgame_image_unload_impl                          (&tmp);
    }
    // Getters
    static inline int  _cgame_image_get_width_impl             (const CGameImage* img) { return img ? img -> width    : 0; }
    static inline int  _cgame_image_get_height_impl            (const CGameImage* img) { return img ? img -> height   : 0; }
    static inline int  _cgame_image_get_channels_impl          (const CGameImage* img) { return img ? img -> channels : 0; }

    static inline HICON _cgame_create_icon_from_image          (const CGameImage* img) 
    {
        if (!img || !img -> pixels) return NULL;

        // Prepare BITMAPV5HEADER for 32-bit ARGB
        BITMAPV5HEADER bi;
        ZeroMemory                 (&bi, sizeof(bi));
        bi.bV5Size        = sizeof (BITMAPV5HEADER);
        bi.bV5Width       =  img -> width;
        bi.bV5Height      = -img -> height; // top-down
        bi.bV5Planes      = 1;
        bi.bV5BitCount    = 32;
        bi.bV5Compression = BI_BITFIELDS;
        bi.bV5RedMask     =  0x00FF0000;
        bi.bV5GreenMask   =  0x0000FF00;
        bi.bV5BlueMask    =  0x000000FF;
        bi.bV5AlphaMask   =  0xFF000000;

        HDC hdc           = GetDC (NULL);
        void* bits        = NULL;
        HBITMAP colorBmp  = CreateDIBSection (hdc, (BITMAPINFO*)&bi, DIB_RGB_COLORS, &bits, NULL, 0);
        ReleaseDC (NULL, hdc);
        if (!colorBmp || !bits) 
        {
            if (colorBmp) DeleteObject (colorBmp);
            return NULL;
        }

        // Copy pixels (straight RGBA → BGRA with alpha)
        int w = img -> width, h = img -> height, c = img -> channels;
        for (int y = 0; y < h; ++y) 
        {
            for (int x = 0; x < w; ++x) 
            {
                unsigned char* dst       = (unsigned char*)bits + (y * w + x) * 4;
                const unsigned char* src = img -> pixels + ((y * w + x) * c);

                dst[0] = src[2]; // B
                dst[1] = src[1]; // G
                dst[2] = src[0]; // R
                dst[3] = (c >= 4) ? src[3] : 255; // A
            }
        }

        // Create monochrome mask (unused but required)
        HBITMAP maskBmp = CreateBitmap(w, h, 1, 1, NULL);
        ICONINFO ii;
        ZeroMemory (&ii, sizeof (ii));
        ii.fIcon    = TRUE;
        ii.xHotspot = 0;
        ii.yHotspot = 0;
        ii.hbmMask  = maskBmp;
        ii.hbmColor = colorBmp;

        HICON hIcon = CreateIconIndirect (&ii);

        DeleteObject (colorBmp);
        DeleteObject (maskBmp);
        return hIcon;
    }

    static inline bool _cgame_display_set_icon_from_image_impl (const CGameImage* img) 
    {
        if (!img) return false;
        //  Prevent setting icon on undecorated windows
        if (_cgame_display_flags & CGAME_FLAG_UNDECORATED) 
        {
            MessageBoxW (NULL,
                L"Cannot set window icon on an undecorated (borderless) window.",
                L"CGame Error",
                MB_OK | MB_ICONERROR);
            return false;
        }

        HICON hIcon = _cgame_create_icon_from_image (img);
        if (!hIcon) return false;

        _cgame_window_icon = hIcon;
        if (_cgame_screen.hwnd) 
        {
            SendMessage (_cgame_screen.hwnd, WM_SETICON, ICON_BIG,   (LPARAM)hIcon);
            SendMessage (_cgame_screen.hwnd, WM_SETICON, ICON_SMALL, (LPARAM)hIcon);
        }

        return true;
    }
    
    // =========================
    // TERMINAL FUNCTIONS
    // =========================
    static inline void _cgame_console_set_color_impl           (int fg, int bg) 
    {
        HANDLE hConsole = GetStdHandle (STD_OUTPUT_HANDLE);
        SetConsoleTextAttribute        (hConsole, (WORD)((bg << 4) | (fg & 0x0F)));
    }
    static inline void _cgame_console_reset_color_impl         (void) 
    {
        HANDLE hConsole = GetStdHandle (STD_OUTPUT_HANDLE);
        SetConsoleTextAttribute        (hConsole, (WORD)(CGAME_CONSOLE_COLOR_WHITE | (CGAME_CONSOLE_COLOR_BLACK << 4)));
    }
    static inline void _cgame_console_clear_impl               (void) 
    {
        HANDLE hConsole = GetStdHandle (STD_OUTPUT_HANDLE);
        CONSOLE_SCREEN_BUFFER_INFO csbi;
        DWORD  cellCount, count;
        COORD  homeCoords = { 0, 0 };

        if (hConsole == INVALID_HANDLE_VALUE) return;

        if (!GetConsoleScreenBufferInfo(hConsole, &csbi)) return;
        cellCount = csbi.dwSize.X * csbi.dwSize.Y;

        FillConsoleOutputCharacter (hConsole, (TCHAR)' ', cellCount, homeCoords, &count);
        FillConsoleOutputAttribute (hConsole, csbi.wAttributes, cellCount, homeCoords, &count);
        SetConsoleCursorPosition   (hConsole, homeCoords);
    }

    // =========================
    // MESSAGE BOX FUNCTIONS
    // =========================
    static inline int _cgame_message_box_impl                  (const char* title, const char* text, UINT type)
    {
        int lenTitle    = MultiByteToWideChar (CP_UTF8, 0, title, -1, NULL, 0);
        wchar_t* wTitle = (wchar_t*)malloc    (lenTitle * sizeof (wchar_t));
        if     (!wTitle) return -1;
        MultiByteToWideChar                   (CP_UTF8, 0, title, -1, wTitle, lenTitle);

        // Convert text
        int lenText    = MultiByteToWideChar (CP_UTF8, 0, text, -1, NULL, 0);
        wchar_t* wText = (wchar_t*)malloc    (lenText * sizeof (wchar_t));
        if (!wText) { free (wTitle); return -1; }
        MultiByteToWideChar                  (CP_UTF8, 0, text, -1, wText, lenText);

        // Call wide version of MessageBox
        int result = MessageBoxW(NULL, wText, wTitle, type);

        // Clean up
        free(wTitle);
        free(wText);

        switch (result)
        {
            case IDOK    :  return CGAME_MSGBOX_RESULT_OK;
            case IDCANCEL:  return CGAME_MSGBOX_RESULT_CANCEL;
            case IDYES   :  return CGAME_MSGBOX_RESULT_YES;
            case IDNO    :  return CGAME_MSGBOX_RESULT_NO;
            case 0       :  return -1;
            default:        return -1;
        }
    }

    // =========================
    // CORE FUNCTIONS
    // =========================
    static inline void _cgame_init_impl                        (void) 
    {
        _cgame_hInstance = GetModuleHandleW (NULL);
        _cgame_running   = true;
        _cgame_event     = 0;

        // Start GDI+ (if not already)
        if (!_cgame_gdiplus_inited) 
        {
            Gdiplus::GdiplusStartupInput gdiplusStartupInput;
            if (GdiplusStartup (&_cgame_gdiplusToken, &gdiplusStartupInput, NULL) == Gdiplus::Ok) 
            {
                _cgame_gdiplus_inited = true;
            }
        }
        _cgame_time_init_impl ();
    }
    static inline void _cgame_quit_impl                        (void) 
    {
        _cgame_running = false;
        if (_cgame_screen.hwnd) 
        {
            if (_cgame_screen.use_opengl) 
            {
                _cgame_cleanup_opengl (_cgame_screen.hdc, _cgame_screen.hglrc);
            } else if (_cgame_screen.use_vulkan) 
            {
                _cgame_cleanup_vulkan (_cgame_screen.vk_lib);
            } else if (_cgame_screen.use_d3d12) 
            {
                _cgame_cleanup_d3d12 (_cgame_screen.d3d12_lib);
            } else 
            {
                if (_cgame_screen.hdc) ReleaseDC (_cgame_screen.hwnd, _cgame_screen.hdc);
            }
            DestroyWindow (_cgame_screen.hwnd);
        }
        _cgame_free_backbuffer ();
        UnregisterClassW       (L"CGameWindowClass", _cgame_hInstance);

        // Shutdown GDI+ if inited
        if (_cgame_gdiplus_inited) 
        {
            Gdiplus::GdiplusShutdown (_cgame_gdiplusToken);
            _cgame_gdiplus_inited = false;
            _cgame_gdiplusToken   = 0;
        }
    }

    // =========================
    // DISPLAY FUNCTIONS
    // =========================
    static inline CGameScreen   _cgame_set_mode_impl           (int w, int h, int flags) 
    {
    if (_cgame_screen.hwnd)
    {
        DestroyWindow(_cgame_screen.hwnd);
        _cgame_screen.hwnd = NULL;
    }

        // --- Check conflicting GPU API flags ---
        int gpu_api_count = (!!(flags & CGAME_FLAG_OPENGL)) +
                            (!!(flags & CGAME_FLAG_VULKAN)) +
                            (!!(flags & CGAME_FLAG_D3D12));
        if (gpu_api_count > 1) 
        {
            MessageBoxW (NULL,
                L"Cannot combine multiple GPU APIs.\nChoose only one: OpenGL, Vulkan, or Direct3D 12.",
                L"CGame Error",
                MB_OK | MB_ICONERROR);
            return _cgame_screen;
        }

        // --- MSAA flags validation ---
        int msaa_flags_count = 0;
        int requested_samples = 0;
        if (flags & CGAME_FLAG_MSAA_X2 ) { msaa_flags_count++; requested_samples = 2; }
        if (flags & CGAME_FLAG_MSAA_X4 ) { msaa_flags_count++; requested_samples = 4; }
        if (flags & CGAME_FLAG_MSAA_X8 ) { msaa_flags_count++; requested_samples = 8; }
        if (flags & CGAME_FLAG_MSAA_X16) { msaa_flags_count++; requested_samples = 16; }

        if (msaa_flags_count > 1)
        {
            // More than one MSAA flag set -> warn and default to x2
            MessageBoxW (NULL,
                L"Multiple MSAA flags set. Defaulting to MSAA x2.",
                L"CGame MSAA Warning",
                MB_OK | MB_ICONWARNING);
            requested_samples = 2;
        }

        // If no MSAA flag set, requested_samples remains 0 -> treat as disabled (1)
        if (requested_samples <= 1) requested_samples = 1;

        if (flags & CGAME_FLAG_DPI_AWARE) SetProcessDPIAware ();

        // --- Register window class ---
        WNDCLASSW wc     = {0};
        wc.style         = CS_HREDRAW | CS_VREDRAW;
        wc.lpfnWndProc   = _cgame_WndProc;
        wc.hInstance     = _cgame_hInstance;
        wc.hCursor       = LoadCursor (NULL, IDC_ARROW);
        wc.lpszClassName = L"CGameWindowClass";
        static bool class_registered = false;
        if (!class_registered)
        {
            RegisterClassW(&wc);
            class_registered = true;
        }


        // --- Window style ---
        DWORD style      = WS_OVERLAPPEDWINDOW;

        // Undecorated (borderless) window
        if      (flags & CGAME_FLAG_UNDECORATED) 
        {
            style = WS_POPUP | WS_MINIMIZEBOX | WS_SYSMENU;
        }
        else if (!(flags & CGAME_FLAG_RESIZABLE)) 
        {
            style &= ~WS_THICKFRAME;
            style &= ~WS_MAXIMIZEBOX;
        }

        // --- Adjust rect for client size ---
        RECT rect     = {0, 0, w, h};
        AdjustWindowRect (&rect, style, FALSE);
        int adjWidth  = rect.right - rect.left;
        int adjHeight = rect.bottom - rect.top;

        // --- Create window ---
        HWND hwnd = CreateWindowExW (
            0,
            wc.lpszClassName,
            (_cgame_window_title[0] != L'\0') ? _cgame_window_title : L"CGame Window",
            style,
            CW_USEDEFAULT, CW_USEDEFAULT, adjWidth, adjHeight,
            NULL, NULL, _cgame_hInstance, NULL
        );

        if (flags & CGAME_FLAG_UNDECORATED) 
        {
            RECT screenRect;
            GetWindowRect (GetDesktopWindow (), &screenRect);
            int posX =    (screenRect.right - adjWidth) / 2;
            int posY =    (screenRect.bottom - adjHeight) / 2;
            SetWindowPos  (hwnd, nullptr, posX, posY, adjWidth, adjHeight, SWP_NOZORDER | SWP_NOACTIVATE);
        }
        if (!hwnd) 
        {
            MessageBoxW (NULL, L"Failed to create window.", L"CGame Error", MB_OK | MB_ICONERROR);
            return _cgame_screen;
        }
        _cgame_screen.hwnd = hwnd;

        // --- Apply stored title (if set after creation, it still updates) ---
        if (_cgame_window_title[0]) 
        {
            SetWindowTextW (hwnd, _cgame_window_title);
        }

        // --- Apply stored icon (if any) ---
        if (_cgame_window_icon) 
        {
            SendMessage (hwnd, WM_SETICON, ICON_BIG,   (LPARAM)_cgame_window_icon);
            SendMessage (hwnd, WM_SETICON, ICON_SMALL, (LPARAM)_cgame_window_icon);
        }

        ShowWindow   (hwnd, SW_SHOW);
        UpdateWindow (hwnd);

        // --- Fill screen struct basic flags ---
        _cgame_screen.use_opengl      = (flags & CGAME_FLAG_OPENGL) != 0;
        _cgame_screen.use_vulkan      = (flags & CGAME_FLAG_VULKAN) != 0;
        _cgame_screen.use_d3d12       = (flags & CGAME_FLAG_D3D12) != 0;

        // Initialize GPU handles to NULL
        _cgame_screen.vk_lib          = NULL;
        _cgame_screen.vk_instance     = NULL;
        _cgame_screen.vk_device       = NULL;
        _cgame_screen.vk_surface      = NULL;
        _cgame_screen.vk_swapchain    = NULL;

        _cgame_screen.d3d12_lib       = NULL;
        _cgame_screen.d3d12_device    = NULL;
        _cgame_screen.d3d12_cmdqueue  = NULL;
        _cgame_screen.d3d12_swapchain = NULL;

        // --- Get actual client area size ---
        RECT clientRect;
        GetClientRect (hwnd, &clientRect);
        _cgame_screen.width  = clientRect.right  - clientRect.left;
        _cgame_screen.height = clientRect.bottom - clientRect.top ;

        // --- MSAA / SSAA decision ---
        // Ensure the CGameScreen struct contains: int msaa_samples; int ssaa_scale;
        _cgame_screen.msaa_samples = 1;
        _cgame_screen.ssaa_scale   = 1;

        if (_cgame_screen.use_opengl || _cgame_screen.use_vulkan || _cgame_screen.use_d3d12)
        {
            // GPU path: expose requested sample count for engine to use when creating pixel formats / swapchains
            _cgame_screen.msaa_samples = requested_samples;
            _cgame_screen.ssaa_scale   = 1; // GPU will handle multisampling
        }
        else
        {
            // CPU path: use integer supersample scale equal to requested_samples (SSAA)
            // Note: very large scales are expensive; warn if scale >= 4
            _cgame_screen.msaa_samples = 1;
            _cgame_screen.ssaa_scale   = requested_samples;
            if (_cgame_screen.ssaa_scale >= 8)
            {
                MessageBoxW (NULL,
                    L"High CPU SSAA scale requested. This may consume large amounts of memory and be very slow.",
                    L"CGame SSAA Warning",
                    MB_OK | MB_ICONWARNING);
            }
        }

        // --- Choose API and create contexts / backbuffers ---
        if (_cgame_screen.use_opengl) 
        {
            if (!_cgame_init_opengl (hwnd, &_cgame_screen.hdc, &_cgame_screen.hglrc)) 
            {
                DestroyWindow (hwnd);
                _cgame_screen.hwnd = NULL;
            }
        } 
        else if (_cgame_screen.use_vulkan) 
        {
            if (!_cgame_init_vulkan(hwnd, &_cgame_screen.vk_lib)) 
            {
                DestroyWindow(hwnd);
                _cgame_screen.hwnd = NULL;
            } 
            else 
            {
                _cgame_screen.hdc = NULL; // Vulkan doesn’t use GDI
            }
        } 
        else if (_cgame_screen.use_d3d12) 
        {
            if (!_cgame_init_d3d12 (hwnd, &_cgame_screen.d3d12_lib)) 
            {
                DestroyWindow (hwnd);
                _cgame_screen.hwnd = NULL;
            } else 
            {
                _cgame_screen.hdc  = NULL; // D3D12 doesn’t use GDI
            }
        } 
        else 
        {
            // CPU/GDI backbuffer
            _cgame_screen.hdc = GetDC (hwnd);

            // If CPU SSAA is enabled, create a larger backbuffer to render into
            int bb_w = _cgame_screen.width;
            int bb_h = _cgame_screen.height;
            if (_cgame_screen.ssaa_scale > 1)
            {
                // Multiply client size by scale for SSAA render target
                // Be cautious about overflow; clamp to a reasonable maximum if desired
                bb_w = _cgame_screen.width  * _cgame_screen.ssaa_scale;
                bb_h = _cgame_screen.height * _cgame_screen.ssaa_scale;
            }

            _cgame_make_backbuffer (bb_w, bb_h);
        }

        _cgame_display_flags = flags;
        return _cgame_screen;
    }
    static inline void _cgame_display_set_title_impl           (const char * title) 
    {
        if (!title) return;
        //  Prevent setting title on undecorated windows
        if (_cgame_display_flags & CGAME_FLAG_UNDECORATED)
        {
            MessageBoxW(NULL,
                L"Cannot set window title on an undecorated (borderless) window.",
                L"CGame Error",
                MB_OK | MB_ICONERROR);
            return;
        }

        // --- Existing title logic ---
        _cgame_window_title[0] = L'\0';
        int len = MultiByteToWideChar (
            CP_UTF8,
            MB_ERR_INVALID_CHARS,
            title, -1,
            _cgame_window_title,
            255
        );

        if (len == 0) wcscpy_s (_cgame_window_title, 256, L"CGame Window");
        if (_cgame_screen.hwnd) 
        {
            if (!SetWindowTextW (_cgame_screen.hwnd, _cgame_window_title)) 
            {
                MessageBoxW     (NULL, L"SetWindowTextW failed!", L"CGame Debug", MB_OK);
            }
        }
    }
    static inline bool _cgame_display_set_icon_impl            (const char * path) 
    {
        if (!path) return false;
        //  Prevent setting icon on undecorated windows
        if (_cgame_display_flags & CGAME_FLAG_UNDECORATED) 
        {
            MessageBoxW (NULL,
                L"Cannot set window icon on an undecorated (borderless) window.",
                L"CGame Error",
                MB_OK | MB_ICONERROR);
            return false;
        }

        int wlen     = MultiByteToWideChar (CP_UTF8, 0, path, -1, NULL, 0);
        WCHAR* wpath = (WCHAR*)malloc      (wlen * sizeof (WCHAR));
        MultiByteToWideChar                (CP_UTF8, 0, path, -1, wpath, wlen);
        HICON hIcon  = NULL; //  Declare here so it’s in full scope

        if   (wpath) 
        {
            hIcon   = (HICON)LoadImageW(NULL, wpath, IMAGE_ICON, 0, 0,
                LR_LOADFROMFILE | LR_DEFAULTSIZE | LR_SHARED);
            if (hIcon && _cgame_screen.hwnd) 
            {
                SendMessageW (_cgame_screen.hwnd, WM_SETICON, ICON_BIG,   (LPARAM)hIcon);
                SendMessageW (_cgame_screen.hwnd, WM_SETICON, ICON_SMALL, (LPARAM)hIcon);
            }
        }
        free (wpath);
        if   (!hIcon) return false;
        _cgame_window_icon = hIcon;
        return true;
    }
    static inline void _cgame_display_clear_impl         (int r, int g, int b) 
    {
        _cgame_bgcolor = RGB (r,g,b);
        if (!_cgame_screen.use_opengl && !_cgame_screen.use_vulkan && _cgame_memdc) 
        {
            _cgame_fill_dc (_cgame_memdc, _cgame_screen.width, _cgame_screen.height, _cgame_bgcolor);
        }
        /* For OpenGL/Vulkan the bg color is stored in _cgame_bgcolor,
           but clearing should be done by the user's rendering code (glClear / vkCmdClearAttachments). */
    }

    static inline void _cgame_display_flip_impl                (void) 
    {
        if      (!_cgame_screen.hwnd) return;
        if      (_cgame_screen.use_opengl) 
        {
            SwapBuffers(_cgame_screen.hdc);
        } 
        else if (_cgame_screen.use_vulkan) 
        {
            /* For Vulkan mode, the user must call vkQueuePresentKHR / present their swapchain.
               This library only performs runtime detection and provides placeholders. */
        } 
        else 
        {
            HDC wnddc = GetDC    (_cgame_screen.hwnd);
            if                   (wnddc && _cgame_memdc) 
            {
                BitBlt           (wnddc, 0, 0, _cgame_screen.width, _cgame_screen.height, _cgame_memdc, 0, 0, SRCCOPY);
            }
            if (wnddc) ReleaseDC (_cgame_screen.hwnd, wnddc);
        }
    }
    static inline int  _cgame_display_get_width_impl           (void) { return _cgame_screen.width ; }
    static inline int  _cgame_display_get_height_impl          (void) { return _cgame_screen.height; }
    static inline int  _cgame_display_get_monitor_width_impl   (void)
    {
        DEVMODE             dm ;
        dm.dmSize = sizeof (dm);
        if (EnumDisplaySettings (NULL, ENUM_CURRENT_SETTINGS, &dm)) 
        {
            return dm.dmPelsWidth;   // physical width
        }
        return GetSystemMetrics (SM_CXSCREEN); // fallback
    }
    static inline int  _cgame_display_get_monitor_height_impl  (void) 
    {
        DEVMODE             dm ;
        dm.dmSize = sizeof (dm);
        if (EnumDisplaySettings (NULL, ENUM_CURRENT_SETTINGS, &dm)) 
        {
            return dm.dmPelsHeight;  // physical height
        }
        return GetSystemMetrics (SM_CYSCREEN); // fallback
    }
    static inline void _cgame_display_set_pos_impl             (int x, int y) 
    {
        if           (!_cgame_screen.hwnd) return;
        SetWindowPos (_cgame_screen.hwnd, nullptr, x, y, 0, 0, SWP_NOSIZE | SWP_NOZORDER);
    }
    static inline int  _cgame_display_get_posX_impl            (void) 
    {
        if            (!_cgame_screen.hwnd) return 0;
        RECT rect;
        GetWindowRect (_cgame_screen.hwnd, &rect);
        return rect.left;
    }
    static inline int  _cgame_display_get_posY_impl            (void) 
    {
        if            (!_cgame_screen.hwnd) return 0;
        RECT rect;
        GetWindowRect (_cgame_screen.hwnd, &rect);
        return rect.top;
    }
    static inline void _cgame_display_center_impl              (void) 
    {
        if (!_cgame_screen.hwnd) return;
        RECT rect;
        GetWindowRect (_cgame_screen.hwnd, &rect);
        int width   = rect.right - rect.left;
        int height  = rect.bottom - rect.top;

        int screenW = GetSystemMetrics (SM_CXSCREEN);
        int screenH = GetSystemMetrics (SM_CYSCREEN);
        int posX    = (screenW - width ) / 2;
        int posY    = (screenH - height) / 2;
        SetWindowPos  (_cgame_screen.hwnd, nullptr, posX, posY, 0, 0, SWP_NOSIZE | SWP_NOZORDER);
    }
    static inline void _cgame_display_focus_impl               (void) 
    {
        if                  (!_cgame_screen.hwnd) return;
        SetForegroundWindow (_cgame_screen.hwnd);
    }
    static inline void _cgame_display_minimize_impl            (void) 
    {
        if         (!_cgame_screen.hwnd) return;
        ShowWindow (_cgame_screen.hwnd, SW_MINIMIZE);
    }
    static inline void _cgame_display_restore_impl             (void) 
    {
        if         (!_cgame_screen.hwnd) return;
        ShowWindow (_cgame_screen.hwnd, SW_SHOW);
    }

    // =========================
    // DRAWING FUNCTIONS
    // =========================
    static inline void _cgame_draw_fillrect_impl               (int x, int y, int w, int h, int r, int g, int b) 
    {
        if (!_cgame_memdc || _cgame_screen.use_opengl || _cgame_screen.use_vulkan) return;
        int offset = 1;
        if (x + w                    + offset < 0) return;                
        if (y + h                    + offset < 0) return;               
        if (x > _cgame_screen.width  + offset    ) return;            
        if (y > _cgame_screen.height + offset    ) return;
        HBRUSH brush = CreateSolidBrush (RGB (r,g,b));
        RECT rc = { x, y, x + w, y + h };
        FillRect                        (_cgame_memdc, &rc, brush);
        DeleteObject                    (brush);
    }
    static inline void _cgame_draw_rect_impl                   (int x, int y, int w, int h, int border_width, int r, int g, int b) 
    {
        if (!_cgame_memdc || _cgame_screen.use_opengl || _cgame_screen.use_vulkan) return;
        int offset = 1;
        if (x + w                    + offset < 0) return;                
        if (y + h                    + offset < 0) return;               
        if (x > _cgame_screen.width  + offset    ) return;            
        if (y > _cgame_screen.height + offset    ) return;
        // Create a pen with custom thickness
        HPEN pen         = CreatePen    (PS_SOLID, border_width, RGB  (r, g, b));
        HGDIOBJ oldPen   = SelectObject (_cgame_memdc, pen);
        HGDIOBJ oldBrush = SelectObject (_cgame_memdc, GetStockObject (NULL_BRUSH));

        // Draw rectangle
        Rectangle (_cgame_memdc, x, y, x + w, y + h);

        // Restore old objects
        SelectObject (_cgame_memdc, oldPen);
        SelectObject (_cgame_memdc, oldBrush);
        DeleteObject (pen);
    }
    // -------------------------
    // Polygon drawing
    // -------------------------
    static inline void _cgame_draw_polygon_impl                (const int* xs, const int* ys, int count, int border_width, int r, int g, int b) 
    {
        if (!_cgame_memdc || !xs || !ys || count < 2) return;

        Gdiplus::Graphics gdi (_cgame_memdc);
        gdi.SetSmoothingMode  (Gdiplus::SmoothingModeHighQuality);

        Gdiplus::Pen pen      (Gdiplus::Color(255, r, g, b),  (Gdiplus::REAL)border_width);

        Gdiplus::Point* pts = (Gdiplus::Point*)malloc (sizeof (Gdiplus::Point) * count);
        if (!pts)       return; //  protect against NULL before dereferencing

        for (int i = 0; i < count; i++) 
        {
            pts[i] = Gdiplus::Point (xs[i], ys[i]);
        }
        gdi.DrawPolygon (&pen, pts, count);
        free            (pts);
    }
    static inline void _cgame_draw_fill_polygon_impl           (const int* xs, const int* ys, int count, int r, int g, int b) 
    {
        if (!_cgame_memdc || !xs || !ys || count < 3) return;

        Gdiplus::Graphics   gdi   (_cgame_memdc);
        Gdiplus::SolidBrush brush (Gdiplus::Color (255, r, g, b));

        Gdiplus::Point*     pts = (Gdiplus::Point*)malloc (sizeof (Gdiplus::Point) * count);
        if (!pts)           return; //  avoid dereferencing NULL

        for (int i = 0; i < count; i++)
        {
            pts [i] = Gdiplus::Point (xs [i], ys [i]);
        }
        gdi.FillPolygon (&brush, pts, count);
        free            (pts);
    }
    static inline void _cgame_draw_line_impl                   (int x1, int y1, int x2, int y2, int border_width, int r, int g, int b)
    {
        if (!_cgame_memdc) return;

        // Construct COLORREF from r,g,b
        COLORREF color = RGB(r, g, b);

        // Use the border_width parameter
        HPEN pen = CreatePen(PS_SOLID, border_width, color);
        if (!pen) return;

        HGDIOBJ oldPen = SelectObject(_cgame_memdc, pen);

        MoveToEx(_cgame_memdc, x1, y1, NULL);
        LineTo(_cgame_memdc, x2, y2);

        // Restore previous pen and cleanup
        SelectObject(_cgame_memdc, oldPen);
        DeleteObject(pen);
    }

    // -------------------------
    // Rounded rectangle drawing
    // -------------------------
    static inline Gdiplus::GraphicsPath* _cgame_create_rounded_rect_path    (int x, int y, int w, int h, int radius) 
    {
        Gdiplus::GraphicsPath* path = new Gdiplus::GraphicsPath   ();
        int diameter                = radius * 2;
        if                  (diameter > w) diameter  = w;
        if                  (diameter > h) diameter  = h;

        path -> AddArc      (x, y, diameter, diameter, 180, 90);
        path -> AddArc      (x + w - diameter, y, diameter, diameter, 270, 90);
        path -> AddArc      (x + w - diameter, y + h - diameter, diameter, diameter, 0, 90);
        path -> AddArc      (x, y + h - diameter, diameter, diameter, 90, 90);
        path -> CloseFigure ();
        return path;
    }
    static inline void                   _cgame_draw_rounded_rect_impl      (int x, int y, int w, int h, int radius, int border_width, int r, int g, int b) 
    {
        if                    (!_cgame_memdc) return;
        int offset = 1;
        if (x + w                    + offset < 0) return;                
        if (y + h                    + offset < 0) return;               
        if (x > _cgame_screen.width  + offset    ) return;            
        if (y > _cgame_screen.height + offset    ) return;
        Gdiplus::Graphics gdi (_cgame_memdc);
        Gdiplus::Pen pen      (Gdiplus::Color (255, r, g, b), (Gdiplus::REAL)border_width);
        Gdiplus::GraphicsPath* path = _cgame_create_rounded_rect_path (x, y, w, h, radius);
        gdi.DrawPath                                                  (&pen, path);
        delete path;
    }
    static inline void                   _cgame_draw_rounded_fill_rect_impl (int x, int y, int w, int h, int radius, int r, int g, int b) 
    {
        if                        (!_cgame_memdc) return;
        int offset = 1;
        if (x + w                    + offset < 0) return;                
        if (y + h                    + offset < 0) return;               
        if (x > _cgame_screen.width  + offset    ) return;            
        if (y > _cgame_screen.height + offset    ) return;
        Gdiplus::Graphics gdi     (_cgame_memdc);
        Gdiplus::SolidBrush brush (Gdiplus::Color (255, r, g, b));
        Gdiplus::GraphicsPath* path = _cgame_create_rounded_rect_path (x, y, w, h, radius);
        gdi.FillPath                                                  (&brush, path);
        delete path;
    }
    // -------------------------
    // Circle drawing 
    // -------------------------
    static inline void _cgame_draw_circle_impl                 (int x, int y, int radius, int border_width, int r, int g, int b) 
    {
        if (!_cgame_memdc) return;

        // Determine actual backbuffer scale (1 if not scaled)
        int actual_scale = _cgame_get_backbuffer_scale();

        // Convert logical/window coords -> backbuffer coords
        int sx  = x * actual_scale;
        int sy  = y * actual_scale;
        int sr  = radius * actual_scale;
        int sbw = (border_width > 0) ? border_width * actual_scale : 1;

        
        int offset = 1;
        int diameter = sr * 2;

        // Bounding box of circle
        int left   = sx - sr;
        int top    = sy - sr;
        int right  = sx + sr;
        int bottom = sy + sr;

        // Skip drawing if completely outside screen
        if (right                         + offset < 0) return;                     
        if (bottom                        + offset < 0) return;                       
        if (left   > _cgame_screen.width  + offset    ) return;     
        if (top    > _cgame_screen.height + offset    ) return;     

        // GDI+ draw
        Gdiplus::Graphics gdi(_cgame_memdc);
        gdi.SetSmoothingMode(Gdiplus::SmoothingModeAntiAlias);

        Gdiplus::Pen pen(Gdiplus::Color(255, r, g, b), (Gdiplus::REAL)sbw);

        gdi.DrawEllipse(&pen, sx - sr, sy - sr, diameter, diameter);
    }
    static inline void _cgame_draw_fill_circle_impl            (int x, int y, int radius, int r, int g, int b) 
    {
        if (!_cgame_memdc) return;

        int actual_scale = _cgame_get_backbuffer_scale();

        int sx = x * actual_scale;
        int sy = y * actual_scale;
        int sr = radius * actual_scale;
        
        int offset = 1;
        int diameter = sr * 2;

        // Bounding box of circle
        int left   = sx - sr;
        int top    = sy - sr;
        int right  = sx + sr;
        int bottom = sy + sr;

        // Skip drawing if completely outside screen
        if (right                         + offset < 0) return;                     
        if (bottom                        + offset < 0) return;                       
        if (left   > _cgame_screen.width  + offset    ) return;     
        if (top    > _cgame_screen.height + offset    ) return;     

        Gdiplus::Graphics gdi(_cgame_memdc);
        gdi.SetSmoothingMode(Gdiplus::SmoothingModeAntiAlias);

        Gdiplus::SolidBrush brush(Gdiplus::Color(255, r, g, b));

        gdi.FillEllipse(&brush, sx - sr, sy - sr, diameter, diameter);
    }

    // =========================
    // EVENT FUNCTIONS
    // =========================
    static inline int  _cgame_event_get_impl                    (void)
    {
        // Update delta-time + enforce FPS cap
        _cgame_time_update_impl ();
        MSG msg;
        _cgame_key_poll_impl    ();
        while (PeekMessageW(&msg, _cgame_screen.hwnd, 0, 0, PM_REMOVE))
        {
            if (msg.message == WM_QUIT) 
            {
                return CGAME_QUIT;
            }
            TranslateMessage (&msg);
            DispatchMessageW (&msg);

            if (_cgame_event != 0) 
            {
                int    ev    = _cgame_event;
                _cgame_event = 0;
                return ev;
            }
        }
        return 0;
    }

    // =========================
    // TEXT FUNCTIONS
    // =========================
    static inline void _cgame_text_draw_impl                    (const char * text, int x, int y, int r, int g, int b) 
    {
        if (!_cgame_memdc || !text) return;
        Gdiplus::Graphics   gdi   (_cgame_memdc);
        Gdiplus::SolidBrush brush (Gdiplus::Color (255, r, g, b));
        Gdiplus::Font       font  (L"Arial", 16); // default font, size 16
        WCHAR wtext [512];
        MultiByteToWideChar       (CP_UTF8, 0, text, -1, wtext, 512);
        gdi.DrawString            (wtext, -1, &font, Gdiplus::PointF ((Gdiplus::REAL)x, (Gdiplus::REAL)y), &brush);
    }
    // -------------------------
    // Load custom font (TTF file)
    // -------------------------
    static inline CGameFont _cgame_text_load_font_impl          (const char* filename)
    {
        CGameFont font = {0};
        // Initialize GDI+ once
        if (!_cgame_gdiplus_inited)
        {
            Gdiplus::GdiplusStartupInput input;
            if (Gdiplus::GdiplusStartup (&_cgame_gdiplusToken, &input, NULL) != Gdiplus::Ok) { return font; }
            _cgame_gdiplus_inited = true;
        }

        // Convert UTF-8 filename → UTF-16
        int wlen = MultiByteToWideChar (CP_UTF8, 0, filename, -1, NULL, 0);
        if (wlen <= 0) return font;

        std::wstring wpath;
        wpath.resize        (wlen);
        MultiByteToWideChar (CP_UTF8, 0, filename, -1, wpath.data (), wlen);

        // Create font collection
        font.collection = new Gdiplus::PrivateFontCollection ();

        // Attempt to load TTF file
        if (font.collection -> AddFontFile (wpath.c_str ()) != Gdiplus::Ok)
        {
            delete font.collection;
            font.collection = NULL;
            return font;
        }

        // Check for families inside the font
        INT count = font.collection -> GetFamilyCount ();
        if (count <= 0)
        {
            delete font.collection;
            font.collection = NULL;
            return font;
        }

        // Read family
        font.family = new Gdiplus::FontFamily ();
        INT found   = 0;
        font.collection -> GetFamilies (1, font.family, &found);

        if (!found)
        {
            delete font.collection;
            font.collection = NULL;
            delete font.family;
            font.family     = NULL;
            return font;
        }

        font.family -> GetFamilyName (font.name);
        font.loaded = true;
        return font;
    }
    static inline void _cgame_text_unload_font_impl             (CGameFont* font)
    {
        if (!font) { return; }
        // Free FontFamily
        if (font -> family  ) { delete font -> family; font -> family = nullptr; }

        // Free PrivateFontCollection
        if (font->collection) { delete font -> collection; font -> collection = nullptr; }
        // Reset metadata
        font->loaded  = false;
        font->name[0] = L'\0';
    }

    // -------------------------
    // Draw text with loaded TTF font
    // -------------------------
    static inline void _cgame_text_draw_complex_impl            (const char* text, int x, int y, CGameFont* font, float size, int r, int g, int b)
    {
        if (!text || !font || !font -> loaded || !font -> family) { return; }
        if (!_cgame_memdc)                                        { return; }

        // UTF-8 → UTF-16
        int wlen = MultiByteToWideChar (CP_UTF8, 0, text, -1, NULL, 0);
        if (wlen <= 0) { return; }

        std::wstring wtext;
        wtext.resize        (static_cast<size_t> (wlen));
        MultiByteToWideChar (CP_UTF8, 0, text, -1, wtext.data (), wlen);

        // Draw into backbuffer
        Gdiplus::Graphics gfx    (_cgame_memdc);
        gfx.SetTextRenderingHint (Gdiplus::TextRenderingHintAntiAlias);

        Gdiplus::Font drawFont    (font -> family, size);
        Gdiplus::SolidBrush brush (Gdiplus::Color(255, (BYTE)r, (BYTE)g, (BYTE)b));

        gfx.DrawString            (wtext.c_str(), -1, &drawFont, Gdiplus::PointF ((float)x, (float)y), &brush);
    }

    // =========================
    // KEYBOARD FUNCTIONS
    // =========================
    // -------------------------
    // poll all virtual-key codes into the arrays. Call this exactly once per frame.
    // -------------------------
    static inline void   _cgame_key_poll_impl                   (void)
    {
        // Copy key states
        for (int i = 0; i < 512; ++i)
        {
            _cgame_key_prev_state [i] = _cgame_key_state  [i];
        }
        for (int i = 0; i < 6; ++i)
        {
            _cgame_mouse_prev     [i] = _cgame_mouse_state[i];
        }

    }
    static inline bool   _cgame_key_held_impl                   (int key) 
    {
        if (key < 0 || key >= 512) return false;
        return _cgame_key_state [key];
    }
    static inline bool   _cgame_key_pressed_impl                (int key) 
    {
        if (key < 0 || key >= 512) return false;
        return _cgame_key_state [key] && !_cgame_key_prev_state [key];
    }
    static inline bool   _cgame_key_released_impl               (int key) 
    {
        if (key < 0 || key >= 512) return false;
        return !_cgame_key_state [key] && _cgame_key_prev_state [key];
    }
    static inline WPARAM _cgame_key_last_impl                   (void) { return _cgame_last_key; }


    // =========================
    // TIME FUNCTIONS
    // =========================
    static LARGE_INTEGER _cgame_freq         = {0};
    static LARGE_INTEGER _cgame_start_time   = {0};
    static LARGE_INTEGER _cgame_last_time    = {0};
    static float         _cgame_last_dt      = 0.016f;
    static float         _cgame_last_fps     = 60.0f;
    static float         _cgame_frame_target = 0.0f;
    static double        _cgame_next_frame   = 0.0;
    // -------------------------
    // Initialize high-resolution timer
    // -------------------------
    static inline void _cgame_time_init_impl                     (void)
    {
        timeBeginPeriod           (1); // enable 1 ms sleep precision
        QueryPerformanceFrequency (&_cgame_freq);
        QueryPerformanceCounter   (&_cgame_start_time);
        _cgame_last_time   = _cgame_start_time;
        _cgame_next_frame  = 0.0;
    }
    // -------------------------
    // Set target FPS (0 = uncapped)
    // -------------------------
    static inline void _cgame_time_set_fps_impl                  (int fps)
    {
        if (fps > 0) _cgame_frame_target = 1.0f / (float)fps;
        else         _cgame_frame_target = 0.0f;

        LARGE_INTEGER            now;
        QueryPerformanceCounter (&now);
        double time_now   =     (double) (now.QuadPart - _cgame_start_time.QuadPart) / (double)_cgame_freq.QuadPart;
        _cgame_next_frame = time_now + _cgame_frame_target;
    }
    // -------------------------
    // Update timing (to be called every frame inside event.get())
    // -------------------------
    static inline void _cgame_time_update_impl                   (void)
    {
        if (_cgame_freq.QuadPart == 0) _cgame_time_init_impl ();
        LARGE_INTEGER             now;
        QueryPerformanceCounter (&now);

        double current_time = (double) (now.QuadPart - _cgame_start_time.QuadPart) / (double)_cgame_freq.QuadPart;
        // ---------------------------
        // Frame limiter (accurate)
        // ---------------------------
        if (_cgame_frame_target > 0.0f)
        {
            while (current_time < _cgame_next_frame)
            {
                float remain = (float) (_cgame_next_frame - current_time);

                if (remain > 0.002f) Sleep(1); // coarse wait (ms-level)
                else
                {
                    // micro busy-wait for last few hundred µs
                    do 
                    {
                        QueryPerformanceCounter (&now);
                        current_time =  (double)(now.QuadPart - _cgame_start_time.QuadPart) / (double)_cgame_freq.QuadPart;
                    } while (current_time < _cgame_next_frame);
                    break;
                }
                QueryPerformanceCounter (&now);
                current_time = (double) (now.QuadPart - _cgame_start_time.QuadPart)  / (double)_cgame_freq.QuadPart;
            }
        }
        // ---------------------------
        // Delta and FPS calculation
        // ---------------------------
        float diff = (float)  ((double) (now.QuadPart - _cgame_last_time.QuadPart) / (double)_cgame_freq.QuadPart);
        if (diff < 0.000001f) diff = 0.000016f;

        _cgame_last_dt   = (_cgame_last_dt * 0.9f) + (diff * 0.1f); // smoother
        _cgame_last_fps  = 1.0f / _cgame_last_dt;
        _cgame_last_time = now;
        if (_cgame_frame_target > 0.0f) _cgame_next_frame += _cgame_frame_target;
    }
    // -------------------------
    // Public getters
    // -------------------------
    static inline float _cgame_time_get_dt_impl                  (void) { return _cgame_last_dt ; }
    static inline float _cgame_time_get_fps_impl                 (void) { return _cgame_last_fps; }

    // =========================
    // MOUSE FUNCTIONS
    // =========================
    static inline bool _cgame_mouse_pressed_impl                 (int btn)  { return (btn >= 0 && btn < 6) ? _cgame_mouse_state[btn] && !_cgame_mouse_prev[btn] : false; }
    static inline bool _cgame_mouse_held_impl                    (int btn)  { return (btn >= 0 && btn < 6) ? _cgame_mouse_state[btn] : false; }
    static inline bool _cgame_mouse_released_impl                (int btn)  { return (btn >= 0 && btn < 6) ? !_cgame_mouse_state[btn] && _cgame_mouse_prev[btn] : false; }
    static inline int  _cgame_mouse_get_posX_impl                (void) {return _cgame_mouse_x;}
    static inline int  _cgame_mouse_get_posY_impl                (void) {return _cgame_mouse_y;}
    static inline int  _cgame_mouse_get_globalX_impl             (void) 
    {
        POINT p;
        GetCursorPos (&p);
        return p.x;
    }
    static inline int _cgame_mouse_get_globalY_impl              (void) 
    {
        POINT p;
        GetCursorPos (&p);
        return p.y;
    }
    static inline void _cgame_mouse_set_pos_impl                 (int x, int y) 
    {
        _cgame_mouse_x = x;
        _cgame_mouse_y = y;
        if (_cgame_screen.hwnd) 
        {
            POINT pt = {x, y};
            ClientToScreen (_cgame_screen.hwnd, &pt);
            SetCursorPos   (pt.x, pt.y);
        }
    }
    static inline int _cgame_mouse_get_wheel_impl                (void) 
    {
        int delta          = _cgame_mouse_wheel;
        _cgame_mouse_wheel = 0; // reset after read
        return delta;
    }

    // ==================
    // CGAME VERSION FUNCTIONS
    // ==================
    static inline const char * _cgame_version_get_impl           (void) 
    {
        static char buffer [50];  // Static so it persists after function returns
        sprintf (buffer, "%d.%d VERSION [WINDOWS]", CGAME_VERSION_MAJOR, CGAME_VERSION_MINOR);
        return  buffer;
    }
    static inline const char * _cgame_version_get_patch_impl     (void)
    {
        static char buffer [60];
        sprintf (buffer, "%d PATCH VERSION [WINDOWS]", CGAME_VERSION_PATCH);
        return  buffer;
    }

#elif defined (linux)

// |---------------------------------------------------------------------------|
//     []   []     [][][] []  [] []  [] []  []
//      []  []       []   [][ [] []  []  [][]
// [][][][] []       []   [][][] []  []   []
//      []  []       []   [] ][] []  []  [][]
//     []   [][][] [][][] []  []  [][]  []  []
// |---------------------------------------------------------------------------|

#elif defined (MACOS)

// |---------------------------------------------------------------------------|
//     []   []    []   []    [][]  [][]    [][]
//      []  [][][][] []  [] []    []  [] []
// [][][][] [] [] [] [][][] []    []  [] [][][]
//      []  []    [] []  [] []    []  []     []
//     []   []    [] []  []  [][]  [][]  [][]
// |---------------------------------------------------------------------------|

    #include <macos.h>
#error "cgame.h only supports Windows"
#endif

// |---------------------------------------------------------------------------|
//     []   [][][] []  [] [][]   []     [][][]  [][]       []   [][][] [][][]
//      []  []  [] []  [] []  [] []       []   []        []  [] []  []   []
// [][][][] [][][] []  [] [][]   []       []   []        [][][] [][][]   []
//      []  []     []  [] []  [] []       []   []        []  [] []       []
//     []   []      [][]  [][]   [][][] [][][]  [][]     []  [] []     [][][]
// |---------------------------------------------------------------------------|

    static struct 
    {
        void (*init)(void);
        void (*quit)(void);

        struct 
        {
            CGameScreen (*set_mode)(int w, int h, int flags);
            void (*clear)(int r, int g, int b);
            void (*flip)(void);
            int  (*get_width)(void);
            int  (*get_height)(void);
            int  (*get_monitor_width)  (void);
            int  (*get_monitor_height) (void);
            void (*set_pos)(int x, int y);
            void (*center)(void);
            int  (*get_posX)(void);
            int  (*get_posY)(void);
            void (*focus)(void);
            void (*minimize) (void);
            void (*restore) (void);
            void (*set_title)(const char * title);
            bool (*set_icon)(const char * path);
            bool (*set_icon_from_image)(const CGameImage* img);
        } display;


        // console reset and set color
        struct 
        {
            void (*set_color)(int fg, int bg);
            void (*reset_color)(void);
            void (*clear) (void);
        } console;

        // msg box show 
        struct 
        {
            int (*show)(const char* title, const char* text, unsigned int type);
        } messagebox;


        struct 
        {
            int (*get)(void);
        } event;

        // keyboard api
        struct 
        {
            bool (*pressed)(int key);
            bool (*just_pressed)(int key);
            bool (*just_released)(int key);
            WPARAM (*get_last)(void);
        } key;

        // mouse api
        struct 
        {
            bool (*pressed)(int button);
            bool (*just_pressed)(int button);
            bool (*just_released)(int button);
            int  (*get_posX) (void);
            int  (*get_posY) (void);
            int  (*get_global_posX) (void);
            int  (*get_global_posY) (void);
            void (*set_pos)(int x, int y);
            int  (*get_wheel)(void);
        } mouse;

        // polygon draw api
        struct 
        {
            void (*rect)              (int x, int y, int w, int h, int border_width, int r, int g, int b);
            void (*rect_fill)         (int x, int y, int w, int h, int r, int g, int b);
            void (*polygon)           (const int* xs, const int* ys, int count, int border_width, int r, int g, int b);
            void (*polygon_fill)      (const int* xs, const int* ys, int count, int r, int g, int b);
            void (*rounded_rect)      (int x, int y, int w, int h, int radius, int border_width, int r, int g, int b);
            void (*rounded_rect_fill) (int x, int y, int w, int h, int radius, int r, int g, int b);
            void (*circle)            (int x, int y, int radius, int border_width, int r, int g, int b);
            void (*circle_fill)       (int x, int y, int radius, int r, int g, int b);
            void (*line)              (int x1, int y1, int x2, int y2, int border_width, int r, int g, int b);
        } draw;


        // image api
        struct 
        {
            CGameImage (*load)            (const char * path);
            CGameImage (*load_from_memory)(const void* data, size_t size);
            void (*unload)                (CGameImage* img);
            void (*draw)                  (const CGameImage* img, int x, int y);
            void (*draw_scaled)           (const CGameImage* img, int x, int y, int w, int h);
            void (*draw_rotated)          (const CGameImage* img, int x, int y, float angle_deg);
            void (*draw_advanced)         (const CGameImage* img, int x, int y, int imageX, int imageY, int imageW, int imageH);
            CGameImage (*resize)          (const CGameImage* src, int w, int h);
            CGameImage (*flip_horizontal) (const CGameImage* img);
            CGameImage (*flip_vertical)   (const CGameImage* img);
            CGameImage (*rotate)          (const CGameImage *src, float angle_deg);    
            int (*get_width)              (const CGameImage* img);
            int (*get_height)             (const CGameImage* img);
            int (*get_channels)           (const CGameImage* img);
        } image;

        // timing
        struct 
        {
            void       (*set_fps)   (int fps);
            float      (*get_fps)   (void);
            float      (*get_dt)    (void);
        } time;


        // text rendering
        struct 
        {
            void      (*draw)         (const char * text, int x, int y, int r, int g, int b);
            void      (*draw_complex) (const char * text, int x, int y, CGameFont *font, float size, int r, int g, int b);
            CGameFont (*load_font  )  (const char * path);
            void      (*unload_font)  (CGameFont *font);
        } text;

        struct 
        {
            const char *(*get)       (void);
            const char *(*get_patch) (void);
        } version;

        int QUIT;
        int VIDEORESIZE;
        int KEYDOWN;
        int KEYUP;

    int K_a, K_b, K_c, K_d, K_e, K_f, K_g, K_h, K_i, K_j, K_k, 
        K_l, K_m, K_n, K_o, K_p, K_q, K_r, K_s, K_t, K_u, K_v, 
        K_w, K_x, K_y, K_z,
        K_0, K_1, K_2, K_3, K_4, K_5, K_6, K_7, K_8, K_9,
        K_SPACE, K_RETURN, K_ESCAPE, K_LEFT, K_RIGHT, K_UP, K_DOWN,
        // - NEW KEYS -
        K_LSHIFT, K_RSHIFT, K_LCTRL, K_RCTRL,

        // ── Function keys ──
        K_F1, K_F2, K_F3, K_F4, K_F5, K_F6,
        K_F7, K_F8, K_F9, K_F10, K_F11, K_F12,

        // ── Numpad keys ──
        K_NUM0, K_NUM1, K_NUM2, K_NUM3, K_NUM4, 
        K_NUM5, K_NUM6, K_NUM7, K_NUM8, K_NUM9,
        K_NUM_ADD, K_NUM_SUB, K_NUM_MUL, K_NUM_DIV,
        K_NUM_DECIMAL, K_NUM_ENTER;

    } cgame;

    // =========================
    // Initialize function table
    // =========================
    static void _cgame_init_struct (void) 
    {
        cgame.init                        = _cgame_init_impl;
        cgame.quit                        = _cgame_quit_impl;

        // window cutomization API bindings
        cgame.display.set_title           = _cgame_display_set_title_impl;
        cgame.display.set_icon            = _cgame_display_set_icon_impl;
        cgame.display.set_icon_from_image = _cgame_display_set_icon_from_image_impl;
        cgame.display.set_mode            = _cgame_set_mode_impl;
        cgame.display.clear               = _cgame_display_clear_impl;
        cgame.display.flip                = _cgame_display_flip_impl;
        cgame.display.get_width           = _cgame_display_get_width_impl;
        cgame.display.get_height          = _cgame_display_get_height_impl;
        cgame.display.get_monitor_width   = _cgame_display_get_monitor_width_impl;
        cgame.display.get_monitor_height  = _cgame_display_get_monitor_height_impl;
        cgame.display.set_pos             = _cgame_display_set_pos_impl; 
        cgame.display.center              = _cgame_display_center_impl;
        cgame.display.get_posX            = _cgame_display_get_posX_impl;
        cgame.display.get_posY            = _cgame_display_get_posY_impl;
        cgame.display.focus               = _cgame_display_focus_impl;
        cgame.display.restore             = _cgame_display_restore_impl;
        cgame.display.minimize            = _cgame_display_minimize_impl;

        cgame.event.get                   = _cgame_event_get_impl;

        //  console 
        cgame.console.set_color           = _cgame_console_set_color_impl;
        cgame.console.reset_color         = _cgame_console_reset_color_impl;
        cgame.console.clear               = _cgame_console_clear_impl; 
        // msg box
        cgame.messagebox.show             = _cgame_message_box_impl;


        // keyboard API bindings
        cgame.key.pressed                 = _cgame_key_held_impl;
        cgame.key.just_pressed            = _cgame_key_pressed_impl;
        cgame.key.just_released           = _cgame_key_released_impl;
        cgame.key.get_last                = _cgame_key_last_impl;

        // mouse API bindings
        cgame.mouse.pressed               = _cgame_mouse_held_impl;
        cgame.mouse.just_pressed          = _cgame_mouse_pressed_impl;
        cgame.mouse.just_released         = _cgame_mouse_released_impl;
        cgame.mouse.get_posX              = _cgame_mouse_get_posX_impl;
        cgame.mouse.get_posY              = _cgame_mouse_get_posY_impl;
        cgame.mouse.get_global_posX       = _cgame_mouse_get_globalX_impl;
        cgame.mouse.get_global_posY       = _cgame_mouse_get_globalY_impl;
        cgame.mouse.set_pos               = _cgame_mouse_set_pos_impl;
        cgame.mouse.get_wheel             = _cgame_mouse_get_wheel_impl;

        // polygon drawing API bindings
        cgame.draw.rect_fill              = _cgame_draw_fillrect_impl;
        cgame.draw.rect                   = _cgame_draw_rect_impl;
        cgame.draw.rounded_rect           = _cgame_draw_rounded_rect_impl;
        cgame.draw.rounded_rect_fill      = _cgame_draw_rounded_fill_rect_impl;
        cgame.draw.circle                 = _cgame_draw_circle_impl;
        cgame.draw.circle_fill            = _cgame_draw_fill_circle_impl;
        cgame.draw.polygon                = _cgame_draw_polygon_impl;
        cgame.draw.polygon_fill           = _cgame_draw_fill_polygon_impl;
        cgame.draw.line                   = _cgame_draw_line_impl;

        // image API bindings
        cgame.image.load                  = _cgame_image_load_impl;
        cgame.image.load_from_memory      = _cgame_image_load_from_memory_impl;       
        cgame.image.unload                = _cgame_image_unload_impl;
        cgame.image.draw                  = _cgame_image_draw_impl;
        cgame.image.draw_scaled           = _cgame_image_draw_scaled_impl;
        cgame.image.draw_rotated          = _cgame_image_draw_rotated_impl;
        cgame.image.draw_advanced         = _cgame_image_draw_advanced_impl;
        cgame.image.resize                = _cgame_image_resize_nearest_impl;
        cgame.image.rotate                = _cgame_image_rotate_impl;
        cgame.image.flip_horizontal       = _cgame_image_flip_horizontal_impl;
        cgame.image.flip_vertical         = _cgame_image_flip_vertical_impl;
        cgame.image.get_width             = _cgame_image_get_width_impl;
        cgame.image.get_height            = _cgame_image_get_height_impl;
        cgame.image.get_channels          = _cgame_image_get_channels_impl;

        // timing API bidings
        cgame.time.set_fps                = _cgame_time_set_fps_impl;
        cgame.time.get_fps                = _cgame_time_get_fps_impl;
        cgame.time.get_dt                 = _cgame_time_get_dt_impl;

        // text API bindings
        cgame.text.draw                   = _cgame_text_draw_impl;
        cgame.text.draw_complex           = _cgame_text_draw_complex_impl;
        cgame.text.load_font              = _cgame_text_load_font_impl;
        cgame.text.unload_font            = _cgame_text_unload_font_impl;

        // version 
        cgame.version.get                 = _cgame_version_get_impl;
        cgame.version.get_patch           = _cgame_version_get_patch_impl;

        // MAJOR EVENTSSSSSSSSSSS....
        cgame.QUIT               = CGAME_QUIT;
        cgame.VIDEORESIZE        = CGAME_VIDEORESIZE;
        cgame.KEYDOWN            = CGAME_KEYDOWN;
        cgame.KEYUP              = CGAME_KEYUP;

        cgame.K_a           = CGAME_K_a;
        cgame.K_b           = CGAME_K_b;
        cgame.K_c           = CGAME_K_c;
        cgame.K_d           = CGAME_K_d;
        cgame.K_e           = CGAME_K_e;
        cgame.K_f           = CGAME_K_f;
        cgame.K_g           = CGAME_K_g;
        cgame.K_h           = CGAME_K_h;
        cgame.K_i           = CGAME_K_i;
        cgame.K_j           = CGAME_K_j;
        cgame.K_k           = CGAME_K_k;
        cgame.K_l           = CGAME_K_l;
        cgame.K_m           = CGAME_K_m;
        cgame.K_n           = CGAME_K_n;
        cgame.K_o           = CGAME_K_o;
        cgame.K_p           = CGAME_K_p;
        cgame.K_q           = CGAME_K_q;
        cgame.K_r           = CGAME_K_r;
        cgame.K_s           = CGAME_K_s;
        cgame.K_t           = CGAME_K_t;
        cgame.K_u           = CGAME_K_u;
        cgame.K_v           = CGAME_K_v;
        cgame.K_w           = CGAME_K_w;
        cgame.K_x           = CGAME_K_x;
        cgame.K_y           = CGAME_K_y;
        cgame.K_z           = CGAME_K_z;

        cgame.K_0           = CGAME_K_0;
        cgame.K_1           = CGAME_K_1;
        cgame.K_2           = CGAME_K_2;
        cgame.K_3           = CGAME_K_3;
        cgame.K_4           = CGAME_K_4;
        cgame.K_5           = CGAME_K_5;
        cgame.K_6           = CGAME_K_6;
        cgame.K_7           = CGAME_K_7;
        cgame.K_8           = CGAME_K_8;
        cgame.K_9           = CGAME_K_9;

        cgame.K_SPACE       = CGAME_K_SPACE ;
        cgame.K_RETURN      = CGAME_K_RETURN;
        cgame.K_ESCAPE      = CGAME_K_ESCAPE;
        cgame.K_LEFT        = CGAME_K_LEFT  ;
        cgame.K_RIGHT       = CGAME_K_RIGHT ;
        cgame.K_UP          = CGAME_K_UP    ;
        cgame.K_DOWN        = CGAME_K_DOWN  ;

        cgame.K_LSHIFT      = CGAME_K_LSHIFT;
        cgame.K_RSHIFT      = CGAME_K_RSHIFT;
        cgame.K_LCTRL       = CGAME_K_LCTRL ;
        cgame.K_RCTRL       = CGAME_K_RCTRL ;

        cgame.K_F1          = CGAME_K_F1;
        cgame.K_F2          = CGAME_K_F2;
        cgame.K_F3          = CGAME_K_F3;
        cgame.K_F4          = CGAME_K_F4;
        cgame.K_F5          = CGAME_K_F5;
        cgame.K_F6          = CGAME_K_F6;
        cgame.K_F7          = CGAME_K_F7;
        cgame.K_F8          = CGAME_K_F8;
        cgame.K_F9          = CGAME_K_F9;
        cgame.K_F10         = CGAME_K_F10;
        cgame.K_F11         = CGAME_K_F11;
        cgame.K_F12         = CGAME_K_F12;


        cgame.K_NUM0        = CGAME_K_NUM0;
        cgame.K_NUM1        = CGAME_K_NUM1;
        cgame.K_NUM2        = CGAME_K_NUM2;
        cgame.K_NUM3        = CGAME_K_NUM3;
        cgame.K_NUM4        = CGAME_K_NUM4;
        cgame.K_NUM5        = CGAME_K_NUM5;
        cgame.K_NUM6        = CGAME_K_NUM6;
        cgame.K_NUM7        = CGAME_K_NUM7;
        cgame.K_NUM8        = CGAME_K_NUM8;
        cgame.K_NUM9        = CGAME_K_NUM9;
        cgame.K_NUM_ADD     = CGAME_K_NUM_ADD;
        cgame.K_NUM_SUB     = CGAME_K_NUM_SUB;
        cgame.K_NUM_MUL     = CGAME_K_NUM_MUL;
        cgame.K_NUM_DIV     = CGAME_K_NUM_DIV;
        cgame.K_NUM_DECIMAL = CGAME_K_NUM_DECIMAL;
        cgame.K_NUM_ENTER   = CGAME_K_NUM_ENTER;
    }

    static int _cgame_dummy_init = (_cgame_init_struct (), 0);
// -----------------------------------------------------------
// Entry point shim for MinGW when using -municode
// -----------------------------------------------------------
#if defined(_WIN32) && (defined(__MINGW32__) || defined(__MINGW64__)) && !defined(CGAME_NO_WINMAIN_SHIM)

extern "C" int main(void); // forward declare user main()

#ifdef CGAME_ENTRY_POINT  // 
int WINAPI wWinMain(HINSTANCE hInstance, HINSTANCE hPrevInstance,
                    LPWSTR lpCmdLine, int nShowCmd)
{
    (void)hInstance;
    (void)hPrevInstance;
    (void)lpCmdLine;
    (void)nShowCmd;
    return main(); // call your real main()
}
#endif // CGAME_DEFINE_ENTRY_POINT
#endif // platform guard


#endif // CGAME_H
