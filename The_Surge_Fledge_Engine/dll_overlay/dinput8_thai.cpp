/*
 * The Surge Thai Mod V11 - Cipher String Patching
 * Patches UTF-16 strings in memory to use Japanese codepoints (0x3041+)
 * mapping from Thai codepoints (0x0E01+) as a cipher text approach.
 * This avoids breaking fonts.bin internal structure.
 */

#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <objbase.h>
#include <psapi.h>
#include <cstdio>
#include <cstring>
#include <string>
#include <vector>
#include <fstream>
#include <thread>

#pragma comment(lib, "psapi.lib")

static FILE* g_log = NULL;
static HMODULE g_hRealDI8 = NULL;
static std::string g_dllDir;

typedef HRESULT(WINAPI* pfnDI8Create)(HINSTANCE, DWORD, const IID&, LPVOID*, IUnknown*);
static pfnDI8Create g_pDI8Create = NULL;

static void Log(const char* fmt, ...) {
    if (!g_log) return;
    va_list a; va_start(a, fmt);
    vfprintf(g_log, fmt, a); fprintf(g_log, "\n"); fflush(g_log);
    va_end(a);
}

extern "C" __declspec(dllexport) HRESULT WINAPI
MyDirectInput8Create(HINSTANCE h, DWORD v, const IID& r, LPVOID* p, IUnknown* u) {
    return g_pDI8Create ? g_pDI8Create(h, v, r, p, u) : E_FAIL;
}

// Translation entry
struct Trans {
    std::wstring en;
    std::wstring cipher;
};

static std::vector<Trans> g_trans;

static void LoadTranslations(const std::string& path) {
    std::ifstream f(path, std::ios::binary);
    if (!f.is_open()) return;
    
    // BOM check
    char bom[3];
    f.read(bom, 3);
    if (!(bom[0] == (char)0xEF && bom[1] == (char)0xBB && bom[2] == (char)0xBF))
        f.seekg(0);
    
    std::string line;
    while (std::getline(f, line)) {
        if (!line.empty() && line.back() == '\r') line.pop_back();
        if (line.empty() || line[0] == '#') continue;
        
        size_t tab = line.find('\t');
        if (tab == std::string::npos) continue;
        
        std::string en_utf8 = line.substr(0, tab);
        std::string th_utf8 = line.substr(tab + 1);
        
        // Convert UTF-8 to UTF-16
        int en_len = MultiByteToWideChar(CP_UTF8, 0, en_utf8.c_str(), -1, NULL, 0);
        int th_len = MultiByteToWideChar(CP_UTF8, 0, th_utf8.c_str(), -1, NULL, 0);
        if (en_len <= 0 || th_len <= 0) continue;
        
        std::wstring en_w(en_len - 1, 0), th_w(th_len - 1, 0);
        MultiByteToWideChar(CP_UTF8, 0, en_utf8.c_str(), -1, &en_w[0], en_len);
        MultiByteToWideChar(CP_UTF8, 0, th_utf8.c_str(), -1, &th_w[0], th_len);
        
        // Only add if Thai is shorter or equal to English (in-place replacement)
        if (th_w.length() <= en_w.length()) {
            Trans t;
            t.en = en_w;
            
            // Cipher: Convert Thai codepoints to Japanese
            t.cipher = th_w;
            for (size_t i = 0; i < t.cipher.length(); i++) {
                wchar_t c = t.cipher[i];
                if (c >= 0x0E01 && c <= 0x0E5B) {
                    t.cipher[i] = 0x3040 + (c - 0x0E00); // 0x0E01 -> 0x3041
                }
            }
            
            // Pad cipher with spaces if shorter
            while (t.cipher.length() < t.en.length())
                t.cipher += L' ';
            g_trans.push_back(t);
            
            Log("Loaded trans: len %d", (int)t.en.length());
        }
    }
}

static int PatchStrings() {
    HANDLE proc = GetCurrentProcess();
    HMODULE mods[1024];
    DWORD needed;
    int totalPatched = 0;
    
    // Scan all memory regions
    MEMORY_BASIC_INFORMATION mbi;
    unsigned char* addr = NULL;
    
    while (VirtualQuery(addr, &mbi, sizeof(mbi))) {
        if (mbi.State == MEM_COMMIT && 
            (mbi.Protect == PAGE_READWRITE || mbi.Protect == PAGE_EXECUTE_READWRITE) &&
            mbi.RegionSize >= 1024) {
            
            unsigned char* base = (unsigned char*)mbi.BaseAddress;
            SIZE_T size = mbi.RegionSize;
            
            for (auto& t : g_trans) {
                const wchar_t* needle = t.en.c_str();
                size_t needleBytes = t.en.length() * 2;
                
                for (SIZE_T i = 0; i + needleBytes <= size; i += 2) {
                    if (memcmp(base + i, needle, needleBytes) == 0) {
                        // Found! Replace with Cipher string
                        DWORD oldProt;
                        VirtualProtect(base + i, needleBytes, PAGE_READWRITE, &oldProt);
                        memcpy(base + i, t.cipher.c_str(), needleBytes);
                        VirtualProtect(base + i, needleBytes, oldProt, &oldProt);
                        totalPatched++;
                    }
                }
            }
        }
        addr = (unsigned char*)mbi.BaseAddress + mbi.RegionSize;
    }
    
    return totalPatched;
}

static void PatchThread() {
    // Wait for game to load strings
    Sleep(8000);
    
    LoadTranslations(g_dllDir + "\\translations.tsv");
    Log("Loaded %d translation entries", (int)g_trans.size());
    
    if (g_trans.empty()) return;
    
    // Patch strings every 3 seconds for 30 seconds
    for (int round = 0; round < 10; round++) {
        int patched = PatchStrings();
        Log("Round %d: patched %d strings", round, patched);
        Sleep(3000);
    }
}

BOOL APIENTRY DllMain(HMODULE hMod, DWORD reason, LPVOID) {
    if (reason == DLL_PROCESS_ATTACH) {
        DisableThreadLibraryCalls(hMod);
        char p[MAX_PATH]; GetModuleFileNameA(hMod, p, MAX_PATH);
        g_dllDir = std::string(p); g_dllDir = g_dllDir.substr(0, g_dllDir.find_last_of("\\/"));
        g_log = fopen((g_dllDir + "\\thai_mod.log").c_str(), "w");
        Log("Thai Mod V11 (Cipher String Patch) loaded");
        
        char sys[MAX_PATH]; GetSystemDirectoryA(sys, MAX_PATH); strcat_s(sys, "\\dinput8.dll");
        g_hRealDI8 = LoadLibraryA(sys);
        if (g_hRealDI8) g_pDI8Create = (pfnDI8Create)GetProcAddress(g_hRealDI8, "DirectInput8Create");
        
        std::thread(PatchThread).detach();
    }
    else if (reason == DLL_PROCESS_DETACH) {
        if (g_hRealDI8) FreeLibrary(g_hRealDI8);
        if (g_log) fclose(g_log);
    }
    return TRUE;
}
