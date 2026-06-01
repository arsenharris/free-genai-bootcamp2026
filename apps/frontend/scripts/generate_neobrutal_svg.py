import json
import os
import hashlib

INPUT_JSON = os.path.join(os.path.dirname(__file__), '..', 'src', 'data', 'flashcards_all.json')
OUT_DIR = os.path.join(os.path.dirname(__file__), '..', 'public', 'flashcards_neo')

PALETTE = [('#ff6b6b','#ffd6a5'), ('#00a5ad','#cfe8ff'), ('#e6a23c','#fef3d6'), ('#b28fd6','#f3e8ff'), ('#48cae4','#d8f5ff')]

SVG_TEMPLATE = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 140">
  <rect width="100%" height="100%" fill="#ffffff"/>
  <g fill="{main}">
    {shape}
  </g>
  <g fill="{accent}">
    {detail}
  </g>
</svg>
'''


def slugify(text):
    s = text.lower()
    import unicodedata
    s = ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
    s = ''.join(c for c in s if c.isalnum() or c.isspace())
    s = '-'.join(s.split())
    return s


def choose_shapes(hash_int):
    # choose simple geometric shapes based on hash
    r = hash_int % 5
    if r == 0:
        shape = '<circle cx="100" cy="70" r="34" />'
        detail = '<rect x="96" y="30" width="8" height="20" rx="4" transform="rotate(-20 100 40)" />'
    elif r == 1:
        shape = '<rect x="36" y="56" width="128" height="44" rx="12" />'
        detail = '<rect x="56" y="42" width="88" height="24" rx="10" />'
    elif r == 2:
        shape = '<ellipse cx="100" cy="84" rx="64" ry="28" />'
        detail = '<rect x="88" y="46" width="24" height="8" rx="4" />'
    elif r == 3:
        shape = '<rect x="52" y="28" width="96" height="84" rx="10" />'
        detail = '<rect x="78" y="12" width="44" height="20" rx="6" />'
    else:
        shape = '<rect x="44" y="60" width="112" height="40" rx="12" />'
        detail = '<rect x="120" y="40" width="28" height="18" rx="8" transform="rotate(-18 134 49)" />'
    return shape, detail


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    if not isinstance(data, list):
        print('No list found in', INPUT_JSON)
        return
    for item in data:
        word = item.get('spanish') or item.get('word')
        if not word:
            continue
        slug = slugify(word)
        h = int(hashlib.sha256(word.encode('utf-8')).hexdigest(), 16)
        main_col, accent_col = PALETTE[h % len(PALETTE)]
        shape, detail = choose_shapes(h)
        svg = SVG_TEMPLATE.format(main=main_col, accent=accent_col, shape=shape, detail=detail)
        out_path = os.path.join(OUT_DIR, slug + '.svg')
        with open(out_path, 'w', encoding='utf-8') as out:
            out.write(svg)
    print('Generated', len(data), 'SVGs to', OUT_DIR)

if __name__ == '__main__':
    main()
