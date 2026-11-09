# CLAUDE.md — FAYADORT ERP (règles permanentes)

Référence détaillée : `docs/PROMPT_MAITRE_V2.3.md`. En cas de doute, la relire.
Décisions validées : `DECISIONS.md`. Ne jamais les modifier silencieusement.

## État du projet

- **Phase en cours : 0-A — Audit technique du socle Odoo 19.0 Community.**
- **Dernier point validé :** prompt maître V2.3 adopté ; Odoo 19.0 Community verrouillé (DEC-001).
- Livrables 0-A remis le 2026-11-09 : **en attente de validation** (propositions P-001 à P-008 dans `DECISIONS.md`).
- Prochaine étape après validation : exécuter `scripts/test_install.sh` (P-001), puis phase 0-B
  (nécessite les réponses métier de Fayadort).

## Décisions verrouillées

1. Odoo **19.0 Community** exclusivement. Pas de comparaison avec Odoo 20, pas d'Enterprise.
2. Aucune dépendance obligatoire à un module Enterprise.
3. Aucun module OPL sans autorisation explicite du responsable du projet.
4. Chaque dépôt (Odoo, OCA) est figé sur un **commit précis** (`repos.yaml`).
   Aucune montée de version sans analyse, tests et décision dans `DECISIONS.md`.

## Méthode de travail (obligatoire)

- Une étape à la fois : analyser → proposer → attendre validation → développer → tester → documenter → rendre compte → attendre.
- Le silence n'est jamais une validation. Ne jamais passer seul à l'étape ou à la phase suivante.
- Aucune modification irréversible ou destructive sans autorisation explicite.
- Ne pas développer de fonctionnalités non demandées.
- Regrouper les questions qui demandent une décision ; ne pas inventer les réponses métier.

## Phase 0 (cadrage) — limites

- Aucun module métier `fay_*` pendant la phase 0.
- Environnement Docker de **test** autorisé (jamais de données réelles sensibles).
- Trois arrêts obligatoires : 0-A (audit), 0-B (architecture et processus), 0-C (technique, planification, recette).

## Architecture : native-first

1. Fonction couverte par Odoo 19 Community ? → l'utiliser.
2. Sinon, module OCA 19.0 vérifié (licence, dépendances, code, tests) ? → l'utiliser.
3. Sinon seulement → extension spécifique `fay_*`, justifiée et documentée.

Interdits : stock, production, comptabilité ou ventes parallèles ; doublon des plans analytiques ;
seconde saisie des dépenses d'importation (le réel vient des factures `account.move`).
Les objets natifs (`stock.move`, `stock.quant`, `stock.lot`, `mrp.production`, `mrp.workorder`,
`purchase.order`, `account.move`) restent la source de vérité. L'interface atelier alimente ces objets.

## Code

- Ne jamais modifier le code source d'Odoo ni d'un module OCA : héritage et points d'extension uniquement.
- Éviter de surcharger les méthodes privées `_xxx` si un point d'extension public existe.
- Code, modèles, champs, méthodes, identifiants : **anglais**. Libellés et interface : **français** (i18n, `fr.po`).
- Conventions Odoo ; pas de logique métier dans les vues ; pas de dépendances inutiles ou circulaires.
- Sécurité côté serveur : groupes, ACL, record rules, contrôles ORM. Masquer un bouton n'est pas une sécurité.
- Transactions validées : jamais supprimées, corrigées par des opérations traçables.
- Aucun secret, mot de passe ou clé API dans Git.

## Tests

- Tests automatisés pour chaque comportement personnalisé (calculs, états, stocks, coûts, droits).
- Ne jamais déclarer un test réussi sans l'avoir exécuté. Distinguer : réussi / échoué / non exécuté / à créer.
- Distinguer dans les rapports : **confirmé / testé / recommandé / à décider**.
- Le scénario d'acceptation chiffré (phase 0-C) deviendra le test de bout en bout de la tranche 1.

## Git

- Un commit par étape validée et testée ; messages descriptifs ; pas de changements non liés mélangés.
- Environnements séparés : développement, test, production. Rien de non testé en production.

## Données et estimations

- Ne jamais inventer de formulations, de règles industrielles, fiscales ou sociales.
- Coûts de matériel et d'hébergement : toujours des **estimations à confirmer par des devis locaux**.
- Paie et fiscalité : validation obligatoire par un spécialiste camerounais.

## Communication

- Rapports en français, structurés, avec sources vérifiables et date de consultation.
- Le responsable du projet code avec Claude Code et participe aux revues : explications techniques,
  reliées aux conséquences métier pour Fayadort.
