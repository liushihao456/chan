import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import './App.css';
import { Chart, Series } from './components/Chart';
import { Indicators } from './components/Indicators';
import './css/colors.css';
import './css/switch.css';
import { read_kline_csv, read_trades_csv } from './data/reader';

const App = () => {
    const [theme, setTheme] = useState('dark');
    const chart = useRef(null);
    const series1 = useRef(null);
    const series2 = useRef(null);

    const freqs = useMemo(() => ['5min', '30min', 'daily'], []);
    const [freq, setFreq] = React.useState(freqs[0]);
    const klineRef = useRef({});

    const updateKline = useCallback(async (f) => {
        const kline = klineRef.current;
        if (f in kline && series1.current && series2.current) {
            series1.current.setData(kline[f]);
            series2.current.setData(
                kline[f].map((x) => {
                    return { time: x.time, value: x.volume };
                })
            );
            chart.current.timeScale().fitContent();
        }
    }, []);

    useEffect(() => {
        updateKline(freq);
    }, [freq]);

    // Load kline and trades data
    useEffect(() => {
        freqs.forEach(f => {
            read_kline_csv(`./data/${f}.csv`).then((res) => {
                klineRef.current[f] = res;
                if (f == freq)
                    updateKline(freq);
            })
        });

        read_trades_csv(`./data/trades/trades.csv`).then((v) => {
            const markers = [];
            v.forEach((o) => {
                markers.push({
                    time: o.size > 0 ? o.entryTime : o.exitTime,
                    position: 'belowBar',
                    color: '#FF7F7F',
                    shape: 'arrowUp',
                    text: 'B',
                });
                markers.push({
                    time: o.size > 0 ? o.exitTime : o.entryTime,
                    position: 'aboveBar',
                    color: '#40FF3A',
                    shape: 'arrowDown',
                    text: 'S',
                });
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

    const chartOptions = useMemo(() => {
        return {
            layout: {
                background: {
                    color: theme == 'light' ? 'white' : '#222',
                },
                textColor: theme == 'light' ? 'black' : '#DDD',
            },
            grid: {
                vertLines: {
                    color: theme == 'light' ? '#D6DCDE' : '#444',
                },
            },
        };
    }, [theme]);

    return (
        <div className={'App' + (theme == 'light' ? ' theme-light' : ' theme-dark')}>
            <div style={{ marginBottom: '10px' }}>
                <div className="switch" style={{ order: 2, margin: 0, padding: 1 }}>
                    {freqs.map((f, i) => (
                        <>
                            <button
                                className={'switch-item' + (freq === f ? ' on' : '')}
                                style={{ width: 40 }}
                                onClick={() => setFreq(f)}
                            >
                                {f}
                            </button>
                            {i != freqs.length - 1 && <div className="switch-separator"></div>}
                        </>
                    ))}
                </div>
            </div>

            {
            // <div style={{ position: 'absolute', top: '10px', right: '10px' }}>
            //     <button onClick={() => setTheme((t) => (t == 'dark' ? 'light' : 'dark'))}>theme</button>
            // </div>
            }

            <Chart ref={chart} {...chartOptions}>
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
                <Indicators freq={freq} />
            </Chart>
        </div>
    );
};

export default App;
