import os
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="sk-lm-FGSsQAGO:X4nhoD89WqUz1IZKoRpB")

def clean_llm_output(raw_text):
    # Qwen echoes the prompt then adds thinking. Extract text after the second "Thai:"
    parts = raw_text.split('Text:')
    if len(parts) >= 2:
        thai_response = parts[0]
        thai_idx = thai_response.rfind('Thai:')
        if thai_idx >= 0:
            result = thai_response[thai_idx+5:].strip()
        else:
            result = thai_response.strip()
    else:
        result = raw_text.strip()
    
    # Remove trailing thinking/explanation
    result = re.split(r'\n(Okay,|I need to|Let me|First,|The translation|This is)', result, flags=re.IGNORECASE)[0]
    result = re.split(r'\n(เหตุผล|หมายเหตุ|Note)', result, flags=re.IGNORECASE)[0]
    result = result.strip().strip('"').strip("'").strip()
    
    if len(result) < 2:
        result = raw_text.strip()
    
    return result

def translate_with_qwen(text):
    p = "คุณคือนักแปลเกม Dishonored สไตล์ดาร์กแฟนตาซี กฎเหล็ก: ห้ามอธิบาย ให้พิมพ์เฉพาะภาษาไทยเท่านั้น"
    try:
        r = client.completions.create(
            model="qwen/qwen3-14b",
            prompt=p + "\n" + "Text: " + text + "\nThai:",
            max_tokens=300,
            temperature=0.3
        )
        raw = r.choices[0].text
        return clean_llm_output(raw)
    except Exception as e:
        print("API Error:", e)
        return text

def process_int_file(source_path, output_path):
    print("เริ่ม:", os.path.basename(source_path))
    
    # Detect encoding from BOM
    with open(source_path, 'rb') as f:
        raw = f.read()
    
    if raw[:2] == b'\xff\xfe':
        encoding = 'utf-16le'
    elif raw[:4] == b'\x00\x5b\x54\x77':  # UTF-16BE BOM 005B "T" 0077 "w"
        encoding = 'utf-16be'
    elif raw[:4] == b'\xfe\xff':
        encoding = 'utf-16be'
    else:
        encoding = 'utf-8'
    
    with open(source_path, 'r', encoding=encoding) as f:
        lines = f.readlines()

    translated_lines = []
    for line in lines:
        ol = line.strip()
        if not ol or ol.startswith("[") or ol.startswith(";"):
            translated_lines.append(line)
            continue
        m = re.match(r'([^=]+)="([^"]*)"', ol)
        if m:
            key = m.group(1)
            ot = m.group(2)
            if ot:
                print("  ต้นฉบับ:", ot)
                tt = translate_with_qwen(ot)
                print("  แปลผล:", tt)
                translated_lines.append(key + '="' + tt + '"' + "\n")
            else:
                translated_lines.append(line)
        else:
            translated_lines.append(line)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # Write as UTF-8 (UE3 can handle it, or convert later)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)
    print("เสร็จ =>", output_path)

src = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\01_source\Twk_UI_MainMenu.int"
out = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Twk_UI_MainMenu.int"
process_int_file(src, out)
