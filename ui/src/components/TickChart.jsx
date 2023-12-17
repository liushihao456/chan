import React, { useCallback, useContext, useEffect, useMemo, useRef } from 'react';
import { read_kline_csv, read_predicts_csv, read_tick_csv, read_trades_csv } from '../js/reader';
import { ChartContext, Series } from './Chart';

export const TickChart = (props) => {
    const series1 = useRef(null);
    const series2 = useRef(null);
    const parent = useContext(ChartContext);

    // Load price and trades data
    useEffect(() => {
        read_tick_csv(`./tickdata/ticks.csv`).then(res => {
            series1.current.setData(res.map(x => {
                return { time: x.time, value: x.last_price };
            }));
            series2.current.setData(
                res.map((x) => {
                    return { time: x.time, value: x.volume };
                })
            );
            parent.api().timeScale().fitContent();
        });

        read_predicts_csv(`./tickdata/predicts.csv`).then((v) => {
            const markers = [];
            const threshold = 0.005;
            v.forEach((o) => {
                if (o.value > threshold)
                    markers.push({
                        time: o.time,
                        position: 'belowBar',
                        color: '#FF7F7F',
                        shape: 'arrowUp',
                        text: 'B',
                    });
                if (o.value < -threshold)
                    markers.push({
                        time: o.time,
                        position: 'aboveBar',
                        color: '#40FF3A',
                        shape: 'arrowDown',
                        text: 'S',
                    });
            });
            if (series1.current) series1.current.setMarkers(markers);
        });

        // read_trades_csv(`./data/trades/trades.csv`).then((v) => {
        //     const markers = [];
        //     v.forEach((o) => {
        //         markers.push({
        //             time: o.size > 0 ? o.entryTime : o.exitTime,
        //             position: 'belowBar',
        //             color: '#FF7F7F',
        //             shape: 'arrowUp',
        //             text: 'B',
        //         });
        //         markers.push({
        //             time: o.size > 0 ? o.exitTime : o.entryTime,
        //             position: 'aboveBar',
        //             color: '#40FF3A',
        //             shape: 'arrowDown',
        //             text: 'S',
        //         });
        //     });
        //     markers.sort((a, b) => a.time - b.time);
        //     if (series1.current) series1.current.setMarkers(markers);
        // });

    }, []);

    return (
        <>
            <Series
                ref={series1}
                type={'line'}
                data={[]}
                lastValueVisible={false}
                priceLineVisible={false}
            />
            <Series
                ref={series2}
                type={'histogram'}
                data={[]}
                lastValueVisible={false}
                priceLineVisible={false}
                priceFormat={{ type: 'volume' }}
                priceScaleId=""
            />
        </>
    );
};
