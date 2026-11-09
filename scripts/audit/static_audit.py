#!/usr/bin/env python3
"""Audit statique des modules candidats — Phase 0-A (outil de cadrage, pas une validation).

Vérifie SANS installer Odoo, pour chaque candidat ET pour toute sa chaîne de dépendances :
  - présence du module et absence de doublon de nom entre dépôts ;
  - manifeste : `installable`, version 19.0.x pour les modules OCA, licence, maturité ;
  - résolution récursive des dépendances Odoo dans l'ensemble Odoo 19 Community + OCA figé ;
  - dépendances externes déclarées (Python et binaires) de toute la chaîne, comparées aux
    dépendances fournies par l'environnement d'exécution d'Odoo (requirements.txt d'Odoo) ;
  - existence des fichiers déclarés (data, demo) ;
  - syntaxe Python (grammaire Python 3.10, minimum d'Odoo 19, et compilation par l'interpréteur
    courant) et bonne formation des fichiers XML ;
  - nombre de fichiers de tests ;
  - imports Python de premier niveau non couverts (heuristique, avertissement seulement ;
    les scripts `migrations/` sont exclus car ils ne s'exécutent qu'en mise à jour).

Statuts :
  BLOQUANT              : problème qui empêchera certainement l'installation
  DEP_EXTERNE_A_FOURNIR : dépendance externe absente de l'environnement Odoo standard
  STATIQUE_OK           : aucun problème statique détecté (≠ installé, ≠ testé)

Limites (non détectables sans installation) : erreurs de chargement des vues et des données,
conflits entre modules, modules installés automatiquement (auto_install), compatibilité réelle
des versions de bibliothèques, comportement fonctionnel. → scripts/test_install.sh

Usage : static_audit.py <odoo_src> <oca_root> <candidates.txt> <sortie.json>
Code de retour : 0 si aucun candidat testable n'est BLOQUANT, 1 sinon.
"""
import ast
import json
import os
import re
import sys
from collections import defaultdict

from lxml import etree

TESTABLE = {'retenu', 'a_evaluer', 'piste_separee'}
CATEGORIES = TESTABLE | {'differe', 'rejete'}

# Noms d'import différents du nom de distribution (dépendances d'Odoo et cas courants)
DIST_TO_IMPORT = {
    'python-dateutil': 'dateutil', 'pillow': 'PIL', 'pyopenssl': 'OpenSSL',
    'python-ldap': 'ldap', 'python-stdnum': 'stdnum', 'python-magic': 'magic',
    'libsass': 'sass', 'pyserial': 'serial', 'pyusb': 'usb', 'pypdf2': 'PyPDF2',
    'pypdf': 'pypdf', 'lxml-html-clean': 'lxml_html_clean', 'pypiwin32': 'win32api',
    'markupsafe': 'markupsafe', 'jinja2': 'jinja2', 'babel': 'babel',
    'werkzeug': 'werkzeug', 'xlsxwriter': 'xlsxwriter', 'zeep': 'zeep',
}


def norm(name):
    return re.sub(r'[-_.]+', '-', name.strip().lower())


def read_candidates(path):
    out = []
    for raw in open(path, encoding='utf-8'):
        line = raw.split('#', 1)[0].strip()
        if not line:
            continue
        parts = [p.strip() for p in line.split('|')]
        if len(parts) < 3 or parts[0] not in CATEGORIES:
            sys.exit(f'Ligne de candidats invalide : {raw.rstrip()}')
        out.append({'category': parts[0], 'domain': parts[1], 'module': parts[2],
                    'note': parts[3] if len(parts) > 3 else ''})
    names = [c['module'] for c in out]
    dup = {n for n in names if names.count(n) > 1}
    if dup:
        sys.exit(f'Modules en double dans {path} : {sorted(dup)}')
    return out


def runtime_python(odoo_src):
    """Distributions et noms d'import fournis par requirements.txt d'Odoo."""
    dists = set()
    for raw in open(os.path.join(odoo_src, 'requirements.txt'), encoding='utf-8'):
        line = raw.split('#', 1)[0].split(';', 1)[0].strip()
        if line:
            dists.add(norm(re.split(r'[<>=!~ \[]', line, maxsplit=1)[0]))
    imports = {DIST_TO_IMPORT.get(d, d.replace('-', '_')) for d in dists}
    return dists, imports


def manifest(path):
    src = open(os.path.join(path, '__manifest__.py'), encoding='utf-8').read()
    return ast.literal_eval(src[src.index('{'):])


def build_index(odoo_src, oca_root):
    index, dups = {}, defaultdict(list)
    roots = [('odoo', os.path.join(odoo_src, 'addons')),
             ('odoo', os.path.join(odoo_src, 'odoo', 'addons'))]
    roots += [(f'OCA/{r}', os.path.join(oca_root, r)) for r in sorted(os.listdir(oca_root))
              if os.path.isdir(os.path.join(oca_root, r))]
    for src, base in roots:
        for m in sorted(os.listdir(base)):
            p = os.path.join(base, m)
            if os.path.isfile(os.path.join(p, '__manifest__.py')):
                dups[m].append(src)
                index.setdefault(m, (src, p))
    return index, {m: s for m, s in dups.items() if len(s) > 1}


def closure(name, index):
    """Chaîne complète des dépendances ; renvoie (modules trouvés, chaînes manquantes)."""
    seen, missing, stack = set(), set(), [(name, (name,))]
    while stack:
        mod, chain = stack.pop()
        if mod in seen:
            continue
        seen.add(mod)
        if mod not in index:
            missing.add(' > '.join(chain))
            continue
        for dep in manifest(index[mod][1]).get('depends', []):
            stack.append((dep, chain + (dep,)))
    return seen - {m for m in seen if m not in index}, missing


def check_sources(path):
    """Syntaxe Python (3.10 + interpréteur courant), XML, imports de premier niveau."""
    errors, imports, n_py, n_xml, n_tests = [], set(), 0, 0, 0
    local = set(os.listdir(path))
    for root, _, files in os.walk(path):
        for f in files:
            p = os.path.join(root, f)
            rel = os.path.relpath(p, path)
            if f.endswith('.py'):
                n_py += 1
                if rel.startswith('tests' + os.sep) and f.startswith('test_'):
                    n_tests += 1
                src = open(p, encoding='utf-8').read()
                try:
                    tree = ast.parse(src, filename=rel, feature_version=(3, 10))
                    compile(src, rel, 'exec')
                except SyntaxError as e:
                    errors.append(f'PY {rel}:{e.lineno}: {e.msg}')
                    continue
                if rel.startswith('migrations' + os.sep):
                    continue  # scripts de migration : exécutés seulement lors d'une mise à jour
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imports.update(a.name.split('.')[0] for a in node.names)
                    elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                        imports.add(node.module.split('.')[0])
            elif f.endswith('.xml'):
                n_xml += 1
                try:
                    etree.parse(p)
                except etree.XMLSyntaxError as e:
                    errors.append(f'XML {rel}: {e}')
    stdlib = set(sys.stdlib_module_names)
    imports = {i for i in imports if i not in stdlib and i not in local and i != 'odoo'}
    return n_py, n_xml, n_tests, errors, imports


def main():
    odoo_src, oca_root, cand_file, out = sys.argv[1:5]
    cands = read_candidates(cand_file)
    index, duplicates = build_index(odoo_src, oca_root)
    rt_dists, rt_imports = runtime_python(odoo_src)
    rt_norm = rt_dists | {norm(i) for i in rt_imports}
    oca_names = {m for m, (s, _) in index.items() if s != 'odoo'}

    results = []
    for c in cands:
        r = dict(c)
        name = c['module']
        if name not in index:
            r['status'] = 'ABSENT'
            results.append(r)
            continue
        src, path = index[name]
        m = manifest(path)
        mods, missing = closure(name, index)
        blocking, ext_missing, warnings = [], [], []

        if missing:
            blocking.append(f'dépendances introuvables : {sorted(missing)}')
        for dep in sorted(mods):
            dsrc, dpath = index[dep]
            dm = manifest(dpath)
            if not dm.get('installable', True):
                blocking.append(f'{dep} : installable=False')
            if dsrc != 'odoo' and not str(dm.get('version', '')).startswith('19.0.'):
                blocking.append(f'{dep} : version {dm.get("version")!r} (19.0.x attendu)')
            if dep in duplicates:
                warnings.append(f'{dep} présent dans plusieurs dépôts {duplicates[dep]} '
                                f'(utilisé : {dsrc})')
            ext = dm.get('external_dependencies') or {}
            for py in ext.get('python', []):
                if norm(py) not in rt_norm:
                    ext_missing.append(f'python:{py} (requis par {dep})')
            for b in ext.get('bin', []):
                ext_missing.append(f'bin:{b} (requis par {dep}) — à vérifier dans l\'image')
            for key in ('data', 'demo'):
                for f in dm.get(key, []):
                    if not os.path.isfile(os.path.join(dpath, f)):
                        blocking.append(f'{dep} : fichier {key} absent {f}')

        n_py, n_xml, n_tests, errs, imports = check_sources(path)
        blocking += errs
        if src != 'odoo':
            covered = rt_imports | oca_names
            declared = {DIST_TO_IMPORT.get(norm(p), p.replace('-', '_'))
                        for d in mods for p in (manifest(index[d][1]).get('external_dependencies')
                                                or {}).get('python', [])}
            undeclared = sorted(imports - covered - declared)
            if undeclared:
                warnings.append(f'imports non couverts (heuristique, peut être optionnel) : {undeclared}')
        if n_tests == 0:
            warnings.append('aucun fichier tests/test_*.py')

        r.update({
            'source': src, 'version': m.get('version', ''),
            'license': m.get('license', 'LGPL-3 (défaut Odoo)'),
            'development_status': m.get('development_status', ''),
            'depends': m.get('depends', []), 'closure_size': len(mods) - 1,
            'oca_in_closure': sorted(d for d in mods if index[d][0] != 'odoo' and d != name),
            'py_files': n_py, 'xml_files': n_xml, 'test_files': n_tests,
            'blocking': blocking, 'external_missing': sorted(set(ext_missing)),
            'warnings': warnings,
        })
        r['status'] = ('BLOQUANT' if blocking else
                       'DEP_EXTERNE_A_FOURNIR' if ext_missing else 'STATIQUE_OK')
        results.append(r)

    json.dump(results, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)

    by_cat = defaultdict(lambda: defaultdict(int))
    for r in results:
        by_cat[r['category']][r['status']] += 1
        flag = ''
        if r.get('blocking'):
            flag += f" BLOQUANT={r['blocking']}"
        if r.get('external_missing'):
            flag += f" EXT={r['external_missing']}"
        if r.get('warnings'):
            flag += f" AVERT={r['warnings']}"
        print(f"{r['status']:22} {r['category']:13} {r['module']:36} {r.get('source', ''):30} "
              f"{r.get('license', ''):8} tests={r.get('test_files', '-')}{flag}")
    print('\nSynthèse par catégorie :')
    for cat in sorted(by_cat):
        print(f'  {cat:13} ' + ', '.join(f'{s}={n}' for s, n in sorted(by_cat[cat].items())))
    bad = [r['module'] for r in results
           if r['category'] in TESTABLE and r['status'] in ('BLOQUANT', 'ABSENT')]
    if bad:
        print(f'\nCandidats testables bloquants ou absents : {bad}')
    sys.exit(1 if bad else 0)


if __name__ == '__main__':
    main()
