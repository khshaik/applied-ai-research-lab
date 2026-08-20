# Calibration Implementation Revision Log v1.0

## Attempt 1

The locked runner verified the lock and computed decisions in memory, then stopped with `ENOENT` while creating `calibration/results/calibration_v1.0`. The parent `results` directory did not exist and `mkdirSync` used `recursive: false`.

No result file was created, no metric or gate result was printed, and no scientific output was inspected.

## Authorized correction

Change exactly:

```text
mkdirSync(resultDir, {recursive:false})
```

to:

```text
mkdirSync(resultDir, {recursive:true})
```

No case, reference label, policy mapping, threshold, loss weight, metric, gate, or analysis rule changed. A superseding v1.2 lock is required before the second execution attempt.
