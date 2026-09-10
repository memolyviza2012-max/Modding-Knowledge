import glob
import yaml

def check_all():
    files = glob.glob('02_Translations_Workspace/**/*_TH.yaml', recursive=True)
    corrupted = []
    errors = []

    for f in files:
        with open(f, 'r', encoding='utf-8', errors='replace') as file:
            content = file.read()
            
        if '?????' in content:
            corrupted.append(f)
            
        try:
            yaml.safe_load(content)
        except Exception as e:
            errors.append((f, str(e)))

    print(f'Checked {len(files)} TH YAML files.')
    print(f'\nCorrupted files (contains ?????): {len(corrupted)}')
    for c in corrupted:
        print(' - ' + c)

    print(f'\nSyntax errors: {len(errors)}')
    for e in errors:
        print(f' - {e[0]}: {e[1].splitlines()[0]}')

if __name__ == '__main__':
    check_all()
