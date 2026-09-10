import sys; sys.stdout.reconfigure(encoding='utf-8')
import yaml

# Test: original INT value
int_val = 'This "Outsider"... could there truly be such an entity?'
yaml_line = f'DisConv_Blurb.3891.DisConv_Blurb: {int_val}'
print('INT YAML:', yaml_line)

data = yaml.safe_load(yaml_line)
print('Parsed value:', repr(data['DisConv_Blurb.3891.DisConv_Blurb']))
print()

# Test: current broken TH value
broken_val = '"ดิ เอาท์ไซเดอร์"... มีสิ่งมีชีวิตเช่นนั้นจริงหรือ'
broken_line = f'DisConv_Blurb.3891.DisConv_Blurb: {broken_val}'
try:
    data = yaml.safe_load(broken_line)
    print('BROKEN parsed OK:', data)
except Exception as e:
    print('BROKEN error:', e)

print()

# Test: fixed TH value (escape internal quotes)
fixed_val = '"\\\"ดิ เอาท์ไซเดอร์\\\"\"... มีสิ่งมีชีวิตเช่นนั้นจริงหรือ'
fixed_line = f'DisConv_Blurb.3891.DisConv_Blurb: {fixed_val}'
try:
    data = yaml.safe_load(fixed_line)
    print('FIXED parsed OK:', repr(data['DisConv_Blurb.3891.DisConv_Blurb']))
except Exception as e:
    print('FIXED error:', e)
