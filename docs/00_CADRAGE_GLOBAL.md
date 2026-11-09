# 00 — Cadrage global (Phase 0-A)

| | |
|---|---|
| Projet | FAYADORT ERP — Fayadort Cameroun SA |
| Phase | 0-A — Audit technique du socle Odoo 19.0 Community |
| Date du relevé | 9 novembre 2026 |
| Référence | `docs/PROMPT_MAITRE_V2.3.md` |
| Statut | **Revue corrective effectuée le 9 nov. 2026 — en attente de validation** (arrêt obligatoire 0-A) |

## 1. Objet de la phase 0-A

Établir, à partir des sources officielles, ce que fournit Odoo 19.0 Community, ce que l'OCA
apporte en 19.0, ce qui manque, et figer les versions des sources. Aucun module métier
`fay_*` n'a été créé.

## 2. Méthode

1. **Code source plutôt que documentation commerciale.** Toutes les affirmations sur Odoo et
   l'OCA proviennent de la lecture des dépôts Git officiels (manifestes, modèles Python),
   aux commits figés dans `repos.yaml`.
2. **Audit statique automatisé** (`scripts/audit/static_audit.py`) des 78 modules candidats
   **et de toute leur chaîne de dépendances** : présence et unicité du nom, `installable`, version 19.0.x,
   résolution récursive des dépendances dans Odoo 19 Community + OCA figé (pour détecter une dépendance
   Enterprise ou un dépôt manquant), **dépendances externes Python et binaires comparées à
   l'environnement Odoo standard**, existence des fichiers déclarés, syntaxe Python (grammaire 3.10)
   et XML. L'outil a lui-même été testé sur des modules volontairement défectueux.
3. **Vérifications ciblées dans le code** pour les fonctions critiques pour Fayadort :
   frais d'approche, sous-produits et répartition des coûts, valorisation par lot,
   propriétés de lot, coût horaire des postes, contrats RH, localisation camerounaise.
4. **Verrouillage** de Odoo et de 20 dépôts OCA sur des commits précis ; script de
   récupération testé (`scripts/fetch_repos.py`).

## 3. Limite importante : tests d'installation non exécutés

L'environnement dans lequel l'audit a été réalisé dispose de Docker, mais **sans démon Docker
actif ni accès réseau pour installer des paquets**. Il a donc été **impossible d'installer
Odoo et d'exécuter les tests des modules**. La logique du script de tests a été vérifiée avec un
Docker simulé, ce qui ne remplace pas une exécution réelle.

Conséquence : tous les modules OCA sont classés au mieux **« retenu (à tester) »**, jamais « validé ».

### Commandes à exécuter sur une machine disposant de Docker

```bash
cd fayadort-erp
python3 -m pip install --user pyyaml          # si PyYAML est absent
python3 scripts/fetch_repos.py                # Odoo + OCA aux commits figés (plusieurs minutes)
bash scripts/pin_postgres_digest.sh           # fige PostgreSQL par digest (voir 01 §3.1)
git add docker/docker-compose.test.yml && git commit -m "Fige l'image PostgreSQL de test par digest"
python3 scripts/test_plan.py --check          # couverture du plan de tests
bash scripts/test_install.sh                  # demande confirmation avant de remettre à zéro l'environnement de TEST
cat test-logs/*/RESULTS.md                    # synthèse ; détails dans test-logs/<campagne>/
docker compose -p fayadort-test -f docker/docker-compose.test.yml down -v   # nettoyage final
```

Ce que garantit `test_install.sh` : environnement de test remis à zéro à chaque campagne (volumes du
seul projet `fayadort-test`, après confirmation) ; bases neuves au nom unique, refus de réutiliser une
base existante ; installation et tests automatisés dans deux bases distinctes ; vérification en base
que chaque module est bien à l'état `installed` ; comptage des erreurs et du bilan officiel des tests ;
séparation des groupes de validation (V-*), d'évaluation (E-*) et de piste séparée (S-*).

## 4. Légende utilisée dans tous les documents

| Statut | Signification |
|---|---|
| **Confirmé** | Vérifié dans le code source au commit figé |
| **Testé** | Installé et exécuté dans un environnement de test (aucun à ce stade) |
| **Statique OK** | Manifeste, chaîne de dépendances, dépendances externes, fichiers, syntaxe Python et XML vérifiés ; non installé |
| **Dépendance externe à fournir** | Statique OK, mais une bibliothèque ou un binaire hors environnement Odoo standard est requis |
| **Recommandé** | Proposition argumentée, à valider |
| **À décider** | Décision du responsable du projet ou de Fayadort requise |

## 5. Synthèse des résultats

1. **Le socle Odoo 19.0 Community couvre la colonne vertébrale du projet** : achats avec comparaison
   d'offres, stocks, lots, frais d'approche, fabrication avec sous-produits et répartition des coûts,
   maintenance, ventes, RH (employés, contrats, présences, congés), comptabilité de base.
   La localisation camerounaise (`l10n_syscohada`, `l10n_cm`) n'apporte qu'une **couverture partielle** :
   plan de comptes SYSCOHADA, 7 taxes, déclaration de TVA ; ni états financiers, ni DSF, ni retenues à la
   source, ni déclarations sociales. **La conformité comptable et fiscale n'est pas acquise** (`02` §2.8,
   P-011). → `02_AUDIT_MODULES_NATIFS.md`
2. **L'OCA comble la majorité des manques fonctionnels.** 66 modules retenus pour validation
   (28 natifs, 38 OCA), 3 à évaluer, 1 en piste séparée, 6 différés, 2 rejetés. Audit statique : aucun
   module bloquant ; une dépendance externe à fournir (`openupgradelib`, pour `hr_holidays_public`),
   ajoutée à l'image de test. → `03_AUDIT_OCA.md`
3. **Développements spécifiques réellement nécessaires** (confirmé par absence dans Community et OCA 19.0) :
   interface atelier et scan (`fay_shopfloor`) ; cure, libération et découpe avec répartition du coût au
   volume (`fay_foam`) ; dossier d'importation (`fay_import`) ; déclencheurs qualité (portage OCA ou
   `fay_quality`) ; rapport d'écarts standard / réel (`fay_mrp`) ; états financiers SYSCOHADA
   (`mis_builder`) ; règles de paie camerounaise (piste séparée).
4. **Deux points techniques qui conditionnent l'architecture** (détaillés dans `02`) :
   - la répartition du coût entre plaques via `cost_share` **ne fonctionne que pour des articles valorisés
     en coût moyen (AVCO) ou FIFO**, pas en coût standard ;
   - Odoo 19 Community ne gère pas de coût par employé sur les ordres de travail : le coût de main-d'œuvre
     passe par le **taux horaire du poste de travail**.
5. **Licences** : 42 modules LGPL-3, 34 AGPL-3, aucun OPL ; bibliothèque `openupgradelib` en AGPL-3.
   L'AGPL n'impose rien de particulier pour un usage interne sans modification ; la licence des futurs
   modules `fay_*` dépend de leurs dépendances et d'une éventuelle commercialisation, et demande un avis
   juridique dans ce cas (`03` §5, P-007).

## 6. Décisions attendues

La liste complète et argumentée figure dans `DECISIONS.md` (propositions P-001 à P-011).

## 7. Livrables de la phase 0-A

| Fichier | Contenu |
|---|---|
| `CLAUDE.md` | Règles permanentes, phase en cours, dernier point validé |
| `docs/00_CADRAGE_GLOBAL.md` | Ce document |
| `docs/01_SOCLE_ODOO19.md` | Version, commit, prérequis, environnement de test, procédure du digest PostgreSQL |
| `docs/02_AUDIT_MODULES_NATIFS.md` | Modules natifs par domaine, fonctions vérifiées, limites (dont comptabilité camerounaise) |
| `docs/03_AUDIT_OCA.md` | Catégories, fiches OCA, décisions, analyse des licences |
| `DECISIONS.md` | Décisions validées et propositions à valider |
| `repos.yaml` | Verrouillage des commits Odoo et OCA |
| `scripts/audit/candidates.txt` | **Source unique** des modules candidats et de leur catégorie |
| `scripts/audit/static_audit.py` | Audit statique reproductible |
| `scripts/fetch_repos.py` | Récupération des sources aux commits figés |
| `scripts/test_plan.py` | Plan de tests généré depuis `candidates.txt`, contrôle de couverture |
| `scripts/test_install.sh` | Campagne de tests d'installation et de tests automatisés |
| `scripts/parse_odoo_log.py` | Analyse des journaux Odoo (erreurs, bilan des tests) |
| `scripts/pin_postgres_digest.sh` | Figer l'image PostgreSQL par digest |
| `docker/docker-compose.test.yml`, `docker/Dockerfile.test`, `docker/requirements-extra.txt` | Environnement de test |
