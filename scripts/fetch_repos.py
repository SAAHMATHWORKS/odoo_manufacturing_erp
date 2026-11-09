#!/usr/bin/env python3
"""Récupère Odoo et les dépôts OCA aux commits figés dans repos.yaml.

- Chaque dépôt est placé dans src/odoo ou src/oca/<dépôt>, au commit exact (HEAD détachée).
- Génère docker/odoo.test.conf avec l'addons_path correspondant (chemins vus depuis le conteneur).
- N'utilise jamais un nom de branche pour se positionner : seul le commit fait foi.

Usage :
    python3 scripts/fetch_repos.py             # tout récupérer
    python3 scripts/fetch_repos.py --oca-only  # seulement les dépôts OCA
"""
import os
import subprocess
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTAINER_SRC = '/mnt/src'  # point de montage de src/ dans le conteneur de test


def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


def checkout(url, commit, dest):
    """Place le dépôt `url` au commit `commit` dans `dest` (clone superficiel par commit)."""
    if os.path.isdir(os.path.join(dest, '.git')):
        current = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=dest,
                                 capture_output=True, text=True).stdout.strip()
        if current == commit:
            print(f'= {dest} déjà au commit {commit[:12]}')
            return
    else:
        os.makedirs(dest, exist_ok=True)
        run(['git', 'init', '-q'], cwd=dest)
        run(['git', 'remote', 'add', 'origin', url], cwd=dest)
    print(f'> {url} @ {commit[:12]} -> {os.path.relpath(dest, ROOT)}')
    run(['git', 'fetch', '-q', '--depth', '1', 'origin', commit], cwd=dest)
    run(['git', 'checkout', '-q', '--detach', 'FETCH_HEAD'], cwd=dest)
    got = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=dest,
                         capture_output=True, text=True).stdout.strip()
    if got != commit:
        sys.exit(f'ERREUR : {dest} est au commit {got}, attendu {commit}')


def main():
    oca_only = '--oca-only' in sys.argv
    cfg = yaml.safe_load(open(os.path.join(ROOT, 'repos.yaml'), encoding='utf-8'))

    if not oca_only:
        o = cfg['odoo']
        checkout(o['url'], o['commit'], os.path.join(ROOT, o['path']))

    addons = [f'{CONTAINER_SRC}/odoo/addons', f'{CONTAINER_SRC}/odoo/odoo/addons']
    for name, repo in cfg['oca'].items():
        checkout(repo['url'], repo['commit'], os.path.join(ROOT, 'src', 'oca', name))
        addons.append(f'{CONTAINER_SRC}/oca/{name}')

    conf = os.path.join(ROOT, 'docker', 'odoo.test.conf')
    with open(conf, 'w', encoding='utf-8') as f:
        f.write('; Généré par scripts/fetch_repos.py — environnement de TEST uniquement\n'
                '[options]\n'
                'db_host = db\n'
                'db_port = 5432\n'
                'db_user = odoo\n'
                'db_password = odoo_test_only\n'
                'data_dir = /var/lib/odoo\n'
                'list_db = True\n'
                f'addons_path = {",".join(addons)}\n')
    print(f'Configuration écrite : {os.path.relpath(conf, ROOT)}')


if __name__ == '__main__':
    main()
