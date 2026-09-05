from exporter.models import Account

DSN = "postgresql://replica.internal/billing?target_session_attrs=read-only"


def changed_since(since):
    """Every account with changed_at > since, across all regions, oldest
    first. One cursor over the replica; no batching, no ordering by region."""
    raise NotImplementedError("cursor over the read replica")
