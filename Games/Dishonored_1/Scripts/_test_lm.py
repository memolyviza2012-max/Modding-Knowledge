import sys; sys.stdout.reconfigure(encoding='utf-8')
import os
from openai import OpenAI

client = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio", timeout=30)

SYSTEM = """/no_think
Dishonored Translator (EN->TH).
RULES: "ID: English" → "ID: Thai" | exact line count | no commentary | preserve variables
GLOSSARY: Corvo Attano=คอร์โว อัตตาโน|The Outsider=ดิ เอาท์ไซเดอร์|Blink=บลิงก์"""

lines = ["DisConv_Blurb.6154.DisConv_Blurb: Somebody give me a hand!\n"]
prompt = "".join(lines) + "\n[OUTPUT TRANSLATED LINES ONLY]"

print("Testing LM Studio...")
res = client.chat.completions.create(
    model="qwen/qwen3-14b",
    messages=[
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": prompt}
    ],
    temperature=0.1,
    max_tokens=256,
)
print("Response:", repr(res.choices[0].message.content))
