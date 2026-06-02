import requests, time

LM_URL = "http://127.0.0.1:1234/v1/chat/completions"

TEST_LINES = [
    "DisConv_Blurb.4009.DisConv_Blurb: Trespass and we'll feed your guts to the hagfish.",
    "DisConv_Blurb.4010.DisConv_Blurb: Ring the alarm!",
    "DisConv_Blurb.4011.DisConv_Blurb: Cut that shit out.",
]

LOG = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\03_tools\test_seallm_log.txt"

with open(LOG, "w", encoding="utf-8") as f:
    for MODEL in ["seallms-v3-7b-chat-uncensored", "qwen/qwen3-14b"]:
        print(f"\n=== Testing {MODEL} ===")
        f.write(f"\n=== Testing {MODEL} ===\n")
        
        text = "\n".join(TEST_LINES)
        payload = {
            "model": MODEL,
            "messages": [{"role": "user", "content": f"Translate to Thai:\n{text}"}],
            "temperature": 0.3,
            "max_tokens": 300
        }
        try:
            r = requests.post(LM_URL, json=payload, timeout=180)
            data = r.json()
            if "choices" in data:
                result = data["choices"][0]["message"]["content"]
                f.write(f"Result:\n{result}\n")
                print(f"Result preview: {result[:200]}")
                
                lines = [l.strip() for l in result.split("\n") if l.strip()]
                f.write(f"Total lines: {len(lines)}\n")
                for l in lines[:5]:
                    f.write(f"  {l}\n")
            else:
                f.write(f"No choices: {str(data)[:300]}\n")
                print(f"No choices: {str(data)[:200]}")
        except Exception as e:
            f.write(f"Error: {e}\n")
            print(f"Error: {e}")
        time.sleep(2)

print("\nDone - check log file")