| policy | battery life (years) | avg current (uA) | mean error at gateway (0.01 C) | event latency (s) | missed events | TX attempts / day |
|---|---|---|---|---|---|---|
| periodic-10s | 2.40 ± 0.00 | 7.50 | 4.1 | 4 | 0.4% | 9600 |
| periodic-60s | 6.16 ± 0.00 | 2.92 | 5.1 | 28 | 0.6% | 1599 |
| periodic-300s | 8.23 ± 0.00 | 2.18 | 10.0 | 151 | 1.1% | 320 |
| change-trigger(10s) | 5.01 ± 0.00 | 3.58 | 8.2 | 5 | 0.4% | 200 |
| adaptive(10-120s) | 8.08 ± 0.01 | 2.22 | 10.8 | 59 | 0.7% | 178 |
| adaptive(10-300s) | 8.44 ± 0.00 | 2.13 | 13.6 | 146 | 1.0% | 165 |

Sensitivity of battery life (years) to each parameter varied -50%/+50% (link_success 0.7/0.98):

| parameter | periodic-60s lo..hi | adaptive(10-120s) lo..hi |
|---|---|---|
| usable_frac | 3.08..8.80 | 4.04..11.54 |
| sleep_uA | 9.37..4.59 | 14.68..5.57 |
| tx_mA | 6.67..5.72 | 8.17..7.99 |
| tx_ms | 6.67..5.72 | 8.17..7.99 |
| link_success | 5.80..6.28 | 8.01..8.10 |
| rx_mA | 6.40..5.93 | 8.12..8.04 |
| rx_ms | 6.40..5.93 | 8.12..8.04 |
| wake_ms | 6.34..5.99 | 8.27..7.90 |
| wake_mA | 6.34..5.99 | 8.27..7.90 |
| sample_mA | 6.25..6.07 | 8.17..7.99 |
| sample_ms | 6.25..6.07 | 8.17..7.99 |
