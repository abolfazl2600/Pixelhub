"""Build-time module and asset selection for product-specific Flutter artifacts.

Flutter's runtime feature flags alone do not remove resources from the package.
This module limits each build to explicit resources and provides compile-time
constants for tree shaking. The original pubspec is restored on all exits.
"""
from __future__ import annotations

import json
import zipfile
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path

from registry import ROOT, ConfigurationError

APP = ROOT / 'apps/game'
PUBSPEC = APP / 'pubspec.yaml'
# Feature flag -> compile-time Dart symbol. Existing product manifests are the
# sole source of truth; don't maintain a second feature registry in CI.
COMPILED_MODULES = {
    'museum': 'MUSEUM',
    'achievements': 'BADGES',
    'image_import': 'IMAGE_IMPORT',
    'profile': 'PROFILE',
    'diamond_painting': 'DIAMOND',
    'canvas_painting': 'CANVAS',
    'animations': 'ANIMATIONS',
    'sound_effects': 'SOUNDS',
    'online_catalog': 'ONLINE',
}
ASSET_PREFIXES = (
    'assets/levels/', 'assets/animations/', 'assets/brand/',
    'assets/products/', 'assets/sounds/',
)


@dataclass(frozen=True)
class AssetPlan:
    product: str
    assets: tuple[str, ...]
    modules: dict[str, bool]

    @property
    def dart_defines(self) -> list[str]:
        return [
            f'--dart-define=MODULE_{symbol}={str(self.modules[feature]).lower()}'
            for feature, symbol in COMPILED_MODULES.items()
        ]

    def as_report(self) -> dict:
        return {
            'modules': {key: self.modules[key] for key in COMPILED_MODULES},
            'bundled_asset_count': len(self.assets),
            'bundled_source_bytes': sum((APP / name).stat().st_size for name in self.assets),
            'bundled_assets': list(self.assets),
        }


def plan_assets(product) -> AssetPlan:
    product.require_ready()
    features = product.data['features']
    content = product.data['content']
    files = {
        'assets/levels/metadata.json',
        content['offline_manifest'].removeprefix('apps/game/'),
        product.data['identity']['icon'].removeprefix('apps/game/'),
    }
    offline_manifest = ROOT / content['offline_manifest']
    try:
        pictures = json.loads(offline_manifest.read_text())
    except (OSError, ValueError) as exc:
        raise ConfigurationError('Invalid offline picture manifest') from exc
    level_ids = set()
    for name in pictures:
        if (Path(name).name != name or not name.endswith('.json')):
            raise ConfigurationError(f'Unsafe bundled level name: {name}')
        asset = f'assets/levels/{name}'
        files.add(asset)
        try:
            level = json.loads((APP / asset).read_text())
        except (OSError, ValueError) as exc:
            raise ConfigurationError(f'Invalid bundled level {name}') from exc
        level_ids.add(level['levelId'])

    if features['animations']:
        files.add('assets/animations/catalog.json')
        animation_catalog = json.loads((APP / 'assets/animations/catalog.json').read_text())
        for level_id in level_ids:
            if level_id in animation_catalog:
                animation = animation_catalog[level_id]
                if Path(animation).name != animation:
                    raise ConfigurationError('Unsafe animation filename')
                files.add(f'assets/animations/{animation}')

    if features['sound_effects']:
        files.add('assets/sounds/painting_completed.wav')
        if features['coins']:
            files.update({
                'assets/sounds/coin_purchase.wav',
                'assets/sounds/coins_earned.wav',
            })
    for name in files:
        if not name.startswith('assets/') or not (APP / name).is_file():
            raise ConfigurationError(f'Missing selected asset: {name}')
    return AssetPlan(product=product.id,
                     assets=tuple(sorted(files)),
                     modules={flag: features[flag] for flag in COMPILED_MODULES})


def pubspec_for(plan: AssetPlan, original: str) -> str:
    start_token = '\n  assets:\n'
    end_token = '\n  fonts:\n'
    start = original.find(start_token)
    end = original.find(end_token, start + len(start_token))
    if start < 0 or end < 0 or end <= start:
        raise ConfigurationError('Unexpected Flutter pubspec asset section')
    selected = ''.join(f'    - {path}\n' for path in plan.assets)
    return original[:start] + start_token + selected + original[end:]


@contextmanager
def selected_product_assets(plan: AssetPlan):
    """Select only these resources for flutter pub get/build, then restore Git.

    A matrix job has its own checkout; local concurrent builds in the same
    working tree are deliberately unsupported.
    """
    previous = PUBSPEC.read_bytes()
    content = pubspec_for(plan, previous.decode('utf-8'))
    PUBSPEC.write_text(content)
    try:
        yield
    finally:
        PUBSPEC.write_bytes(previous)


def _verify_allowed(actual: set[str], plan: AssetPlan) -> dict:
    expected = set(plan.assets)
    selected = {name for name in actual if name.startswith(ASSET_PREFIXES)}
    missing = expected - selected
    unexpected = selected - expected
    if missing or unexpected:
        raise ConfigurationError(
            f'{plan.product}: wrong packaged assets; '
            f'missing={sorted(missing)}, unexpected={sorted(unexpected)}')
    return {'asset_count_verified': len(selected)}


def inspect_android(path: Path, plan: AssetPlan) -> dict:
    """Inspect real APK/AAB zip contents; do not trust source configuration."""
    with zipfile.ZipFile(path) as archive:
        actual = set()
        for filename in archive.namelist():
            separator = 'flutter_assets/'
            if separator in filename and not filename.endswith('/'):
                relative = filename.split(separator, 1)[1]
                if relative.startswith('assets/'):
                    actual.add(relative)
        result = _verify_allowed(actual, plan)
    return result


def inspect_web(web: Path, plan: AssetPlan) -> dict:
    actual = {
        file.relative_to(web / 'assets').as_posix()
        for file in (web / 'assets').rglob('*') if file.is_file()
    }
    return _verify_allowed(actual, plan)
