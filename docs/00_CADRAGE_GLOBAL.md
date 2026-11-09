# 00 — Cadrage global (Phase 0-A)

| | |
|---|---|
| Projet | FAYADORT ERP — Fayadort Cameroun SA |
| Phase | 0-A — Audit technique du socle Odoo 19.0 Community |
| Date du relevé | 9 novembre 2026 |
| Référence | `docs/PROMPT_MAITRE_V2.3.md` |
| Statut | **En attente de validation** (arrêt obligatoire 0-A) |

## 1. Objet de la phase 0-A

Établir, à partir des sources officielles, ce que fournit Odoo 19.0 Community, ce que l'OCA
apporte en 19.0, ce qui manque, et figer les versions des sources. Aucun module métier
`fay_*` n'a été créé.

## 2. Méthode

1. **Code source plutôt que documentation commerciale.** Toutes les affirmations sur Odoo et
   l'OCA proviennent de la lecture des dépôts Git officiels (manifestes, modèles Python),
   aux commits figés dans `repos.yaml`.
2. **Audit statique automatisé** (`scripts/audit/static_audit.py`) des 78 modules candidats :
   présence, version 19.0, licence, statut `installable`, maturité déclarée, dépendances
   Python externes, **résolution récursive des dépendances** dans l'ensemble
   Odoo 19 Community + OCA figé (pour détecter une dépendance Enterprise ou un dépôt manquant),
   compilation de tous les fichiers Python (1 582) et analyse de tous les fichiers XML (1 141).
3. **Vérifications ciblées dans le code** pour les fonctions critiques pour Fayadort :
   frais d'approche, sous-produits et répartition des coûts, valorisation par lot,
   propriétés de lot, coût horaire des postes, contrats RH, localisation camerounaise.
4. **Verrouillage** de Odoo et de 20 dépôts OCA sur des commits précis ; script de
   récupération testé (`scripts/fetch_repos.py`).

## 3. Limite importante : tests d'installation non exécutés

L'environnement dans lequel l'audit a été réalisé dispose de Docker, mais **sans démon Docker
actif ni accès réseau pour installer des paquets**. Il a donc été **impossible d'installer
Odoo et d'exécuter les tests des modules**.

Conséquence : tous les modules OCA sont classés **« retenu (à tester) »** et non « validé ».
Un environnement de test reproductible et un script de tests sont fournis :

```bash
pip install pyyaml                     # sur la machine hôte, si absent
python3 scripts/fetch_repos.py         # récupère Odoo + OCA aux commits figés
bash scripts/test_install.sh           # installe les modules par groupe, lance leurs tests
cat test-logs/RESULTS.md               # synthèse
```

Ces tests doivent être exécutés sur ta machine (ou un serveur de test) **avant** la validation
définitive de la liste des modules OCA. C'est la première décision demandée (voir §6).

## 4. Légende utilisée dans tous les documents

| Statut | Signification |
|---|---|
| **Confirmé** | Vérifié dans le code source au commit figé |
| **Testé** | Installé et exécuté dans un environnement de test (aucun à ce stade) |
| **Statique OK** | Manifeste, dépendances, syntaxe Python et XML vérifiés ; non installé |
| **Recommandé** | Proposition argumentée, à valider |
| **À décider** | Décision du responsable du projet ou de Fayadort requise |

## 5. Synthèse des résultats

1. **Le socle Odoo 19.0 Community couvre la colonne vertébrale du projet** : achats avec
   comparaison d'offres, stocks, lots, frais d'approche, fabrication avec sous-produits et
   répartition des coûts, maintenance, ventes, comptabilité avec plan SYSCOHADA et TVA
   camerounaise, RH (employés, contrats, présences, congés). → `02_AUDIT_MODULES_NATIFS.md`
2. **L'OCA comble la majorité des manques** : demandes d'achat, validations par seuils,
   planification multi-niveaux avec prévisions, qualité (base), maintenance préventive,
   états comptables, rapprochement bancaire, immobilisations, budgets, journal d'audit.
   49 modules OCA audités : 47 statiquement OK, 2 différés. → `03_AUDIT_OCA.md`
3. **Développements spécifiques réellement nécessaires** (confirmé par absence dans
   Community et OCA 19.0) :
   - interface atelier sur tablette et scan code-barres (`fay_shopfloor`) ;
   - processus mousse : cure, libération, découpe avec répartition du coût au volume (`fay_foam`) ;
   - dossier d'importation, jalons, budget, génération des frais d'approche (`fay_import`) ;
   - déclencheurs qualité sur réceptions et fabrications (portage OCA ou `fay_quality`) ;
   - rapport d'écarts de production standard / réel (`fay_mrp`) ;
   - états financiers SYSCOHADA (modèles `mis_builder`) ;
   - règles de paie camerounaise (sur le moteur OCA `payroll`, piste séparée).
4. **Deux points techniques qui conditionnent l'architecture** (détaillés dans `02`) :
   - la répartition du coût entre plaques via `cost_share` **ne fonctionne que pour des
     articles valorisés en coût moyen (AVCO) ou FIFO**, pas en coût standard ;
   - Odoo 19 Community ne gère pas de coût par employé sur les ordres de travail :
     le coût de main-d'œuvre passe par le **taux horaire du poste de travail**.
5. **Licences** : 42 modules LGPL-3, 34 AGPL-3, **aucun OPL**. → `03_AUDIT_OCA.md` §5

## 6. Décisions attendues

La liste complète et argumentée figure dans `DECISIONS.md` (propositions P-001 à P-008).

## 7. Livrables de la phase 0-A

| Fichier | Contenu |
|---|---|
| `CLAUDE.md` | Règles permanentes, phase en cours, dernier point validé |
| `docs/00_CADRAGE_GLOBAL.md` | Ce document |
| `docs/01_SOCLE_ODOO19.md` | Version, commit, prérequis, environnement d'exécution |
| `docs/02_AUDIT_MODULES_NATIFS.md` | Modules natifs par domaine, fonctions vérifiées, manques |
| `docs/03_AUDIT_OCA.md` | Fiches OCA, décisions, registre des licences |
| `DECISIONS.md` | Décisions validées et propositions à valider |
| `repos.yaml` | Verrouillage des commits Odoo et OCA |
| `scripts/fetch_repos.py` | Récupération des sources aux commits figés (exécuté avec succès pour l'OCA) |
| `scripts/audit/static_audit.py` + `candidates.txt` | Audit statique reproductible |
| `docker/docker-compose.test.yml` + `scripts/test_install.sh` | Environnement et tests d'installation (à exécuter) |
