# -*- coding: utf-8 -*-
"""Dead Space 2 Thai mod - command line installer. Mod TH By Lung Dear.

The same six-region patch the graphical installer applies, driven from a
terminal instead, so it runs anywhere Python does: Windows without the .exe,
and Linux or macOS where the game runs under Proton, Wine or CrossOver.

    python ds2_thai.py install [game folder]
    python ds2_thai.py uninstall [game folder]
    python ds2_thai.py status [game folder]

The folder is optional. Without it the game is looked for in the usual places
for this operating system, and the folder this script sits in is tried first so
that unzipping the mod straight into the game just works.

Nothing is written until every one of the six regions has been checked against
the SHA-256 of the bytes the game shipped.
"""
import io
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, 'tools'))
import ds2_patch                                            # noqa: E402

PAYLOAD = HERE
BACKUP_NAME = '_ThaiMod_Backup_Original'
MARKERS = ('deadspace2.exe', 'DS2DAT2.DAT')
FOLDER_HINTS = ('Dead Space 2', 'DeadSpace2', 'Dead Space 2 Complete')


# ---------------------------------------------------------------- output --

def out(text):
    """Print Thai without tripping over a legacy console codepage.

    Windows terminals still default to cp874 or cp437, where printing Thai
    raises UnicodeEncodeError and the installer dies before it does anything.
    """
    try:
        print(text)
    except UnicodeEncodeError:
        enc = getattr(sys.stdout, 'encoding', None) or 'ascii'
        print(text.encode(enc, 'replace').decode(enc, 'replace'))


def setup_console():
    if os.name == 'nt':
        try:                                   # UTF-8 console where available
            import ctypes
            ctypes.windll.kernel32.SetConsoleOutputCP(65001)
        except Exception:
            pass
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass                               # Python < 3.7: out() copes


# ------------------------------------------------------------ finding it --

def is_game(path):
    if not path or not os.path.isdir(path):
        return False
    try:
        have = {e.lower() for e in os.listdir(path)}
    except OSError:
        return False
    return all(m.lower() in have for m in MARKERS)


def drives():
    """Fixed drive letters that exist, C first."""
    out_ = []
    for letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
        root = '%s:\\' % letter
        if os.path.isdir(root):
            out_.append(root)
    return out_


def steam_roots():
    """Every Steam library root worth looking in on this OS."""
    home = os.path.expanduser('~')
    roots = []
    if os.name == 'nt':
        for env in ('ProgramFiles(x86)', 'ProgramFiles'):
            base = os.environ.get(env)
            if base:
                roots.append(os.path.join(base, 'Steam'))
        for drive in drives():
            roots.append(os.path.join(drive, 'Steam'))
            roots.append(os.path.join(drive, 'SteamLibrary'))
    elif sys.platform == 'darwin':
        roots.append(os.path.join(home, 'Library', 'Application Support', 'Steam'))
    else:
        roots += [
            os.path.join(home, '.steam', 'steam'),
            os.path.join(home, '.steam', 'root'),
            os.path.join(home, '.local', 'share', 'Steam'),
            # Flatpak keeps its own copy of the whole Steam tree
            os.path.join(home, '.var', 'app', 'com.valvesoftware.Steam',
                         '.local', 'share', 'Steam'),
            '/run/media',                      # Steam Deck SD cards
        ]
    return [r for r in roots if os.path.isdir(r)]


def library_folders(root):
    """Extra library paths Steam records in libraryfolders.vdf.

    Read with a plain string scan rather than a VDF parser: the file is small,
    the only thing wanted from it is the quoted paths, and a dependency would
    defeat the point of a script that runs on a bare Python.
    """
    found = [root]
    for name in (os.path.join('steamapps', 'libraryfolders.vdf'),
                 os.path.join('config', 'libraryfolders.vdf')):
        path = os.path.join(root, name)
        if not os.path.isfile(path):
            continue
        try:
            text = io.open(path, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        for line in text.splitlines():
            parts = line.split('"')
            if len(parts) < 4:
                continue
            # Newer Steam writes "path" "<dir>"; older writes "1" "<dir>"
            if parts[1] != 'path' and not parts[1].isdigit():
                continue
            cand = parts[3].replace('\\\\', os.sep).replace('\\', os.sep)
            if os.path.isdir(cand):
                found.append(cand)
    return found


def candidates():
    """Where the game might be, best guess first."""
    seen, out_ = [], []

    def add(path):
        if path and path not in seen:
            seen.append(path)
            out_.append(path)

    add(HERE)                                  # unzipped into the game folder
    add(os.path.dirname(HERE))
    for root in steam_roots():
        for lib in library_folders(root):
            for hint in FOLDER_HINTS:
                add(os.path.join(lib, 'steamapps', 'common', hint))
    if os.name == 'nt':
        # Not just %ProgramFiles%: a second drive commonly carries its own
        # 'Program Files (x86)\EA Games' tree, which is where this game most
        # often ends up on a machine with a small system disk.
        bases = [os.environ.get(e) for e in ('ProgramFiles(x86)', 'ProgramFiles')]
        for drive in drives():
            bases += [os.path.join(drive, 'Program Files (x86)'),
                      os.path.join(drive, 'Program Files'),
                      os.path.join(drive, 'Games'),
                      drive]
        for base in bases:
            if not base or not os.path.isdir(base):
                continue
            for pub in ('EA Games', 'Electronic Arts', 'Origin Games',
                        os.path.join('GOG Galaxy', 'Games'), ''):
                for hint in FOLDER_HINTS:
                    add(os.path.join(base, pub, hint) if pub
                        else os.path.join(base, hint))
    else:
        # Proton and Wine prefixes put the Windows drive under drive_c
        home = os.path.expanduser('~')
        for prefix in (os.path.join(home, '.wine'),
                       os.path.join(home, 'Games')):
            for pub in ('EA Games', 'Electronic Arts', 'Origin Games'):
                for hint in FOLDER_HINTS:
                    add(os.path.join(prefix, 'drive_c', 'Program Files (x86)',
                                     pub, hint))
    return out_


def find_game(given=None):
    if given:
        given = os.path.abspath(os.path.expanduser(given))
        if not is_game(given):
            raise SystemExit(
                u'\nไม่พบเกมในโฟลเดอร์ที่ระบุ:\n  %s\n'
                u'โฟลเดอร์ที่ถูกต้องต้องมีไฟล์ deadspace2.exe และ DS2DAT2.DAT'
                % given)
        return given
    for path in candidates():
        if is_game(path):
            return path
    raise SystemExit(
        u'\nหาโฟลเดอร์เกมไม่เจอ ลองระบุเองดูครับ:\n'
        u'  python ds2_thai.py install "<โฟลเดอร์ที่มี deadspace2.exe>"')


# --------------------------------------------------------------- writing --

def writable(game):
    """Can we actually modify the archives, or is this a permission problem?

    On Windows the game usually lives in Program Files, where opening for
    write fails unless the terminal was started as administrator. Saying so
    up front beats a traceback halfway through the first archive.
    """
    probe = ds2_patch.dat_path(game, 'DS2DAT2.DAT')
    try:
        with open(probe, 'r+b'):
            return True
    except OSError:
        return False


def deny(game):
    if os.name == 'nt':
        return (u'\nเขียนไฟล์เกมไม่ได้ (%s)\n'
                u'ให้คลิกขวาที่ install.bat แล้วเลือก "Run as administrator"'
                % game)
    return (u'\nเขียนไฟล์เกมไม่ได้ (%s)\n'
            u'ลองตรวจสิทธิ์ของโฟลเดอร์ หรือรันด้วย sudo' % game)


def progress(msg, pct):
    out(u'  [%3d%%] %s' % (int(pct), msg))


# ---------------------------------------------------------------- verbs --

def do_status(game):
    state, detail = ds2_patch.check(game, PAYLOAD)
    out(u'\nโฟลเดอร์เกม : %s' % game)
    out(u'สถานะ       : %s' % detail)
    backup = os.path.join(game, BACKUP_NAME)
    if os.path.isdir(backup):
        n = len([f for f in os.listdir(backup) if f.endswith('.bin')])
        out(u'ไฟล์สำรอง   : %d ไฟล์ ใน %s' % (n, BACKUP_NAME))
    else:
        out(u'ไฟล์สำรอง   : ยังไม่มี')
    return 0 if state != 'unknown' else 1


def do_install(game):
    state, detail = ds2_patch.check(game, PAYLOAD)
    if state == 'unknown':
        out(u'\n%s' % detail)
        return 1
    if state == 'installed':
        out(u'\nติดตั้งม็อดไว้อยู่แล้ว ไม่ต้องทำอะไรเพิ่ม')
        return 0
    if not writable(game):
        out(deny(game))
        return 1
    out(u'\nโฟลเดอร์เกม : %s' % game)
    n = ds2_patch.install(game, PAYLOAD, os.path.join(game, BACKUP_NAME),
                          say=progress)
    out(u'\nติดตั้งเสร็จแล้ว (%d ส่วน) เปิดเกมได้เลยครับ' % n)
    out(u'ไฟล์เดิมสำรองไว้ที่  %s  อย่าลบถ้ายังอยากถอนม็อดได้' % BACKUP_NAME)
    return 0


def do_uninstall(game):
    if not writable(game):
        out(deny(game))
        return 1
    out(u'\nโฟลเดอร์เกม : %s' % game)
    try:
        n = ds2_patch.restore(game, PAYLOAD, os.path.join(game, BACKUP_NAME),
                              say=progress)
    except RuntimeError as e:
        out(u'\n%s' % e)
        return 1
    out(u'\nคืนไฟล์เดิมแล้ว (%d ส่วน) เกมกลับเป็นภาษาอังกฤษเหมือนเดิมทุกไบต์' % n)
    return 0


VERBS = {'install': do_install, 'uninstall': do_uninstall, 'status': do_status}


def main(argv):
    setup_console()
    verb = argv[0] if argv else 'install'
    if verb in ('-h', '--help', 'help'):
        out(__doc__)
        return 0
    if verb not in VERBS:
        out(u'คำสั่งที่ใช้ได้: install / uninstall / status')
        return 2
    out(u'=' * 58)
    out(u'  Dead Space 2 - ม็อดภาษาไทย  ·  Mod TH By Lung Dear')
    out(u'=' * 58)
    return VERBS[verb](find_game(argv[1] if len(argv) > 1 else None))


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
