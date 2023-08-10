if (!window._bt_scale_range) {
    window._bt_scale_range = function (range, min, max, pad) {
        "use strict";
        if (min !== Infinity && max !== -Infinity) {
            pad = pad ? (max - min) * .03 : 0;
            range.start = min - pad;
            range.end = max + pad;
        } else console.error('backtesting: scale range error:', min, max, range);
    };
}

clearTimeout(window._bt_autoscale_timeout);

window._bt_autoscale_timeout = setTimeout(function () {
    /**
     * @variable cb_obj `fig_ohlc.x_range`.
     * @variable source `ColumnDataSource`
     * @variable ohlc_range `fig_ohlc.y_range`.
     * @variable volume_range `fig_volume.y_range`.
     */
    "use strict";

    let i = Math.max(Math.floor(cb_obj.start), 0),
        j = Math.min(Math.ceil(cb_obj.end), source.data['high'].length);

    let max = Math.max.apply(null, source.data['high'].slice(i, j)),
        min = Math.min.apply(null, source.data['low'].slice(i, j));
    _bt_scale_range(ohlc_range, min, max, true);

    if (typeof volume_range !== 'undefined') {
        max = Math.max.apply(null, source.data['volume'].slice(i, j));
        _bt_scale_range(volume_range, 0, max * 1.1, false);
    }

    // if (typeof equity_range !== 'undefined') {
    //     min = Math.min.apply(null, source.data['equity'].slice(i, j));
    //     max = Math.max.apply(null, source.data['equity'].slice(i, j));
    //     _bt_scale_range(equity_range, min, max, true);
    // }

    // if (typeof return_range !== 'undefined') {
    //     min = Math.min.apply(null, source.data['eq_return'].slice(i, j));
    //     max = Math.max.apply(null, source.data['eq_return'].slice(i, j));
    //     _bt_scale_range(return_range, min, max, true);
    // }

    // if (typeof indicator_ranges !== 'undefined') {
    //     let keys = Object.keys(indicator_ranges);
    //     for(var count=0;count<keys.length;count++){
    //         if(keys[count]){
    //             max = Math.max.apply(null, source.data[keys[count]+'_max'].slice(i, j));
    //             min = Math.min.apply(null, source.data[keys[count]+'_min'].slice(i, j));
    //             if(min && max){
    //                 _bt_scale_range(indicator_ranges[keys[count]], min, max, true);
    //             }    
    //         }
    //     }
    // }

}, 50);
