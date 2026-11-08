# Load test harness

`kubectl apply -f k8s/loadtest/` brings up the Locust master and workers and
the results database. Every run writes its summary to `results-db`, and the
perf dashboard in the `monitoring` namespace reads from it.
