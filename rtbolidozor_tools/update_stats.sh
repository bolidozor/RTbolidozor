#!/bin/bash
# Manually regenerate cached statistics.
# Usage: ./update_stats.sh
set -e

echo "Regenerating statistics..."
docker exec django_app python manage.py shell -c \
  "from rtbolidozor_backend.tasks import generate_statistics; print(generate_statistics())"
