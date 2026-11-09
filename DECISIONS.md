# DECISIONS.md — Registre des décisions

Une décision validée ne se modifie pas silencieusement : toute remise en cause passe par une
nouvelle entrée qui la remplace explicitement.

## Décisions validées

| ID | Date | Décision | Source |
|---|---|---|---|
| DEC-001 | 2026-11-09 | **Odoo 19.0 Community exclusivement.** Pas de comparaison avec Odoo 20, aucune dépendance Enterprise. Une migration future fera l'objet d'une étude distincte. | Prompt V2.3 §2 |
| DEC-002 | 2026-11-09 | `docs/PROMPT_MAITRE_V2.3.md` est la référence du projet ; il remplace V2, V2.1 et V2.2. | Prompt V2.3 §17 |
| DEC-003 | 2026-11-09 | Phase 0 en trois arrêts obligatoires (0-A audit, 0-B architecture et processus, 0-C technique, planification, recette). Aucun module métier avant validation de la phase 0. | Prompt V2.3 §8 |
| DEC-004 | 2026-11-09 | Architecture *native-first* : natif Community, puis OCA vérifié, puis développement `fay_*` justifié. Aucun système parallèle de stock, production, comptabilité ou ventes ; pas de doublon des plans analytiques ; dépenses réelles d'importation issues des factures. | Prompt V2.3 §4-5 |
| DEC-005 | 2026-11-09 | Chaque dépôt (Odoo, OCA) est figé sur un commit précis dans `repos.yaml`. Aucune montée de version sans analyse, tests et décision. Aucun module OPL sans autorisation. | Prompt V2.3 §6 |
| DEC-006 | 2026-11-09 | Code et identifiants en anglais, interface en français (i18n). Un commit Git par étape validée. Aucune modification du code source d'Odoo ou de l'OCA. | Prompt V2.3 §5.3, §11 |
| DEC-007 | 2026-11-09 | Développement par tranches complètes (slices 1 à 4) ; RH, paie et facturation électronique en chantiers distincts. | Prompt V2.3 §9 |

## Propositions issues de la phase 0-A — en attente de validation

### P-001 — Exécuter les tests d'installation avant de figer la liste OCA *(bloquant)*
- **Constat** : l'audit statique est concluant, mais aucun module n'a pu être installé dans
  l'environnement d'audit (pas de démon Docker ni de réseau d'installation).
- **Proposition** : exécuter `python3 scripts/fetch_repos.py` puis `bash scripts/test_install.sh`
  sur une machine disposant de Docker ; corriger ou écarter tout module en échec ; figer le digest
  de l'image PostgreSQL.
- **Impact si refusé** : la phase 0-B s'appuierait sur des modules dont l'installation n'est pas prouvée.

### P-002 — Socle technique
- **Proposition** : Ubuntu Server 24.04 LTS, Python 3.12, PostgreSQL 16 ; image d'exécution
  construite depuis `odoo/docker` @ `f900094` ; code Odoo exécuté depuis le commit figé.
- **Justification** : distribution de référence d'Odoo 19 (`requirements.txt`) ; image officielle
  basée sur `ubuntu:noble` ; exigences `release.py` respectées (Python 3.10-3.14, PostgreSQL ≥ 13).
- **Alternative** : Debian 12 (également référence) — aucun avantage identifié pour Fayadort.

### P-003 — Liste des modules OCA
- **Proposition** : retenir pour tests les modules marqués « Retenu (à tester) » dans
  `docs/03_AUDIT_OCA.md` §2 ; rejeter `purchase_landed_cost` et `mrp_production_back_to_draft` ;
  différer `queue_job`, `dms`, `stock_inventory*` ; trancher en 0-B `stock_landed_costs_purchase_auto`
  et `stock_secondary_unit`.

### P-004 — Déclencheurs qualité sur réceptions et fabrications
- **Constat** : `quality_control_stock_oca` et `quality_control_mrp_oca` existent en 18.0, pas en 19.0.
- **Option A (recommandée)** : les porter en 19.0 dans le dépôt du projet, puis proposer le portage
  à l'OCA. Code éprouvé, maintenance partagée à terme.
- **Option B** : écrire des déclencheurs spécifiques dans `fay_quality`. Plus simple au départ,
  maintenance entièrement à la charge de Fayadort.
- **Calendrier** : tranche 3 ; aucune urgence pour la tranche 1.

### P-005 — Méthode de valorisation des stocks *(à valider aussi par l'expert-comptable)*
- **Constat technique** : la répartition du coût d'un bloc entre ses plaques (`cost_share`) n'est
  appliquée par Odoo **qu'aux articles valorisés en coût moyen (AVCO) ou FIFO** ; en coût standard,
  le pourcentage est ignoré (`mrp_account/models/mrp_production.py` l.76-93).
- **Proposition** :
  - valorisation **comptable en coût moyen (AVCO)** pour les matières premières (intégrant les
    frais d'approche), les blocs et les plaques, avec **valorisation par lot** pour les blocs ;
  - le **coût standard** devient une **référence de gestion** portée par `fay_mrp` (révisée
    périodiquement) pour calculer les écarts, sans être la méthode comptable ;
  - méthode des matelas finis : à trancher en 0-C avec l'expert-comptable.
- **Alternative** : coût standard comptable pour les semi-finis → impossible de répartir le coût
  des blocs au volume avec les mécanismes natifs ; il faudrait un développement plus lourd.

### P-006 — Coût de main-d'œuvre et d'énergie
- **Constat** : Odoo 19 Community ne calcule pas de coût par employé sur les ordres de travail.
- **Proposition** : intégrer main-d'œuvre directe, énergie (réseau et groupe électrogène) et
  amortissement machine dans le **taux horaire de chaque poste de travail**, revu périodiquement
  à partir de la comptabilité. Pas de coût individuel par opérateur en tranche 1.

### P-007 — Licence des modules `fay_*`
- **Proposition** : **AGPL-3** pour tous les modules `fay_*`, cohérente avec les modules AGPL dont
  ils dépendront, sans ambiguïté pour un usage interne.
- **Point d'attention** : si Fayadort envisage un jour de vendre ou céder ses modules, une analyse
  juridique sera nécessaire avant toute distribution.

### P-008 — Politique de mise à jour des commits figés
- **Proposition** : revue des correctifs Odoo 19.0 et OCA **une fois par mois** (et immédiatement
  pour une faille de sécurité) ; montée de commit uniquement après relance de
  `scripts/test_install.sh` et des tests du projet ; trace dans ce registre.

## Informations métier attendues de Fayadort (bloquantes pour la phase 0-B)

1. Coulée de la mousse : discontinue (blocs, moules) ou continue ? Dimensions habituelles des blocs ?
2. Découpe : machines utilisées ? Logiciel d'optimisation ou travail manuel ?
3. Chutes : jetées, vendues ou recyclées sur place (mousse agglomérée) ?
4. Ressorts : fabriqués sur place ou achetés assemblés ?
5. Production des matelas : sur stock, sur commande, ou les deux ?
6. Paie : logiciel existant ? Peut-il être conservé 6 à 12 mois ?
