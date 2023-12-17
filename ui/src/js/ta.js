export function RSI(close, period) {
    const rsi_s1 = new Array(close.length);
    const rsi_s2 = new Array(close.length);
    const res = new Array(close.length);
    for (var i = 0; i < close.length; i++) {
        res[i] = {};
        if (i > 0) {
            const diff = close[i].value - close[i - 1].value;
            rsi_s1[i] = diff > 0 ? diff : 0;
            rsi_s2[i] = diff < 0 ? -diff : 0;
        }

        if (i < period + 1) {
            res[i].time = close[i].time;
            res[i].value = NaN;
        } else {
            const maUp = rsi_s1.slice(i - period, i).reduce((p, v) => p + v, 0) / period;
            const maDown = rsi_s2.slice(i - period, i).reduce((p, v) => p + v, 0) / period;
            res[i].time = close[i].time;
            const rs = maUp / maDown;
            res[i].value = 1. - 1. / (1 + rs);
        }
    }
    return res;
}
