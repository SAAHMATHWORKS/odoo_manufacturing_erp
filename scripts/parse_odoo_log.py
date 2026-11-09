#!/usr/bin/env python3
"""Analyse un journal Odoo 19 (sortie d'odoo-bin) et produit des compteurs fiables en JSON.

Format des lignes Odoo : « AAAA-MM-JJ HH:MM:SS,mmm PID NIVEAU base logger: message ».
Les lignes suivantes (traces Python) appartiennent à l'entrée précédente.

Compteurs :
  critical / error / warning : nombre d'ENTRÉES de journal par niveau (pas de lignes de trace).
      Les entrées ERROR de bilan de tests (« odoo.tests.result: … » et « Module X: n failures »)
      sont exclues de `error` et comptées dans `tests` pour éviter le double comptage.
  db_init_failed : « Failed to initialize database » (échec de chargement de la base)
  tests : bilan officiel d'Odoo (odoo/tests/result.py) « F failed, E error(s) of N tests
      when loading database » -> {failed, errors, run} ; None si aucun bilan (tests non lancés)
  test_modules_failed : modules signalés « Module X: n failures, m errors of t tests »
  browser_tests_skipped : entrées « Chrome executable not found » (tests navigateur ignorés)

Usage : parse_odoo_log.py <journal>
"""
import json
import re
import sys

ENTRY = re.compile(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3} \d+ (\w+) (\S+) ([\w.]+): (.*)$')
SUMMARY = re.compile(r'(\d+) failed, (\d+) error\(s\) of (\d+) tests when loading database')
MODULE_FAIL = re.compile(r'Module (\S+): (\d+) failures, (\d+) errors of (\d+) tests')


def parse(path):
    res = {'critical': 0, 'error': 0, 'warning': 0, 'db_init_failed': False,
           'tests': None, 'test_modules_failed': [], 'browser_tests_skipped': 0,
           'first_errors': []}
    for line in open(path, encoding='utf-8', errors='replace'):
        m = ENTRY.match(line.rstrip('\n'))
        if not m:
            continue
        level, _db, logger, msg = m.groups()
        s = SUMMARY.search(msg)
        if s and logger == 'odoo.tests.result':
            f, e, n = map(int, s.groups())
            t = res['tests'] or {'failed': 0, 'errors': 0, 'run': 0}
            res['tests'] = {'failed': t['failed'] + f, 'errors': t['errors'] + e, 'run': t['run'] + n}
            continue
        mf = MODULE_FAIL.search(msg)
        if mf:
            res['test_modules_failed'].append(mf.group(1))
            continue
        if 'Chrome executable not found' in msg:
            res['browser_tests_skipped'] += 1
        if 'Failed to initialize database' in msg:
            res['db_init_failed'] = True
        if level == 'CRITICAL':
            res['critical'] += 1
        elif level == 'ERROR':
            res['error'] += 1
            if len(res['first_errors']) < 5:
                res['first_errors'].append(f'{logger}: {msg[:200]}')
        elif level == 'WARNING':
            res['warning'] += 1
    return res


if __name__ == '__main__':
    print(json.dumps(parse(sys.argv[1]), ensure_ascii=False))
