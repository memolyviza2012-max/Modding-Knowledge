from openai import OpenAI
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio", timeout=120.0)

# Test with system prompt
r = c.chat.completions.create(
    model="qwen3-14b",
    messages=[
        {"role": "system", "content": "You are a translator. Output ONLY the translation."},
        {"role": "user", "content": "Translate to Thai: Hello world"}
    ],
    max_tokens=100,
    temperature=0.3
)
print("Response:", repr(r.choices[0].message.content))
