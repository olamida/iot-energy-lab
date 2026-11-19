#include "report_policy.h"

static int16_t abs16(int32_t x) { return (int16_t)(x < 0 ? -x : x); }

void rp_init(rp_t *p, int16_t deadband, uint16_t min_gap, uint16_t max_gap,
             uint16_t period_min, uint16_t period_max, uint8_t adaptive)
{
    p->deadband = deadband; p->min_gap = min_gap; p->max_gap = max_gap;
    p->period_min = period_min; p->period_max = period_max; p->adaptive = adaptive;
    p->ewma = 0; p->last_sent = 0; p->since_sent = 0;
    p->period = period_min; p->primed = 0;
}

int rp_step(rp_t *p, int16_t sample)
{
    int send = 0;
    /* ticks elapsed since the previous wake-up (saturating) */
    uint32_t s = (uint32_t)p->since_sent + p->period;
    p->since_sent = (uint16_t)(s > 65535u ? 65535u : s);

    if (!p->primed) {                      /* first sample: send and prime filter */
        p->ewma = sample; p->last_sent = sample; p->since_sent = 0;
        p->primed = 1; p->period = p->period_min;
        return 1;
    }
    p->ewma = (int16_t)(p->ewma + (((int32_t)sample - p->ewma) >> 2));
    int32_t dev = (int32_t)p->ewma - p->last_sent;
    int16_t adev = abs16(dev);

    if (p->since_sent >= p->max_gap || (adev >= p->deadband && p->since_sent >= p->min_gap)) {
        send = 1;
        p->last_sent = p->ewma;
        p->since_sent = 0;
        adev = 0;
    }
    if (p->adaptive) {
        if (adev >= (p->deadband >> 1)) {
            p->period = p->period_min;
        } else {
            uint32_t d = (uint32_t)p->period << 1;
            p->period = (uint16_t)(d > p->period_max ? p->period_max : d);
        }
    } else {
        p->period = p->period_min;
    }
    return send;
}
