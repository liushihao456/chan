import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import './App.css';
import { Chart, Series } from './components/Chart';
import { InlineIndicators } from './components/InlineIndicators';
import { Kline } from './components/Kline';
import { TickChart } from './components/TickChart';
import './css/colors.css';
import { read_csv, read_indicator_csv, read_predicts_csv, read_tick_csv } from './js/reader';
import { RSI } from './js/ta';

const App = () => {
    const [theme, setTheme] = useState('dark');
    const chart1 = useRef();
    const equitySeries = useRef();

    const indicators = useRef({});
    const [inlineInds, setInlineInds] = useState([]);
    const [inds, setInds] = useState([]);
    const [equity, setEquity] = useState([]);

    useEffect(() => {
        read_indicator_csv(`./data/indicators.csv`).then((res) => {
            if (res.length > 0) indicators.current = res;
            else indicators.current = [];
            setInlineInds(indicators.current.filter((v) => v['value'][v['value'].length - 1]['value'] > 2));
            setInds(indicators.current.filter((v) => v['value'][v['value'].length - 1]['value'] <= 2));
        });
    }, []);

    useEffect(() => {
        read_csv(`./data/equity.csv`).then((res) => {
            setEquity(
                res.map((o) => {
                    return { time: o.time, value: o.Equity / res[0].Equity };
                })
            );
        });
    }, []);

    // useEffect(() => {
    //     read_tick_csv(`./tickdata/ticks.csv`).then(res => {
    //         const rsi = RSI(res.map(x => {
    //             return { time: x.time, value: x.last_price };
    //         }), 14);
    //         setInds(x => [...x, {name: 'RSI', value: rsi}]);
    //     });
    // }, []);

    // useEffect(() => {
    //     read_predicts_csv(`./tickdata/predicts.csv`).then((res) => {
    //         console.log(res);
    //         setInds([{name: 'predicts', value: res}]);
    //     });
    //     // read_tick_csv(`./tickdata/ticks.csv`).then(res => {
    //     //     const rsi = RSI(res.map(x => {
    //     //         return { time: x.time, value: x.last_price };
    //     //     }), 14);
    //     //     setInds(x => [...x, {name: 'RSI', value: rsi}]);
    //     // });
    // }, []);

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
            {
                // <div style={{ position: 'absolute', top: '10px', right: '10px' }}>
                //     <button onClick={() => setTheme((t) => (t == 'dark' ? 'light' : 'dark'))}>theme</button>
                // </div>
            }

            <Chart ref={chart1} {...chartOptions}>
                <Kline theme={theme} />
                <InlineIndicators data={inlineInds} />
                {
                    // <TickChart />
                }
            </Chart>
            {inds.map((v, i) => (
                <Chart height="10%" mainChart={chart1} {...chartOptions} key={i}>
                    <div className="legend-wrapper">
                        <div className={'legend'} key={i}>
                            {v['name']}
                        </div>
                    </div>
                    <Series
                        type={'line'}
                        data={v['value']}
                        lastValueVisible={false}
                        priceLineVisible={false}
                        lineWidth={1}
                    />
                </Chart>
            ))}
            {equity.length > 0 && (
                <Chart height="15%" mainChart={chart1} {...chartOptions}>
                    <div className="legend-wrapper">
                        <div className={'legend'}>Equity</div>
                    </div>
                    <Series
                        ref={equitySeries}
                        type={'line'}
                        data={equity}
                        lastValueVisible={false}
                        priceLineVisible={false}
                        lineWidth={1}
                    />
                </Chart>
            )}
        </div>
    );
};

export default App;
