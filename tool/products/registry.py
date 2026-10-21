"""Product registry. Manifests use JSON syntax (a strict, portable YAML subset).

No YAML executable tags, third-party parser, credentials or ambient defaults.
"""
from __future__ import annotations
import json
import re
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATEGORIES = ['nature', 'animals', 'objects', 'masterpieces', 'persian_architecture', 'patterns', 'space']
FEATURES = ['coins', 'achievements', 'animations', 'image_import', 'diamond_painting', 'canvas_painting', 'sound_effects', 'online_catalog', 'profile', 'museum', 'free_painting', 'background_music']

class ConfigurationError(ValueError):
    pass


def validate_schema(value, schema, path='$'):
    """Validate the deliberately small JSON Schema vocabulary used by schema.json."""
    types = {'object': dict, 'array': list, 'string': str, 'integer': int, 'boolean': bool}
    expected = schema.get('type')
    if expected and (not isinstance(value, types[expected]) or (expected == 'integer' and isinstance(value, bool))):
        raise ConfigurationError(f'{path}: expected {expected}')
    if 'enum' in schema and value not in schema['enum']:
        raise ConfigurationError(f'{path}: expected one of {schema["enum"]}')
    if isinstance(value, dict):
        props = schema.get('properties', {})
        for key in schema.get('required', []):
            if key not in value:
                raise ConfigurationError(f'{path}.{key}: required')
        if schema.get('additionalProperties') is False:
            extra = value.keys() - props.keys()
            if extra:
                raise ConfigurationError(f'{path}: unknown keys {sorted(extra)}')
        for key, item in value.items():
            if key in props:
                validate_schema(item, props[key], f'{path}.{key}')
    if isinstance(value, list):
        if len(value) < schema.get('minItems', 0) or len(value) != len(set(map(json.dumps, value))) and schema.get('uniqueItems'):
            raise ConfigurationError(f'{path}: empty or duplicate entries')
        for index, item in enumerate(value):
            validate_schema(item, schema.get('items', {}), f'{path}[{index}]')
    if isinstance(value, str):
        if len(value) < schema.get('minLength', 0) or ('pattern' in schema and not re.fullmatch(schema['pattern'], value)):
            raise ConfigurationError(f'{path}: invalid string {value!r}')
    if type(value) is int:
        if value < schema.get('minimum', value) or value > schema.get('maximum', value):
            raise ConfigurationError(f'{path}: integer out of bounds')


@dataclass(frozen=True)
class Product:
    id: str
    ready: bool
    application_id: str
    version_name: str
    version_code: int
    signing_prefix: str
    data: dict

    @classmethod
    def read(cls, path: Path):
        try:
            data = json.loads(path.read_text())
        except (ValueError, OSError) as exc:
            raise ConfigurationError(f'{path}: expected JSON-compatible YAML: {exc}') from exc
        validate_schema(data, json.loads((ROOT / 'products/schema.json').read_text()), str(path))
        if path.stem != data['id']:
            raise ConfigurationError(f'{path}: filename must equal product ID')
        return cls(data['id'], data['ready'], data['identity']['application_id'], data['identity']['version_name'], data['identity']['version_code'], data['distribution']['signing_prefix'], data)

    def require_ready(self):
        if not self.ready:
            raise ConfigurationError(f'{self.id}: product is configured but not ready; add content and branding before building')
        return self


def safe_path(relative: str) -> Path:
    if Path(relative).is_absolute():
        raise ConfigurationError(f'Expected a repository-relative path: {relative}')
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ConfigurationError(f'Path outside repository: {relative}')
    return path


def load_registry() -> dict[str, Product]:
    result = {}
    packages, scopes, web_paths = set(), set(), set()
    for path in sorted((ROOT / 'products').glob('*.yaml')):
        product = Product.read(path)
        d = product.data
        for value, seen, label in [(product.application_id, packages, 'application ID'), (d['identity']['storage_scope'], scopes, 'storage scope'), (d['distribution']['web_base_href'], web_paths, 'web path')]:
            if value in seen:
                raise ConfigurationError(f'{product.id}: duplicate {label}: {value}')
            seen.add(value)
        if product.id == 'pixelhub':
            if product.application_id != 'io.github.abolfazl2600.pixelhub' or d['identity']['storage_scope'] != 'pixelhub':
                raise ConfigurationError('PixelHub identity/storage must remain unchanged')
            if d['distribution']['web_base_href'] != '/Pixelhub/':
                raise ConfigurationError('PixelHub Web base href must remain /Pixelhub/')
            version = re.search(r'^version:\s*(\S+)', (ROOT / 'apps/game/pubspec.yaml').read_text(), re.M).group(1)
            if version != f'{product.version_name}+{product.version_code}':
                raise ConfigurationError('PixelHub pubspec version must match its product version')
        elif d['distribution']['web_base_href'] == '/Pixelhub/' or not d['distribution']['web_base_href'].startswith('/Pixelhub/'):
            raise ConfigurationError('Additional Pages products need a separate path under /Pixelhub/')
        elif d['identity']['storage_scope'].startswith('pixelhub.'):
            raise ConfigurationError('New storage scopes must not fall under the legacy clear-data prefix')
        manifest_path = d['content']['online_manifest']
        if manifest_path.startswith('/') or '..' in manifest_path.split('/'):
            raise ConfigurationError(f'{product.id}: unsafe online manifest path')
        f = d['features']
        if f['free_painting'] or f['background_music']:
            raise ConfigurationError(f'{product.id}: free painting/background music are not implemented capabilities')
        if f['canvas_painting'] is False and d['appearance']['default_style'] == 'canvas' or f['diamond_painting'] is False and d['appearance']['default_style'] == 'diamond':
            raise ConfigurationError(f'{product.id}: default texture requires its feature')
        if f['museum'] and not f['profile']:
            raise ConfigurationError(f'{product.id}: museum requires profile')
        if not set(d['content']['default_categories']) <= set(d['content']['categories']):
            raise ConfigurationError(f'{product.id}: default categories must be available')
        if f['online_catalog'] != bool(d['content']['online_root']):
            raise ConfigurationError(f'{product.id}: online_catalog requires an HTTPS online_root; disabled products must use an empty root')
        if d['content']['online_root'] and not re.fullmatch(r'https://[^\s]+/', d['content']['online_root']):
            raise ConfigurationError(f'{product.id}: online_root must be an HTTPS directory')
        if product.ready:
            icon = safe_path(d['identity']['icon'])
            if not icon.is_file():
                raise ConfigurationError(f'{product.id}: missing icon {icon}')
            manifest = safe_path(d['content']['offline_manifest'])
            content = json.loads(manifest.read_text())
            if not isinstance(content, list) or not content or len(content) != len(set(content)):
                raise ConfigurationError(f'{product.id}: invalid offline manifest')
            metadata = json.loads((ROOT / 'apps/game/assets/levels/metadata.json').read_text())
            for filename in content:
                if not re.fullmatch(r'[a-z0-9-]+\.json', filename):
                    raise ConfigurationError(f'{product.id}: invalid level path')
                level = json.loads((ROOT / 'apps/game/assets/levels' / filename).read_text())
                if metadata[level['levelId']]['category'] not in d['content']['categories'] or max(level['width'], level['height']) > d['content']['max_dimension']:
                    raise ConfigurationError(f'{product.id}: {filename} violates content policy')
        result[product.id] = product
    if 'pixelhub' not in result:
        raise ConfigurationError('Missing original PixelHub product')
    return result


def select(application: str) -> list[Product]:
    products = load_registry()
    if application == 'all':
        return [p for p in products.values() if p.ready]
    if application not in products:
        raise ConfigurationError(f'Unknown product: {application}')
    return [products[application].require_ready()]
