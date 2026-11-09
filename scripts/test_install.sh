#!/usr/bin/env bash
# Tests d'installation des modules candidats — Phase 0-A (environnement de TEST jetable).
#
# Pour chaque groupe : base neuve, installation des modules, puis exécution des tests
# automatisés des modules OCA du groupe. Un dernier groupe installe TOUT ensemble pour
# détecter les conflits entre modules. Résultats : test-logs/RESULTS.md
#
# Préalables : Docker + Docker Compose, puis `python3 scripts/fetch_repos.py`.
set -uo pipefail
cd "$(dirname "$0")/.."
COMPOSE="docker compose -f docker/docker-compose.test.yml"
mkdir -p test-logs

[ -f src/odoo/odoo-bin ] || { echo "src/odoo absent : lancez d'abord python3 scripts/fetch_repos.py"; exit 1; }
[ -f docker/odoo.test.conf ] || { echo "docker/odoo.test.conf absent : lancez scripts/fetch_repos.py"; exit 1; }

declare -A MODGROUPS
MODGROUPS[g1_achats]="purchase_requisition_stock purchase_mrp purchase_request base_tier_validation purchase_tier_validation purchase_request_tier_validation"
MODGROUPS[g2_imports_stocks]="stock_landed_costs mrp_landed_costs stock_landed_costs_purchase_auto stock_no_negative scrap_reason_code product_expiry stock_picking_batch stock_secondary_unit stock_analytic"
MODGROUPS[g3_fabrication_planif_qualite]="mrp_account sale_mrp mrp_stock_analytic mrp_bom_hierarchy mrp_bom_tracking mrp_warehouse_calendar stock_demand_estimate mrp_multi_level mrp_multi_level_estimate quality_control_oca"
MODGROUPS[g4_maintenance]="maintenance maintenance_plan maintenance_equipment_status maintenance_request_purchase maintenance_product"
MODGROUPS[g5_comptabilite]="l10n_cm account_financial_report account_tax_balance partner_statement mis_builder mis_builder_budget mis_builder_cash_flow account_reconcile_oca account_statement_base account_asset_management account_fiscal_year account_lock_date_update account_analytic_required purchase_analytic sale_margin"
MODGROUPS[g6_rh]="hr_attendance hr_holidays hr_skills hr_holidays_public hr_attendance_reason payroll"
MODGROUPS[g7_transverse]="auditlog report_xlsx date_range web_responsive web_environment_ribbon base_automation spreadsheet_dashboard"
ORDER="g1_achats g2_imports_stocks g3_fabrication_planif_qualite g4_maintenance g5_comptabilite g6_rh g7_transverse"
ALL=""; for g in $ORDER; do ALL="$ALL ${MODGROUPS[$g]}"; done
MODGROUPS[g8_tout_ensemble]="$ALL"; ORDER="$ORDER g8_tout_ensemble"

# Modules OCA (leurs propres tests sont exécutés ; ceux d'Odoo ne le sont pas, pour la durée)
OCA_MODULES=$(python3 -c "
import yaml,os
c=yaml.safe_load(open('repos.yaml'))
for r in c['oca']:
    for m in os.listdir(os.path.join('src','oca',r)):
        if os.path.isfile(os.path.join('src','oca',r,m,'__manifest__.py')): print(m)")

$COMPOSE build odoo && $COMPOSE up -d || exit 1
echo "Digest de l'image PostgreSQL (à reporter dans docker-compose.test.yml) :"
docker image inspect postgres:16 --format '{{index .RepoDigests 0}}' | tee test-logs/postgres_digest.txt

ODOO="$COMPOSE exec -T odoo python3 /mnt/src/odoo/odoo-bin -c /etc/odoo/odoo.test.conf"
DEMO=""; $ODOO --help 2>/dev/null | grep -q -- '--with-demo' && DEMO="--with-demo"

{ echo "# Résultats des tests d'installation — $(date -Iseconds)"; echo
  echo "Odoo : $(cd src/odoo && git rev-parse HEAD)"; echo
  echo "| Groupe | Installation | Tests OCA | Erreurs | Échecs |"; echo "|---|---|---|---|---|"; } > test-logs/RESULTS.md

for g in $ORDER; do
  mods=$(echo ${MODGROUPS[$g]} | tr ' ' ',')
  db="fay0a_$g"
  echo "=== $g"
  $ODOO -d "$db" --db-filter="^$db\$" -i "$mods" $DEMO --stop-after-init --log-level=info \
        --logfile="/mnt/logs/$g.install.log"
  inst=$?
  tags=""; for m in ${MODGROUPS[$g]}; do echo "$OCA_MODULES" | grep -qx "$m" && tags="$tags,/$m"; done
  if [ $inst -eq 0 ] && [ -n "$tags" ] && [ "$g" != "g8_tout_ensemble" ]; then
    $ODOO -d "$db" --db-filter="^$db\$" -u "$mods" --test-enable --test-tags="${tags#,}" \
          --stop-after-init --log-level=test --logfile="/mnt/logs/$g.tests.log"
    tst=$?
  else tst="-"; fi
  err=$(grep -hc " ERROR " test-logs/$g.*.log 2>/dev/null | awk "{s+=\$1} END {print s+0}")
  fail=$(grep -hcE "FAIL:|failed, " test-logs/$g.*.log 2>/dev/null | awk "{s+=\$1} END {print s+0}")
  echo "| $g | $([ $inst -eq 0 ] && echo OK || echo ÉCHEC) | $tst | ${err:-0} | ${fail:-0} |" >> test-logs/RESULTS.md
done

echo; cat test-logs/RESULTS.md
echo "Journaux détaillés : test-logs/*.log — pour arrêter : $COMPOSE down -v"
