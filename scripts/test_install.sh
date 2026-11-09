#!/usr/bin/env bash
# Tests d'installation des modules candidats — Phase 0-A (environnement de TEST jetable).
#
# Garanties :
#   - chaque campagne repart d'un environnement vierge : les volumes du SEUL projet Docker
#     « fayadort-test » sont supprimés au démarrage (confirmation demandée, ou option --yes) ;
#   - chaque groupe utilise des bases neuves au nom unique (campagne + groupe) ; le script
#     s'arrête si une base de ce nom existe déjà : aucune base n'est réutilisée ;
#   - installation et tests automatisés sont exécutés dans DEUX bases distinctes ;
#   - Odoo ne peut joindre que le service « db » de ce projet (aucun port publié) ;
#     le script refuse de démarrer si la configuration pointe vers un autre serveur ;
#   - le code Odoo exécuté est uniquement celui de src/ (commit figé) : vérifié avant la campagne
#     et dans le journal de chaque exécution (« addons paths ») ;
#   - données de démonstration chargées par défaut (conditions des tests OCA) ; --no-demo pour s'en passer.
#
# Préalables : Docker + Docker Compose v2, Python 3 avec PyYAML, `python3 scripts/fetch_repos.py`.
# Usage      : bash scripts/test_install.sh [--yes] [--no-demo] [--only GROUPE1,GROUPE2]
#              (liste des groupes : python3 scripts/test_plan.py --check)
# Résultats  : test-logs/<campagne>/RESULTS.md (+ journaux et JSON par groupe)
set -euo pipefail
cd "$(dirname "$0")/.."

PROJECT=fayadort-test
COMPOSE=(docker compose -p "$PROJECT" -f docker/docker-compose.test.yml)
BASE_IMAGE=fayadort/odoo19-runtime-base:f900094
BASE_CONTEXT="https://github.com/odoo/docker.git#f900094eb7492968332868d686caf22b966592ca:19.0"
TEST_IMAGE=fayadort/odoo19-test:local
die() { echo "ERREUR : $*" >&2; exit 1; }

ASSUME_YES=0; WITH_DEMO=1; ONLY=""
while [ $# -gt 0 ]; do
  case "$1" in
    --yes) ASSUME_YES=1 ;;
    --no-demo) WITH_DEMO=0 ;;
    --only) [ $# -ge 2 ] || die "--only attend une liste de groupes séparés par des virgules"; ONLY="$2"; shift ;;
    *) die "Option inconnue : $1" ;;
  esac
  shift
done

# --- Préalables -----------------------------------------------------------------------------
command -v docker >/dev/null || die "Docker introuvable."
docker compose version >/dev/null 2>&1 || die "Docker Compose v2 introuvable."
python3 -c "import yaml" 2>/dev/null || die "PyYAML absent : pip install pyyaml"
[ -f src/odoo/odoo-bin ] || die "src/odoo absent : lancez python3 scripts/fetch_repos.py"
[ -f docker/odoo.test.conf ] || die "docker/odoo.test.conf absent : lancez python3 scripts/fetch_repos.py"
grep -qx "db_host = db" docker/odoo.test.conf \
  || die "docker/odoo.test.conf doit contenir exactement « db_host = db » (base de test interne uniquement)."
grep -Eq "^\s*ports:" docker/docker-compose.test.yml \
  && die "docker-compose.test.yml ne doit publier aucun port."

# Vérifie que les sources sont aux commits figés
python3 - <<'EOF' || die "Sources différentes de repos.yaml : relancez python3 scripts/fetch_repos.py"
import subprocess, sys, yaml
c = yaml.safe_load(open('repos.yaml'))
items = [('src/odoo', c['odoo']['commit'])] + [(f'src/oca/{k}', v['commit']) for k, v in c['oca'].items()]
bad = [p for p, sha in items
       if subprocess.run(['git', '-C', p, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip() != sha]
if bad: print('Commits inattendus :', bad); sys.exit(1)
EOF

python3 scripts/test_plan.py --check >/dev/null || { python3 scripts/test_plan.py --check; die "Plan de tests invalide."; }
PLAN=$(python3 scripts/test_plan.py --tsv)
if [ -n "$ONLY" ]; then
  ALL_GROUPS=$(cut -f1 <<< "$PLAN")
  for g in ${ONLY//,/ }; do grep -qx -- "$g" <<< "$ALL_GROUPS" || die "Groupe inconnu : $g"; done
  PLAN=$(awk -F'\t' -v only=",$ONLY," 'index(only, "," $1 ",") > 0' <<< "$PLAN")
fi

# --- Remise à zéro de l'environnement de test ---------------------------------------------
CAMPAIGN=$(date +%Y%m%d_%H%M%S)
LOGDIR="test-logs/$CAMPAIGN"
mkdir -p "$LOGDIR"
echo "Campagne $CAMPAIGN : les volumes Docker du projet « $PROJECT » (bases de TEST uniquement) vont être supprimés."
if [ $ASSUME_YES -ne 1 ]; then
  read -r -p "Confirmer la remise à zéro de l'environnement de test ? [o/N] " ans
  [[ "$ans" =~ ^[oOyY]$ ]] || die "Abandon à la demande de l'utilisateur."
fi
"${COMPOSE[@]}" down -v --remove-orphans

# --- Construction des images ----------------------------------------------------------------
docker build -t "$BASE_IMAGE" "$BASE_CONTEXT"
docker build --build-arg BASE_IMAGE="$BASE_IMAGE" -t "$TEST_IMAGE" -f docker/Dockerfile.test docker/
"${COMPOSE[@]}" up -d --wait

DB_IMAGE_REF=$(grep -E "^\s*image:\s*postgres" docker/docker-compose.test.yml | awk '{print $2}')
DB_IMAGE_ID=$(docker inspect "$("${COMPOSE[@]}" ps -q db)" --format '{{.Image}}')
DB_DIGEST=$(docker image inspect "$DB_IMAGE_ID" --format '{{join .RepoDigests ", "}}')
PG_PINNED="NON — à figer (scripts/pin_postgres_digest.sh)"; [[ "$DB_IMAGE_REF" == *@sha256:* ]] && PG_PINNED="oui"
"${COMPOSE[@]}" exec -T odoo cat /opt/fayadort-pip-freeze.txt > "$LOGDIR/pip-freeze.txt"

ODOO=("${COMPOSE[@]}" exec -T odoo python3 /mnt/src/odoo/odoo-bin -c /etc/odoo/odoo.test.conf)
PSQL=("${COMPOSE[@]}" exec -T db psql -U odoo -d postgres -Atc)
# Le code Odoo importable doit provenir exclusivement de /mnt/src (commit figé)
"${COMPOSE[@]}" exec -T odoo python3 -c "
import sys; sys.path.insert(0, '/mnt/src/odoo')
import odoo, odoo.addons
paths = list(odoo.__path__) + list(odoo.addons.__path__)
bad = [p for p in paths if not p.startswith('/mnt/src/')]
print('Chemins odoo :', paths)
sys.exit(1 if bad else 0)" < /dev/null \
  || die "Du code Odoo hors de src/ est importable dans l'image de test (voir chemins ci-dessus)."

DEMO=""
if [ $WITH_DEMO -eq 1 ]; then
  HELP=$("${ODOO[@]}" --help < /dev/null 2>&1 || true)   # capturé d'abord : pas de grep -q dans un tube avec pipefail
  grep -q -- '--with-demo' <<< "$HELP" || die "Option --with-demo introuvable dans odoo-bin --help."
  DEMO="--with-demo"
fi

db_exists() { [ "$("${PSQL[@]}" "SELECT 1 FROM pg_database WHERE datname='$1'")" = "1" ]; }
new_db_name() { echo "t${CAMPAIGN}_$(echo "$1" | tr '[:upper:]-' '[:lower:]_' | cut -c1-30)$2"; }
installed_count() {  # $1 = base, $2 = modules séparés par des virgules
  "${COMPOSE[@]}" exec -T db psql -U odoo -d "$1" -Atc \
    "SELECT count(*) FROM ir_module_module WHERE state='installed' AND name = ANY(string_to_array('$2', ','))"
}
jget() { python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(eval(sys.argv[2], {}, {'d': d}))" "$1" "$2"; }

{
  echo "# Résultats des tests d'installation — campagne $CAMPAIGN"
  echo
  echo "- Odoo : \`$(git -C src/odoo rev-parse HEAD)\` ; OCA : commits de \`repos.yaml\`"
  echo "- Image PostgreSQL : \`$DB_IMAGE_REF\` — digest exécuté \`$DB_DIGEST\` — figée par digest : $PG_PINNED"
  echo "- Données de démonstration : $([ -n "$DEMO" ] && echo 'chargées (--with-demo)' || echo 'NON chargées (--no-demo)')"
  echo "- Code Odoo : vérifié importable uniquement depuis /mnt/src (commit figé) ; contrôle répété dans chaque journal"
  if [ -n "$ONLY" ]; then echo "- **Campagne partielle** : groupes $ONLY"; fi
  echo "- Tests automatisés : ceux des modules **OCA** du groupe (les tests des modules natifs Odoo ne sont pas lancés)"
  echo "- Tests navigateur : ignorés si Chrome est absent de l'image (compteur « nav. ignorés »)"
  echo
  echo "> Les groupes **EVALUATION** (E-*) et **PISTE_SEPAREE** (S-*) sont informatifs : un succès ne vaut pas validation (P-003)."
  echo
  echo "| Groupe | Type | Modules | Installation | Inst. installés | Inst. ERROR / CRITICAL | Tests (exécutés / échecs / erreurs) | Nav. ignorés | Verdict |"
  echo "|---|---|---|---|---|---|---|---|---|"
} > "$LOGDIR/RESULTS.md"

# --- Campagne -------------------------------------------------------------------------------
# Lecture du plan sur le descripteur 3 : les commandes « docker compose exec » lisent l'entrée standard
# et consommeraient sinon les lignes suivantes du plan.
while IFS=$'\t' read -r GROUP KIND MODS TAGS <&3; do
  n_mods=$(echo "$MODS" | tr ',' '\n' | wc -l | tr -d ' ')
  echo "=== $GROUP ($KIND, $n_mods modules)"

  # 1) Installation dans une base neuve
  DB=$(new_db_name "$GROUP" "")
  db_exists "$DB" && die "La base $DB existe déjà : refus de la réutiliser."
  set +e
  "${ODOO[@]}" -d "$DB" --db-filter="^${DB}\$" -i "$MODS" $DEMO --stop-after-init --log-level=info \
      > "$LOGDIR/$GROUP.install.log" 2>&1
  RC_I=$?
  set -e
  python3 scripts/parse_odoo_log.py "$LOGDIR/$GROUP.install.log" > "$LOGDIR/$GROUP.install.json"
  N_INST=0; db_exists "$DB" && N_INST=$(installed_count "$DB" "$MODS")
  E_I=$(jget "$LOGDIR/$GROUP.install.json" "d['error']")
  C_I=$(jget "$LOGDIR/$GROUP.install.json" "d['critical']")
  F_I=$(jget "$LOGDIR/$GROUP.install.json" "len(d['foreign_addons_paths'])")
  if [ "$F_I" != "0" ]; then INST="ÉCHEC (code hors src/)"
  elif [ $RC_I -eq 0 ] && [ "$N_INST" = "$n_mods" ] && [ "$C_I" = "0" ] && [ "$E_I" = "0" ]; then INST=OK
  elif [ $RC_I -eq 0 ] && [ "$N_INST" = "$n_mods" ] && [ "$C_I" = "0" ]; then INST="OK, erreurs à analyser"
  else INST="ÉCHEC (code $RC_I)"; fi

  # 2) Tests automatisés dans une seconde base neuve (seulement si l'installation a réussi)
  TESTS="aucun module OCA (tests natifs non lancés)"; NAV="-"; T_OK=1
  if [ -n "$TAGS" ]; then
    if [[ "$INST" == OK* ]]; then
      DBT=$(new_db_name "$GROUP" "_t")
      db_exists "$DBT" && die "La base $DBT existe déjà : refus de la réutiliser."
      set +e
      "${ODOO[@]}" -d "$DBT" --db-filter="^${DBT}\$" -i "$MODS" $DEMO --test-enable --test-tags="$TAGS" \
          --stop-after-init --log-level=test > "$LOGDIR/$GROUP.tests.log" 2>&1
      RC_T=$?
      set -e
      python3 scripts/parse_odoo_log.py "$LOGDIR/$GROUP.tests.log" > "$LOGDIR/$GROUP.tests.json"
      TESTS=$(jget "$LOGDIR/$GROUP.tests.json" \
        "'aucun bilan (code $RC_T)' if d['tests'] is None else '%d / %d / %d (code $RC_T)' % (d['tests']['run'], d['tests']['failed'], d['tests']['errors'])")
      NAV=$(jget "$LOGDIR/$GROUP.tests.json" "d['browser_tests_skipped']")
      T_OK=$(jget "$LOGDIR/$GROUP.tests.json" \
        "1 if ($RC_T == 0 and d['tests'] is not None and d['tests']['failed'] == 0 and d['tests']['errors'] == 0 and not d['foreign_addons_paths']) else 0")
      if [ "$(jget "$LOGDIR/$GROUP.tests.json" "len(d['foreign_addons_paths'])")" != "0" ]; then
        TESTS="$TESTS — code hors src/ !"
      fi
    else
      TESTS="non lancés (installation en échec)"; T_OK=0
    fi
  fi

  if [[ "$INST" == ÉCHEC* ]] || [ "$T_OK" = "0" ]; then VERDICT="ÉCHEC"
  elif [ "$INST" = "OK" ]; then VERDICT="OK"
  else VERDICT="À ANALYSER"; fi
  [ "$KIND" != "VALIDATION" ] && VERDICT="$VERDICT (informatif)"

  echo "| $GROUP | $KIND | $n_mods | $INST | $N_INST / $n_mods | $E_I / $C_I | $TESTS | $NAV | $VERDICT |" >> "$LOGDIR/RESULTS.md"
done 3<<< "$PLAN"

{
  echo
  echo "Légende : « Inst. installés » = modules du groupe à l'état \`installed\` dans la base après installation."
  echo "« ERROR / CRITICAL » = entrées de journal pendant l'installation (bilans de tests exclus)."
  echo "« Tests » = bilan officiel d'Odoo (\`odoo.tests.result\`) dans une base distincte. Détails : *.log et *.json."
} >> "$LOGDIR/RESULTS.md"

echo; cat "$LOGDIR/RESULTS.md"
echo
echo "Journaux : $LOGDIR/ — environnement laissé actif pour inspection."
echo "Arrêt et suppression des bases de test : docker compose -p $PROJECT -f docker/docker-compose.test.yml down -v"
