# 03 — Audit des modules OCA (branche 19.0)

Relevé du 9 novembre 2026. Dépôts figés dans `repos.yaml`. Audit **statique** (voir `00` §2-3) :
aucun module n'a encore été installé. « Retenu (à tester) » signifie : candidat sérieux,
**à confirmer par `scripts/test_install.sh`** avant validation définitive.

## 1. Résultat global

- 49 modules OCA examinés, répartis dans 20 dépôts figés.
- **47 statiquement OK** : manifeste en version 19.0, `installable`, toutes les dépendances
  résolues dans Odoo 19 Community + OCA figé (aucune dépendance Enterprise), Python compilable,
  XML valide, dossier de tests présent pour chacun.
- 2 modules **différés et non figés** : `queue_job` (dépendance Python `openupgradelib` absente
  de l'image officielle ; pas de besoin immédiat), `dms` (gestion documentaire ; les pièces jointes
  natives suffisent pour la tranche 1).
- Deux dépendances indirectes ont imposé l'ajout de dépôts : `product_secondary_unit`
  (OCA/product-attribute) et `calendar_public_holiday` (OCA/calendar).

## 2. Fiches des modules

| Domaine | Module | Dépôt @ commit | Version | Licence | Maturité déclarée | Tests | Audit statique | Décision |
|---|---|---|---|---|---|---|---|---|
| Achats | `purchase_request` | purchase-workflow @ `8c86d5a2bd14` | 19.0.1.0.4 | LGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Achats | `base_tier_validation` | tier-validation @ `4f16809993cc` | 19.0.1.6.0 | AGPL-3 | Mature | oui | OK | RETENU (à tester) |
| Achats | `purchase_tier_validation` | tier-validation @ `4f16809993cc` | 19.0.1.1.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Achats | `purchase_request_tier_validation` | tier-validation @ `4f16809993cc` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Achats | `purchase_landed_cost` | purchase-workflow @ `8c86d5a2bd14` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | REJETÉ |
| Importations | `stock_landed_costs_purchase_auto` | stock-logistics-workflow @ `bb03506a306e` | 19.0.1.0.2 | AGPL-3 | non renseigné | oui | OK | À ÉVALUER |
| Stocks | `stock_no_negative` | stock-logistics-workflow @ `bb03506a306e` | 19.0.1.0.1 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Stocks | `scrap_reason_code` | stock-logistics-workflow @ `bb03506a306e` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Stocks | `stock_inventory` | stock-logistics-warehouse @ `e53710de6053` | 19.0.1.1.0 | LGPL-3 | Beta | oui | OK | DIFFÉRÉ |
| Stocks | `stock_inventory_discrepancy` | stock-logistics-warehouse @ `e53710de6053` | 19.0.1.0.1 | AGPL-3 | non renseigné | oui | OK | DIFFÉRÉ |
| Stocks | `stock_inventory_justification` | stock-logistics-warehouse @ `e53710de6053` | 19.0.1.1.0 | AGPL-3 | non renseigné | oui | OK | DIFFÉRÉ |
| Stocks | `stock_secondary_unit` | stock-logistics-warehouse @ `e53710de6053` | 19.0.1.0.1 | AGPL-3 | Production/Stable | oui | OK | À ÉVALUER (0-B) |
| Stocks | `stock_analytic` | account-analytic @ `f841015584f8` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Fabrication | `mrp_stock_analytic` | account-analytic @ `f841015584f8` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Fabrication | `mrp_bom_hierarchy` | manufacture @ `ca0a97252048` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Fabrication | `mrp_production_back_to_draft` | manufacture @ `ca0a97252048` | 19.0.1.0.1 | AGPL-3 | non renseigné | oui | OK | REJETÉ (provisoire) |
| Fabrication | `mrp_warehouse_calendar` | manufacture @ `ca0a97252048` | 19.0.1.0.0 | LGPL-3 | Production/Stable | oui | OK | RETENU (à tester) |
| Fabrication | `mrp_bom_tracking` | manufacture @ `ca0a97252048` | 19.0.1.1.0 | LGPL-3 | Production/Stable | oui | OK | RETENU (à tester) |
| Qualité | `quality_control_oca` | manufacture @ `ca0a97252048` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) — incomplet seul |
| Maintenance | `maintenance_plan` | maintenance @ `24ae3dfb690e` | 19.0.1.0.2 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Maintenance | `maintenance_equipment_status` | maintenance @ `24ae3dfb690e` | 19.0.1.0.0 | LGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Maintenance | `maintenance_request_purchase` | maintenance @ `24ae3dfb690e` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Maintenance | `maintenance_product` | maintenance @ `24ae3dfb690e` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Planification | `stock_demand_estimate` | stock-logistics-warehouse @ `e53710de6053` | 19.0.1.1.0 | LGPL-3 | Production/Stable | oui | OK | RETENU (à tester) |
| Planification | `mrp_multi_level` | manufacture @ `ca0a97252048` | 19.0.1.0.5 | LGPL-3 | Production/Stable | oui | OK | RETENU (à tester) |
| Planification | `mrp_multi_level_estimate` | manufacture @ `ca0a97252048` | 19.0.1.0.0 | LGPL-3 | Production/Stable | oui | OK | RETENU (à tester) |
| Comptabilité | `account_financial_report` | account-financial-reporting @ `f48b4ea777c4` | 19.0.0.0.26 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Comptabilité | `account_tax_balance` | account-financial-reporting @ `f48b4ea777c4` | 19.0.1.0.3 | AGPL-3 | Mature | oui | OK | RETENU (à tester) |
| Comptabilité | `partner_statement` | account-financial-reporting @ `f48b4ea777c4` | 19.0.1.1.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Comptabilité | `mis_builder` | mis-builder @ `cd4938376f66` | 19.0.1.2.2 | AGPL-3 | Production/Stable | oui | OK | RETENU (à tester) |
| Comptabilité | `mis_builder_budget` | mis-builder @ `cd4938376f66` | 19.0.1.0.1 | AGPL-3 | Production/Stable | oui | OK | RETENU (à tester) |
| Comptabilité | `mis_builder_cash_flow` | account-financial-reporting @ `f48b4ea777c4` | 19.0.1.0.0 | AGPL-3 | Beta | oui | OK | À ÉVALUER (Beta) |
| Comptabilité | `account_reconcile_oca` | account-reconcile @ `81321938a1a9` | 19.0.1.1.2 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Comptabilité | `account_statement_base` | account-reconcile @ `81321938a1a9` | 19.0.1.0.1 | LGPL-3 | Mature | oui | OK | RETENU (à tester) |
| Comptabilité | `account_asset_management` | account-financial-tools @ `b3c7c0be3708` | 19.0.1.0.4 | AGPL-3 | Mature | oui | OK | RETENU (à tester) |
| Comptabilité | `account_fiscal_year` | account-financial-tools @ `b3c7c0be3708` | 19.0.1.0.0 | AGPL-3 | Production/Stable | oui | OK | RETENU (à tester) |
| Comptabilité | `account_lock_date_update` | account-financial-tools @ `b3c7c0be3708` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Comptabilité | `account_analytic_required` | account-analytic @ `f841015584f8` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Comptabilité | `purchase_analytic` | account-analytic @ `f841015584f8` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| RH | `hr_holidays_public` | hr-holidays @ `abd1ff286b50` | 19.0.1.0.4 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| RH | `hr_attendance_reason` | hr-attendance @ `c5964bd1b322` | 19.0.1.0.0 | LGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| RH | `payroll` | payroll @ `2eca6caafc74` | 19.0.1.0.2 | LGPL-3 | non renseigné | oui | OK | PISTE SÉPARÉE (à tester) |
| Transverse | `auditlog` | server-tools @ `a828058ebaca` | 19.0.2.0.2 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Transverse | `queue_job` | — | — | — | — | — | non audité ici | DIFFÉRÉ (non figé) |
| Transverse | `report_xlsx` | reporting-engine @ `2e3240211960` | 19.0.1.0.3 | AGPL-3 | Mature | oui | OK | RETENU (à tester) |
| Transverse | `date_range` | server-ux @ `af19073dc864` | 19.0.1.0.2 | LGPL-3 | Mature | oui | OK | RETENU (à tester) |
| Transverse | `web_responsive` | web @ `80f85e9bc628` | 19.0.1.1.1 | LGPL-3 | Production/Stable | oui | OK | RETENU (à tester) |
| Transverse | `web_environment_ribbon` | web @ `80f85e9bc628` | 19.0.1.0.0 | AGPL-3 | non renseigné | oui | OK | RETENU (à tester) |
| Transverse | `dms` | — | — | — | — | — | non audité ici | DIFFÉRÉ (non figé) |

« Maturité déclarée » = champ `development_status` du manifeste ; « non renseigné » est courant
et ne préjuge pas de la qualité.

## 3. Justification des décisions particulières

| Module | Décision | Raison |
|---|---|---|
| `purchase_landed_cost` | **Rejeté** | Système de répartition des frais **parallèle** à `stock_landed_costs` natif (sa propre description le présente comme une alternative au module officiel). Contraire à la règle « une seule source de vérité ». |
| `mrp_production_back_to_draft` | **Rejeté (provisoire)** | Permet de remettre en brouillon un ordre confirmé ou annulé. Contraire au principe de correction traçable des opérations validées. À réexaminer seulement si un besoin précis apparaît. |
| `stock_landed_costs_purchase_auto` | **À évaluer** | Crée automatiquement un frais d'approche vide, rattaché à **une** commande et à sa réception. Le dossier d'importation pourra regrouper **plusieurs** commandes (groupage) : risque de doublon avec `fay_import`. Décision en 0-B. |
| `quality_control_oca` | **Retenu (à tester), incomplet seul** | Fournit l'infrastructure générique (tests, inspections, déclencheurs). Les modules qui déclenchent les contrôles **sur les réceptions** (`quality_control_stock_oca`) et **sur les fabrications** (`quality_control_mrp_oca`) existent en 18.0 mais **ne sont pas encore migrés en 19.0** (vérifié dans la branche 18.0 de OCA/manufacture). Options : porter ces deux modules en 19.0 (contribution OCA) ou écrire ces déclencheurs dans `fay_quality`. Proposition P-004. |
| `stock_secondary_unit` | **À évaluer (0-B)** | Double unité (ex. bloc en pièces et en m³, rouleau en pièces et en mètres). Utile si la mousse doit être suivie simultanément en nombre et en volume. Dépend des réponses de Fayadort. |
| `stock_inventory*` | **Différé** | Les ajustements d'inventaire natifs suffisent pour la tranche 1. |
| `mis_builder_cash_flow` | **À évaluer** | Statut « Beta ». |
| `payroll` | **Piste séparée** | Moteur de paie générique, **migré sur `hr.version`** (vérifié). Son README précise qu'il s'agit d'un rétroportage du code d'Odoo SA, hors accord de contribution OCA. Les règles camerounaises (CNPS, IRPP, CAC, etc.) restent entièrement à écrire et à faire valider. |

## 4. Développements spécifiques confirmés nécessaires

Aucun module Community ou OCA 19.0 ne couvre :

1. l'interface atelier sur tablette et le scan (`fay_shopfloor`) ;
2. la cure, la libération et la découpe avec répartition du coût au volume (`fay_foam`) ;
3. le dossier d'importation avec jalons, budget et génération des frais d'approche (`fay_import`) ;
4. les déclencheurs qualité sur réceptions et fabrications (portage ou `fay_quality`) ;
5. le rapport d'écarts standard / réel par ordre de fabrication (`fay_mrp`) ;
6. les états financiers SYSCOHADA (paramétrage `mis_builder`, pas de code Python a priori) ;
7. les règles de paie camerounaise (sur `payroll`).

## 5. Registre des licences

| Licence | Nombre de modules audités | Modules |
|---|---|---|
| LGPL-3 | 42 (dont tous les modules natifs) | natifs ; `purchase_request`, `stock_inventory`, `stock_demand_estimate`, `mrp_multi_level`, `mrp_multi_level_estimate`, `mrp_warehouse_calendar`, `mrp_bom_tracking`, `maintenance_equipment_status`, `account_statement_base`, `hr_attendance_reason`, `payroll`, `date_range`, `web_responsive` |
| AGPL-3 | 34 | tous les autres modules OCA retenus, dont `base_tier_validation`, `quality_control_oca`, `maintenance_plan`, `account_financial_report`, `mis_builder`, `account_reconcile_oca`, `account_asset_management`, `auditlog`, `report_xlsx` |
| OPL (propriétaire, Odoo Apps Store) | **0** | Aucun. Tout module OPL est exclu sans autorisation explicite. |

Le détail module par module figure dans le tableau du §2 (colonne « Licence ») et dans
`scripts/audit/static_audit.py` (sortie JSON).

### Conséquences pratiques de l'AGPL-3 (à valider juridiquement si nécessaire)

- L'AGPL ajoute à la GPL une obligation **réseau** : si un programme AGPL **modifié** est utilisé
  par des personnes à travers un réseau, ces utilisateurs doivent pouvoir obtenir le code source
  de la version modifiée.
- Pour Fayadort, utilisateur interne de son propre ERP, l'impact pratique est **faible** :
  les utilisateurs sont ses employés, et la règle du projet est de **ne jamais modifier** le code
  OCA (extensions par héritage dans des modules `fay_*` séparés).
- La question devient réelle si Fayadort **distribuait ou commercialisait** ses modules `fay_*`
  (à un autre industriel, par exemple). Il faudrait alors une analyse juridique, les modules
  dépendant de modules AGPL.
- La licence des modules `fay_*` est à décider : proposition P-007.

## 6. Tests

| Type de test | État |
|---|---|
| Audit statique (manifeste, dépendances, Python, XML) | **Exécuté** — 47/47 OCA OK, 29/29 natifs OK |
| Récupération des dépôts aux commits figés (`fetch_repos.py --oca-only`) | **Exécuté** — 20/20 dépôts au bon commit |
| Installation des modules par groupe | **Non exécuté** (pas de démon Docker ni de réseau d'installation dans l'environnement d'audit) |
| Tests automatisés des modules OCA | **Non exécuté** (même raison) |
| Installation de tous les modules ensemble (conflits) | **Non exécuté** (même raison) |

Groupes prévus dans `scripts/test_install.sh` : achats ; importations et stocks ; fabrication,
planification et qualité ; maintenance ; comptabilité ; RH ; transverse ; **tout ensemble**.

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
