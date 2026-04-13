from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterable

PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from zti.demo.export import export_terminal_output

SITE_ROOT = PROJECT_ROOT / 'dev' / 'site'
SRC_ROOT = SITE_ROOT / '_src'
CONFIG_PATH = SRC_ROOT / 'config' / 'site.json'
TOKEN_PATTERN = re.compile(r'{{([A-Z0-9_]+)}}')

PAGE_PATHS = {
    'protocol': 'index.html',
    'adopt': 'adopt/index.html',
    'core': 'core/index.html',
    'adopt_demo': 'adopt/demo/index.html',
    'request_access': 'adopt/request-access/index.html',
    'request_success': 'adopt/request-access/success/index.html',
}


def _load_config() -> dict[str, object]:
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))


def _target_base_path(target: str) -> str:
    if target == 'dev':
        return '/dev/site'
    if target == 'prod':
        return ''
    raise ValueError(f'Unsupported target: {target}')


def _join(base: str, suffix: str) -> str:
    if not base:
        return suffix
    if suffix == '/':
        return f'{base}/'
    return f'{base}{suffix}'


def _route_map(base_path: str) -> dict[str, str]:
    return {
        'protocol': _join(base_path, '/'),
        'adopt': _join(base_path, '/adopt/'),
        'core': _join(base_path, '/core/'),
        'adopt_demo': _join(base_path, '/adopt/demo/'),
        'request_access': _join(base_path, '/adopt/request-access/'),
        'request_success': _join(base_path, '/adopt/request-access/success/'),
        'assets': _join(base_path, '/assets'),
    }


def _render_tokens(text: str, context: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key not in context:
            raise KeyError(f'Missing template token: {key}')
        return context[key]

    rendered = TOKEN_PATTERN.sub(replace, text)
    leftovers = TOKEN_PATTERN.findall(rendered)
    if leftovers:
        raise ValueError(f'Unrendered tokens remain: {leftovers}')
    return rendered


def _nav_items(config: dict[str, object], routes: dict[str, str]) -> str:
    items: list[str] = []
    show_core = bool(config.get('show_core_in_navigation', False))
    for item in config['navigation']:
        route_key = item['route_key']
        if route_key == 'core' and not show_core:
            continue
        items.append(
            f'    <li><a href="{routes[route_key]}" data-nav-key="{item["key"]}"><span class="sidebar-dot" aria-hidden="true">●</span><span>{item["label"]}</span></a></li>'
        )
    return '\n'.join(items)


def _context_for(target: str) -> dict[str, str]:
    config = _load_config()
    base_path = _target_base_path(target)
    routes = _route_map(base_path)
    sidebar_template = (SRC_ROOT / 'partials' / 'sidebar.html').read_text(encoding='utf-8')
    sidebar = _render_tokens(sidebar_template, {'NAV_ITEMS': _nav_items(config, routes)})
    return {
        'BASE_PATH': base_path,
        'GOOGLE_FONTS_URL': str(config['fonts_url']),
        'SIDEBAR': sidebar,
        'ASSETS_URL': routes['assets'],
        'PROTOCOL_URL': routes['protocol'],
        'ADOPT_URL': routes['adopt'],
        'CORE_URL': routes['core'],
        'ADOPT_DEMO_URL': routes['adopt_demo'],
        'REQUEST_ACCESS_URL': routes['request_access'],
        'REQUEST_SUCCESS_URL': routes['request_success'],
        'TRANSCRIPT_URL': f"{routes['assets']}/demo-output.txt",
    }


def _ensure_clean_output(output_dir: Path) -> None:
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)


def _copy_static(output_dir: Path) -> None:
    static_root = SRC_ROOT / 'static'
    for path in static_root.rglob('*'):
        if not path.is_file():
            continue
        destination = output_dir / path.relative_to(static_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(path.read_bytes())


def _render_assets(output_dir: Path, context: dict[str, str]) -> None:
    assets_root = SRC_ROOT / 'assets'
    out_assets = output_dir / 'assets'
    for path in assets_root.rglob('*'):
        if not path.is_file():
            continue
        destination = out_assets / path.relative_to(assets_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(_render_tokens(path.read_text(encoding='utf-8'), context), encoding='utf-8')


def _render_pages(output_dir: Path, context: dict[str, str]) -> None:
    pages_root = SRC_ROOT / 'pages'
    for path in pages_root.rglob('*.html'):
        destination = output_dir / path.relative_to(pages_root)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(_render_tokens(path.read_text(encoding='utf-8'), context), encoding='utf-8')


def _stage_transcript(output_dir: Path, project_root: Path) -> Path:
    transcript_source = export_terminal_output(project_root)
    destination = output_dir / 'assets' / 'demo-output.txt'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(transcript_source.read_text(encoding='utf-8'), encoding='utf-8')
    return destination


def build_site(target: str, output_dir: Path, project_root: Path | None = None) -> Path:
    project_root = project_root or PROJECT_ROOT
    output_dir = output_dir.resolve()
    context = _context_for(target)
    _ensure_clean_output(output_dir)
    _copy_static(output_dir)
    _render_assets(output_dir, context)
    _stage_transcript(output_dir, project_root)
    _render_pages(output_dir, context)
    return output_dir


def _digest_directory(directory: Path) -> dict[str, str]:
    digests: dict[str, str] = {}
    for path in sorted(p for p in directory.rglob('*') if p.is_file()):
        rel = path.relative_to(directory).as_posix()
        digests[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
    return digests


def _assert_prod_paths(prod_dir: Path) -> None:
    for path in prod_dir.rglob('*'):
        if not path.is_file() or path.suffix not in {'.html', '.css', '.js', '.txt'}:
            continue
        contents = path.read_text(encoding='utf-8')
        if '/dev/site/' in contents or '/dev/site<' in contents or '/dev/site"' in contents or '/dev/site\'' in contents:
            raise AssertionError(f'Prod output leaked /dev/site path in {path}')


def check_build(project_root: Path | None = None) -> None:
    project_root = project_root or PROJECT_ROOT
    with tempfile.TemporaryDirectory() as tmp:
        tmp_root = Path(tmp)
        dev_one = build_site('dev', tmp_root / 'dev-one', project_root)
        dev_two = build_site('dev', tmp_root / 'dev-two', project_root)
        prod_one = build_site('prod', tmp_root / 'prod-one', project_root)
        prod_two = build_site('prod', tmp_root / 'prod-two', project_root)

        if _digest_directory(dev_one) != _digest_directory(dev_two):
            raise AssertionError('Dev preview output is not deterministic')
        if _digest_directory(prod_one) != _digest_directory(prod_two):
            raise AssertionError('Prod artifact output is not deterministic')

        _assert_prod_paths(prod_one)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='Build the ZTI website from a single source tree.')
    parser.add_argument('--target', choices=['dev', 'prod'])
    parser.add_argument('--out', type=Path)
    parser.add_argument('--check', action='store_true')
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = _parser().parse_args(list(argv) if argv is not None else None)
    if args.check:
        check_build()
        return 0
    if not args.target or not args.out:
        raise SystemExit('--target and --out are required unless --check is used')
    build_site(args.target, args.out)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
