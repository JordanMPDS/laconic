# scratch

Working space for the training jobs. Everything here lives on this machine
only: nothing under scratch/ is synced or backed up.

- `shards/` - preprocessed training shards. The preprocessing job rebuilds
  them from the raw images in about twenty minutes.
- `tmp/` - per-run temporaries. Safe to delete at any time.
- `cache/` - downloaded model weights, fetched again on the next run.
- `labels/` - the hand labels from the annotation vendor, six weeks of their
  work. Their contract ended in October and they deleted their copy, so this
  directory is the only one. `train.yaml` reads it as `labels_dir`.
