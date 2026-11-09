# 02 — Audit des modules natifs Odoo 19.0 Community

Relevé du 9 novembre 2026, commit Odoo `a27a1090`. Tous les modules listés sont **présents
dans le dépôt Community, licence LGPL-3, dépendances résolues sans Enterprise** (audit statique).
Les chemins de fichiers sont relatifs à la racine du dépôt Odoo.

## 1. Modules natifs par domaine

| Domaine | Module | Rôle pour Fayadort | Dépendances directes | Statut |
|---|---|---|---|---|
| Achats | `purchase` | Demandes de prix, commandes fournisseurs | account | Confirmé |
| Achats | `purchase_stock` | Réceptions liées aux commandes, délais | stock_account, purchase | Confirmé |
| Achats | `purchase_requisition` | Offres alternatives et comparaison ; contrats-cadres | purchase | Confirmé |
| Achats | `purchase_requisition_stock` | Lien contrats-cadres / stock | purchase_requisition, purchase_stock | Confirmé |
| Achats | `purchase_mrp` | Achats déclenchés par la fabrication | mrp, purchase_stock | Confirmé |
| Importations | `stock_landed_costs` | Frais d'approche intégrés à la valeur du stock | stock_account, purchase_stock | Confirmé |
| Importations | `mrp_landed_costs` | Frais additionnels sur ordres de fabrication | stock_landed_costs, mrp | Confirmé |
| Stocks | `stock` | Entrepôts, emplacements, mouvements, lots, réapprovisionnement | product, barcodes_gs1_nomenclature, digest | Confirmé |
| Stocks | `stock_account` | Valorisation (standard, FIFO, coût moyen), valorisation par lot | stock, account | Confirmé |
| Stocks | `product_expiry` | Dates de péremption (produits chimiques) | stock | Confirmé |
| Stocks | `stock_picking_batch` | Préparations groupées | stock | Confirmé |
| Fabrication | `mrp` | Nomenclatures, gammes, postes, ordres de fabrication et de travail, sous-produits, rebuts, désassemblage | product, stock, resource | Confirmé |
| Fabrication | `mrp_account` | Coût des ordres de fabrication, analytique | mrp, stock_account | Confirmé |
| Fabrication | `mrp_subcontracting` | Sous-traitance (si besoin) | mrp | Confirmé |
| Maintenance | `maintenance` | Équipements, demandes de maintenance | mail | Confirmé |
| Maintenance | `repair` | Réparations (sert surtout au SAV) | sale_stock, sale_management | Confirmé |
| Ventes | `sale_management`, `sale_stock`, `sale_mrp`, `sale_margin` | Devis, commandes, livraisons, marge | — | Confirmé |
| Comptabilité | `account` | Facturation, écritures, paiements, rapprochement de base | base_setup, product, analytic, … | Confirmé |
| Comptabilité | `analytic` | Plans analytiques (multi-axes) | base, mail, uom | Confirmé |
| Comptabilité | `l10n_syscohada` | Plan comptable SYSCOHADA (et SYSCEBNL) — **couverture partielle** (§2.8) | account | Confirmé (présence) |
| Comptabilité | `l10n_cm` | Taxes et positions fiscales Cameroun, déclaration de TVA — **couverture partielle** (§2.8) | l10n_syscohada, account | Confirmé (présence) |
| Comptabilité | `account_edi_ubl_cii` | Factures électroniques UBL/CII (base possible pour la future e-facture) | account | Confirmé, différé |
| RH | `hr` | Employés, départements, postes, **contrats** (`hr.version`) | base_setup, resource_mail, … | Confirmé |
| RH | `hr_attendance` | Pointage, mode kiosque | hr, barcodes, base_geolocalize | Confirmé |
| RH | `hr_holidays` | Congés et absences | hr, calendar, resource | Confirmé |
| RH | `hr_skills` | Compétences, formations | hr | Confirmé |
| RH | `hr_recruitment` | Recrutement | hr, calendar, … | Confirmé |
| Transverse | `base_automation` | Règles d'automatisation (alertes) | base, mail, … | Confirmé |
| Transverse | `spreadsheet_dashboard` | Tableaux de bord sous forme de feuilles de calcul | spreadsheet | Confirmé |
| Transverse | `barcodes` | Lecture de douchette dans l'interface (pas une application de scan) | web | Confirmé |

## 2. Fonctions critiques vérifiées dans le code

### 2.1 Frais d'approche — Confirmé
- Méthodes de répartition : **égale, quantité, coût actuel, poids, volume**
  (`addons/stock_landed_costs/models/stock_landed_cost.py`, l.12-16).
- Méthode par défaut paramétrable par article de frais (`split_method_landed_cost`,
  `addons/stock_landed_costs/models/product.py` l.13).
- **Conséquence** : `fay_import` n'a pas à calculer les répartitions. Il prépare et génère des
  `stock.landed.cost` à partir des factures réelles du dossier.

### 2.2 Sous-produits et répartition du coût — Confirmé, avec une contrainte majeure
- Une nomenclature porte des sous-produits avec un pourcentage de coût `cost_share`
  (`addons/mrp/models/mrp_bom.py` l.41) ; la somme ne peut dépasser 100 %.
- Le `cost_share` est **recopié sur chaque mouvement de sous-produit de l'ordre de fabrication**
  et peut y être modifié (`addons/mrp/models/stock_move.py` l.56 ; contrôles dans
  `addons/mrp/models/mrp_production.py` l.982-984).
- Calcul du coût (`addons/mrp_account/models/mrp_production.py` l.76-93) :
  - sous-produit valorisé en **FIFO ou coût moyen** → `coût total × cost_share / quantité` ;
  - sous-produit valorisé en **coût standard** → prix standard de l'article, **`cost_share` ignoré** ;
  - produit principal → le reste du coût.
- **Conséquence pour la découpe** : un ordre « Découpe » peut transformer 1 bloc en un produit
  principal et N plaques en sous-produits. `fay_foam` pourra calculer les `cost_share` **au volume
  réellement découpé** sur les mouvements de l'ordre, sans stock parallèle. **Mais cela impose que
  les plaques soient valorisées en coût moyen ou FIFO**, ce qui contraint le choix de méthode
  de coût (proposition P-005).
- Limite d'une nomenclature classique : un seul produit principal par ordre. Les plans de découpe
  variables d'un bloc à l'autre devront être générés par ordre (et non figés dans une nomenclature).
  À modéliser en phase 0-B.

### 2.3 Lots : mesures réelles et valorisation — Confirmé
- **Propriétés de lot** natives : champs configurables par article sans développement
  (`lot_properties`, `addons/stock/models/stock_lot.py` l.60 ; définition par article
  `addons/stock/models/product.py` l.126). Candidat pour enregistrer dimensions, poids et densité
  mesurés de chaque bloc. À confirmer en 0-B (besoin de calculs et de contrôles sur ces valeurs).
- **Valorisation par lot** (`lot_valuated`, `addons/stock_account/models/product.py` l.31) :
  chaque bloc peut garder sa propre valeur. Méthodes de coût : standard, FIFO, coût moyen (l.17-19).

### 2.4 Postes de travail et temps — Confirmé
- Coût horaire par poste (`costs_hour`, `addons/mrp/models/mrp_workcenter.py` l.41), repris sur
  les ordres de travail et dans le coût de l'opération (`addons/mrp/models/mrp_workorder.py` l.664).
- Suivi des temps et des arrêts par poste (`mrp.workcenter.productivity`, `mrp_workcenter.py` l.505).
- **Limite** : pas de coût par employé sur les ordres de travail en Community. Le coût de
  main-d'œuvre est intégré au **taux horaire du poste** (machines + équipe + énergie). Proposition P-006.

### 2.5 Planification — Confirmé (partiel)
- Règles de réapprovisionnement avec délais (`lead_days`, `days_to_order`,
  `addons/stock/models/stock_orderpoint.py` l.75 et 91) et délai d'achat paramétrable
  (`days_to_purchase`, `addons/purchase_stock/models/res_config_settings.py` l.11).
- **Pas de prévision de ventes ni de plan directeur** (MPS = Enterprise). → OCA
  `stock_demand_estimate` + `mrp_multi_level` (voir `03`).

### 2.6 Achats : comparaison d'offres — Confirmé
- Offres alternatives regroupées et comparables (`purchase.order.group`, `alternative_po_ids`,
  `addons/purchase_requisition/models/purchase.py` l.14 et 29-31).
- Types de contrats : contrat-cadre et modèle d'achat (`requisition_type`, l.21-23 de
  `purchase_requisition.py`).
- **Pas de demande d'achat interne ni de validation par seuils** en natif → OCA.

### 2.7 Analytique — Confirmé
- Plans analytiques multi-axes (`account.analytic.plan`, `addons/analytic/models/analytic_plan.py`).
- Écritures analytiques générées par les ordres de fabrication et de travail (`mrp_account`).
- **Conséquence** : pas de modèle `fay.cost.center` ; départements, ateliers, lignes et dossiers
  d'importation sont des axes analytiques.

### 2.8 Localisation camerounaise — couverture PARTIELLE, conformité NON acquise

**Ce que contiennent les modules (confirmé dans le code au commit figé) :**
- `l10n_syscohada` : plan de comptes SYSCOHADA (1 134 comptes, `data/template/account.account-syscohada.csv`)
  et variante SYSCEBNL pour les entités à but non lucratif.
- `l10n_cm` : 7 taxes — TVA 19,25 % (ventes, achats de biens, achats de services), 0 % à l'export,
  à l'import, exonéré (ventes et achats) — ; positions fiscales ; structure de déclaration de TVA
  (`data/account_tax_report_data.xml`, 61 enregistrements).
- Aucun des deux modules ne contient de tests automatisés (0 fichier `tests/test_*.py`).

**Ce qu'ils ne contiennent pas (confirmé par absence) :**
- états financiers SYSCOHADA : bilan, compte de résultat, tableau des flux de trésorerie, notes annexes ;
- DSF (déclaration statistique et fiscale) ;
- retenues et prélèvements à la source (retenue de TVA, acomptes et précomptes d'impôt sur le revenu) ;
- droits d'accises : la déclaration de TVA comporte une ligne « Amount of Excise Duty », mais aucune taxe
  d'accise n'est définie ;
- centimes additionnels et autres taxes spécifiques ;
- déclarations sociales (CNPS) ;
- facturation électronique au sens de la loi de finances 2026 (spécifications non publiées) ;
- télédéclaration.

**Ce qui n'a pas été vérifié :**
- la version du référentiel (SYSCOHADA révisé) suivie par le plan de comptes, l'exactitude et
  l'actualité des comptes, des taux, des libellés et des cases de la déclaration au regard de la
  réglementation en vigueur en 2026 ;
- l'adéquation aux pratiques du cabinet comptable de Fayadort.

**Conclusion :** ces modules sont une **base de départ**. Ni la conformité comptable ni la conformité
fiscale ne sont acquises. Elles devront être établies et validées par l'expert-comptable de Fayadort
(proposition P-011), et les états manquants construits (paramétrage `mis_builder`, développements ciblés).

### 2.9 RH — Confirmé
- Contrats intégrés à `hr` via `hr.version` (plus de module `hr_contract` en 19.0) :
  dates de contrat, type, salaire (`addons/hr/models/hr_version.py` l.156-198).
- Pointage avec mode kiosque (`addons/hr_attendance/controllers/main.py`).
- Pas de paie en Community (`hr_payroll` = Enterprise).

## 3. Manques confirmés et réponse proposée

| Besoin | Natif 19 Community | Réponse proposée |
|---|---|---|
| Écran atelier tablette, scan | Absent (Enterprise) | Développement `fay_shopfloor` (OWL) |
| Application de scan magasin | Absente (Enterprise) ; OCA 19.0 très incomplet | Intégré à `fay_shopfloor` / à préciser en 0-B |
| Qualité | Absente (Enterprise) | OCA `quality_control_oca` + déclencheurs à porter ou développer |
| Plan directeur, prévisions | Absent (Enterprise) | OCA `mrp_multi_level` + `stock_demand_estimate` |
| Demandes d'achat, validations | Absentes | OCA `purchase_request`, `*_tier_validation` |
| Maintenance préventive planifiée | Partielle | OCA `maintenance_plan` |
| États financiers, budgets, immobilisations | Absents (Enterprise) | OCA `mis_builder`, `account_financial_report`, `account_asset_management` ; états SYSCOHADA à construire et faire valider |
| Conformité fiscale camerounaise complète | Absente (couverture partielle) | Plan de validation avec l'expert-comptable (P-011) |
| Rapprochement bancaire avancé | Basique | OCA `account_reconcile_oca` |
| Journal d'audit des modifications | Suivi partiel (chatter) | OCA `auditlog` |
| Cure, découpe au volume | Briques natives présentes | Développement `fay_foam` sur `mrp` / `stock` |
| Dossier d'importation | Absent | Développement `fay_import` sur `purchase` / `account` / `stock_landed_costs` |
| Écarts standard / réel | Absent | Développement d'un rapport dans `fay_mrp` |
| Paie camerounaise | Absente | OCA `payroll` + règles spécifiques (piste séparée) |
