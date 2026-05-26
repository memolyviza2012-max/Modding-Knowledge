# Modding Knowledge Base
Welcome to my personal modding knowledge base. This repository is categorized into Engine-specific research and General Modding Techniques.

## Directory Structure

### 🎮 Engines (Engine-Specific Knowledge)

#### Frostbite Engine
- **[Mass Effect: Andromeda](Engines/Frostbite/MassEffectAndromeda/)**
  - [Thai Localization Guide](Engines/Frostbite/MassEffectAndromeda/MEA_Thai_Localization_Guide.md) - Comprehensive guide on Glyph Swapping, ZWSP Word-Wrap, and Binary `.res` encoding to bypass engine limitations.
  - [Localization Scripts](Engines/Frostbite/MassEffectAndromeda/Scripts/) - Python tools for encoding/decoding `.res` files, TTF font swapping, and modifying glyph Y-axis.

- **[Dead Space Remake](Engines/Frostbite/DeadSpaceRemake/)**
  - [Font Replacement Strategy](Engines/Frostbite/DeadSpaceRemake/Font_Replacement_Strategy.md) - Techniques for replacing and injecting custom fonts.

---

### 🛠️ Techniques (General Modding Techniques)

#### [Hooking and Proxy](Techniques/Hooking_and_Proxy/)
- **Proxy DLL Template**: Boilerplate code for creating proxy DLLs (like `dxgi.dll` or `dinput8.dll`) to load custom code into a game process.
- **MinHook Blueprint**: Implementations and best practices for using MinHook to intercept and modify game functions.

#### [Memory Scanning](Techniques/Memory_Scanning/)
- **Pattern Scanner**: Tools and techniques for finding dynamic memory addresses using byte pattern scanning (AOB scanning).

#### [Data Parsing](Techniques/Data_Parsing/)
- **Lightweight JSON Parser**: A minimal C++ JSON parser designed for reading mod configuration files without heavy dependencies.

#### [Build and Deployment](Techniques/Build_and_Deployment/)
- **Deployment Script**: Automated scripts for compiling mods, copying them to the game directory, and launching the game for testing.
