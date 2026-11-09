#!/usr/bin/env bash
# Fige l'image PostgreSQL de l'environnement de test par son digest.
#
# 1. télécharge l'étiquette de référence (postgres:16) ;
# 2. lit son digest de dépôt (RepoDigests : digest de l'index multi-architecture) ;
# 3. remplace dans docker/docker-compose.test.yml « image: postgres:16 » par
#    « image: postgres:16@sha256:<digest> » (copie de sauvegarde .bak) et affiche la différence.
#
# Si l'image est déjà figée, le script n'écrit rien : il compare le digest figé au digest
# actuel de l'étiquette. Pour changer de digest : --update (décision à tracer dans DECISIONS.md).
#
# Usage : bash scripts/pin_postgres_digest.sh [--update]
set -euo pipefail
cd "$(dirname "$0")/.."
FILE=docker/docker-compose.test.yml
TAG=postgres:16

CURRENT=$(grep -E "^\s*image:\s*postgres:" "$FILE" | head -1 | awk '{print $2}')
[ -n "$CURRENT" ] || { echo "Ligne « image: postgres:… » introuvable dans $FILE" >&2; exit 1; }

docker pull -q "$TAG" >/dev/null
DIGEST=$(docker image inspect "$TAG" --format '{{range .RepoDigests}}{{println .}}{{end}}' \
         | grep -E '^(docker\.io/(library/)?)?postgres@sha256:[0-9a-f]{64}$' | head -1 | sed 's/.*@//')
[ -n "$DIGEST" ] || { echo "Digest introuvable pour $TAG" >&2; exit 1; }
TARGET="$TAG@$DIGEST"

if [[ "$CURRENT" == *@sha256:* ]] && [ "${1:-}" != "--update" ]; then
  if [ "$CURRENT" = "$TARGET" ]; then echo "Déjà figé, à jour : $CURRENT"
  else echo "Figé sur      : $CURRENT"; echo "Digest actuel : $TARGET"
       echo "Aucune modification. Pour mettre à jour : bash $0 --update (puis tracer dans DECISIONS.md)."; fi
  exit 0
fi

cp "$FILE" "$FILE.bak"
sed -i.tmp -E "s|^(\s*image:\s*)postgres:[^ ]*|\1$TARGET|" "$FILE" && rm -f "$FILE.tmp"
diff -u "$FILE.bak" "$FILE" || true
docker compose -f "$FILE" config --images | grep postgres
echo
echo "Image figée : $TARGET"
echo "À faire : vérifier la différence ci-dessus, supprimer $FILE.bak, puis committer :"
echo "  git add $FILE && git commit -m \"Fige l'image PostgreSQL de test par digest\""
echo "et ajouter le digest dans DECISIONS.md (P-002)."
