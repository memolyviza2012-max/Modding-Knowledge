import sys; sys.stdout.reconfigure(encoding='utf-8')
import yaml

broken = '"ดิ เอาท์ไซเดอร์"... มีสิ่งมีชีวิตเช่นนั้นจริงหรือ'
key = 'DisConv_Blurb.3891.DisConv_Blurb'
line = key + ': ' + broken

print('Testing:', repr(line[:60]))
try:
    data = yaml.safe_load(line)
    print('PASSES yaml.safe_load:', repr(data[key]))
except Exception as e:
    print('FAILS yaml.safe_load:', str(e)[:80])

# Test with fix
def fix(value):
    stripped = value.strip()
    if not stripped.startswith('"'):
        return value
    qc = stripped.count('"')
    if qc <= 2:
        return value
    inner = stripped[1:-1]
    parts = inner.split('"')
    escaped = '\\"'.join(parts)
    return '"' + escaped + '"'

fixed = fix(broken)
print('Fixed value:', repr(fixed))
line2 = key + ': ' + fixed
print('Testing fixed:', repr(line2[:70]))
try:
    data = yaml.safe_load(line2)
    print('PASSES yaml.safe_load:', repr(data[key]))
except Exception as e:
    print('FAILS yaml.safe_load:', str(e)[:80])
