#!/usr/bin/env python3
"""Collect official arXiv metadata, HTML figure manifests, and selected images."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlparse
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET
from datetime import datetime, timezone


USER_AGENT = 'paper-evidence-research/1.0 (research workflow)'
ARXIV_ID_RE = re.compile(r'^(?:[a-z-]+(?:\.[A-Z]{2})?/\d{7}|\d{4}\.\d{4,5})(?:v\d+)?$', re.I)
ATOM = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
IMAGE_TYPES = {
    'image/png': '.png', 'image/jpeg': '.jpg', 'image/webp': '.webp',
    'image/gif': '.gif', 'image/svg+xml': '.svg',
}


def normalize_id(value):
    value = value.strip()
    if '://' in value:
        path = urlparse(value).path
        value = re.sub(r'^/(?:abs|pdf|html)/', '', path).removesuffix('.pdf').strip('/')
    if not ARXIV_ID_RE.fullmatch(value):
        raise ValueError('expected an arXiv ID or arXiv/alphaXiv paper URL')
    return value


def fetch(url, timeout, max_bytes=25_000_000):
    host = (urlparse(url).hostname or '').lower()
    if host != 'arxiv.org' and not host.endswith('.arxiv.org'):
        raise ValueError('refusing to fetch a non-arXiv host: ' + host)
    request = Request(url, headers={'User-Agent': USER_AGENT, 'Accept': '*/*'})
    with urlopen(request, timeout=timeout) as response:
        data = response.read(max_bytes + 1)
        if len(data) > max_bytes:
            raise ValueError('response exceeds size limit: ' + url)
        return data, response.headers.get_content_type()


def text_of(entry, path):
    node = entry.find(path, ATOM)
    return ' '.join((node.text or '').split()) if node is not None else ''


def fetch_metadata(arxiv_id, timeout):
    url = 'https://export.arxiv.org/api/query?id_list=' + quote(arxiv_id, safe='/')
    payload, _ = fetch(url, timeout)
    root = ET.fromstring(payload)
    entry = root.find('atom:entry', ATOM)
    if entry is None:
        raise ValueError('arXiv API returned no paper for ' + arxiv_id)
    canonical = text_of(entry, 'atom:id').replace('http://', 'https://')
    authors = [text_of(author, 'atom:name') for author in entry.findall('atom:author', ATOM)]
    links = {node.get('rel', ''): node.get('href', '') for node in entry.findall('atom:link', ATOM)}
    return {
        'arxiv_id': canonical.rsplit('/', 1)[-1],
        'title': text_of(entry, 'atom:title'),
        'authors': authors,
        'abstract': text_of(entry, 'atom:summary'),
        'published': text_of(entry, 'atom:published'),
        'updated': text_of(entry, 'atom:updated'),
        'comment': text_of(entry, 'arxiv:comment'),
        'journal_ref': text_of(entry, 'arxiv:journal_ref'),
        'doi': text_of(entry, 'arxiv:doi'),
        'abs_url': canonical,
        'pdf_url': links.get('related') or 'https://arxiv.org/pdf/' + arxiv_id,
        'api_url': url,
    }


class LicenseParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.license_url = ''

    def handle_starttag(self, tag, attrs):
        if tag != 'a' or self.license_url:
            return
        values = dict(attrs)
        href = values.get('href', '')
        title = values.get('title', '').lower()
        rel = values.get('rel', '')
        if 'license' in title or 'license' in rel or '/licenses/' in href:
            self.license_url = urljoin(self.base_url, href)


class FigureParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.current = None
        self.caption_depth = 0
        self.figures = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'figure' and self.current is None:
            self.current = {'id': values.get('id', ''), 'caption': '', 'images': []}
        elif self.current is not None and tag == 'figcaption':
            self.caption_depth = 1
        elif self.current is not None and self.caption_depth:
            self.caption_depth += 1
        if self.current is not None and tag == 'img':
            src = values.get('src') or values.get('data-src')
            if src:
                self.current['images'].append({
                    'source_url': urljoin(self.base_url, src),
                    'alt': ' '.join(values.get('alt', '').split()),
                })

    def handle_endtag(self, tag):
        if self.current is None:
            return
        if tag == 'figcaption' and self.caption_depth == 1:
            self.caption_depth = 0
        elif self.caption_depth:
            self.caption_depth -= 1
        if tag == 'figure':
            caption = ' '.join(self.current['caption'].split())
            self.current['caption'] = re.sub(r'\s+([,.;:!?])', r'\1', caption)
            if self.current['images']:
                self.figures.append(self.current)
            self.current = None
            self.caption_depth = 0

    def handle_data(self, data):
        if self.current is not None and self.caption_depth:
            self.current['caption'] += ' ' + data


def fetch_html_evidence(arxiv_id, timeout):
    html_url = 'https://arxiv.org/html/' + arxiv_id
    payload, _ = fetch(html_url, timeout)
    text = payload.decode('utf-8', errors='replace')
    figures = FigureParser(html_url)
    figures.feed(text)
    return html_url, figures.figures


def fetch_license(abs_url, timeout):
    try:
        payload, _ = fetch(abs_url, timeout, max_bytes=3_000_000)
    except (HTTPError, URLError, ValueError):
        return ''
    parser = LicenseParser(abs_url)
    parser.feed(payload.decode('utf-8', errors='replace'))
    return parser.license_url


def selection(value, total):
    if not value:
        return set()
    if value.lower() == 'all':
        return set(range(1, total + 1))
    chosen = set()
    for token in value.split(','):
        number = int(token.strip())
        if number < 1 or number > total:
            raise ValueError('figure index outside available range: ' + str(number))
        chosen.add(number)
    return chosen


def extension(url, content_type):
    suffix = Path(urlparse(url).path).suffix.lower()
    if suffix in {'.png', '.jpg', '.jpeg', '.webp', '.gif', '.svg'}:
        return '.jpg' if suffix == '.jpeg' else suffix
    return IMAGE_TYPES.get(content_type, '.bin')


def download_selected(figures, chosen, output, timeout):
    figure_dir = output / 'figures'
    if chosen:
        figure_dir.mkdir(parents=True, exist_ok=True)
    for figure_index, figure in enumerate(figures, 1):
        figure['index'] = figure_index
        for image_index, image in enumerate(figure['images'], 1):
            image.setdefault('local_path', '')
            if figure_index not in chosen:
                continue
            payload, content_type = fetch(image['source_url'], timeout)
            if not content_type.startswith('image/'):
                raise ValueError('figure response is not an image: ' + image['source_url'])
            name = 'figure-{0:03d}-{1:02d}{2}'.format(
                figure_index, image_index, extension(image['source_url'], content_type))
            target = figure_dir / name
            part = target.with_suffix(target.suffix + '.part')
            part.write_bytes(payload)
            part.replace(target)
            image['local_path'] = 'figures/' + name
            image['content_type'] = content_type
            image['bytes'] = len(payload)
            image['sha256'] = hashlib.sha256(payload).hexdigest()


def write_outputs(output, metadata, html_url, figures, license_url):
    manifest = {
        'retrieved_at': datetime.now(timezone.utc).isoformat(),
        'metadata': metadata,
        'license_url': license_url,
        'html_url': html_url,
        'figures': figures,
        'notice': 'Check the paper version and license before redistributing figures.',
    }
    output.mkdir(parents=True, exist_ok=True)
    manifest_path = output / 'manifest.json'
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    lines = [
        '# ' + metadata['title'], '',
        '- arXiv: ' + metadata['abs_url'],
        '- Version resolved: ' + metadata['arxiv_id'],
        '- Published: ' + metadata['published'],
        '- Updated: ' + metadata['updated'],
        '- License: ' + (license_url or 'not detected; inspect the paper page'),
        '- HTML source: ' + (html_url or 'unavailable; use PDF fallback'), '',
        '## Abstract', '', metadata['abstract'], '',
        '## Figure inventory', '',
    ]
    if not figures:
        lines.append('No HTML figures were detected. Use the PDF fallback workflow.')
    for figure in figures:
        caption = figure['caption'] or 'No caption detected'
        lines.extend(['### Figure ' + str(figure['index']), '', caption, ''])
        for image in figure['images']:
            if image.get('local_path'):
                alt = image['alt'] or 'Figure ' + str(figure['index'])
                lines.append('![' + alt.replace(']', '') + '](' + image['local_path'] + ')')
            lines.append('- Source image: ' + image['source_url'])
        lines.append('')
    (output / 'evidence.md').write_text('\n'.join(lines).rstrip() + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('paper', help='arXiv ID or arXiv/alphaXiv paper URL')
    parser.add_argument('--out', required=True, help='output evidence directory')
    parser.add_argument('--figures', default='', help='one-based indexes such as 1,3 or all')
    parser.add_argument('--timeout', type=int, default=30)
    parser.add_argument('--refresh', action='store_true', help='ignore a cached manifest and re-fetch arXiv')
    args = parser.parse_args()
    try:
        arxiv_id = normalize_id(args.paper)
        output = Path(args.out).resolve()
        manifest_path = output / 'manifest.json'
        cached = None
        if manifest_path.is_file() and not args.refresh:
            cached = json.loads(manifest_path.read_text(encoding='utf-8'))
            cached_id = cached.get('metadata', {}).get('arxiv_id', '')
            same_paper = re.sub(r'v\d+$', '', cached_id) == re.sub(r'v\d+$', '', arxiv_id)
            requested_version = bool(re.search(r'v\d+$', arxiv_id))
            if not same_paper or (requested_version and cached_id != arxiv_id):
                cached = None
        if cached:
            metadata = cached['metadata']
            license_url = cached.get('license_url', '')
            html_url = cached.get('html_url', '')
            figures = cached.get('figures', [])
        else:
            metadata = fetch_metadata(arxiv_id, args.timeout)
            license_url = fetch_license(metadata['abs_url'], args.timeout)
            try:
                html_url, figures = fetch_html_evidence(arxiv_id, args.timeout)
            except HTTPError as error:
                if error.code not in {404, 406}:
                    raise
                html_url, figures = '', []
        chosen = selection(args.figures, len(figures))
        download_selected(figures, chosen, output, args.timeout)
        write_outputs(output, metadata, html_url, figures, license_url)
    except (ValueError, HTTPError, URLError, ET.ParseError, OSError) as error:
        print('error:', error, file=sys.stderr)
        return 2
    print('paper:', metadata['arxiv_id'])
    print('figures:', len(figures), '| downloaded:', len(chosen))
    print('output:', output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
