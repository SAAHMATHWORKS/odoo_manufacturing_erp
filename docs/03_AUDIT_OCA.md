# 03 — Audit des modules OCA (branche 19.0)

Relevé du 9 novembre 2026, revu le même jour (revue corrective 0-A). Dépôts figés dans `repos.yaml`.
Audit **statique** uniquement (voir `00` §3) : aucun module n'a encore été installé.

## 1. Catégories et effectifs

La catégorie de chaque module est définie **à un seul endroit** : `scripts/audit/candidates.txt`.
L'audit statique et le plan de tests lisent ce même fichier.

| Catégorie | Signification | Natifs | OCA |
|---|---|---|---|
| Retenu (à tester) | Candidat retenu, soumis aux tests de **validation** (groupes V-*) | 28 | 37 |
| À évaluer | Testé à part pour information (groupes E-*). **Un succès ne vaut pas validation.** | — | 4 |
| Piste séparée | Chantier distinct, testé isolément (groupe S-*) | — | 1 |
| Différé | Non testé ; non figé ou reporté | 1 | 5 |
| Rejeté | Exclu, raison au §3 | — | 2 |

## 2. Résultat de l'audit statique

Vérifications appliquées **à chaque module et à toute sa chaîne de dépendances** (détail dans
`scripts/audit/static_audit.py`) : présence et unicité du nom, `installable`, version 19.0.x,
dépendances Odoo résolues dans Odoo 19 Community + OCA figé, **dépendances externes Python et
binaires comparées à l'environnement Odoo standard** (`requirements.txt` d'Odoo), existence des
fichiers déclarés, syntaxe Python (grammaire 3.10), XML bien formé, fichiers de tests.

| Statut | Retenu | À évaluer | Piste séparée | Différé | Rejeté |
|---|---|---|---|---|---|
| STATIQUE_OK | 64 | 4 | 1 | 4 | 2 |
| DÉPENDANCE EXTERNE À FOURNIR | **1** | — | — | — | — |
| BLOQUANT | 0 | 0 | 0 | 0 | 0 |
| Absent (dépôt non figé) | — | — | — | 2 | — |

**Correction par rapport à la première version de l'audit** : `hr_holidays_public` avait été classé
« statique OK » à tort. Sa dépendance `calendar_public_holiday` (OCA/calendar) exige la bibliothèque
Python **`openupgradelib`** à l'installation (utilisée dans `hooks.py`), absente de l'image officielle
d'Odoo. Elle est désormais ajoutée à l'image de test (`docker/requirements-extra.txt`, version 3.13.7)
— proposition P-009.

Avertissement non bloquant : `account_asset_management` importe `openupgradelib` uniquement dans un
script de migration (`migrations/19.0.1.0.4/pre-migrate.py`), exécuté lors d'une mise à jour depuis une
version antérieure, pas lors d'une installation neuve.

## 3. Fiches des modules OCA

| Catégorie | Domaine | Module | Dépôt @ commit | Version | Licence | Maturité déclarée | Fichiers de tests | Audit statique | Remarques |
|---|---|---|---|---|---|---|---|---|---|
| Retenu (à tester) | Achats | `purchase_request` | purchase-workflow @ `8c86d5a2bd14` | 19.0.1.0.4 | LGPL-3 | non renseigné | 4 | OK |  |
| Retenu (à tester) | Achats | `base_tier_validation` | tier-validation @ `4f16809993cc` | 19.0.1.6.0 | AGPL-3 | Mature | 3 | OK |  |
| Retenu (à tester) | Achats | `purchase_tier_validation` | tier-validation @ `4f16809993cc` | 19.0.1.1.0 | AGPL-3 | non renseigné | 2 | OK |  |
| Retenu (à tester) | Achats | `purchase_request_tier_validation` | tier-validation @ `4f16809993cc` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Stocks | `stock_no_negative` | stock-logistics-workflow @ `bb03506a306e` | 19.0.1.0.1 | AGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Stocks | `scrap_reason_code` | stock-logistics-workflow @ `bb03506a306e` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Stocks | `stock_analytic` | account-analytic @ `f841015584f8` | 19.0.1.0.0 | AGPL-3 | non renseigné | 2 | OK |  |
| Retenu (à tester) | Fabrication | `mrp_stock_analytic` | account-analytic @ `f841015584f8` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Fabrication | `mrp_bom_hierarchy` | manufacture @ `ca0a97252048` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Fabrication | `mrp_warehouse_calendar` | manufacture @ `ca0a97252048` | 19.0.1.0.0 | LGPL-3 | Production/Stable | 1 | OK |  |
| Retenu (à tester) | Fabrication | `mrp_bom_tracking` | manufacture @ `ca0a97252048` | 19.0.1.1.0 | LGPL-3 | Production/Stable | 1 | OK |  |
| Retenu (à tester) | Qualite | `quality_control_oca` | manufacture @ `ca0a97252048` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK | incomplet seul (déclencheurs 18.0 non migrés) |
| Retenu (à tester) | Maintenance | `maintenance_plan` | maintenance @ `24ae3dfb690e` | 19.0.1.0.2 | AGPL-3 | non renseigné | 3 | OK |  |
| Retenu (à tester) | Maintenance | `maintenance_equipment_status` | maintenance @ `24ae3dfb690e` | 19.0.1.0.0 | LGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Maintenance | `maintenance_request_purchase` | maintenance @ `24ae3dfb690e` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Maintenance | `maintenance_product` | maintenance @ `24ae3dfb690e` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Planification | `stock_demand_estimate` | stock-logistics-warehouse @ `e53710de6053` | 19.0.1.1.0 | LGPL-3 | Production/Stable | 1 | OK |  |
| Retenu (à tester) | Planification | `mrp_multi_level` | manufacture @ `ca0a97252048` | 19.0.1.0.5 | LGPL-3 | Production/Stable | 1 | OK |  |
| Retenu (à tester) | Planification | `mrp_multi_level_estimate` | manufacture @ `ca0a97252048` | 19.0.1.0.0 | LGPL-3 | Production/Stable | 1 | OK |  |
| Retenu (à tester) | Comptabilite | `account_financial_report` | account-financial-reporting @ `f48b4ea777c4` | 19.0.0.0.26 | AGPL-3 | non renseigné | 7 | OK |  |
| Retenu (à tester) | Comptabilite | `account_tax_balance` | account-financial-reporting @ `f48b4ea777c4` | 19.0.1.0.3 | AGPL-3 | Mature | 1 | OK |  |
| Retenu (à tester) | Comptabilite | `partner_statement` | account-financial-reporting @ `f48b4ea777c4` | 19.0.1.1.0 | AGPL-3 | non renseigné | 9 | OK |  |
| Retenu (à tester) | Comptabilite | `mis_builder` | mis-builder @ `cd4938376f66` | 19.0.1.2.2 | AGPL-3 | Production/Stable | 16 | OK |  |
| Retenu (à tester) | Comptabilite | `mis_builder_budget` | mis-builder @ `cd4938376f66` | 19.0.1.0.1 | AGPL-3 | Production/Stable | 3 | OK |  |
| Retenu (à tester) | Comptabilite | `account_reconcile_oca` | account-reconcile @ `81321938a1a9` | 19.0.1.1.2 | AGPL-3 | non renseigné | 3 | OK |  |
| Retenu (à tester) | Comptabilite | `account_statement_base` | account-reconcile @ `81321938a1a9` | 19.0.1.0.1 | LGPL-3 | Mature | 1 | OK |  |
| Retenu (à tester) | Comptabilite | `account_asset_management` | account-financial-tools @ `b3c7c0be3708` | 19.0.1.0.4 | AGPL-3 | Mature | 2 | OK |  |
| À évaluer | Comptabilite | `account_fiscal_year` | account-financial-tools @ `b3c7c0be3708` | 19.0.1.0.0 | AGPL-3 | Production/Stable | 1 | OK | conflit de droits avec `mis_builder` (campagne 1) ; utilité à confirmer (exercice civil OHADA) |
| Retenu (à tester) | Comptabilite | `account_lock_date_update` | account-financial-tools @ `b3c7c0be3708` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Comptabilite | `account_analytic_required` | account-analytic @ `f841015584f8` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Comptabilite | `purchase_analytic` | account-analytic @ `f841015584f8` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | RH | `hr_holidays_public` | hr-holidays @ `abd1ff286b50` | 19.0.1.0.4 | AGPL-3 | non renseigné | 2 | Dépendance externe à fournir | python:openupgradelib (requis par calendar_public_holiday) |
| Retenu (à tester) | RH | `hr_attendance_reason` | hr-attendance @ `c5964bd1b322` | 19.0.1.0.0 | LGPL-3 | non renseigné | 1 | OK |  |
| Retenu (à tester) | Transverse | `auditlog` | server-tools @ `a828058ebaca` | 19.0.2.0.2 | AGPL-3 | non renseigné | 6 | OK |  |
| Retenu (à tester) | Transverse | `report_xlsx` | reporting-engine @ `2e3240211960` | 19.0.1.0.3 | AGPL-3 | Mature | 1 | OK |  |
| Retenu (à tester) | Transverse | `date_range` | server-ux @ `af19073dc864` | 19.0.1.0.2 | LGPL-3 | Mature | 4 | OK |  |
| Retenu (à tester) | Transverse | `web_responsive` | web @ `80f85e9bc628` | 19.0.1.1.1 | LGPL-3 | Production/Stable | 2 | OK |  |
| Retenu (à tester) | Transverse | `web_environment_ribbon` | web @ `80f85e9bc628` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK |  |
| À évaluer | Importations | `stock_landed_costs_purchase_auto` | stock-logistics-workflow @ `bb03506a306e` | 19.0.1.0.2 | AGPL-3 | non renseigné | 1 | OK | risque de doublon avec fay_import (groupage) |
| À évaluer | Stocks | `stock_secondary_unit` | stock-logistics-warehouse @ `e53710de6053` | 19.0.1.0.1 | AGPL-3 | Production/Stable | 1 | OK | double unité pièces / m³ : dépend des réponses Fayadort |
| À évaluer | Comptabilite | `mis_builder_cash_flow` | account-financial-reporting @ `f48b4ea777c4` | 19.0.1.0.0 | AGPL-3 | Beta | 1 | OK | statut Beta |
| Piste séparée | RH | `payroll` | payroll @ `2eca6caafc74` | 19.0.1.0.2 | LGPL-3 | non renseigné | 6 | OK | règles camerounaises à écrire et faire valider |
| Différé | Stocks | `stock_inventory` | stock-logistics-warehouse @ `e53710de6053` | 19.0.1.1.0 | LGPL-3 | Beta | 1 | OK |  |
| Différé | Stocks | `stock_inventory_discrepancy` | stock-logistics-warehouse @ `e53710de6053` | 19.0.1.0.1 | AGPL-3 | non renseigné | 1 | OK |  |
| Différé | Stocks | `stock_inventory_justification` | stock-logistics-warehouse @ `e53710de6053` | 19.0.1.1.0 | AGPL-3 | non renseigné | 1 | OK |  |
| Différé | Transverse | `queue_job` | non figé | — | — | — | — | non audité | dépendance openupgradelib ; dépôt non figé |
| Différé | Transverse | `dms` | non figé | — | — | — | — | non audité | dépôt non figé |
| Rejeté | Achats | `purchase_landed_cost` | purchase-workflow @ `8c86d5a2bd14` | 19.0.1.0.0 | AGPL-3 | non renseigné | 1 | OK | système de frais d'approche parallèle au natif |
| Rejeté | Fabrication | `mrp_production_back_to_draft` | manufacture @ `ca0a97252048` | 19.0.1.0.1 | AGPL-3 | non renseigné | 1 | OK | contraire à la correction traçable |

« Maturité déclarée » = champ `development_status` du manifeste ; « non renseigné » est courant.

### Justification des décisions particulières

| Module | Décision | Raison |
|---|---|---|
| `purchase_landed_cost` | **Rejeté** | Système de répartition des frais **parallèle** à `stock_landed_costs` natif (sa description le présente comme une alternative au module officiel). Contraire à la règle « une seule source de vérité ». |
| `mrp_production_back_to_draft` | **Rejeté (provisoire)** | Remet en brouillon un ordre confirmé ou annulé. Contraire au principe de correction traçable des opérations validées. |
| `stock_landed_costs_purchase_auto` | **À évaluer** | Crée automatiquement un frais d'approche vide rattaché à **une** commande et à sa réception. Un dossier d'importation pourra regrouper **plusieurs** commandes (groupage) : risque de doublon avec `fay_import`. Décision en 0-B. |
| `stock_secondary_unit` | **À évaluer** | Double unité (bloc en pièces et en m³, rouleau en pièces et en mètres). Dépend des réponses de Fayadort (0-B). |
| `mis_builder_cash_flow` | **À évaluer** | Statut « Beta ». |
| `account_fiscal_year` | **À évaluer** (était « retenu ») | Campagne 1 : avec ce module installé, un utilisateur sans droits comptables complets qui calcule un rapport `mis_builder` obtient une erreur d'accès. Cause lue dans le code : le module surcharge `res.company.compute_fiscalyear_dates` (`models/res_company.py`) et recherche `account.fiscal.year` sans élévation de droits, alors que ses droits de lecture sont réservés aux groupes comptables (`security/ir.model.access.csv`). Par ailleurs, l'exercice OHADA correspond en principe à l'année civile, que le paramétrage natif de la société (dernier jour et mois de l'exercice) gère déjà : utilité à confirmer avec l'expert-comptable. Proposition P-012. |
| `quality_control_oca` | **Retenu (à tester), incomplet seul** | Infrastructure générique de contrôle. Les déclencheurs sur réceptions (`quality_control_stock_oca`) et fabrications (`quality_control_mrp_oca`) existent en 18.0, **pas encore en 19.0** (vérifié dans la branche 18.0 de OCA/manufacture). Proposition P-004. |
| `payroll` | **Piste séparée** | Moteur de paie générique, migré sur `hr.version` (vérifié). Son README indique un rétroportage du code d'Odoo SA, hors accord de contribution OCA. Les règles camerounaises restent entièrement à écrire et à faire valider. |
| `stock_inventory*`, `queue_job`, `dms` | **Différés** | Pas de besoin en tranche 1 ; `queue_job` exige en plus `openupgradelib`. |

## 4. Développements spécifiques confirmés nécessaires

Aucun module Community ou OCA 19.0 ne couvre : l'interface atelier et le scan (`fay_shopfloor`) ;
la cure, la libération et la découpe avec répartition du coût au volume (`fay_foam`) ; le dossier
d'importation (`fay_import`) ; les déclencheurs qualité (portage ou `fay_quality`) ; le rapport d'écarts
standard / réel (`fay_mrp`) ; les états financiers SYSCOHADA (paramétrage `mis_builder`) ; les règles
de paie camerounaise (sur `payroll`).

## 5. Licences

### 5.1 Registre

| Licence | Modules audités | Détail |
|---|---|---|
| LGPL-3 | 42 | 29 natifs Odoo ; 13 OCA : `purchase_request`, `stock_inventory`, `stock_demand_estimate`, `mrp_multi_level`, `mrp_multi_level_estimate`, `mrp_warehouse_calendar`, `mrp_bom_tracking`, `maintenance_equipment_status`, `account_statement_base`, `hr_attendance_reason`, `payroll`, `date_range`, `web_responsive` |
| AGPL-3 | 34 | tous les autres modules OCA audités (colonne « Licence » du §3) |
| OPL (propriétaire) | **0** | Aucun ; tout module OPL est exclu sans autorisation explicite |
| Bibliothèque Python ajoutée | 1 | `openupgradelib` 3.13.7 — AGPL-3 (déclarée dans le `setup.py` du projet) |

Les chiffres incluent les modules différés et rejetés audités. Licence de `payroll` : LGPL-3, avec la
particularité de provenance indiquée au §3.

### 5.2 Ce que l'AGPL-3 impose, et ce qu'elle n'impose pas

> Analyse technique d'un non-juriste, destinée à préparer une décision. Elle ne remplace pas l'avis
> d'un avocat (droit de la propriété intellectuelle, Cameroun / OHADA, et droit des pays où un logiciel
> serait distribué).

| Situation | Obligation AGPL-3 | Application à Fayadort |
|---|---|---|
| Utiliser des modules AGPL non modifiés, en interne | Aucune obligation de publication | Cas actuel |
| **Modifier** un module AGPL et le faire utiliser **à distance** (réseau) | Art. 13 : offrir aux utilisateurs distants le code source de la version modifiée | Évité par la règle « jamais de modification du code OCA » ; les utilisateurs seraient de toute façon les employés |
| **Distribuer** (« convoyer ») un module AGPL, modifié ou non | Fournir le code source sous AGPL-3, sans restriction supplémentaire | Seulement en cas de cession ou de vente à un tiers |
| Distribuer un module `fay_*` qui **dépend** d'un module AGPL | **Question ouverte** : un module qui hérite des classes d'un module AGPL est-il une œuvre dérivée ? Les avis divergent ; l'usage répandu dans l'écosystème OCA est de publier ces modules sous une licence compatible AGPL | À trancher par un juriste **avant** toute distribution |
| Distribuer un module `fay_*` qui ne dépend que de modules LGPL | La LGPL permet une licence différente, y compris propriétaire, pour le module | Possible si la conception évite les dépendances AGPL |

### 5.3 Dépendances entre modules : ce qu'il faudra mesurer

La licence d'un module `fay_*` ne peut être raisonnée qu'à partir de **ses dépendances réelles**,
directes et indirectes. `scripts/audit/static_audit.py` calcule déjà la chaîne de dépendances
(`closure`) : il pourra produire, pour chaque futur module `fay_*`, la liste des modules AGPL qu'il
entraîne. Exemples prévisibles, **à confirmer** quand les modules existeront :

| Futur module | Dépendances AGPL probables |
|---|---|
| `fay_purchase` | `base_tier_validation`, `purchase_tier_validation` |
| `fay_quality` | `quality_control_oca` |
| `fay_dashboard` | `mis_builder`, `report_xlsx` |
| `fay_foam`, `fay_import`, `fay_mrp` | aucune a priori (natif LGPL), sauf choix contraire en 0-B |

### 5.4 Conséquences possibles d'une commercialisation future

1. **Vente ou licence des modules `fay_*` à un autre industriel** (installation chez lui) : c'est une
   distribution. Pour les modules dépendant de modules AGPL, une licence propriétaire serait juridiquement
   risquée ; le modèle économique porterait plutôt sur le service (intégration, maintenance, formation).
2. **Hébergement de l'ERP pour des tiers (SaaS)** : l'article 13 s'appliquerait à toute version modifiée
   d'un programme AGPL utilisée à distance par ces clients.
3. **Modules conçus pour être vendus** : les isoler dès la conception pour qu'ils ne dépendent que de
   modules LGPL, ce qui laisse le choix de la licence.
4. **Cession de l'entreprise ou de l'ERP** : à examiner avec le juriste au cas par cas.

La décision de licence des modules `fay_*` est la proposition **P-007** (`DECISIONS.md`) : elle doit être
prise avant la création du premier module (le manifeste Odoo exige une clé `license`) et, en cas
d'intention de commercialiser, après un avis juridique.

## 6. Tests

| Type de test | État |
|---|---|
| Audit statique (manifeste, chaîne de dépendances, dépendances externes, fichiers, syntaxe, XML) | **Exécuté** — aucun BLOQUANT ; 1 dépendance externe à fournir (traitée) |
| Auto-test de l'audit statique sur 10 modules volontairement défectueux | **Exécuté** — les 7 types de défauts détectés |
| Récupération des dépôts aux commits figés (`fetch_repos.py --oca-only`) | **Exécuté** — 20/20 au bon commit |
| Logique de `test_install.sh` (plan, bases, comptage, garde-fous) avec un Docker simulé | **Exécuté** — conforme ; ne remplace pas une exécution réelle |
| Installation par groupe, tests OCA, installation de l'ensemble | Campagne 1 exécutée le 9 nov. 2026 — **résultats non probants** (§6.1) ; campagne 2 à lancer |

Plan de tests (généré par `scripts/test_plan.py`, couverture vérifiée automatiquement) : 11 groupes
V-domaine + V-ENSEMBLE (65 modules retenus) ; 4 groupes E-module + E-ENSEMBLE (69) ; 1 groupe S-payroll.

### 6.1 Campagne 1 (9 nov. 2026, 20261109_133810) — résultats non probants

**Résultats bruts** : les 66 modules alors retenus se sont installés par domaine et ensemble, sans
erreur ; 9 groupes de validation sur 10 avec tests OCA sans échec ; **V-Comptabilite : 278 tests,
1 échec, 3 erreurs** ; E-stock_landed_costs_purchase_auto : 5 tests, 5 erreurs ; autres groupes E/S sans échec.

**Deux défauts de l'environnement de test invalident la campagne** (corrigés) :

1. **Code Odoo mélangé.** En 19.0, `odoo` et `odoo.addons` sont des paquets d'espace de noms (pas de
   `__init__.py`) : tous les dossiers `odoo/` du chemin Python sont fusionnés. Le paquet Odoo nightly
   préinstallé dans l'image officielle (`/usr/lib/python3/dist-packages/odoo`) passait devant
   `src/odoo` pour les modules standard (visible dans les traces : `…/dist-packages/odoo/addons/purchase/…`).
   Le cœur venait du commit figé, les modules standard du paquet du 2 nov. Correction : suppression de ce
   paquet dans `docker/Dockerfile.test` ; contrôle avant campagne et dans chaque journal (`addons paths`).
2. **Données de démonstration non chargées.** La détection de `--with-demo` échouait (`grep -q` dans un
   tube avec `pipefail`). Les tests OCA supposent les données de démonstration. Correction : détection
   fiable ; option rendue obligatoire sauf `--no-demo`.

**Analyse des 9 erreurs et échecs** (journaux transmis le 9 nov.) :

| Test | Cause | Nature |
|---|---|---|
| `stock_landed_costs_purchase_auto` (5 erreurs) | « no default journal is configured for landed costs » : base sans plan comptable ni journaux | Environnement (démo absente). **Enseignement fonctionnel** : ce module bloque la confirmation de toute commande d'achat tant qu'un journal de frais d'approche n'est pas configuré |
| `partner_statement` (2 erreurs) | « No journal could be found … for any of those types: sale » : base sans journaux | Environnement (démo absente) |
| `mis_builder.test_unprivileged` (1 erreur) | Erreur d'accès sur `account.fiscal.year` via `account_fiscal_year` | **Réelle** : interaction entre deux modules OCA (P-012) |
| `mis_builder.test_drilldown_action_name_with_account` (1 échec) | Nom d'action différent de celui attendu ; l'assertion n'affiche pas les valeurs | Indéterminée : à revoir après la campagne 2 |

## 7. Commits figés (`repos.yaml`)

| Dépôt OCA | Commit | Date |
|---|---|---|
| tier-validation | `4f16809993cc4df04853534191867da7713970c1` | 2026-11-09 |
| purchase-workflow | `8c86d5a2bd1430f124e71005f0b19d607643ce13` | 2026-11-08 |
| stock-logistics-workflow | `bb03506a306e5c81812361db8c682f60c4ec165a` | 2026-11-08 |
| stock-logistics-warehouse | `e53710de6053e9fd13b13dc855be944b085f6c8c` | 2026-11-05 |
| product-attribute | `01799382ea09d2bc1c7a525f0e6559f48f3c5a4c` | 2026-11-07 |
| manufacture | `ca0a97252048a47206a27c3807d77620e2595418` | 2026-11-03 |
| maintenance | `24ae3dfb690e0c2240484de8a08dfe61a470202a` | 2026-11-03 |
| account-analytic | `f841015584f829c50a2cd5584fb50e6bb3a4a4c6` | 2026-11-08 |
| account-financial-reporting | `f48b4ea777c444256aa1c215ec3117d604b5feff` | 2026-10-21 |
| mis-builder | `cd4938376f66cd780c576f553df70b7570030a3a` | 2026-11-08 |
| account-reconcile | `81321938a1a9bfbcff8982891f2fb9e88d816913` | 2026-11-08 |
| account-financial-tools | `b3c7c0be3708abaabeb668978a74839cd59396c4` | 2026-11-09 |
| hr-holidays | `abd1ff286b505d95f8fd6219adbe1a711f1a3ba7` | 2026-10-15 |
| calendar | `a0f55db96b9f5e1d7889b1b50dc0c3e5dd677baf` | 2026-08-17 |
| hr-attendance | `c5964bd1b322199e616eb4a627577a0fcc57bc45` | 2026-10-24 |
| payroll | `2eca6caafc74d4a592ee0ca75606b4c6e3ce75b9` | 2026-11-03 |
| server-tools | `a828058ebaca96a2320f8eb5172d86d10a8409e8` | 2026-11-03 |
| server-ux | `af19073dc86443bad8590811649a54172a81a1ef` | 2026-11-06 |
| reporting-engine | `2e3240211960f34bf6e07c1f0e849aaf249a6dfc` | 2026-11-06 |
| web | `80f85e9bc62858b36f1c18471afba48960305a72` | 2026-11-03 |
