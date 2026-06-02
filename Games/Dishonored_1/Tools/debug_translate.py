import sys
sys.stdout.reconfigure(encoding='utf-8')
import re
from openai import OpenAI

client = OpenAI(base_url="http://127.0.0.1:1234/v1", api_key="sk-lm-FGSsQAGO:X4nhoD89WqUz1IZKoRpB")

def clean_llm_output(raw_text):
    # The model echoes the prompt and adds its thinking.
    # Strategy: Find the LAST occurrence of "Thai:" and get text after it,
    # OR find text after first "Thai:" but before the next "Text:" or explanation.
    # Better: find first Thai block between two "Thai:" markers
    
    # Find second Thai: (model echoes prompt then responds)
    parts = raw_text.split('Text:')
    if len(parts) >= 2:
        # text after first Text: is the echo, take from parts[0] after last Thai:
        thai_response = parts[0]
        thai_idx = thai_response.rfind('Thai:')
        if thai_idx >= 0:
            result = thai_response[thai_idx+5:].strip()
        else:
            result = thai_response.strip()
    else:
        result = raw_text.strip()
    
    # Remove trailing explanation/thinking
    result = re.split(r'\n(Okay,|I need to,|Let me,|First,|The translation|This is)', result, flags=re.IGNORECASE)[0]
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

# Test
test_text = "You are not signed in. In order to save progress, you will need to be signed in."
result = translate_with_qwen(test_text)
print("Result:", result)
print("Has Thai:", any(ord(c) > 0xE00 for c in result))
