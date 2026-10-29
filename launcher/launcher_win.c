/* Original Windows bootstrap. No game or toolkit code is linked here. */
#define UNICODE
#define _UNICODE
#define WIN32_LEAN_AND_MEAN
#include <windows.h>
#include <wchar.h>
#include <strsafe.h>

static int quote(WCHAR *out, size_t cap, size_t *used, const WCHAR *text) {
    size_t slashes = 0;
    if (*used + 2 >= cap) return 0;
    out[(*used)++] = L'"';
    for (;;) {
        WCHAR ch = *text++;
        if (ch == L'\\') { slashes++; continue; }
        size_t n = (ch == L'"' || ch == 0) ? slashes * 2 : slashes;
        if (*used + n + 3 >= cap) return 0;
        while (n--) out[(*used)++] = L'\\';
        slashes = 0;
        if (ch == 0) break;
        if (ch == L'"') out[(*used)++] = L'\\';
        out[(*used)++] = ch;
    }
    out[(*used)++] = L'"'; out[*used] = 0;
    return 1;
}

int WINAPI wWinMain(HINSTANCE instance, HINSTANCE previous, PWSTR args, int show) {
    (void)instance; (void)previous; (void)show;
    WCHAR root[8192], python[8192], script[8192], command[32768], pid[64];
    DWORD length = GetModuleFileNameW(NULL, root, 8192);
    if (!length || length >= 8192) goto failed;
    WCHAR *slash = wcsrchr(root, L'\\');
    if (!slash) goto failed;
    slash[1] = 0;
    if (FAILED(StringCchPrintfW(python, 8192, L"%ssupport\\python\\pythonw.exe", root)) ||
        FAILED(StringCchPrintfW(script, 8192, L"%sapp\\tools\\portable_launcher.py", root))) goto failed;
    if (GetFileAttributesW(python) == INVALID_FILE_ATTRIBUTES || GetFileAttributesW(script) == INVALID_FILE_ATTRIBUTES) {
        MessageBoxW(NULL, L"Extract the complete Nitrogen-Squared folder before running launcher.exe. Its supporting files are missing.", L"Nitrogen Squared", MB_OK | MB_ICONERROR);
        return 1;
    }
    size_t used = 0;
    command[0] = 0;
    if (!quote(command,32768,&used,python)) goto failed;
    if (FAILED(StringCchCatW(command,32768,L" -I -B "))) goto failed;
    used = wcslen(command);
    if (!quote(command,32768,&used,script)) goto failed;
    if (FAILED(StringCchCatW(command,32768,L" --root "))) goto failed;
    used = wcslen(command);
    if (!quote(command,32768,&used,root)) goto failed;
    StringCchPrintfW(pid,64,L" --launcher-pid %lu ",GetCurrentProcessId());
    if (FAILED(StringCchCatW(command,32768,pid)) || FAILED(StringCchCatW(command,32768,args))) goto failed;
    STARTUPINFOW startup = {sizeof(startup)};
    PROCESS_INFORMATION process;
    if (!CreateProcessW(python,command,NULL,NULL,FALSE,0,NULL,root,&startup,&process)) goto failed;
    CloseHandle(process.hThread);
    WaitForSingleObject(process.hProcess,INFINITE);
    DWORD code = 1;
    GetExitCodeProcess(process.hProcess,&code);
    CloseHandle(process.hProcess);
    return (int)code;
failed:
    MessageBoxW(NULL,L"The launcher could not start. Extract the complete package into a writable folder and try again.",L"Nitrogen Squared",MB_OK|MB_ICONERROR);
    return 1;
}
