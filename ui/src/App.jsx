import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import './App.css';
import { Chart, Series } from './components/Chart';
import './css/colors.css';
import './css/switch.css';
import { read_kline_csv } from './data/reader';

const App = () => {
    const [theme, setTheme] = useState('dark');
    const chart = useRef(null);
    const series1 = useRef(null);
    const series2 = useRef(null);

    const freqs = useMemo(() => ['5min', '30min', 'daily'], []);
    const [freq, setFreq] = React.useState(freqs[0]);

    useEffect(() => {
        read_kline_csv(`./data/${freq}.csv`).then((v) => {
            series1.current.setData(v);
            series2.current.setData(
                v.map((x) => {
                    return { time: x.time, value: x.volume };
                })
            );
            chart.current.timeScale().fitContent();
        });
    }, [freq]);

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
                    <button onClick={() => setTheme((t) => (t == 'dark' ? 'light' : 'dark'))}>theme</button>
                </div>
            </div>
            <Chart ref={chart} {...chartOptions}>
                <Series ref={series1} type={'candlestick'} data={[]} {...klineOptions} />
                <Series ref={series2} type={'histogram'} data={[]} priceFormat={{ type: 'volume' }} priceScaleId="" />
            </Chart>
        </div>
    );
};

export default App;
