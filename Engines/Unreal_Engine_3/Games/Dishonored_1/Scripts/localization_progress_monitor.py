# localization_progress_monitor.py
# Monitor progress of localization batch translate
import sys; sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import os, glob, re, json
from datetime import datetime

SOURCE_DIR = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\02_translated\Localization\INT"
STATE_FILE = r"D:\Mod_Workspace\Dishonored_Mod_Workspace\localization_state.json"

GEMINI_INPUT_COST = 0.075  # $ per 1M tokens
GEMINI_OUTPUT_COST = 0.15  # $ per 1M tokens
EST_INPUT_TOKENS_PER_LINE = 20  # rough estimate
EST_OUTPUT_TOKENS_PER_LINE = 15  # rough estimate

def count_tokens(num_lines):
    """Estimate cost based on line count."""
    inp = num_lines * EST_INPUT_TOKENS_PER_LINE
    out = num_lines * EST_OUTPUT_TOKENS_PER_LINE
    inp_cost = inp * GEMINI_INPUT_COST / 1_000_000
    out_cost = out * GEMINI_OUTPUT_COST / 1_000_000
    return inp, out, inp_cost, out_cost

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {"batches_sent": 0, "lines_translated": 0, "files_translated": 0, "started_at": datetime.now().isoformat()}

def save_state(state):
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f)

def get_progress():
    all_files = glob.glob(SOURCE_DIR + "\\*.int")
    files_with_eng = 0
    files_done = 0
    total_eng_lines = 0

    for path in all_files:
        for enc in ('utf-16-le', 'utf-16-be', 'utf-8-sig', 'utf-8'):
            try:
                with open(path, 'r', encoding=enc, newline='') as f:
                    content = f.read()
                lines = content.split('\r\n') if enc == 'utf-16-le' else content.split('\n')
                eng_lines = [l for l in lines if re.search(r'[a-zA-Z]{2,}', l) and not l.strip().startswith(';') and not l.strip().startswith('[') and ('=' in l or ': ' in l)]
                if eng_lines:
                    files_with_eng += 1
                    total_eng_lines += len(eng_lines)
                else:
                    files_done += 1
                break
            except:
                continue

    return {
        "total_files": len(all_files),
        "files_with_eng": files_with_eng,
        "files_done": files_done,
        "total_eng_lines": total_eng_lines,
        "all_files": all_files
    }

def format_cost(inp, out):
    inp_cost = inp * GEMINI_INPUT_COST / 1_000_000
    out_cost = out * GEMINI_OUTPUT_COST / 1_000_000
    return inp_cost, out_cost

def main():
    state = load_state()
    prog = get_progress()

    total = prog["total_files"]
    done = prog["files_done"]
    with_eng = prog["files_with_eng"]
    eng_lines = prog["total_eng_lines"]

    pct = done / total * 100 if total > 0 else 0

    print(f"📊 Localization Progress — {datetime.now().strftime('%H:%M')}")
    print(f"───────────────────────────")
    print(f"Files total:    {total}")
    print(f"Files done:     {done} ({pct:.1f}%)")
    print(f"With English:   {with_eng}")
    print()
    print(f"English lines remaining: {eng_lines}")

    # Cost estimate
    batches = state.get("batches_sent", 0)
    lines_done = state.get("lines_translated", 0)
    inp, out, inp_cost, out_cost = count_tokens(lines_done)
    total_cost = inp_cost + out_cost

    print()
    print(f"💰 Cost Estimate")
    print(f"───────────────────────────")
    print(f"Batches sent:   {batches}")
    print(f"Lines done:     {lines_done:,}")
    print(f"Input used:    ~{inp:,} tokens (~${inp_cost:.4f})")
    print(f"Output used:   ~{out:,} tokens (~${out_cost:.4f})")
    print(f"───────────────────────────")
    print(f"Total cost:            ~${total_cost:.4f}")

    # Project full cost
    if eng_lines > 0 and lines_done > 0:
        cost_per_line = total_cost / lines_done
        full_cost = total_cost + (eng_lines * cost_per_line)
        print(f"Projected full cost:   ~${full_cost:.4f}")
    elif lines_done == 0:
        # Estimate based on batch size
        full_inp = eng_lines * EST_INPUT_TOKENS_PER_LINE
        full_out = eng_lines * EST_OUTPUT_TOKENS_PER_LINE
        full_cost = (full_inp * GEMINI_INPUT_COST + full_out * GEMINI_OUTPUT_COST) / 1_000_000
        print(f"Projected full cost:   ~${full_cost:.4f} (est.)")

if __name__ == "__main__":
    main()
