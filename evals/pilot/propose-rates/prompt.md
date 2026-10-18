pricing is spread over `zone_rates.csv`, `weight_bands.csv` and `apply_remote_correction`, and people keep changing one without noticing the others. Is there a simpler way to hold it? Work out what you'd change and tell me — don't change anything yet.
<!-- turn -->
so the change would mean we drop the two separate lookup tables and the correction step, and just have one combined table keyed on both zone and weight band?
