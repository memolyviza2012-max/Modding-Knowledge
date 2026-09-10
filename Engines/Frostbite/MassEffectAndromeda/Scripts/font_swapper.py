"""
Auto Glyph Swapper for Frostbite Engine (Mass Effect: Andromeda)
================================================================
Reads a TTF font, finds Thai glyphs (U+0E00 - U+0E7F), and maps them
to the Japanese block (U+3040 - U+30BF) using a direct offset.
Offset: Japanese_Code = Thai_Code + 0x2240.
"""

import sys
import os
from fontTools.ttLib import TTFont

def swap_glyphs(input_ttf, output_ttf):
    print("Loading font: {}...".format(os.path.basename(input_ttf)))
    try:
        font = TTFont(input_ttf)
    except Exception as e:
        print("Error loading font: {}".format(e))
        return False

    cmap_table = font['cmap']
    
    # Mapping Thai (0x0E00 - 0x0E7F) to Chinese CJK Unified Ideographs (0x4E00 - 0x4E7F)
    # This prevents word-wrapping crashes (no Kinsoku Shori rules for standard Hanzi)
    OFFSET = -0x4000
    
    mapped_count = 0
    
    for table in cmap_table.tables:
        if table.isUnicode():
            new_mappings = {}
            for code_point, glyph_name in table.cmap.items():
                if 0x0E00 <= code_point <= 0x0E7F:
                    target_code = code_point - OFFSET
                    new_mappings[target_code] = glyph_name
            
            if new_mappings:
                table.cmap.update(new_mappings)
                mapped_count = max(mapped_count, len(new_mappings))

    if mapped_count > 0:
        print("Successfully mapped {} Thai glyphs to Japanese slots.".format(mapped_count))
        print("Saving modified font to: {}...".format(os.path.basename(output_ttf)))
        font.save(output_ttf)
        print("Done!")
        return True
    else:
        print("Warning: No Thai glyphs (U+0E00-U+0E7F) found in the input font.")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 3:
        input_font = r"E:\Mod_Workspace\Tool\ThaiFont\fonts_main\1_IBMPlexSans_PUA.ttf"
        output_font = r"E:\Mod_Workspace\MEAndromeda_Mod_Workspace\Working_Files\Thai_T\1_IBMPlexSans_ChineseMapped.ttf"
    else:
        input_font = sys.argv[1]
        output_font = sys.argv[2]
        
    swap_glyphs(input_font, output_font)
