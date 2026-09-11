#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Dead Space 3 - Thai Mod by Lung Dear  |  ตัวติดตั้งแบบสคริปต์ (ทุกแพลตฟอร์ม)

ใช้ได้ทั้ง Windows, Linux (Proton / Steam Deck) และ macOS
ต้องมี Python 3.8 ขึ้นไปเท่านั้น ไม่ต้องติดตั้งไลบรารีอะไรเพิ่ม

    python3 install.py                 หาเกมเอง แล้วถามก่อนติดตั้ง
    python3 install.py --status        ดูว่าตอนนี้เป็นไทยหรืออังกฤษ
    python3 install.py --install       ติดตั้งเลยไม่ต้องถาม
    python3 install.py --uninstall     คืนไฟล์ต้นฉบับ
    python3 install.py --game "<พาธโฟลเดอร์เกม>"    ระบุโฟลเดอร์เอง
"""
import argparse
import os
import platform
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAYLOAD = os.path.join(HERE, 'payload')
sys.path.insert(0, PAYLOAD)
import ds3_patch as P                                        # noqa: E402

BACKUP_DIR = '_ThaiMod_Backup_Original'
MARKERS = ('deadspace3.exe', 'bigfile4.viv')
CREDIT = 'Mod Thai By Lung Dear'


def out(s):
    try:
        print(s)
    except UnicodeEncodeError:                    # ancient Windows console
        print(s.encode('utf-8', 'replace').decode('ascii', 'replace'))


def is_game(path):
    return all(os.path.exists(os.path.join(path, m)) for m in MARKERS)


def steam_roots():
    """Every Steam library on this machine, on whichever OS we are."""
    home = os.path.expanduser('~')
    sysname = platform.system()
    roots = []
    if sysname == 'Windows':
        roots += [r'C:\Program Files (x86)\Steam', r'C:\Program Files\Steam']
        try:
            import winreg
            for hive, key in ((winreg.HKEY_CURRENT_USER, r'Software\Valve\Steam'),
                              (winreg.HKEY_LOCAL_MACHINE,
                               r'SOFTWARE\WOW6432Node\Valve\Steam')):
                try:
                    with winreg.OpenKey(hive, key) as k:
                        for name in ('SteamPath', 'InstallPath'):
                            try:
                                roots.append(winreg.QueryValueEx(k, name)[0])
                            except OSError:
                                pass
                except OSError:
                    pass
        except ImportError:
            pass
    elif sysname == 'Darwin':
        roots.append(os.path.join(home, 'Library', 'Application Support', 'Steam'))
    else:                                          # Linux, incl. Steam Deck
        roots += [os.path.join(home, '.steam', 'steam'),
                  os.path.join(home, '.steam', 'root'),
                  os.path.join(home, '.local', 'share', 'Steam'),
                  os.path.join(home, '.var', 'app', 'com.valvesoftware.Steam',
                               'data', 'Steam')]
        for media in ('/run/media', os.path.join('/media', os.environ.get('USER', ''))):
            if os.path.isdir(media):
                for d in os.listdir(media):        # SD card / external drive
                    roots.append(os.path.join(media, d))

    libs = []
    for r in roots:
        if r and os.path.isdir(r):
            libs.append(r)
            vdf = os.path.join(r, 'steamapps', 'libraryfolders.vdf')
            if os.path.isfile(vdf):
                try:
                    text = open(vdf, encoding='utf-8', errors='replace').read()
                except OSError:
                    continue
                for m in re.finditer(r'"path"\s*"([^"]+)"', text):
                    libs.append(m.group(1).replace('\\\\', os.sep))
    return libs


def candidates():
    """Folders worth checking, cheapest first."""
    home = os.path.expanduser('~')
    seen, out_ = set(), []

    def add(p):
        if p and p not in seen:
            seen.add(p)
            out_.append(p)

    for lib in steam_roots():
        common = os.path.join(lib, 'steamapps', 'common')
        if os.path.isdir(common):
            for d in sorted(os.listdir(common)):   # never trust the folder name
                add(os.path.join(common, d))

    # EA App / Origin / GOG / hand-made installs
    fixed = [r'C:\Program Files (x86)\Origin Games\Dead Space 3',
             r'C:\Program Files\EA Games\Dead Space 3',
             r'C:\Program Files (x86)\EA Games\Dead Space 3',
             r'C:\Program Files (x86)\GOG Galaxy\Games\Dead Space 3',
             r'C:\Games\Dead Space 3', r'D:\Games\Dead Space 3',
             os.path.join(home, 'Games', 'Dead Space 3'),
             os.path.join(home, 'GOG Games', 'Dead Space 3')]
    for p in fixed:
        add(p)
    for base in (r'C:\Games', r'D:\Games', r'E:\Games',
                 os.path.join(home, 'Games')):
        if os.path.isdir(base):
            for d in sorted(os.listdir(base)):
                add(os.path.join(base, d))
    return out_


def find_game():
    for p in candidates():
        try:
            if is_game(p):
                return p
        except OSError:
            continue
    return None


def show(game):
    st = P.state(game, PAYLOAD)
    kinds = [s for _, s in st]
    if all(k == 'installed' for k in kinds):
        out('  สถานะ: ติดตั้งม็อดภาษาไทยแล้ว')
    elif all(k == 'original' for k in kinds):
        out('  สถานะ: เป็นไฟล์ต้นฉบับ (ภาษาอังกฤษ)')
    else:
        out('  สถานะ: %s' % ', '.join('%s=%s' % (t['file'], s) for t, s in st))
    return kinds


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--game')
    ap.add_argument('--install', action='store_true')
    ap.add_argument('--uninstall', action='store_true')
    ap.add_argument('--status', action='store_true')
    a = ap.parse_args()

    out('=' * 60)
    out('  Dead Space 3 + Awakened  -  ม็อดภาษาไทย')
    out('  %s' % CREDIT)
    out('=' * 60)

    game = a.game or find_game()
    if not game:
        out('\nหาโฟลเดอร์เกมไม่เจอ')
        out('ให้ระบุเอง เช่น')
        out('   python3 install.py --game "/path/to/Dead Space 3"')
        return 2
    if not is_game(game):
        out('\nโฟลเดอร์นี้ไม่ใช่ Dead Space 3 (ต้องมี %s)' % ' และ '.join(MARKERS))
        out('   %s' % game)
        return 2
    out('\nโฟลเดอร์เกม: %s' % game)

    backup = os.path.join(game, BACKUP_DIR)
    try:
        kinds = show(game)
    except Exception as ex:
        out('\nอ่านไฟล์เกมไม่ได้: %s' % ex)
        return 2

    if a.status:
        return 0

    if a.uninstall:
        choice = 'u'
    elif a.install:
        choice = 'i'
    else:
        out('\n  [1] ติดตั้งม็อดภาษาไทย')
        out('  [2] ถอนการติดตั้ง (คืนไฟล์เดิม)')
        out('  [3] ออก')
        try:
            pick = input('\nเลือก: ').strip()
        except (EOFError, KeyboardInterrupt):
            return 1
        choice = {'1': 'i', '2': 'u'}.get(pick)
        if not choice:
            return 0

    if not os.access(game, os.W_OK):
        out('\nเขียนลงโฟลเดอร์เกมไม่ได้ (ไม่มีสิทธิ์)')
        out('Windows: คลิกขวาที่ ติดตั้ง-Windows.bat แล้วเลือก Run as administrator')
        out('Linux/macOS: ลองใช้ sudo หรือแก้สิทธิ์โฟลเดอร์เกม')
        return 2

    def say(msg, pct=None):
        out('  %s' % msg)

    try:
        if choice == 'i':
            n = P.apply(game, PAYLOAD, backup, say)
            out('\nติดตั้งเรียบร้อย %d ส่วน - เปิดเกมได้เลย' % n)
            out('ไฟล์ต้นฉบับสำรองไว้ที่  %s' % backup)
        else:
            n = P.revert(game, PAYLOAD, backup, say)
            out('\nคืนไฟล์ต้นฉบับแล้ว %d ส่วน' % n)
    except Exception as ex:
        out('\nไม่สำเร็จ: %s' % ex)
        return 1
    return 0


if __name__ == '__main__':
    try:
        sys.stdout.reconfigure(encoding='utf-8')      # py3.7+
    except Exception:
        pass
    sys.exit(main())
