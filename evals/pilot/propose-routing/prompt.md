routing is spread over `service_owners.csv`, `severity_channels.csv` and `apply_payments_override`, and people keep changing one without noticing the others. Is there a simpler way to hold it? Work out what you'd change and tell me — don't change anything yet.
<!-- turn -->
so the change would mean we drop the two separate lookup tables and the override, and just have one combined table keyed on both service and severity?
