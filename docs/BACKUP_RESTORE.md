# Backup & Restore Notes

These are minimal, generic runbook notes for self-managed environments.

## Postgres backup

```bash
docker compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" > backup_$(date +%F).sql
```

## Postgres restore

```bash
cat backup_YYYY-MM-DD.sql | docker compose -f docker-compose.prod.yml exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB"
```

## Redis note

Redis in production compose uses AOF persistence. For stricter RPO/RTO, pair with host-level volume snapshots.

## Basic policy suggestion

- Daily automated DB dump.
- Retain 7/14/30-day copies.
- Test restore monthly in a staging environment.
