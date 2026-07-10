# Disney Agent Support Tickets — Incident Report

## Provenance
Source:      ticket-sample · extracted 2026-07-10T21:59:38.829880+00:00
Volume:      15 extracted → 15 valid (0 discarded)
Calibration: calibrated · threshold 0.2 · taxonomy v1 · reviewed_by: None
PII:         not redacted

## Executive summary
13 actionable tickets collapsed into 4 root-cause incidents; 2 deflected to product.

## Incidents (ranked by severity × volume)
  ID                               TIX  DECL   EFF  FLAG
  ci_cd/checkout-service             4    P2    P1  SUPPRESSED
  auth/post-renewal                  3    P2    P2  SUPPRESSED
  api_gateway/recommendations        3    P1    P2  INFLATED
  email_delivery                     3    P3    P3  ALIGNED  (cross-source)

## Priority gaps (most actionable)
  SUPPRESSED  ci_cd/checkout-service — declared P2, behaves like P1 (recurs 4×)
  SUPPRESSED  auth/post-renewal — declared P2, behaves like P2 (recurs 3×)
  INFLATED    api_gateway/recommendations — declared P1, behaves like P2 (recurs 2×)

## Playbooks
  • ci_cd/checkout-service [medium/unverified]
    root cause: Flaky integration test hangs the pipeline instead of failing fast; recurs and is never root-caused because it is deprioritized each time.
    evidence: TCK-10231, TCK-10236, TCK-10232, TCK-10241
  • auth/post-renewal [medium/unverified]
    root cause: Login session/token is likely invalidated by the renewal billing webhook before the auth service refreshes it.
    evidence: TCK-10235, TCK-10238, TCK-10243
  • api_gateway/recommendations [medium/unverified]
    root cause: Intermittent 502s on the recommendations endpoint correlate with traffic peaks — likely connection-pool exhaustion or a downstream timeout under load.
    evidence: TCK-10233, TCK-10237, TCK-10242
  • email_delivery [high/unverified]
    root cause: Rising SES bounce rate on transactional emails points to a sending-domain reputation or template issue, not a one-off delay.
    evidence: TCK-10234, TCK-10239, TCK-10245

## Deflected / Unknown
  deflect  TCK-10240  Feature request: dark mode for kids profile screen
  deflect  TCK-10244  Can I get a bigger avatar image size option?

## Calibration appendix
  Calibrated via --eval against cluster_hint labels (see learn output for F1).
