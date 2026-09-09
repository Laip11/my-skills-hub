#!/usr/bin/env python3
"""Offline tests for identifier, license, and figure extraction behavior."""
import importlib.util
from pathlib import Path


MODULE_PATH = Path(__file__).with_name('harvest_arxiv.py')
SPEC = importlib.util.spec_from_file_location('harvest_arxiv', MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


SAMPLE_HTML = """
<html><body>
<a title="License information" href="/licenses/by/4.0/">License</a>
<figure id="S1.F1">
  <img src="figure1.png" alt="Architecture overview">
  <figcaption><span>Figure 1:</span> Architecture <b>overview</b>.</figcaption>
</figure>
<figure id="S2.F2">
  <img src="panel-a.svg" alt="Panel A"><img src="panel-b.svg" alt="Panel B">
  <figcaption>Figure 2: Ablation results.</figcaption>
</figure>
</body></html>
"""


def main():
    assert MODULE.normalize_id('2401.12345') == '2401.12345'
    assert MODULE.normalize_id('https://arxiv.org/pdf/2401.12345v2.pdf') == '2401.12345v2'
    assert MODULE.normalize_id('https://www.alphaxiv.org/abs/2401.12345') == '2401.12345'

    license_parser = MODULE.LicenseParser('https://arxiv.org/abs/2401.12345')
    license_parser.feed(SAMPLE_HTML)
    assert license_parser.license_url == 'https://arxiv.org/licenses/by/4.0/'

    figure_parser = MODULE.FigureParser('https://arxiv.org/html/2401.12345/')
    figure_parser.feed(SAMPLE_HTML)
    assert len(figure_parser.figures) == 2
    assert 'Figure 1' in figure_parser.figures[0]['caption']
    assert 'Architecture overview.' in figure_parser.figures[0]['caption']
    assert len(figure_parser.figures[1]['images']) == 2
    assert figure_parser.figures[1]['images'][1]['source_url'].endswith('/panel-b.svg')

    assert MODULE.selection('1,2', 2) == {1, 2}
    assert MODULE.selection('all', 2) == {1, 2}
    print('self-test: ok')


if __name__ == '__main__':
    main()
