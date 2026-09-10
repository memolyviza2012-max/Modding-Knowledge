from openai import OpenAI
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

c = OpenAI(base_url="http://localhost:1234/v1", api_key="lm-studio", timeout=120.0)

# Try with the full model name
r = c.chat.completions.create(
    model="qwen/qwen3-14b",
    messages=[
        {"role": "system", "content": "You are a translator."},
        {"role": "user", "content": "Say hello in Thai"}
    ],
    max_tokens=50,
    temperature=0.3
)
print("Response:", repr(r.choices[0].message.content))
print("Finish reason:", r.choices[0].finish_reason)
print("Usage:", r.usage)
