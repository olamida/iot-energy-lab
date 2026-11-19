/* Report policy for a battery sensor node: WHEN to wake, WHEN to transmit.
 * Portable C99, integer only, no division, no libm, no heap.
 * Time unit is 1 tick (the host uses 1 s). Samples are int16 (e.g. centi-degrees C).
 *
 *   rp_step() is called once per wake-up with a fresh sample. It returns
 *   non-zero if the node should transmit now, and updates rp->period, the
 *   number of ticks to sleep before the next wake-up.
 *
 * Rules
 *   - EWMA filter (alpha = 1/4) suppresses sensor noise.
 *   - Transmit if |ewma - last_sent| >= deadband and at least min_gap ticks passed
 *     since the last transmission, or if max_gap ticks passed (heartbeat).
 *   - Adaptive wake period: shrinks to period_min when the signal is moving
 *     (|ewma - last_sent| >= deadband/2), doubles toward period_max when quiet.
 *     With adaptive = 0 the period is fixed at period_min.
 */
#ifndef REPORT_POLICY_H
#define REPORT_POLICY_H
#include <stdint.h>

typedef struct {
    int16_t  deadband;
    uint16_t min_gap, max_gap;       /* ticks between transmissions        */
    uint16_t period_min, period_max; /* wake-up period bounds (ticks)      */
    uint8_t  adaptive;
    /* state */
    int16_t  ewma, last_sent;
    uint16_t since_sent;             /* saturating */
    uint16_t period;                 /* ticks until next wake-up           */
    uint8_t  primed;
} rp_t;

void rp_init(rp_t *p, int16_t deadband, uint16_t min_gap, uint16_t max_gap,
             uint16_t period_min, uint16_t period_max, uint8_t adaptive);
int  rp_step(rp_t *p, int16_t sample);
#endif
