#!/usr/bin/env python3
"""Construit le plan de tests à partir de scripts/audit/candidates.txt et vérifie sa couverture.

Groupes générés :
  V-<domaine>   VALIDATION    modules « retenu » du domaine ; installation + tests OCA
  V-ENSEMBLE    VALIDATION    tous les modules « retenu » ensemble ; installation seule
  E-<module>    EVALUATION    chaque module « a_evaluer » seul ; installation + ses tests
  E-ENSEMBLE    EVALUATION    « retenu » + « a_evaluer » ensemble ; installation seule
  S-<module>    PISTE_SEPAREE chaque module « piste_separee » seul ; installation + ses tests

Un groupe EVALUATION ou PISTE_SEPAREE réussi ne vaut pas validation (décision P-003).
Les modules « differe » et « rejete » ne figurent dans aucun groupe.

Usage :
  test_plan.py --check   rapport de couverture ; code 1 si une règle est violée
  test_plan.py --tsv     plan exploitable par test_install.sh :
                         groupe <TAB> type <TAB> modules,... <TAB> tags_tests,... (vide = pas de tests)
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CAND = os.path.join(ROOT, 'scripts', 'audit', 'candidates.txt')
TESTABLE = ('retenu', 'a_evaluer', 'piste_separee')


def read_candidates():
    out = []
    for raw in open(CAND, encoding='utf-8'):
        line = raw.split('#', 1)[0].strip()
        if line:
            cat, dom, mod = [p.strip() for p in line.split('|')][:3]
            out.append((cat, dom, mod))
    return out


def module_source(mod):
    """'odoo', 'oca' ou None selon l'endroit où le module est trouvé dans src/."""
    for base in ('src/odoo/addons', 'src/odoo/odoo/addons'):
        if os.path.isfile(os.path.join(ROOT, base, mod, '__manifest__.py')):
            return 'odoo'
    oca = os.path.join(ROOT, 'src', 'oca')
    if os.path.isdir(oca):
        for repo in os.listdir(oca):
            if os.path.isfile(os.path.join(oca, repo, mod, '__manifest__.py')):
                return 'oca'
    return None


def build_plan(cands):
    groups = []
    retenu = [m for c, _, m in cands if c == 'retenu']
    domains = []
    for c, d, _ in cands:
        if c == 'retenu' and d not in domains:
            domains.append(d)
    for d in domains:
        mods = [m for c, dd, m in cands if c == 'retenu' and dd == d]
        groups.append((f'V-{d}', 'VALIDATION', mods, True))
    groups.append(('V-ENSEMBLE', 'VALIDATION', retenu, False))
    evals = [m for c, _, m in cands if c == 'a_evaluer']
    for m in evals:
        groups.append((f'E-{m}', 'EVALUATION', [m], True))
    if evals:
        groups.append(('E-ENSEMBLE', 'EVALUATION', retenu + evals, False))
    for m in [m for c, _, m in cands if c == 'piste_separee']:
        groups.append((f'S-{m}', 'PISTE_SEPAREE', [m], True))
    return groups


def check(cands, groups):
    errors = []
    in_groups = {}
    for name, kind, mods, _ in groups:
        for m in mods:
            in_groups.setdefault(m, []).append(name)
    for cat, _, m in cands:
        g = in_groups.get(m, [])
        if cat in TESTABLE and not [x for x in g if not x.endswith('ENSEMBLE')]:
            errors.append(f'{m} ({cat}) absent de tout groupe testé individuellement')
        if cat == 'retenu' and 'V-ENSEMBLE' not in g:
            errors.append(f'{m} (retenu) absent de V-ENSEMBLE')
        if cat != 'retenu' and any(x.startswith('V-') for x in g):
            errors.append(f'{m} ({cat}) présent dans un groupe de VALIDATION')
        if cat in ('differe', 'rejete') and g:
            errors.append(f'{m} ({cat}) ne doit figurer dans aucun groupe')
    if os.path.isdir(os.path.join(ROOT, 'src')):
        for cat, _, m in cands:
            if cat in TESTABLE and module_source(m) is None:
                errors.append(f'{m} ({cat}) introuvable dans src/ (lancer scripts/fetch_repos.py)')
    return in_groups, errors


def main():
    cands = read_candidates()
    groups = build_plan(cands)
    in_groups, errors = check(cands, groups)
    if '--tsv' in sys.argv:
        if errors:
            sys.exit('Plan de tests invalide :\n  ' + '\n  '.join(errors))
        for name, kind, mods, with_tests in groups:
            tags = [m for m in mods if with_tests and module_source(m) == 'oca']
            print(f"{name}\t{kind}\t{','.join(mods)}\t{','.join('/' + t for t in tags)}")
        return
    print('Couverture du plan de tests\n')
    for cat, dom, m in cands:
        print(f'  {cat:13} {dom:13} {m:36} -> {", ".join(in_groups.get(m, [])) or "(aucun groupe)"}')
    print(f'\n{len(groups)} groupes :')
    for name, kind, mods, with_tests in groups:
        print(f'  {name:42} {kind:13} {len(mods):3} modules  tests={"oui" if with_tests else "non (installation seule)"}')
    if errors:
        print('\nERREURS :\n  ' + '\n  '.join(errors))
        sys.exit(1)
    print('\nCouverture conforme.')


if __name__ == '__main__':
    main()
