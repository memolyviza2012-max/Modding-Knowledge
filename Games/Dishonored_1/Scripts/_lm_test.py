from openai import OpenAI
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio", timeout=30.0)
print("LM Studio connected:", c)
r = c.chat.completions.create(model="qwen3-14b", messages=[{"role": "user", "content": "Translate: Hello"}], max_tokens=20, temperature=0.1)
print("Response:", r.choices[0].message.content)
