from openai import OpenAI
import sys
sys.stdout.reconfigure(encoding='utf-8')

client = OpenAI(base_url='http://127.0.0.1:1234/v1', api_key='sk-lm-FGSsQAGO:X4nhoD89WqUz1IZKoRpB')

# Qwen3 models need /enableThought option for thinking disabled
# Let's try with extra_body to disable thinking
resp = client.chat.completions.create(
    model='qwen/qwen3-14b',
    messages=[
        {'role': 'system', 'content': 'You are an expert translator. Reply ONLY with Thai translation.'},
        {'role': 'user', 'content': 'Translate to Thai: The plague has taken so many. We must find a cure.'}
    ],
    max_tokens=200,
    extra_body={'extra_body': {'disable_thinking': True}}  # try to disable reasoning
)
print('CHAT RESULT:', repr(resp.choices[0].message.content))
