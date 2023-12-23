import React, { useContext, useEffect, useMemo, useRef } from 'react';
import { read_kline_csv, read_csv } from '../js/reader';
import { ChartContext, Series } from './Chart';

export const Kline = (props) => {
    const { theme } = props;
    const series1 = useRef(null);
    const series2 = useRef(null);
    const parent = useContext(ChartContext);

    // Load kline and trades data
    useEffect(() => {
        read_kline_csv(`./data/kline.csv`).then((res) => {
            if (series1.current && series2.current) {
                series1.current.setData(res);
                series2.current.setData(
                    res.map((x) => {
                        return { time: x.time, value: x.volume };
                    })
                );
                parent.api().timeScale().fitContent();
            }
        });

        read_csv(`./data/trades.csv`).then((v) => {
            const markers = [];
            v.forEach((o) => {
                if (o.Buy === o.Buy) {
                    markers.push({
                        time: o.time,
                        position: 'belowBar',
                        color: '#FF7F7F',
                        shape: 'arrowUp',
                        text: 'B',
                    });
                }
                if (o.Sell === o.Sell) {
                    markers.push({
                        time: o.time,
                        position: 'aboveBar',
                        color: '#40FF3A',
                        shape: 'arrowDown',
                        text: 'S',
                    });
                }
            });
            markers.sort((a, b) => a.time - b.time);
            if (series1.current) series1.current.setMarkers(markers);
        });
    }, []);

    const klineOptions = useMemo(() => {
        if (theme == 'light') {
            return {
                wickUpColor: 'rgb(255, 0, 0)',
                upColor: 'rgba(255, 255, 255, 0)',
                borderUpColor: 'rgb(255, 0, 0)',
                wickDownColor: 'rgb(83, 148, 68)',
                downColor: 'rgb(83, 148, 68)',
                borderDownColor: 'rgb(83, 148, 68)',
            };
        } else {
            return {
                wickUpColor: 'rgb(255, 0, 0)',
                upColor: 'rgba(0, 0, 0, 0)',
                borderUpColor: 'rgb(255, 0, 0)',
                wickDownColor: 'rgb(0, 255, 255)',
                downColor: 'rgb(0, 255, 255)',
                borderDownColor: 'rgb(0, 255, 255)',
            };
        }
    }, [theme]);

    return (
        <>
            <Series
                ref={series1}
                type={'candlestick'}
                data={[]}
                lastValueVisible={false}
                priceLineVisible={false}
                {...klineOptions}
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
