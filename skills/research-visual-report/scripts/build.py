#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""research-visual-report build pipeline.

Parse a research-survey markdown -> single-file Apple-style interactive HTML
(collapsible paper cards, sticky filter toolbar, scroll-spy TOC, optional
spectrum diagram and evolution timeline). Content fidelity is verified
line-by-line against the source md (missing must be 0).

Usage:
    python build.py path/to/doc.md [custom.config.py]

A custom config file is plain python defining CONFIG = {...} which
deep-overrides DEFAULT_CONFIG. All domain-specific content lives in CONFIG.
"""
import ast
import base64
import html
import json
import mimetypes
import os
import re
import sys
from urllib.parse import urlparse

# ============================ DEFAULT CONFIG ============================
DEFAULT_CONFIG = {
    # ---- I/O ----
    'out': None,                     # default: same name with .html
    'lang': 'zh-CN',                 # document language
    # ---- card system ----
    'card_section': '3',             # '## N.' section holding the card list
    'fam_heading': r'^([A-H])\.',    # regex for '### X.' family headings
    'fams': {                        # family key -> (color, toolbar label); <=8 keys from a..h
        'a': ('#0071e3', 'A 类别一'), 'b': ('#34c759', 'B 类别二'),
        'c': ('#af52de', 'C 类别三'), 'd': ('#ff9500', 'D 类别四'),
    },
    'card_marker_fields': {'核心问题', 'arXiv', 'OpenReview'},
    'field_style': {                 # field name -> (css class, display label)
        '核心问题': ('f-q', '核心问题'),
        '方法': ('f-m', '方法'),
        '关键技术创新点': ('f-i', '关键技术创新点'),
        '实验设置与主要结果': ('f-r', '实验设置与主要结果'),
    },
    # Optional display groups: outer field label -> source field names. Source
    # labels remain visible inside the group so no report detail is discarded.
    'field_groups': None,
    'point_group_fields': (),        # grouped fields rendered as bullet points
    'group_item_limits': {},         # optional visible-item cap per group
    'steps_field': '方法',           # field rendered as numbered steps
    'link_fields': ('arXiv', 'OpenReview'),
    'figure_fields': ('图示', 'Figure', 'Figures'),
    'embed_local_images': True,       # produce a portable single-file HTML
    'max_image_bytes': 12_000_000,    # per-image safety limit
    'alphaxiv': True,                # rewrite arxiv.org/abs/ -> www.alphaxiv.org/abs/
    'default_date': ('2026', '2026.99'),   # cards without a parseable date
    # ---- optional components ----
    'spectrum': None,                # e.g. {'detect': 'token', 'detect_lines': ('token', '细', '方差'),
                                     #       'nodes': [...], 'bar': ('细', '粗'),
                                     #       'labels': ('左标注', '右标注')}
    'timeline': None,                # e.g. {'cols': ['24Q1', ...], 'year_base': 24,
                                     #       'extra_rows': [{'key','color','label',
                                     #                       'items': [(col, short, full)]}],
                                     #       'note': '...'}
    # ---- page copy ----
    'brand': 'Research Survey',
    'eyebrow': '调研报告',
    'meta_desc': '',
    'footer': '',
    'hero_stats': [('{n_cards}', '方法卡片'), ('{n_fams}', '分类体系')],
    'search_placeholder': '搜索方法名、关键词、环境…',
    'sort_button': '⇅ 最新优先',
    'sort_button_alt': '⇅ 时间正序',
    'collapse_button': '收起全部',
    'expand_button': '展开全部',
    'count_tpl': '显示 {visible} / {total} 篇',
    'toc_title': '目录',
}

HEX_COLOR_RE = re.compile(r'^#[0-9a-fA-F]{6}$')


def load_config(path):
    """Load a literal CONFIG dictionary without executing arbitrary Python."""
    tree = ast.parse(open(path, encoding='utf-8').read(), filename=path)
    assignments = [n for n in tree.body if isinstance(n, ast.Assign)]
    if len(tree.body) != 1 or len(assignments) != 1:
        raise ValueError('config.py must contain only: CONFIG = {...}')
    node = assignments[0]
    if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name) \
            or node.targets[0].id != 'CONFIG':
        raise ValueError('config.py must define CONFIG = {...}')
    config = ast.literal_eval(node.value)
    if not isinstance(config, dict):
        raise ValueError('CONFIG must be a dictionary')
    return config


def validate_config(cfg):
    if not re.fullmatch(r'[A-Za-z0-9-]{1,16}', str(cfg['card_section'])):
        raise ValueError('card_section must be a short letter/number identifier')
    if not 1 <= len(cfg['fams']) <= 8:
        raise ValueError('fams must contain 1 to 8 families')
    for key, value in cfg['fams'].items():
        if key not in 'abcdefgh':
            raise ValueError('family keys must be lowercase a through h')
        if not isinstance(value, (tuple, list)) or len(value) != 2:
            raise ValueError('each family must be (color, label)')
        if not HEX_COLOR_RE.fullmatch(value[0]):
            raise ValueError('family colors must use #RRGGBB')
    try:
        fam_pattern = re.compile(cfg['fam_heading'])
    except re.error as error:
        raise ValueError('fam_heading is not a valid regular expression') from error
    if fam_pattern.groups < 1:
        raise ValueError('fam_heading must capture the family key')
    for style in cfg['field_style'].values():
        if not isinstance(style, (tuple, list)) or len(style) != 2:
            raise ValueError('field_style entries must be (css_class, label)')
        if not re.fullmatch(r'[A-Za-z0-9_-]+', style[0]):
            raise ValueError('field_style CSS classes contain invalid characters')
    timeline = cfg.get('timeline')
    if timeline:
        for row in timeline.get('extra_rows', []):
            if not HEX_COLOR_RE.fullmatch(row['color']):
                raise ValueError('timeline colors must use #RRGGBB')
    default_date = cfg['default_date']
    if not isinstance(default_date, (tuple, list)) or len(default_date) != 2:
        raise ValueError('default_date must be (display, sort_key)')
    if not re.fullmatch(r'20\d{2}(?:\.\d{2}|\.99)', str(default_date[1])):
        raise ValueError('default_date sort key must look like 2026.09 or 2026.99')
    if not isinstance(cfg['figure_fields'], (tuple, list)):
        raise ValueError('figure_fields must be a tuple or list')
    field_groups = cfg.get('field_groups')
    if field_groups is not None:
        if not isinstance(field_groups, dict) or not field_groups:
            raise ValueError('field_groups must be a non-empty dictionary or None')
        seen = set()
        for group_name, source_names in field_groups.items():
            if not isinstance(group_name, str) or not group_name.strip():
                raise ValueError('field_groups keys must be non-empty strings')
            if not isinstance(source_names, (tuple, list)) or not source_names:
                raise ValueError('field_groups values must be non-empty tuples or lists')
            for source_name in source_names:
                if source_name in seen:
                    raise ValueError('source field appears in more than one field group: ' + source_name)
                seen.add(source_name)
        unknown_point_groups = set(cfg.get('point_group_fields', ())) - set(field_groups)
        if unknown_point_groups:
            raise ValueError('point_group_fields contains unknown groups')
        unknown_limited_groups = set(cfg.get('group_item_limits', ())) - set(field_groups)
        if unknown_limited_groups:
            raise ValueError('group_item_limits contains unknown groups')
        for group_name, limit in cfg.get('group_item_limits', {}).items():
            if not isinstance(limit, int) or limit < 1:
                raise ValueError('group_item_limits values must be positive integers')
    if not isinstance(cfg['max_image_bytes'], int) or cfg['max_image_bytes'] < 1:
        raise ValueError('max_image_bytes must be a positive integer')

def deep_merge(base, over):
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        else:
            out[k] = v
    return out

MD_PATH = sys.argv[1] if len(sys.argv) > 1 else None
if not MD_PATH:
    sys.exit('usage: python build.py doc.md [custom.config.py]')
CFG = DEFAULT_CONFIG
if len(sys.argv) > 2:
    custom_config = load_config(sys.argv[2])
    CFG = deep_merge(DEFAULT_CONFIG, custom_config)
    if 'fams' in custom_config:
        CFG['fams'] = custom_config['fams']
validate_config(CFG)
CFG['card_section'] = str(CFG['card_section'])

BASE = os.path.dirname(os.path.abspath(MD_PATH))
MD   = open(MD_PATH, encoding='utf-8').read()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS = SCRIPT_DIR
if not os.path.exists(os.path.join(ASSETS, 'style.css')):
    ASSETS = os.path.abspath(os.path.join(SCRIPT_DIR, '..', 'assets'))
CSS  = open(os.path.join(ASSETS, 'style.css'), encoding='utf-8').read()
JS   = open(os.path.join(ASSETS, 'app.js'), encoding='utf-8').read()
OUT  = CFG['out'] or os.path.splitext(MD_PATH)[0] + '.html'
FAMS = CFG['fams']
FAM_KEYS = ''.join(FAMS.keys())
FAM_CLASS = '[' + FAM_KEYS + ']'
BUILD_ERRORS = []
OMITTED_SOURCE_LINES = set()
CARD_SEQ = 0

# inject family colors into the CSS :root variables
for k, (color, _label) in FAMS.items():
    CSS = re.sub(r'(--fam-' + k + r':)[^;]+;', r'\g<1>' + color + ';', CSS)
# runtime copy used by app.js (button labels / count template)
RUNTIME_CONFIG = json.dumps({
    'sortButton': CFG['sort_button'],
    'sortButtonAlt': CFG['sort_button_alt'],
    'collapseButton': CFG['collapse_button'],
    'expandButton': CFG['expand_button'],
    'countTemplate': CFG['count_tpl'],
}, ensure_ascii=False).replace('<', '\\u003c')

# ---------------- inline rendering ----------------
def inline(t):
    t = t.replace('\\*', '\x00')   # escaped literal asterisk
    t = html.escape(t, quote=True)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',
               r'<a href="\2" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r'(?<!["\'>])(https?://[^\s<()（）]+)',
               r'<a href="\1" target="_blank" rel="noopener">\1</a>', t)
    t = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', t)
    t = re.sub(r'\*([^*\n]+)\*', r'<em>\1</em>', t)
    t = re.sub(r'`([^`]+)`', r'<code class="il">\1</code>', t)
    return t.replace('\x00', '*')

def strip_md(t):
    """plain-text form of an md fragment (for verification / attributes)"""
    t = t.replace('\\*', '\x00')
    t = re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', r'\1', t)
    t = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'\1', t)
    t = t.replace('**', '').replace('`', '')
    t = re.sub(r'(?<!\w)\*([^*]+)\*(?!\w)', r'\1', t)
    return t.replace('\x00', '*')

# ---------------- block parser ----------------
def parse_blocks(md):
    lines = md.split('\n')
    blocks, i = [], 0
    def is_item(l): return re.match(r'^\s*(- |\d+\. )', l)
    while i < len(lines):
        l = lines[i]
        if not l.strip():
            i += 1; continue
        if l.startswith('```'):
            buf, i = [], i + 1
            while i < len(lines) and not lines[i].startswith('```'):
                buf.append(lines[i]); i += 1
            blocks.append(('code', '\n'.join(buf))); i += 1; continue
        m = re.match(r'^(#{1,4})\s+(.*)$', l)
        if m:
            blocks.append(('h', len(m.group(1)), m.group(2).strip())); i += 1; continue
        if l.startswith('|'):
            buf = []
            while i < len(lines) and lines[i].startswith('|'):
                buf.append(lines[i]); i += 1
            blocks.append(('table', buf)); continue
        if l.startswith('>'):
            buf = []
            while i < len(lines) and lines[i].startswith('>'):
                buf.append(lines[i].lstrip('>').strip()); i += 1
            blocks.append(('quote', buf)); continue
        if re.match(r'^---\s*$', l):
            i += 1; continue  # hr carries no text
        if is_item(l):
            buf = []
            while i < len(lines):
                if is_item(lines[i]):
                    buf.append(lines[i]); i += 1
                elif not lines[i].strip():
                    j = i
                    while j < len(lines) and not lines[j].strip(): j += 1
                    if j < len(lines) and is_item(lines[j]):
                        i = j
                    else:
                        break
                else:
                    break
            blocks.append(('list', buf)); continue
        buf = []
        while i < len(lines) and lines[i].strip() \
                and not re.match(r'^(#{1,4}\s|```|\||>|---\s*$)', lines[i]) \
                and not is_item(lines[i]):
            buf.append(lines[i]); i += 1
        blocks.append(('para', buf))
    return blocks

# ---------------- renderers ----------------
def field_style(name):
    return CFG['field_style'].get(name, ('f-n', name))

def render_steps(text):
    parts = re.split(r'[;；]?\s*\((\d+)\)\s*', text)
    if len(parts) < 5:   # need >=2 numbered chunks
        return None
    prefix, rest = parts[0].strip(), parts[1:]
    steps = [(rest[k], rest[k+1].strip()) for k in range(0, len(rest) - 1, 2)]
    out = ''
    if prefix:
        out += '<p>' + inline(prefix) + '</p>'
    out += '<div class="steps">'
    for num, txt in steps:
        out += ('<div class="step"><span class="step-n">' + html.escape(num) +
                '</span><span class="step-t">' + inline(txt) + '</span></div>')
    out += '</div>'
    return out


IMAGE_RE = re.compile(
    r'^!\[([^\]]*)\]\(\s*([^\s)]+)(?:\s+["\']([^"\']*)["\'])?\s*\)\s*(.*)$'
)
IMAGE_MIMES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/svg+xml'}


def svg_is_passive(payload):
    """Reject active or externally-referencing SVG before embedding it."""
    text = payload.decode('utf-8', errors='ignore').lower()
    blocked = ('<script', '<foreignobject', 'javascript:', '<iframe', '<object', '<embed')
    if any(token in text for token in blocked):
        return False
    return not re.search(r'(?:href|src)\s*=\s*["\']\s*(?:https?:|//)', text)


def render_figure(text):
    """Render one Markdown image, embedding safe local raster assets by default."""
    match = IMAGE_RE.match(text.strip())
    if not match:
        BUILD_ERRORS.append('invalid figure field; expected ![alt](path "caption")')
        return '<p>' + inline(text) + '</p>'
    alt, source, title, trailing = match.groups()
    caption = (title or trailing or alt).strip()
    parsed = urlparse(source)
    src = source
    data_source = source
    if parsed.scheme:
        if parsed.scheme not in ('http', 'https'):
            BUILD_ERRORS.append('unsupported figure URL scheme: ' + parsed.scheme)
            return '<p>' + inline(text) + '</p>'
    else:
        candidate = os.path.realpath(os.path.join(BASE, source))
        if os.path.commonpath((BASE, candidate)) != BASE:
            BUILD_ERRORS.append('figure path escapes report directory: ' + source)
            return '<p>' + inline(text) + '</p>'
        if not os.path.isfile(candidate):
            BUILD_ERRORS.append('figure file not found: ' + source)
            return '<p>' + inline(text) + '</p>'
        size = os.path.getsize(candidate)
        if size > CFG['max_image_bytes']:
            BUILD_ERRORS.append('figure exceeds max_image_bytes: ' + source)
            return '<p>' + inline(text) + '</p>'
        mime = mimetypes.guess_type(candidate)[0] or ''
        if mime not in IMAGE_MIMES:
            BUILD_ERRORS.append('unsupported figure type: ' + source)
            return '<p>' + inline(text) + '</p>'
        if CFG['embed_local_images']:
            with open(candidate, 'rb') as image_file:
                raw_payload = image_file.read()
            if mime == 'image/svg+xml' and not svg_is_passive(raw_payload):
                BUILD_ERRORS.append('SVG contains active or external content: ' + source)
                return '<p>' + inline(text) + '</p>'
            payload = base64.b64encode(raw_payload).decode('ascii')
            src = 'data:' + mime + ';base64,' + payload
    return ('<figure class="paper-figure"><img src="' + html.escape(src, quote=True) +
            '" data-source="' + html.escape(data_source, quote=True) + '" alt="' +
            html.escape(alt, quote=True) + '" loading="lazy" decoding="async">' +
            ('<figcaption>' + inline(caption) + '</figcaption>' if caption else '') +
            '</figure>')

def render_card(title_raw, children, fam):
    global CARD_SEQ
    CARD_SEQ += 1
    body_id = 'card-body-' + str(CARD_SEQ)
    m = re.match(r'^\*\*([^*]+)\*\*\s*(.*)$', title_raw)
    title, note = (m.group(1), m.group(2)) if m else (title_raw, '')
    note_txt = strip_md(note).strip()
    tag = fam.upper() if fam and fam != 'x' else CFG.get('no_fam_tag', '·')
    # link fields collapse into the card head: jump button (arXiv -> alphaXiv),
    # （…）note -> venue badge, arXiv YYMM -> date badge + sort key
    quick_links, venue_texts, date_txt, data_date = [], [], '', ''
    for fname, fval in children:
        if fname not in CFG['link_fields']:
            continue
        um = re.search(r'(https?://[^\s()（）]+)', fval)
        if um:
            url = um.group(1).rstrip('）)。,;')
            link_url = url.replace('arxiv.org/abs/', 'www.alphaxiv.org/abs/') if CFG['alphaxiv'] else url
            label = 'alphaXiv' if link_url != url else fname
            quick_links.append('<a class="card-link" href="' + html.escape(link_url, quote=True) +
                               '" target="_blank" rel="noopener">' + html.escape(str(label)) + ' ↗</a>')
        vm = re.search(r'（([^）]+)）', fval)
        if vm:
            venue = vm.group(1).strip()
            if venue not in venue_texts:
                venue_texts.append(venue)
        dm = re.search(r'abs/(\d{2})(\d{2})\.\d+', fval)
        if dm:
            date_txt = data_date = '20' + dm.group(1) + '.' + dm.group(2)
        else:
            ym = re.search(r'\b(20\d\d)\b', fval)
            if ym:
                date_txt = ym.group(1)
                data_date = ym.group(1) + '.99'   # month unknown: sorts last in its year
    quick = '<div class="card-links">' + ''.join(quick_links) + '</div>' if quick_links else ''
    if not data_date:
        date_txt, data_date = CFG['default_date']
    search_src = strip_md(title_raw) + ' ' + ' '.join(
        strip_md(n + ' ' + v) for n, v in children)
    body = ''
    lead_figures = []
    content_fields = []
    for fname, fval in children:
        if fname in CFG['link_fields']:
            continue   # already carried by head button + badges
        if fname in CFG['figure_fields']:
            lead_figures.append(render_figure(fval))
            continue
        content_fields.append((fname, fval))

    if CFG.get('field_groups'):
        source_to_group = {
            source_name: group_name
            for group_name, source_names in CFG['field_groups'].items()
            for source_name in (group_name, *source_names)
        }
        grouped = {group_name: [] for group_name in CFG['field_groups']}
        for fname, fval in content_fields:
            group_name = source_to_group.get(fname)
            if group_name is None:
                BUILD_ERRORS.append('ungrouped card field: ' + fname + ' in ' + strip_md(title))
                continue
            grouped[group_name].append((fname, fval))
        for group_name, entries in grouped.items():
            if not entries:
                BUILD_ERRORS.append('empty card field group: ' + group_name + ' in ' + strip_md(title))
                continue
            limit = CFG.get('group_item_limits', {}).get(group_name)
            visible_entries = entries[:limit] if limit else entries
            for fname, fval in entries[len(visible_entries):]:
                OMITTED_SOURCE_LINES.add(fname + ': ' + fval)
            cls, label = field_style(group_name)
            if group_name in CFG.get('point_group_fields', ()):
                content = '<ul class="detail-points">' + ''.join(
                    '<li><strong>' + html.escape(fname) + ':</strong> ' + inline(fval) + '</li>'
                    for fname, fval in visible_entries) + '</ul>'
            else:
                content = '<div class="grouped-copy">' + ''.join(
                    '<p><strong>' + html.escape(fname) + ':</strong> ' + inline(fval) + '</p>'
                    for fname, fval in visible_entries) + '</div>'
            body += ('<div class="field"><span class="flabel ' + cls + '">' +
                     html.escape(label) + '</span><div class="fval">' + content + '</div></div>')
    else:
        for fname, fval in content_fields:
            cls, label = field_style(fname)
            content = render_steps(fval) if fname == CFG['steps_field'] else None
            if content is None:
                content = '<p>' + inline(fval) + '</p>'
            body += ('<div class="field"><span class="flabel ' + cls + '">' +
                     html.escape(label) + '</span><div class="fval">' + content + '</div></div>')
    if len(lead_figures) > 1:
        BUILD_ERRORS.append('more than one main figure in card: ' + strip_md(title))
    lead_figure = ('<div class="card-main-figure">' + lead_figures[0] + '</div>') if lead_figures else ''
    return ('<article class="card fam-' + fam + ' reveal" data-fam="' + fam +
            '" data-date="' + html.escape(str(data_date), quote=True) +
            '" data-search="' + html.escape(search_src, quote=True) + '">' +
            '<div class="card-head"><button class="card-toggle" type="button" aria-expanded="true" '
            'aria-controls="' + body_id + '"><span class="card-tag">' + html.escape(tag) + '</span>' +
            '<div class="card-titlewrap"><h4 class="card-title">' + inline(title) + '</h4>' +
            ('<span class="card-note">' + inline(note_txt) + '</span>' if note_txt else '') +
            '</div>' +
            ''.join('<span class="card-venue">' + html.escape(venue) + '</span>' for venue in venue_texts) +
            ('<span class="card-date">' + html.escape(str(date_txt)) + '</span>' if date_txt else '') +
            '<span class="card-chev" aria-hidden="true">›</span></button>' + quick + '</div>' +
            '<div class="card-body" id="' + body_id + '">' + lead_figure + body + '</div></article>')

def parse_list_items(buf):
    items = []
    for l in buf:
        m = re.match(r'^(\s*)(- |\d+\. )(.*)$', l)
        items.append((len(m.group(1)), m.group(2).strip(), m.group(3)))
    # tree: list of [text, ordered, children[]]
    root, stack = [], []
    for indent, marker, text in items:
        node = [text, marker.endswith('.'), []]
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if stack:
            stack[-1][1][2].append(node)
        else:
            root.append(node)
        stack.append((indent, node))
    return root

def render_generic_list(nodes, ordered):
    tag = 'ol' if ordered else 'ul'
    out = '<' + tag + ' class="plain">'
    for text, node_ordered, kids in nodes:
        out += '<li>' + inline(text)
        if kids:
            out += render_generic_list(kids, kids[0][1])
        out += '</li>'
    return out + '</' + tag + '>'

def is_card_node(t, kids):
    """paper card = bold-only title (+ optional note) + named field children"""
    if not re.match(r'^\*\*[^*]+\*\*\s*(（[^）]*）)?\s*$', t):
        return False
    fnames = set()
    for ktext, _, _ in kids:
        fm = re.match(r'^([^:：]+)[:：]', ktext)
        if fm:
            fnames.add(fm.group(1).strip())
    return bool(fnames & CFG['card_marker_fields'])

def render_list(buf, fam):
    nodes = parse_list_items(buf)
    card_flags = [is_card_node(t, kids) for t, _, kids in nodes]
    is_cards = bool(nodes) and all(card_flags)
    if fam and any(card_flags) and not all(card_flags):
        BUILD_ERRORS.append('mixed card and plain-list items inside family ' + fam.upper())
    if is_cards:
        out = ''
        for text, _, kids in nodes:
            fields = []
            for ktext, _, _ in kids:
                fm = re.match(r'^([^:：]+)[:：]\s*(.*)$', ktext, re.S)
                if fm:
                    fields.append((fm.group(1).strip(), fm.group(2).strip()))
                else:
                    fields.append(('附注', ktext.strip()))
            out += render_card(text, fields, fam or 'x')
        return out
    ordered = nodes[0][1]
    return render_generic_list(nodes, ordered)

SPECTRUM_HTML = ''
if CFG['spectrum']:
    sp = CFG['spectrum']
    SPECTRUM_HTML = (
        '<div class="spectrum reveal"><div class="spec-inner">'
        '<div class="spec-track">'
        + ''.join('<div class="spec-node">' + inline(str(s)) + '</div>' for s in sp['nodes']) +
        '</div>'
        '<div class="spec-bar"><b>' + inline(str(sp['bar'][0])) + '</b><div class="spec-grad"></div><b>' +
        inline(str(sp['bar'][1])) + '</b></div>'
        '<div class="spec-labels"><span>' + inline(str(sp['labels'][0])) + '</span>'
        '<span>' + inline(str(sp['labels'][1])) + '</span></div>'
        '</div></div>')

def render_table(buf):
    rows = []
    for l in buf:
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        rows.append(cells)
    if len(rows) >= 2 and all(set(c) <= set('-: ') for c in rows[1]):
        header, body = rows[0], rows[2:]
    else:
        header, body = None, rows
    out = '<div class="twrap reveal"><table>'
    if header:
        out += '<thead><tr>' + ''.join('<th>' + inline(c) + '</th>' for c in header) + '</tr></thead>'
    out += '<tbody>'
    for r in body:
        out += '<tr>' + ''.join('<td>' + inline(c) + '</td>' for c in r) + '</tr>'
    return out + '</tbody></table></div>'

# ---------------- evolution timeline (auto from card dates) ----------------
def scan_card_meta(cols, year_base):
    meta, fam_scan, cur, in_sec = [], None, None, False
    for l in MD.split('\n'):
        m2 = re.match(r'^##\s+([A-Za-z0-9-]+)[.．、]\s*', l)
        if m2:
            in_sec, fam_scan, cur = (m2.group(1) == CFG['card_section']), None, None
            continue
        if l.startswith('## '):
            in_sec, fam_scan, cur = False, None, None
            continue
        if not in_sec:
            continue
        m3 = re.match(r'^### ' + CFG['fam_heading'].lstrip('^'), l)
        if m3:
            fam_scan, cur = m3.group(1).lower(), None
            continue
        m4 = re.match(r'^- \*\*([^*]+)\*\*', l)
        if m4 and fam_scan:
            cur = m4.group(1).strip()
            continue
        if cur and re.match(r'^\s+- (?:' + '|'.join(re.escape(x) for x in CFG['link_fields']) + r'):', l):
            dm = re.search(r'abs/(\d{2})(\d{2})\.\d+', l)
            if dm:
                col = (int(dm.group(1)) - year_base) * 4 + (int(dm.group(2)) - 1) // 3
                if 0 <= col < len(cols):
                    meta.append((fam_scan, col, cur.split(':')[0].strip(), cur))
                cur = None
    return meta

def build_timeline():
    tl = CFG['timeline']
    if not tl:
        return ''
    cols = tl['cols']
    grid = {}
    for fam_l, col, short, full in scan_card_meta(cols, tl['year_base']):
        grid.setdefault((fam_l, col), []).append((short, full))
    rows = [(k, FAMS[k][0], k.upper()) for k in FAMS]
    for er in tl.get('extra_rows', []):
        for col, short, full in er['items']:
            grid.setdefault((er['key'], col), []).append((short, full))
        rows.append((er['key'], er['color'], er['label']))
    out = ('<div class="tl-wrap reveal"><div class="tl" style="grid-template-columns:' +
           '34px repeat(' + str(len(cols)) + ',minmax(78px,1fr))">' +
           '<div class="tl-h tl-corner">族</div>' +
           ''.join('<div class="tl-h">' + html.escape(str(c)) + '</div>' for c in cols))
    for fam_l, color, label in rows:
        out += ('<div class="tl-fam"><i style="background:' + html.escape(color, quote=True) + '"></i>' +
                html.escape(str(label)) + '</div>')
        for ci in range(len(cols)):
            chips = grid.get((fam_l, ci), [])
            out += ('<div class="tl-cell">' + ''.join(
                '<span class="tl-chip" style="--c:' + html.escape(color, quote=True) + '" title="' +
                html.escape(full, quote=True) + '">' + html.escape(short) +
                '</span>' for short, full in chips) + '</div>')
    note = tl.get('note')
    out += '</div>' + ('<div class="tl-note">' + inline(str(note)) + '</div>' if note else '') + '</div>'
    return out

TIMELINE = build_timeline()
blocks = parse_blocks(MD)
body_parts, toc_entries = [], []
sec = None; fam = None; skip_toc = False; fam_open = False; fam_intro = []
tl_done = False
toolbar_html = ''
hero_title, hero_quote = '', []

def flush_fam_intro():
    global fam_intro
    if fam_intro:
        body_parts.append('<div class="fam-intro">' + ''.join(fam_intro) + '</div>')
        fam_intro = []

def close_fam():
    global fam_open
    flush_fam_intro()
    if fam_open:
        body_parts.append('</div>'); fam_open = False

for bi, blk in enumerate(blocks):
    kind = blk[0]
    if kind == 'h' and blk[1] == 1:
        hero_title = blk[2]; continue
    if kind == 'h' and blk[1] == 2 and blk[2] == CFG['toc_title']:
        skip_toc = True; continue
    if kind == 'h' and blk[1] == 2:
        skip_toc = False
    if skip_toc:
        continue  # TOC section is carried verbatim by the sidebar
    if kind == 'h':
        lvl, text = blk[1], blk[2]
        if lvl == 2:
            close_fam()
            sec_match = re.match(r'^([A-Za-z0-9-]+)[.．、]\s*', text)
            sec = sec_match.group(1) if sec_match else 'section-' + str(len(toc_entries) + 1)
            fam = None
            toc_entries.append(('sec-' + sec, text, False))
            card_attr = ' data-card-section="true"' if sec == str(CFG['card_section']) else ''
            body_parts.append('</section><section id="sec-' + sec + '"' + card_attr + '>')
            body_parts.append('<div class="sec-head"><div class="sec-eyebrow">§ ' + html.escape(sec) +
                              '</div><h2>' + inline(text) + '</h2></div>')
            if sec == CFG['card_section']:
                chips = '<button class="chip on" type="button" data-fam="all">全部</button>'
                for k, (color, name) in FAMS.items():
                    safe_color = html.escape(color, quote=True)
                    chips += ('<button class="chip" type="button" data-fam="' + k + '" data-color="' + safe_color +
                              '"><i style="background:' + safe_color + '"></i>' + html.escape(str(name)) + '</button>')
                toolbar_html = (
                    '<div class="toolbar" aria-label="论文卡片工具栏">' +
                    '<div class="toolbar-row">' +
                    '<div class="search"><svg width="14" height="14" viewBox="0 0 24 24" fill="none" '
                    'stroke="currentColor" stroke-width="2.4" stroke-linecap="round">'
                    '<circle cx="11" cy="11" r="7"/><path d="M20 20l-3.8-3.8"/></svg>'
                    '<input id="card-search" type="search" aria-label="搜索论文卡片" placeholder="' + html.escape(CFG['search_placeholder'], quote=True) + '"></div>' +
                    '<span class="count" role="status" aria-live="polite"></span>' +
                    '<button class="btn" type="button" data-act="sort-date">' + html.escape(CFG['sort_button']) + '</button>' +
                    '<button class="btn" type="button" data-act="toggle-all">' + html.escape(CFG['collapse_button']) + '</button>' +
                    '</div>' +
                    '<div class="toolbar-row fam-row">' + chips + '</div></div>')
            continue
        if lvl == 3:
            fm = re.match(CFG['fam_heading'], text) if sec == CFG['card_section'] else None
            if fm and fm.group(1).lower() in FAMS:
                close_fam()
                if not tl_done and (TIMELINE or toolbar_html):
                    body_parts.append(TIMELINE + toolbar_html); tl_done = True
                fam = fm.group(1).lower()
                toc_entries.append(('fam-' + fam, text, True))
                body_parts.append('<div class="fam-group" data-famgroup="' + fam + '">')
                fam_open = True
                body_parts.append('<h3 class="fam-h-' + fam + '" id="fam-' + fam +
                                  '"><span class="h3bar"></span>' + inline(text) + '</h3>')
            else:
                fam = None
                body_parts.append('<h3><span class="h3bar"></span>' + inline(text) + '</h3>')
            continue
        body_parts.append('<h4>' + inline(text) + '</h4>'); continue
    if kind == 'quote':
        if not hero_quote and sec is None:
            hero_quote = blk[1]; continue
        inner = ''.join('<p>' + inline(l) + '</p>' for l in blk[1] if l)
        html_block = '<div class="callout reveal">' + inner + '</div>'
    elif kind == 'code':
        if CFG['spectrum'] and blk[1].lstrip().startswith(CFG['spectrum']['detect']):
            html_block = SPECTRUM_HTML   # ASCII diagram -> graphical rendering
        else:
            html_block = '<pre class="reveal">' + html.escape(blk[1]) + '</pre>'
    elif kind == 'table':
        html_block = render_table(blk[1])
    elif kind == 'list':
        html_block = render_list(blk[1], fam)
    else:
        html_block = ''.join('<p>' + inline(l) + '</p>' for l in blk[1])
    if fam_open and '<article class="card' not in html_block:
        fam_intro.append(html_block)
    else:
        flush_fam_intro()
        body_parts.append(html_block)
close_fam()
body_html = ''.join(body_parts).replace('</section>', '', 1) + '</section>'
if 'data-card-section="true"' not in body_html:
    BUILD_ERRORS.append('card section ' + CFG['card_section'] + ' was not found')

# counts for hero stats
n_cards = len(re.findall(r'class="card fam-' + FAM_CLASS + r' reveal"', body_html))
n_fams = len(FAMS)
stats_html = ''.join('<div class="stat"><b>' + html.escape(str(n).format(n_cards=n_cards, n_fams=n_fams)) +
                     '</b><span>' + html.escape(str(s)) + '</span></div>' for n, s in CFG['hero_stats'])

# ---------------- nav / toc / hero ----------------
toc_html = '<div class="toc-title">' + html.escape(CFG['toc_title']) + '</div>'
for i, t, sub in toc_entries:
    toc_html += ('<a href="#' + i + '"' + (' class="toc-sub"' if sub else '') +
                 '>' + inline(t) + '</a>')
hero_chips = ''.join('<a href="#' + i + '">' + inline(t) + '</a>'
                     for i, t, sub in toc_entries if not sub)
quote_html = ''.join('<p>' + inline(l) + '</p>' for l in hero_quote if l)

HTML_DOC = ('<!DOCTYPE html>\n<html lang="' + html.escape(CFG['lang'], quote=True) + '">\n<head>\n<meta charset="UTF-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1.0">\n'
    '<title>' + html.escape(hero_title) + '</title>\n'
    '<meta name="description" content="' + html.escape(CFG['meta_desc'], quote=True) + '">\n'
    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">\n'
    '<style>' + CSS + '</style>\n'
    '<noscript><style>.reveal{opacity:1 !important;transform:none !important}</style></noscript>\n</head>\n<body>\n'
    '<nav class="nav"><div class="nav-inner">'
    '<a class="nav-brand" href="#top"><span class="nav-dot"></span><span class="t">' + html.escape(CFG['brand']) + '</span></a>'
    '<button class="theme-toggle" type="button" data-theme-toggle aria-label="切换明暗主题" title="切换明暗主题">◐</button>'
    '</div><div class="progress"></div></nav>\n'
    '<header class="hero" id="top"><span class="eyebrow">' + html.escape(CFG['eyebrow']) + '</span>'
    '<h1>' + inline(hero_title) + '</h1>'
    '<div class="stats">' + stats_html + '</div>'
    '<div class="callout" style="text-align:left;max-width:840px;margin:26px auto 0">' + quote_html + '</div>'
    '<div class="hero-chips">' + hero_chips + '</div></header>\n'
    '<div class="layout"><aside class="toc">' + toc_html + '</aside>\n'
    '<main>' + body_html + '</main></div>\n'
    '<button class="to-top" type="button" aria-label="回到顶部">↑</button>\n'
    '<footer>' + html.escape(CFG['footer']) + '</footer>\n'
    '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>\n'
    '<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>\n'
    '<script type="application/json" id="rvr-config">' + RUNTIME_CONFIG + '</script>\n'
    '<script>' + JS + '</script>\n</body>\n</html>')

# ---------------- verification: no md content lost ----------------
def norm(s):
    """canonical form for presence-checking: the renderer consumes some separator
    chars (field-label colons, (n) step markers, step-separator semicolons), so
    remove that class of chars from BOTH sides, along with all whitespace."""
    s = strip_md(s)
    s = re.sub(r'\((\d+)\)', r'\1', s)
    return re.sub(r'[\s;；:：]+', '', s)

text = re.sub(r'<script.*?</script>|<style.*?</style>', ' ', HTML_DOC, flags=re.S)
hrefs = html.unescape(' '.join(re.findall(r'href="([^"]+)"', text)))
image_sources = html.unescape(' '.join(re.findall(r'data-source="([^"]+)"', text)))
image_alts = html.unescape(' '.join(re.findall(r'<img\b[^>]*\balt="([^"]*)"', text)))
text = re.sub(r'<[^>]+>', '', text)   # strip tags without inserting spaces
text = html.unescape(text)
corpus = norm(text) + ' ' + norm(image_alts) + ' ' + hrefs
omitted_source_lines = {norm(line) for line in OMITTED_SOURCE_LINES}

missing, in_code = [], False
spec_lines = CFG['spectrum']['detect_lines'] if CFG['spectrum'] else ()
link_re = r'^\s*- (?:' + '|'.join(re.escape(x) for x in CFG['link_fields']) + r'):\s*https?://'
for raw in MD.split('\n'):
    l = raw.rstrip()
    if l.startswith('```'):
        in_code = not in_code; continue
    if not l.strip() or re.match(r'^---\s*$', l):
        continue
    if in_code:
        if norm(l):
            if spec_lines and l.lstrip().startswith(spec_lines):
                # spectrum diagram rendered graphically: check element-wise
                for piece in re.split(r'[─▶]+|\s+', l):
                    if piece and norm(piece) not in corpus:
                        missing.append('SPEC: ' + piece[:40])
            elif norm(l) not in corpus:
                missing.append('CODE: ' + l[:70])
        continue
    if l.startswith('|'):
        cells = [c.strip() for c in l.strip().strip('|').split('|')]
        if all(set(c) <= set('-: ') for c in cells):
            continue
        for c in cells:
            if c and norm(c) not in corpus:
                missing.append('CELL: ' + c[:70])
        continue
    if re.match(link_re, l):
        # card link field: ID goes into head-button href, （…）note into venue badge
        idm = re.search(r'(?:abs/|id=)([\w.-]+)', l)
        if idm and idm.group(1) not in hrefs:
            missing.append('LINK: ' + idm.group(1))
        vm = re.search(r'（([^）]+)）', l)
        if vm and norm(vm.group(1)) not in corpus:
            missing.append('VENUE: ' + vm.group(1)[:40])
        continue
    image_match = IMAGE_RE.search(re.sub(r'^\s*-\s*[^:：]+[:：]\s*', '', l))
    if image_match:
        alt, source, title, trailing = image_match.groups()
        for piece in (alt, title or trailing):
            if piece and norm(piece) not in corpus:
                missing.append('FIGURE TEXT: ' + piece[:70])
        if source not in image_sources:
            missing.append('FIGURE SOURCE: ' + source[:70])
        continue
    for url in re.findall(r'\]\((https?://[^)]+)\)', l):
        if url not in hrefs:
            missing.append('URL: ' + url[:70])
    l2 = re.sub(r'^\s*(#{1,4}\s+|>\s*|- |\d+\. )', '', l)
    l2 = re.sub(r'^\s*-\s+', '', l2)
    if norm(l2) in omitted_source_lines:
        continue
    if l2.strip() and norm(l2) not in corpus:
        missing.append('LINE: ' + l2[:70])

print('cards:', n_cards, '| toc entries:', len(toc_entries))
print('missing:', len(missing))
if omitted_source_lines:
    print('condensed source lines:', len(omitted_source_lines))
if CFG['timeline']:
    assert '<div class="tl-wrap' in HTML_DOC, 'timeline not injected'
# default card order within each family must be date-ascending
dates = {}
for dm in re.finditer(r'data-famgroup="(' + FAM_CLASS + r')"|class="card fam-(' + FAM_CLASS +
                      r') reveal"[^>]*data-date="([^"]*)"', body_html):
    if dm.group(2):
        dates.setdefault(dm.group(2), []).append(dm.group(3))
bad_order = [k for k, v in dates.items() if v != sorted(v)]
print('date order ok:', not bad_order, ('BAD: ' + ','.join(bad_order)) if bad_order else '')
for m_ in missing[:25]:
    print(' ', m_)
for error in BUILD_ERRORS:
    print(' ', 'STRUCTURE:', error)
if missing or bad_order or BUILD_ERRORS:
    print('build failed: source report was not overwritten')
    sys.exit(2)

os.makedirs(os.path.dirname(os.path.abspath(OUT)), exist_ok=True)
tmp_out = OUT + '.tmp'
with open(tmp_out, 'w', encoding='utf-8') as out_file:
    out_file.write(HTML_DOC)
os.replace(tmp_out, OUT)
print('output:', OUT, '| bytes:', os.path.getsize(OUT))
