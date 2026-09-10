import sys; sys.stdout.reconfigure(encoding='utf-8')
import yaml

# The broken TH value
broken = '"ดิ เอาท์ไซเดอร์"... มีสิ่งมีชีวิตเช่นนั้นจริงหรือ'
print('Broken value:', repr(broken))

# What we want: entire thing quoted, internal " escaped
# Strip outer quotes
if broken.startswith('"') and broken.endswith('"'):
    inner = broken[1:-1]
else:
    inner = broken

print('Inner:', repr(inner))

# Escape internal quotes
escaped_inner = inner.replace('"', '\\"')
print('Escaped inner:', repr(escaped_inner))

# Re-quote
fixed = '"' + escaped_inner + '"'
print('Fixed value:', repr(fixed))

# Now test with yaml
yaml_line = 'DisConv_Blurb.3891.DisConv_Blurb: ' + fixed
print('Full YAML line:', yaml_line[:80])

try:
    data = yaml.safe_load(yaml_line)
    print('SUCCESS! Parsed value:', repr(data['DisConv_Blurb.3891.DisConv_Blurb']))
except Exception as e:
    print('ERROR:', e)
