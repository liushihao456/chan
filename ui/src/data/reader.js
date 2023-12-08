
export async function read_kline_csv(fname, start_date, end_date) {
    const res = await fetch(fname);
    const text = await res.text();

    const result = [];
    const lines = text.split('\n');
    const headers = lines[0].split(',');

    for (var i = 1; i < lines.length; i++) {
        const obj = {};
        const l = lines[i].split(',');
        if (l.length < headers.length)
            continue;
        let date = 0, year = 0, month = 0, day = 0, hour = 0, minute = 0, sec = 0;
        for (var j = 0; j < headers.length; j++) {
            if (headers[j] == 'TradingDay') {
                year = +l[j].substring(0, 4);
                month = +l[j].substring(4, 6);
                day = +l[j].substring(6, 8);
                // obj['time'] = `${l[j].substring(0, 4)}-${l[j].substring(4, 6)}-${l[j].substring(6, 8)}`;
                date = parseInt(l[j]);
            }
            if (headers[j] == 'TradingTime') {
                if (l[j].length == 8) {
                    hour = +l[j].substring(0, 1);
                    minute = +l[j].substring(1, 3);
                    sec = +l[j].substring(3, 5);
                } else {
                    hour = +l[j].substring(0, 2);
                    minute = +l[j].substring(2, 4);
                    sec = +l[j].substring(4, 6);
                }
            }
            if (headers[j] == 'Open')
                obj['open'] = parseFloat(l[j]);
            if (headers[j] == 'High')
                obj['high'] = parseFloat(l[j]);
            if (headers[j] == 'Low')
                obj['low'] = parseFloat(l[j]);
            if (headers[j] == 'Close')
                obj['close'] = parseFloat(l[j]);
            if (headers[j] == 'Volume')
                obj['volume'] = parseFloat(l[j]);
        }
        const t = new Date(year, month - 1, day, hour, minute, sec);
        obj['time'] = (t.getTime() - t.getTimezoneOffset() * 60000) / 1000;
        if ((!start_date || date >= start_date) && (!end_date || date <= end_date))
            result.push(obj);
    }

    return result;
}
