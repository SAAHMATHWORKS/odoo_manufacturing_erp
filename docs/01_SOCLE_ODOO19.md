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

## 3. Environnement d'exécution Docker

- **Image d'exécution** : construite depuis le Dockerfile officiel `odoo/docker`, dossier `19.0`,
  figé au commit `f900094eb7492968332868d686caf22b966592ca` (2 nov. 2026). Contenu constaté :
  base `ubuntu:noble`, client PostgreSQL, paquet Odoo nightly `19.0.20261102` vérifié par SHA-1.
  Source : `19.0/Dockerfile`, lignes 1, 53-63, 75-79.
- **Code exécuté** : celui de `src/odoo` au commit figé (monté en lecture seule), afin que le
  code testé corresponde exactement à `repos.yaml`. L'image ne sert qu'à fournir les dépendances
  système et Python de la même branche.
- **PostgreSQL** : image `postgres:16`, **à figer par digest** (`postgres:16@sha256:…`) dès le
  premier téléchargement ; `scripts/test_install.sh` affiche ce digest.

> Pourquoi ne pas simplement utiliser l'étiquette `odoo:19.0` ? Parce qu'elle change à chaque
> publication nocturne : deux installations à une semaine d'intervalle n'exécuteraient pas le
> même code. Le prompt maître interdit les étiquettes flottantes.

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
