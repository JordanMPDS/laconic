"""Where an alert goes: the owning team from the service, the channel from the
severity, then the payments override."""
import csv
from pathlib import Path

HERE = Path(__file__).parent
FINANCE_SERVICES = {"payments", "ledger"}
URGENT = {"sev1", "sev2"}


def _load(name, key, value):
    with (HERE / name).open() as f:
        return {r[key]: r[value] for r in csv.DictReader(f)}


OWNERS = _load("service_owners.csv", "service", "team")
CHANNELS = _load("severity_channels.csv", "severity", "channel")


def apply_payments_override(service, severity, team, channel):
    """Urgent money-path alerts page finance on-call as well as the owner,
    because billing's rotation is not staffed overnight."""
    if service in FINANCE_SERVICES and severity in URGENT:
        return "finance-oncall", "page"
    return team, channel


def route(service, severity):
    team = OWNERS[service]
    channel = CHANNELS[severity]
    return apply_payments_override(service, severity, team, channel)
