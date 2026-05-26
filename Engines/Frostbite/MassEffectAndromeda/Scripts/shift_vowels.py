"""
Shift Thai Upper Vowels and Tone Marks
======================================
Moves specific Thai upper vowels and tone marks up by a specific Y offset
to prevent them from hitting the consonants.
"""

import sys
import os
from fontTools.ttLib import TTFont

def shift_glyphs(input_ttf, output_ttf, shift_y=150):
    print(f"Loading font: {os.path.basename(input_ttf)}...")
    font = TTFont(input_ttf)
    glyf = font['glyf']
    cmap = font.getBestCmap()
    
    # Codes for upper vowels and tone marks
    target_codes = [
        0x0E31, 0x0E34, 0x0E35, 0x0E36, 0x0E37, 0x0E4D, 0x0E47, # upper vowels
        0x0E48, 0x0E49, 0x0E4A, 0x0E4B, 0x0E4C,                 # tone marks
        # PUA codes for upper marks
        0xF701, 0xF702, 0xF703, 0xF704,                         # tone marks on upper vowels
        0xF710, 0xF711, 0xF712,                                 # upper vowels shifted left
        0xF713, 0xF714, 0xF715, 0xF716, 0xF717,                 # tone marks shifted left
        0xF718, 0xF719, 0xF71A                                  # tone marks shifted down/left
    ]
    
    shifted_names = set()
    
    for code in target_codes:
        if code in cmap:
            name = cmap[code]
            if name not in shifted_names:
                shifted_names.add(name)
                glyph = glyf[name]
                
                # Check if it has coordinates (simple glyph)
                if hasattr(glyph, 'coordinates'):
                    # Must unpack and repack coordinates
                    new_coords = []
                    for x, y in glyph.coordinates:
                        new_coords.append((x, y + shift_y))
                    glyph.coordinates = fontTools.ttLib.tables._g_l_y_f.GlyphCoordinates(new_coords)
                
                # Check if it is a composite glyph
                elif hasattr(glyph, 'components'):
                    for comp in glyph.components:
                        comp.y += shift_y
    
    if shifted_names:
        print(f"Successfully shifted {len(shifted_names)} glyphs UP by {shift_y} units.")
        print(f"Saving to: {os.path.basename(output_ttf)}...")
        font.save(output_ttf)
        print("Done!")
    else:
        print("No target glyphs found to shift.")

if __name__ == "__main__":
    import fontTools # Ensure fontTools is available for GlyphCoordinates
    if len(sys.argv) < 3:
        input_font = r"E:\Mod_Workspace\Tool\ThaiFont\fonts_main\1_IBMPlexSans_PUA.ttf"
        output_font = r"E:\Mod_Workspace\Tool\ThaiFont\fonts_main\1_IBMPlexSans_PUA_Shifted.ttf"
    else:
        input_font = sys.argv[1]
        output_font = sys.argv[2]
        
    shift_y = 150 # default shift
    if len(sys.argv) == 4:
        shift_y = int(sys.argv[3])
        
    shift_glyphs(input_font, output_font, shift_y)
