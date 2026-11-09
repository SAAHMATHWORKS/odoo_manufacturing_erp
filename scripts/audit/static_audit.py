#!/usr/bin/env python3
"""Audit statique des modules candidats (Phase 0-A, prototype jetable).

Vérifie, sans installer Odoo : présence du module, manifeste (version, licence,
installable, statut de maturité, dépendances Python externes), résolution
récursive des dépendances Odoo dans l'ensemble Odoo 19 Community + OCA figé,
compilation Python et validité XML. Ne remplace PAS un test d'installation.

Usage : static_audit.py <odoo_src> <oca_root> <candidates.txt> <out.json>
"""
import ast, json, os, py_compile, sys, tempfile
from lxml import etree

odoo_src, oca_root, cand_file, out = sys.argv[1:5]

def manifest(path):
    f = os.path.join(path, '__manifest__.py')
    if not os.path.isfile(f):
        return None
    s = open(f, encoding='utf-8').read()
    return ast.literal_eval(s[s.index('{'):])

# Index de tous les modules disponibles : chemin par nom
index = {}
for base in (os.path.join(odoo_src, 'addons'), os.path.join(odoo_src, 'odoo', 'addons')):
    for m in os.listdir(base):
        if os.path.isfile(os.path.join(base, m, '__manifest__.py')):
            index[m] = ('odoo', os.path.join(base, m))
for repo in sorted(os.listdir(oca_root)):
    rp = os.path.join(oca_root, repo)
    if not os.path.isdir(rp):
        continue
    for m in os.listdir(rp):
        if os.path.isfile(os.path.join(rp, m, '__manifest__.py')) and m not in index:
            index[m] = (f'OCA/{repo}', os.path.join(rp, m))

def resolve(name, seen=None, chain=()):
    """Retourne (ensemble des dépendances, dépendances introuvables)."""
    seen = set() if seen is None else seen
    missing = set()
    if name in seen:
        return seen, missing
    seen.add(name)
    if name not in index:
        missing.add(' > '.join(chain + (name,)))
        return seen, missing
    for dep in manifest(index[name][1]).get('depends', []):
        _, mis = resolve(dep, seen, chain + (name,))
        missing |= mis
    return seen, missing

def syntax_check(path):
    errors, n_py, n_xml = [], 0, 0
    for root, _, files in os.walk(path):
        for f in files:
            p = os.path.join(root, f)
            if f.endswith('.py'):
                n_py += 1
                try:
                    py_compile.compile(p, cfile=os.path.join(tempfile.gettempdir(), 'x.pyc'), doraise=True)
                except py_compile.PyCompileError as e:
                    errors.append(f'PY {os.path.relpath(p, path)}: {e.msg.splitlines()[-1]}')
            elif f.endswith('.xml'):
                n_xml += 1
                try:
                    etree.parse(p)
                except etree.XMLSyntaxError as e:
                    errors.append(f'XML {os.path.relpath(p, path)}: {e}')
    return n_py, n_xml, errors

results = []
for line in open(cand_file, encoding='utf-8'):
    line = line.split('#')[0].strip()
    if not line:
        continue
    domain, name = line.split(':', 1)
    r = {'domain': domain.strip(), 'module': name.strip()}
    if r['module'] not in index:
        r['status'] = 'ABSENT'
        results.append(r)
        continue
    src, path = index[r['module']]
    m = manifest(path)
    deps, missing = resolve(r['module'])
    n_py, n_xml, errs = syntax_check(path)
    r.update({
        'source': src,
        'version': m.get('version', ''),
        'license': m.get('license', 'LGPL-3 (défaut Odoo)'),
        'installable': m.get('installable', True),
        'development_status': m.get('development_status', ''),
        'depends': m.get('depends', []),
        'external_python': (m.get('external_dependencies') or {}).get('python', []),
        'all_deps_count': len(deps) - 1,
        'oca_deps': sorted(d for d in deps if d in index and index[d][0] != 'odoo' and d != r['module']),
        'missing_deps': sorted(missing),
        'has_tests': os.path.isdir(os.path.join(path, 'tests')),
        'py_files': n_py, 'xml_files': n_xml, 'syntax_errors': errs,
    })
    ok = (r['installable'] and not missing and not errs
          and str(r['version']).startswith('19.0') if src != 'odoo' else r['installable'] and not missing)
    r['status'] = 'STATIQUE_OK' if ok else 'PROBLEME'
    results.append(r)

json.dump(results, open(out, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for r in results:
    print(f"{r['status']:12} {r['module']:42} {r.get('source',''):32} {r.get('license',''):8} "
          f"{r.get('development_status',''):11} tests={r.get('has_tests','')} missing={r.get('missing_deps','')} "
          f"err={len(r.get('syntax_errors',[]))} ext={r.get('external_python','')}")
