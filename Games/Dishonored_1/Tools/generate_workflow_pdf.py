#!/usr/bin/env python3
"""
Generate Dishonored 1 Thai Mod Workflow PDF
Using reportlab for proper Unicode support
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

OUTPUT_PATH = r"E:\Mod_Workspace\Dishonored_Mod_Workspace\04_output\Dishonored1_ThaiMod_Workflow.pdf"

# Document setup
doc = SimpleDocTemplate(
    OUTPUT_PATH,
    pagesize=A4,
    rightMargin=2*cm, leftMargin=2*cm,
    topMargin=2*cm, bottomMargin=2*cm
)

# Styles
styles = getSampleStyleSheet()
W = A4[0] - 4*cm

title_style = ParagraphStyle(
    'Title', parent=styles['Title'],
    fontSize=18, textColor=colors.HexColor('#1a1a5e'),
    spaceAfter=6, alignment=TA_CENTER
)
subtitle_style = ParagraphStyle(
    'Subtitle', parent=styles['Normal'],
    fontSize=11, textColor=colors.HexColor('#444444'),
    spaceAfter=20, alignment=TA_CENTER, fontName='Helvetica-Oblique'
)
h1_style = ParagraphStyle(
    'H1', parent=styles['Heading1'],
    fontSize=14, textColor=colors.white,
    backColor=colors.HexColor('#1a1a5e'),
    spaceAfter=8, spaceBefore=14,
    leftIndent=-0.5*cm, rightIndent=-0.5*cm,
    borderPadding=(4, 4, 4, 4)
)
h2_style = ParagraphStyle(
    'H2', parent=styles['Heading2'],
    fontSize=12, textColor=colors.HexColor('#1a1a5e'),
    backColor=colors.HexColor('#ddddff'),
    spaceAfter=6, spaceBefore=10,
    borderPadding=(3, 3, 3, 3)
)
body_style = ParagraphStyle(
    'Body', parent=styles['Normal'],
    fontSize=10, leading=14, alignment=TA_JUSTIFY,
    spaceAfter=6
)
bullet_style = ParagraphStyle(
    'Bullet', parent=styles['Normal'],
    fontSize=10, leading=13,
    leftIndent=16, bulletIndent=6,
    spaceAfter=3
)
code_style = ParagraphStyle(
    'Code', parent=styles['Normal'],
    fontSize=8, leading=11,
    fontName='Courier',
    backColor=colors.HexColor('#f0f0f0'),
    borderPadding=(4, 4, 4, 4),
    spaceAfter=8, leftIndent=6, rightIndent=6
)
note_style = ParagraphStyle(
    'Note', parent=styles['Normal'],
    fontSize=9, leading=12, fontName='Helvetica-Oblique',
    backColor=colors.HexColor('#fff8dc'),
    borderPadding=(4, 4, 4, 4),
    spaceAfter=8
)

def h1(text):
    return Paragraph(text, h1_style)

def h2(text):
    return Paragraph(text, h2_style)

def body(text):
    return Paragraph(text, body_style)

def bullet(text):
    return Paragraph("<bullet>&bull;</bullet> " + text, bullet_style)

def code(text):
    return Paragraph(text, code_style)

def note(text):
    return Paragraph(text, note_style)

def hr():
    return HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#aaaaaa'), spaceAfter=6, spaceBefore=6)

# Build content
story = []

# Title
story.append(Paragraph("Dishonored 1 - Thai Modding Workflow", title_style))
story.append(Paragraph("Complete Guide: Extraction, Translation &amp; Repacking", subtitle_style))
story.append(hr())

# Section 1: Overview
story.append(h1("1. OVERVIEW"))
story.append(body(
    'This document describes the complete pipeline used to create the Dishonored 1 Thai mod. '
    'The process converts English text files (INT) into Thai text files (TH) and injects them '
    'back into the game\'s UE2/UPK package files.'
))
story.append(body(
    'The pipeline works with Dishonored\'s "DisConv" dialogue files - binary chunks stored inside '
    'UPK archives. Each UPK file contains multiple DisConv entries (Blurb, PlayerChoice, NonWord types).'
))

# Section 2: Folder Structure
story.append(h1("2. FOLDER STRUCTURE"))
story.append(body('The modding workspace follows this organization:'))
story.append(code(
    "D:\\Mod_Workspace\\Dishonored_Mod_Workspace\\\n"
    "+-- 01_source/              # Original UPK files (compressed)\n"
    "|   +-- CookedPCConsole/   # Main game UPKs (72 files)\n"
    "+-- 02_translated/          # Final patched UPK files\n"
    "+-- 03_working/             # Working directory (temporary)\n"
    "+-- 03_tools/               # Scripts and toolkit\n"
    "|   +-- dishonored-toolkit/ # Main toolkit (from GitHub)\n"
    "+-- 04_output/             # Final installer + documentation\n"
    "+-- _DYextracted/          # Decompressed UPK contents\n"
    "+-- _DYpatched/           # Patched binaries before repack\n"
    "+-- Mods/                 # Loose file overrides (optional)\n"
    "+-- memory/               # Session logs"
))

# Section 3: Engine Background
story.append(h1("3. ENGINE BACKGROUND"))
story.append(h2("3.1 UPK File Format"))
story.append(body('Dishonored uses Unreal Engine 2 (UE2) package files (.upk). Key characteristics:'))
story.append(bullet("Big-endian byte order (different from standard UE3/UE4)"))
story.append(bullet("LZO compression for most files (compFlags = 2)"))
story.append(bullet("Signature: 0x9e2a83c1"))
story.append(bullet('Contains "DisConv" dialogue objects (Blurb, PlayerChoice, NonWord)'))
story.append(Spacer(1, 0.2*cm))

story.append(h2("3.2 DisConv Objects"))
story.append(body('Dialogue is stored in three types of binary objects:'))
story.append(bullet("DisConv_Blurb: Single-line dialogue/subtitle text (m_Text field)"))
story.append(bullet("DisConv_PlayerChoice: Multiple choice options (m_Choices_Static array)"))
story.append(bullet("DisConv_NonWord: Non-verbal sounds/emotes"))
story.append(Spacer(1, 0.2*cm))
story.append(body('Each object has a text region encoded as:'))
story.append(bullet("INT text: ASCII/ISO-8859-1 with null terminator"))
story.append(bullet("TH text: UTF-16LE with null terminator, length negated"))

story.append(PageBreak())

# Section 4: Toolkit
story.append(h1("4. THE TOOLKIT"))
story.append(body('Toolkit: <a href="https://github.com/deadYokai/dishonored-toolkit-main">https://github.com/deadYokai/dishonored-toolkit-main</a>'))
story.append(body(
    'The toolkit was forked and customized for Thai modding. Key scripts in '
    'dishonored-toolkit/scripts/:'
))
story.append(bullet("<b>binary_be.py</b> - Big-endian BinaryStream (drop-in for standard binary.py)"))
story.append(bullet("<b>upkreader_be.py</b> - Big-endian UPK reader (original uses little-endian)"))
story.append(bullet("<b>fix_unpack.py</b> - Decompress LZO UPK + extract to _DYextracted/"))
story.append(bullet("<b>fix_yaml.py</b> - Extract readable ASCII strings from binary DisConv files"))
story.append(bullet("<b>extract_from_extracted.py</b> - Parse binary DisConv files with UpkElements"))
story.append(bullet("<b>pack_thai.py</b> - Patch Thai text into DisConv binaries, repack UPK"))
story.append(bullet("<b>build_upk.py</b> - Rebuild uncompressed UPK from _DYextracted folder"))
story.append(bullet("<b>repack_disfonts.py</b> - Special font UPK repacker"))
story.append(Spacer(1, 0.2*cm))

story.append(h2("4.1 Key Customization: Big-Endian"))
story.append(body(
    'Stock Dishonored UPK files are BIG-ENDIAN, but the original toolkit assumed '
    'little-endian. Solution: created <b>binary_be.py</b> and <b>upkreader_be.py</b> as big-endian '
    'drop-in replacements. The fix_unpack.py script byteswaps the entire file when a '
    'little-endian signature is detected.'
))

# Section 5: Pipeline
story.append(h1("5. THE 5-STEP PIPELINE"))

story.append(h2("Step 1: DECOMPRESS"))
story.append(body(
    'Most Dishonored UPK files are LZO compressed. Must decompress before processing.\n'
    'Tool: decompress.exe (UE3 tool) or fix_unpack.py (Python)\n'
    'Input: 01_source/CookedPCConsole/*.upk (compressed)\n'
    'Output: _DYextracted/&lt;upkname&gt;/ (decompressed binaries)'
))
story.append(code(
    "# Using fix_unpack.py\n"
    "python dishonored-toolkit/scripts/fix_unpack.py &lt;upk_name&gt; &lt;source_path&gt;\n\n"
    "# Or using umodel + manual decompress\n"
    "./decompress.exe input.upk output.upk.decompressed\n"
    "# Then manually extract DisConv objects"
))

story.append(h2("Step 2: UNPACK"))
story.append(body(
    'Extract DisConv dialogue from the decompressed UPK binary into YAML format.\n'
    'Tool: extract_from_extracted.py\n'
    'Input: _DYextracted/&lt;upkname&gt;/ (decompressed binaries + _names.txt)\n'
    'Output: &lt;upkname&gt;_INT.yaml (key-value pairs of English text)'
))
story.append(code(
    "# Extract INT dialogue from specific UPK\n"
    "cd dishonored-toolkit/scripts\n"
    "python extract_from_extracted.py L_Brothel_P L_Brothel_P_INT.yaml INT\n\n"
    "# Files needed in _DYextracted/L_Brothel_P/:\n"
    "#   _names.txt     - dNames array (exported from UPK)\n"
    "#   _header        - UPK header bytes\n"
    "#   _objects.txt   - Object table\n"
    "#   DisConv_*.DisConv_*  - Binary dialogue objects"
))

story.append(h2("Step 3: TRANSLATE"))
story.append(body(
    'Send YAML to AI translation server (LM Studio with qwen3-14b model).\n'
    'Tool: translate_batch.py / translate_shield_v2.py\n'
    'Input: &lt;upkname&gt;_INT.yaml\n'
    'Output: &lt;upkname&gt;_TH.yaml'
))
story.append(code(
    "# Translation script (translate_batch.py)\n"
    "LM_URL = \"http://127.0.0.1:1234/v1/chat/completions\"\n"
    "MODEL = \"qwen/qwen3-14b\"\n"
    "BATCH_SIZE = 20\n\n"
    "payload = {\n"
    "    \"model\": MODEL,\n"
    "    \"messages\": [{\"role\": \"user\", \"content\": prompt}],\n"
    "    \"temperature\": 0.3,\n"
    "    \"max_tokens\": 3000\n"
    "}"
))

story.append(PageBreak())

story.append(h2("Step 3.5: CLEAN YAML"))
story.append(body(
    'AI output often contains extra lines or formatting errors. Clean using <b>fix_yaml.py</b>\n'
    'to ensure YAML keys match the INT file exactly. Also important for Thai: '
    'use PyThaiNLP word_tokenize with engine="newmm" before sending to AI to ensure '
    'proper Thai word segmentation in the prompt.'
))

story.append(h2("Step 4: PACK"))
story.append(body(
    'Inject translated Thai text back into binary DisConv files and repack UPK.\n'
    'Tool: pack_thai.py\n'
    'Input: _DYextracted/&lt;upkname&gt;/ + &lt;upkname&gt;_TH.yaml\n'
    'Output: &lt;upkname&gt;_patched.upk (in _DYpatched/)'
))
story.append(code(
    "# Pack Thai YAML into UPK\n"
    "python pack_thai.py &lt;upk_name&gt; &lt;thai_yaml_path&gt; &lt;output_upk&gt; TH\n\n"
    "# For INT rebuild:\n"
    "python build_upk.py &lt;upk_name&gt; &lt;int_yaml_path&gt; &lt;output_upk&gt; INT\n\n"
    "# Key patching logic (pack_thai.py):\n"
    "if isINT:\n"
    "    eStr = pStr.encode(\"ISO-8859-1\")\n"
    "    eStr += b\"\\\\x00\"\n"
    "else:\n"
    "    # Thai: UTF-16LE encoding\n"
    "    eStr = pStr.encode(\"utf-16le\")\n"
    "    eStr += b\"\\\\x00\\\\x00\"\n"
    "    lStr = lStr * -1  # Negate length for Thai"
))

story.append(h2("Step 5: OUTPUT"))
story.append(body(
    'Copy patched UPK files to 02_translated/ folder for distribution.\n'
    'Use Nullsoft Installer (NSIS) to create installer .exe.'
))
story.append(code(
    "# Copy patched UPKs to output folder\n"
    "Copy-Item \"_DYpatched/*.upk\" -Destination \"02_translated/CookedPCConsole/\"\n\n"
    "# Create installer with NSIS\n"
    "makensis 04_output/d1.0.iss  # installer script"
))

# Section 6: Special Considerations
story.append(h1("6. SPECIAL CONSIDERATIONS"))

story.append(h2("6.1 Thai Text Encoding"))
story.append(body(
    'Thai text requires UTF-16LE encoding (not UTF-8) with null terminator. '
    'Length must be NEGATED in the binary (e.g., Thai text of 5 chars = -5). '
    'The pack_thai.py script handles this automatically.'
))

story.append(h2("6.2 GFxUI.int - DO NOT TRANSLATE"))
story.append(note(
    "WARNING: The file GFxUI.int in the UI folder contains Scaleform/Flash font control codes. "
    "Translating this file will cause the game to crash on boot. Only translate actual "
    "text content, not UI control/metadata files."
))

story.append(h2("6.3 Thai Spacing (PyThaiNLP)"))
story.append(body(
    'Before sending text to AI for translation, Thai text should be word-tokenized '
    'using PyThaiNLP to ensure proper word boundaries:'
))
story.append(code(
    "from pythainlp import word_tokenize\n"
    "text = word_tokenize(english_text, engine=\"newmm\")\n\n"
    "# This prevents the AI from breaking Thai compound words incorrectly."
))

story.append(h2("6.4 Auto-Resume Feature"))
story.append(body(
    'Translation scripts should implement auto-resume: check if output file exists, '
    'load existing translations, and continue from where it left off. This prevents '
    'data loss when the AI server times out or the script is interrupted. '
    '<b>Important:</b> flush() the output file after every batch to ensure data is written.'
))

story.append(PageBreak())

# Section 7: Common Errors
story.append(h1("7. COMMON ERRORS &amp; FIXES"))
story.append(bullet("<b>SIGKILL (timeout)</b>: Increase exec timeout, or split large files into smaller batches"))
story.append(bullet("<b>Signature mismatch</b>: File is wrong endianness - use binary_be.py big-endian reader"))
story.append(bullet("<b>Bad name index</b>: Corrupted UPK export table - rebuild from _DYextracted"))
story.append(bullet("<b>Invalid String ID (Thai)</b>: UTF-16LE encoding issue in Thai strdb - use proper repack"))
story.append(bullet("<b>Font crash</b>: GFxUI.int was translated - restore original, do not translate it"))
story.append(bullet("<b>LZO decompress fail</b>: Check compFlags - some files use ZLIB (1) instead of LZO (2)"))
story.append(Spacer(1, 0.3*cm))

# Section 8: Quick Reference
story.append(h1("8. QUICK REFERENCE"))
story.append(code(
    "# 1. Decompress\n"
    "python fix_unpack.py &lt;upk_name&gt; &lt;source_upk_path&gt;\n\n"
    "# 2. Extract INT YAML\n"
    "python extract_from_extracted.py &lt;upk_name&gt; &lt;output_yaml&gt; INT\n\n"
    "# 3. Translate (batch)\n"
    "python translate_batch.py  # Edit FILE_PATH first\n\n"
    "# 4. Clean YAML\n"
    "python fix_yaml.py &lt;upk_name&gt; &lt;yaml_path&gt;\n\n"
    "# 5. Pack Thai\n"
    "python pack_thai.py &lt;upk_name&gt; &lt;thai_yaml&gt; &lt;output.upk&gt; TH\n\n"
    "# 6. Output\n"
    "Copy _DYpatched/*.upk to 02_translated/CookedPCConsole/"
))

story.append(Spacer(1, 0.5*cm))
story.append(hr())
story.append(body(
    '<i>Document generated: 2026-05-08 | For questions, refer to memory logs in workspace or Discord community.</i>'
))

# Build
doc.build(story)
print(f"PDF generated: {OUTPUT_PATH}")
