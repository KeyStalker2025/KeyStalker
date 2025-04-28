import json
import os
import zipfile

import config


def unzip_manifest_only(ext_path):
    """
    Unzip only 'manifest.json' from the extension package (.crx).
    Returns the extracted directory path.
    """
    try:
        ext_path = os.path.realpath(ext_path)
        ext_id, _ = os.path.splitext(os.path.basename(ext_path))
        extract_dir = os.path.join(config.SOURCE_DIR, ext_id)

        if os.path.exists(os.path.join(extract_dir, 'manifest.json')):
            return extract_dir

        with zipfile.ZipFile(ext_path, 'r') as zip_ref:
            zip_ref.extract('manifest.json', path=extract_dir)

        return extract_dir

    except (UnicodeEncodeError, KeyError, zipfile.BadZipFile) as e:
        print(f"Failed to unzip manifest from: {ext_path} | Error: {e}")
        return None


def unzip_all_files(ext_path, force=False):
    """
    Fully unzip all files from the extension package (.crx).
    Returns the extracted directory path.
    """
    try:
        ext_path = os.path.realpath(ext_path)
        ext_id, _ = os.path.splitext(os.path.basename(ext_path))
        extract_dir = os.path.join(config.SOURCE_DIR, ext_id)

        if os.path.exists(extract_dir) and not force:
            return extract_dir

        with zipfile.ZipFile(ext_path, 'r') as zip_ref:
            zip_ref.extractall(path=extract_dir)

        return extract_dir

    except (UnicodeEncodeError, zipfile.BadZipFile) as e:
        print(f"Failed to unzip extension: {ext_path} | Error: {e}")
        return None


def list_extension_ids():
    """
    List all extension IDs (.crx filenames) under DOWNLOAD_DIR.
    """
    extension_ids = [
        os.path.splitext(file)[0]
        for file in os.listdir(config.DOWNLOAD_DIR)
        if file.endswith('.crx')
    ]
    extension_ids.sort()
    return extension_ids


def find_extracted_dir_by_id(ext_id, search_paths=None):
    """
    Find the extracted directory by extension ID.
    """
    if not search_paths:
        search_paths = config.SOURCE_DIR.split(';')

    for base_path in search_paths:
        candidate_path = os.path.join(base_path, ext_id)
        if os.path.isdir(candidate_path):
            return candidate_path

    return ''


def find_crx_file_by_id(ext_id):
    """
    Find the CRX file path by extension ID.
    """
    ext_path = os.path.join(config.DOWNLOAD_DIR, f"{ext_id}.crx")
    return ext_path if os.path.exists(ext_path) else None


def identify_network_related_extensions():
    """
    Identify extensions that require network permissions.
    """
    ext_ids = list_extension_ids()
    network_exts = set()

    for ext_id in ext_ids:
        ext_dir = find_extracted_dir_by_id(ext_id)
        manifest_path = os.path.join(ext_dir, 'manifest.json')

        if not os.path.exists(manifest_path):
            continue

        with open(manifest_path, encoding='utf-8-sig') as f:
            manifest = json.load(f)

        if is_network_related(manifest):
            network_exts.add(ext_id)
        else:
            clean_manifest(manifest)

    return sorted(network_exts)


def is_network_related(manifest):
    """
    Determine if a manifest indicates network access capabilities.
    """
    web_accessible = any(
        isinstance(resource, dict) and any(res.endswith(('html', 'js')) for res in resource.get('resources', []))
        for resource in manifest.get('web_accessible_resources', [])
    )

    host_permissions = 'host_permissions' in manifest
    chrome_url_overrides = 'chrome_url_overrides' in manifest

    content_scripts = any('js' in script for script in manifest.get('content_scripts', []))

    permissions_flags = ['://', '<all_urls>', 'webRequest']
    has_permissions = any(flag in str(manifest.get('permissions', [])) for flag in permissions_flags)

    has_action = False
    if 'browser_action' in manifest or 'action' in manifest:
        action = manifest.get('action', manifest.get('browser_action'))
        if action and 'default_popup' in action and len(action['default_popup']) > 0:
            has_action = True

    optional_permissions = 'optional_permissions' in manifest

    return any([
        web_accessible, has_permissions, host_permissions,
        content_scripts, has_action, optional_permissions,
        chrome_url_overrides
    ])


def clean_manifest(manifest):
    """
    Remove unnecessary fields from the manifest for non-network extensions.
    """
    keys_to_remove = ['update_url', 'name', 'description', 'short_name', 'icons', 'version', 'default_locale']
    for key in keys_to_remove:
        manifest.pop(key, None)


def main():
    # Step 1: Only extract manifest.json from all CRX files
    for file in os.listdir(config.DOWNLOAD_DIR):
        if file.endswith('.crx'):
            unzip_manifest_only(ext_path=os.path.join(config.DOWNLOAD_DIR, file))

    # Step 2: Identify network-related extensions
    network_ext_ids = identify_network_related_extensions()

    # Step 3: Fully extract network-related extensions
    for ext_id in network_ext_ids:
        print(f"Extracting network extension: {ext_id}")
        ext_path = find_crx_file_by_id(ext_id)
        if ext_path:
            unzip_all_files(ext_path=ext_path, force=True)


if __name__ == '__main__':
    main()
