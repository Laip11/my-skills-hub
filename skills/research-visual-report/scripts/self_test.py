#!/usr/bin/env python3
"""Smoke-test the packaged builder with no third-party dependencies."""
from pathlib import Path
import base64
import subprocess
import sys
import tempfile


BUILDER = Path(__file__).with_name('build.py')

CONFIG = """CONFIG = {
    'card_section': '4',
    'fams': {'a': ('#0071E3', '过程级')},
    'default_date': ('未注明', '2026.99'),
    'field_style': {
        '核心问题/背景': ('f-q', '核心问题 / 背景'),
        '具体方法': ('f-m', '具体方法'),
        '实验设置和结果': ('f-r', '实验设置和结果'),
    },
    'field_groups': {
        '核心问题/背景': ('核心问题', '背景'),
        '具体方法': ('方法',),
        '实验设置和结果': ('实验结果', '补充证据'),
    },
    'point_group_fields': ('具体方法',),
    'group_item_limits': {'实验设置和结果': 1},
}
"""

CARD_1 = """- **First paper**
  - OpenReview: https://openreview.net/forum?id=first（Venue A）
  - arXiv: https://arxiv.org/abs/2401.00001（2024）
  - 核心问题: First question
  - 背景: First background
  - 方法: First method
  - 实验结果: First result
  - 补充证据: Hidden detail
  - 图示: ![Method overview](figure.png "Original Figure 1 caption")
"""

CARD_2 = """- **Second paper**
  - arXiv: https://arxiv.org/abs/2502.00002（Venue B）
  - 核心问题: Second question
  - 背景: Second background
  - 方法: Second method
  - 实验结果: Second result
  - 补充证据: Another hidden detail
"""


def document(cards):
    return "# Test report\n> Test introduction\n\n## 4. Methods\n### A. Process methods\n" + cards


def run_build(folder):
    return subprocess.run(
        [sys.executable, str(BUILDER), 'report.md', 'config.py'],
        cwd=folder,
        text=True,
        capture_output=True,
        check=False,
    )


def main():
    with tempfile.TemporaryDirectory(prefix='rvr-self-test-') as temp:
        folder = Path(temp)
        (folder / 'config.py').write_text(CONFIG, encoding='utf-8')
        (folder / 'figure.png').write_bytes(base64.b64decode(
            'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII='
        ))
        (folder / 'report.md').write_text(document(CARD_1 + CARD_2), encoding='utf-8')

        passed = run_build(folder)
        assert passed.returncode == 0, passed.stdout + passed.stderr
        output = (folder / 'report.html').read_text(encoding='utf-8')
        assert 'data-card-section="true"' in output
        assert output.count('data-fam="a" data-color=') == 1
        assert 'www.alphaxiv.org/abs/2401.00001' in output
        assert 'openreview.net/forum?id=first' in output
        assert '<figure class="paper-figure">' in output
        assert '<div class="card-main-figure"><figure class="paper-figure">' in output
        assert output.index('card-main-figure') < output.index('First question')
        assert output.count('>核心问题 / 背景</span>') == 2
        assert output.count('>具体方法</span>') == 2
        assert output.count('>实验设置和结果</span>') == 2
        assert '<ul class="detail-points">' in output
        assert 'flabel f-q' in output and 'flabel f-m' in output and 'flabel f-r' in output
        assert '<strong>补充证据:</strong>' not in output
        assert 'data:image/png;base64,' in output
        assert 'data-source="figure.png"' in output

        before = output
        (folder / 'report.md').write_text(document(CARD_2 + CARD_1), encoding='utf-8')
        rejected = run_build(folder)
        assert rejected.returncode == 2, rejected.stdout + rejected.stderr
        assert (folder / 'report.html').read_text(encoding='utf-8') == before
        assert 'date order ok: False' in rejected.stdout

        duplicate_figure = CARD_1 + "  - 图示: ![Second figure](figure.png)\n"
        (folder / 'report.md').write_text(document(duplicate_figure + CARD_2), encoding='utf-8')
        rejected = run_build(folder)
        assert rejected.returncode == 2, rejected.stdout + rejected.stderr
        assert 'more than one main figure in card' in rejected.stdout

    print('self-test: ok')


if __name__ == '__main__':
    main()
