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
  l'environnement d'audit (pas de démon Docker ni de réseau d'installation). La logique du script de
  tests a été vérifiée avec un Docker simulé uniquement.
- **Proposition** : exécuter sur une machine disposant de Docker les commandes de `docs/00_CADRAGE_GLOBAL.md`
  §3 (récupération des sources, digest PostgreSQL, `scripts/test_install.sh`) ; transmettre
  `test-logs/<campagne>/RESULTS.md` et les journaux des groupes en échec.
- **Règle d'interprétation** : seuls les groupes **V-*** valident des modules. Un module « retenu » n'est
  validé que si son groupe V-domaine **et** V-ENSEMBLE sont « OK » ; « À ANALYSER » exige une revue des
  erreurs avant décision.
- **Impact si refusé** : la phase 0-B s'appuierait sur des modules dont l'installation n'est pas prouvée.
- **Règle de validation proposée** (aucune condition de test unique ne convient à tous les modules OCA) :
  1. installation de chaque module retenu réussie **avec et sans** données de démonstration ;
  2. tous les tests OCA de chaque groupe de validation réussis dans **au moins une** des deux conditions ;
  3. chaque échec obtenu dans l'autre condition analysé et classé : « test fragile » (documenté, non bloquant)
     ou « défaut fonctionnel » (module retiré, corrigé ou contourné, décision tracée ici).
- **État au 9 nov. 2026** : campagne 1 non probante (`docs/03` §6.1) ; campagnes 2 à 4 : **les trois critères
  sont remplis** — 65/65 modules installés ensemble avec et sans démonstration, 0 erreur ; tous les groupes de
  validation passent dans une condition ; 14 échecs sur 14 classés « test fragile », 0 défaut fonctionnel
  (`docs/03` §6.2 à §6.5). **Proposition : déclarer validés les 65 modules « retenu ».**

### P-002 — Socle technique
- **Proposition** : Ubuntu Server 24.04 LTS, Python 3.12, PostgreSQL 16 ; image d'exécution
  construite depuis `odoo/docker` @ `f900094` complétée par `docker/Dockerfile.test` ; code Odoo exécuté
  depuis le commit figé ; image PostgreSQL figée par digest (`scripts/pin_postgres_digest.sh`).
- **Digest PostgreSQL retenu** : `postgres:16@sha256:f9a7b9ebf6f56201f949db745e47bc423c0f0f8294bafe991cc10bf74b029657`
  (figé le 2026-11-09 par `scripts/pin_postgres_digest.sh`, contrôlé dans la campagne 1).
- **Justification** : distribution de référence d'Odoo 19 (`requirements.txt`) ; image officielle
  basée sur `ubuntu:noble` ; exigences `release.py` respectées (Python 3.10-3.14, PostgreSQL ≥ 13).
- **Alternative** : Debian 12 (également référence) — aucun avantage identifié pour Fayadort.

### P-003 — Catégories des modules candidats
- **Proposition** : adopter les catégories de `scripts/audit/candidates.txt` (source unique) :
  65 « retenu » (28 natifs, 37 OCA), 4 « à évaluer » (`stock_landed_costs_purchase_auto`,
  `stock_secondary_unit`, `mis_builder_cash_flow`, `account_fiscal_year` — voir P-012), 1 « piste séparée » (`payroll`), 6 « différé »,
  2 « rejeté » (`purchase_landed_cost`, `mrp_production_back_to_draft`).
- **Règle** : les modules « à évaluer » et « piste séparée » sont testés dans des groupes distincts (E-*, S-*)
  dont le résultat est **informatif** ; leur réussite ne les fait pas passer en « retenu ». Tout changement
  de catégorie passe par une nouvelle entrée de ce registre.
- Décisions sur les trois modules « à évaluer » : en phase 0-B, à la lumière des réponses de Fayadort et
  des résultats E-*.

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

### P-007 — Licence des modules `fay_*` *(décision ouverte ; avis juridique requis en cas de commercialisation)*
- **Constat** (analyse détaillée : `docs/03_AUDIT_OCA.md` §5) :
  - l'AGPL-3 n'impose **rien de particulier pour un usage interne** de modules non modifiés ;
  - ses obligations naissent de la **modification** d'un programme AGPL utilisé à distance (art. 13) ou de
    la **distribution** de copies ;
  - qu'un module `fay_*` dépendant d'un module AGPL doive lui-même être sous licence compatible AGPL en cas
    de distribution est une **question juridique ouverte** ; l'usage répandu dans l'écosystème OCA va dans
    ce sens, sans que cela vaille avis juridique ;
  - un module qui ne dépend que de modules LGPL laisse le choix de sa licence.
- **Options** :
  | Option | Usage interne | Si commercialisation future |
  |---|---|---|
  | AGPL-3 | Aucune contrainte pratique | Code source à fournir aux clients ; modèle économique de service |
  | LGPL-3 | Aucune contrainte pratique | Permet des modules tiers propriétaires ; compatibilité avec les dépendances AGPL à vérifier |
  | Propriétaire | Aucune contrainte pratique | Envisageable seulement pour des modules sans dépendance AGPL, sous réserve d'avis juridique |
- **Proposition de démarche** (pas de licence imposée à ce stade) :
  1. Fayadort indique si une commercialisation des modules est envisagée ;
  2. pour chaque futur module `fay_*`, produire la liste de ses dépendances AGPL (calculable par
     `static_audit.py`) ;
  3. choisir la licence module par module **avant sa création** (clé `license` obligatoire du manifeste) ;
  4. avis d'un juriste (propriété intellectuelle, Cameroun / OHADA) **avant toute distribution externe**.

### P-008 — Politique de mise à jour des commits figés
- **Proposition** : revue des correctifs Odoo 19.0 et OCA **une fois par mois** (et immédiatement
  pour une faille de sécurité) ; montée de commit uniquement après relance de
  `scripts/test_install.sh` et des tests du projet ; trace dans ce registre.

### P-009 — Dépendance Python `openupgradelib`
- **Constat** : requise à l'installation par `calendar_public_holiday`, dépendance de `hr_holidays_public`
  (jours fériés), et absente de l'image officielle d'Odoo. Licence AGPL-3.
- **Proposition** : l'ajouter à l'image de test (`docker/requirements-extra.txt`, `openupgradelib==3.13.7`,
  dernière étiquette du dépôt OCA au 9 nov. 2026) et, plus tard, à l'image de production.
- **Alternative** : saisir les jours fériés sans `hr_holidays_public` (fonctions natives de calendrier) —
  plus de saisie manuelle chaque année.

### P-010 — Reproductibilité des images
- **Constat** : l'image de base est reconstruite depuis un Dockerfile figé, mais à partir de `ubuntu:noble` et de
  paquets système évolutifs ; la dépendance transitive `cssselect` d'`openupgradelib` n'est pas figée.
- **Proposition** : accepter cette limite pour les tests de phase 0 (le `pip freeze` de chaque campagne est
  archivé) ; en 0-C, prévoir pour la production une image construite une fois puis figée (registre privé ou
  digest), et un fichier de dépendances entièrement figé.
- **Point lié** : l'image officielle ne contient pas Chrome ; les tests navigateur des modules sont donc
  ignorés (comptés dans `RESULTS.md`). Ajouter Chromium à l'image de test est possible : à décider.

### P-011 — Validation comptable et fiscale camerounaise
- **Constat** : `l10n_syscohada` et `l10n_cm` n'apportent qu'une couverture partielle (`docs/02` §2.8) ;
  la conformité n'est pas acquise.
- **Proposition** : en 0-B / 0-C, établir avec l'expert-comptable de Fayadort une liste des obligations
  (états SYSCOHADA, DSF, TVA et retenues, accises éventuelles, déclarations sociales, facture électronique)
  et, pour chacune, la couverture visée (natif, OCA, paramétrage, développement, hors ERP) et le test de
  validation correspondant. Aucune mise en production de la comptabilité sans cette validation.

### P-012 — `account_fiscal_year` : de « retenu » à « à évaluer »
- **Constat** (campagne 1, confirmé dans le code) : installé avec `mis_builder`, ce module provoque une erreur
  d'accès pour tout utilisateur sans droits comptables complets qui calcule un rapport `mis_builder`
  (il recherche les exercices sans élévation de droits ; lecture réservée aux groupes comptables).
  Pour Fayadort : un directeur ou un responsable de production consultant un tableau de bord financier.
- **Analyse** : le module sert aux exercices **non calendaires** ou multiples. L'exercice OHADA correspond en
  principe à l'année civile, déjà géré nativement (dernier jour et mois de l'exercice de la société) —
  **à confirmer par l'expert-comptable**.
- **Proposition** : le passer en « à évaluer » (fait dans `candidates.txt`, réversible), puis en « différé »
  si l'expert-comptable confirme l'exercice civil. Alternative si le module s'avère nécessaire : droits de
  lecture des exercices pour les groupes concernés, dans un module `fay_*`, testés.

## Informations métier attendues de Fayadort (bloquantes pour la phase 0-B)

1. Coulée de la mousse : discontinue (blocs, moules) ou continue ? Dimensions habituelles des blocs ?
2. Découpe : machines utilisées ? Logiciel d'optimisation ou travail manuel ?
3. Chutes : jetées, vendues ou recyclées sur place (mousse agglomérée) ?
4. Ressorts : fabriqués sur place ou achetés assemblés ?
5. Production des matelas : sur stock, sur commande, ou les deux ?
6. Paie : logiciel existant ? Peut-il être conservé 6 à 12 mois ?
