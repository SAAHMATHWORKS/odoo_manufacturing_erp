# 01 — Socle Odoo 19.0 Community

Relevé du 9 novembre 2026. Décision de version : **DEC-001 (validée)** — Odoo 19.0 Community exclusivement.

## 1. Version figée

| Élément | Valeur | Statut | Source |
|---|---|---|---|
| Dépôt | `https://github.com/odoo/odoo.git`, branche `19.0` | Confirmé | — |
| Commit figé | `a27a1090b519a01bf308f0c43c5dd4254458a5ae` (9 nov. 2026) | Confirmé | `repos.yaml` |
| Version déclarée | `version_info = (19, 0, 0, FINAL, 0, '')` | Confirmé | `odoo/release.py` l.15 |
| Licence | LGPL-3 (tous les modules Community audités) | Confirmé | manifestes |
| Modules dans `addons/` | 642 | Confirmé | arborescence au commit figé |

## 2. Prérequis techniques

| Composant | Exigence | Statut | Source |
|---|---|---|---|
| Python | **3.10 minimum, 3.14 maximum** | Confirmé | `odoo/release.py` : `MIN_PY_VERSION = (3, 10)`, `MAX_PY_VERSION = (3, 14)` |
| PostgreSQL | **13 minimum** | Confirmé | `odoo/release.py` : `MIN_PG_VERSION = 13` |
| Distributions de référence | Versions des paquets `python3-*` d'**Ubuntu 24.04** et **Debian 12** | Confirmé | en-tête de `requirements.txt` |
| Dépendances Python | `requirements.txt` (versions selon la version de Python) | Confirmé | `requirements.txt` |

### Recommandation (à valider : P-002)

| Composant | Choix recommandé | Justification |
|---|---|---|
| Système | **Ubuntu Server 24.04 LTS** | Distribution de référence d'Odoo 19 ; image Docker officielle basée sur `ubuntu:noble` |
| Python | **3.12** (celui d'Ubuntu 24.04) | Versions de dépendances officiellement supportées |
| PostgreSQL | **16** | Version d'Ubuntu 24.04, ≥ 13 exigé |

## 3. Environnement de test Docker

Composition (fichiers `docker/`, orchestrés par `scripts/test_install.sh`) :

| Couche | Contenu | Figé par |
|---|---|---|
| Image de base | Dockerfile officiel `odoo/docker`, dossier `19.0` : base `ubuntu:noble` (Python 3.12), client PostgreSQL, wkhtmltopdf, paquet Odoo nightly `19.0.20261102` vérifié par SHA-1 (lignes 1, 53-63, 75-79) | commit `f900094eb7492968332868d686caf22b966592ca` |
| Image de test | `docker/Dockerfile.test` : base + `docker/requirements-extra.txt` (`openupgradelib==3.13.7`) | versions dans `requirements-extra.txt` ; `pip freeze` enregistré à chaque campagne |
| Code Odoo exécuté | `src/odoo`, monté en lecture seule | commit `a27a1090…` (`repos.yaml`) |
| Modules OCA | `src/oca/<dépôt>`, montés en lecture seule | commits de `repos.yaml` |
| PostgreSQL | `postgres:16` | **digest à figer** (§3.1) |

Sécurité de l'environnement de test : projet Docker au nom fixe `fayadort-test` ; **aucun port publié**
(la base n'est joignable que depuis le réseau interne du projet) ; `test_install.sh` refuse de démarrer si
la configuration Odoo pointe vers un autre serveur que le service `db` du projet, ou si un port est publié.

Limite de reproductibilité (proposition P-010) : l'image de base est reconstruite à partir d'un Dockerfile
figé, mais celui-ci part de `ubuntu:noble` et de paquets système dont les versions évoluent ; deux
constructions à plusieurs semaines d'intervalle peuvent différer légèrement. Pour l'environnement de test
de la phase 0, c'est acceptable ; pour la production, il faudra figer l'image construite (registre privé ou
digest) — à traiter en 0-C.

### 3.1 Figer l'image PostgreSQL par digest (procédure)

Une étiquette comme `postgres:16` désigne la dernière version 16.x publiée : elle change dans le temps.
Le **digest** (`sha256:…`) désigne une image précise et immuable.

1. Récupérer les sources (si ce n'est pas déjà fait) : `python3 scripts/fetch_repos.py`
2. Figer l'image : `bash scripts/pin_postgres_digest.sh`
   - télécharge `postgres:16`, lit son digest de dépôt (index multi-architecture, valable sur toute
     machine) et remplace dans `docker/docker-compose.test.yml` la ligne `image: postgres:16` par
     `image: postgres:16@sha256:<digest>` ;
   - affiche la différence et l'image résultante (`docker compose config --images`) ;
   - si l'image est déjà figée, ne modifie rien et signale seulement si un digest plus récent existe
     (`--update` pour changer, décision à tracer).
3. Vérifier la différence, supprimer `docker/docker-compose.test.yml.bak`, puis committer :
   `git add docker/docker-compose.test.yml && git commit -m "Fige l'image PostgreSQL de test par digest"`
4. Reporter le digest dans `DECISIONS.md` (P-002).

Contrôle : chaque campagne de `test_install.sh` indique dans `RESULTS.md` si l'image est figée et le
digest réellement exécuté.

## 4. Fonctions Enterprise absentes du socle (confirmé par absence dans `addons/`)

`mrp_workorder` (écran atelier Shop Floor), `quality`, `quality_control`, `quality_mrp`,
`stock_barcode` (application de scan), `mrp_mps` (plan directeur de production), `mrp_plm`,
`planning`, `documents`, `sign`, `account_accountant`, `account_reports`, `account_asset`,
`account_budget`, `hr_payroll`, `web_studio`, `iot`, `sale_subscription`.

Les solutions de remplacement (OCA ou développement) sont indiquées dans `02` et `03`.

## 5. Points d'attention

1. **Contrats RH** : il n'existe plus de module `hr_contract` en 19.0. Les données
   contractuelles (dates, type de contrat, salaire) sont portées par le modèle `hr.version`
   du module `hr` (`addons/hr/models/hr_version.py`). Le module OCA `payroll` 19.0 hérite
   bien de `hr.version` : il a été réellement migré, pas seulement renommé.
2. **Politique de support d'Odoo** : la durée de maintenance de la 19.0 n'a pas été vérifiée
   sur une source officielle dans le cadre de cet audit. À confirmer en 0-C pour planifier
   une éventuelle migration future (hors périmètre actuel, DEC-001).
3. **Montées de version du commit Odoo** : la branche 19.0 reçoit des correctifs quotidiens.
   Le commit figé ne sera avancé que par décision documentée (sécurité, correctif utile),
   avec relance des tests.
