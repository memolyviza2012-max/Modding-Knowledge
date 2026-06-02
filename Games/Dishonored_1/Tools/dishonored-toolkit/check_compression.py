from binary import BinaryStream
from upkCompressor import DYCompressor

fp = "F:/SteamLibrary/steamapps/common/Dishonored/DishonoredGame/CookedPCConsole/L_Tower_Script.upk"
reader = BinaryStream(open(fp, 'rb'))
reader.seek(0)

sig = reader.readUInt32()
print(f"Signature: 0x{sig:08X}")

pkgVersion = reader.readInt16()
pkgLVersion = reader.readInt16()
headerSize = reader.readInt32()
folderLen = reader.readInt32()
folderStr = reader.readBytes(folderLen)

print(f"pkgVersion: {pkgVersion}")
print(f"pkgLVersion: {pkgLVersion}")
print(f"headerSize: {headerSize}")
print(f"folderLen: {folderLen}")
print(f"folderStr: {folderStr}")

reader.seek(headerSize)

pkgFlags = reader.readUInt32()
nameCount = reader.readUInt32()
nameOffset = reader.readUInt32()
exportCount = reader.readUInt32()
exportOffset = reader.readUInt32()
importCount = reader.readUInt32()
importOffset = reader.readUInt32()
dependsOffset = reader.readUInt32()
somedata1 = reader.readUInt32()
guid = reader.readBytes(16)
genCount = reader.readUInt32()

print(f"pkgFlags: {pkgFlags}")
print(f"nameCount: {nameCount}")
print(f"nameOffset: 0x{nameOffset:08X}")
print(f"exportCount: {exportCount}")
print(f"exportOffset: 0x{exportOffset:08X}")
print(f"genCount: {genCount}")

for i in range(genCount):
    reader.readUInt32()
    reader.readUInt32()
    reader.readUInt32()

engineVer = reader.readUInt32()
cookerVer = reader.readUInt32()
compFlags = reader.readUInt32()

print(f"engineVer: {engineVer}")
print(f"cookerVer: {cookerVer}")
print(f"compFlags: {compFlags}")

compressor = DYCompressor(compFlags)
ctype = compressor.getCompression()
print(f"Compression type: {ctype}")
