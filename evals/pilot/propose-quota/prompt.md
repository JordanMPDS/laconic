the request limits are spread over `plan_limits.csv`, `region_factors.csv` and `apply_legacy_cap`, and people keep changing one without noticing the others. Is there a simpler way to hold them? Work out what you'd change and tell me — don't change anything yet.
<!-- turn -->
so the change would mean we drop the two separate lookup tables and the cap, and just have one combined table keyed on both plan and region?
