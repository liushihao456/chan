import React, { useMemo, useRef, useState } from 'react';
import './App.css';
import { Chart} from './components/Chart';
import { Equity } from './components/Equity';
import { Kline } from './components/Kline';
import { OverlayIndicators } from './components/OverlayIndicators';
import { SubplotIndicators } from './components/SubplotIndicators';
import './css/colors.css';

const App = () => {
    const [theme, setTheme] = useState('dark');
    const chart1 = useRef();

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
            rightPriceScale: {
                minimumWidth: 70,
                scaleMargins: {
                    top: 0.02,
                    bottom: 0.1,
                },
            },
        };
    }, [theme]);

    const subplotChartOptions = useMemo(() => {
        return {
            ...chartOptions,
            grid: {
                vertLines: {
                    color: theme == 'light' ? '#D6DCDE' : '#444',
                },
                horzLines: {
                    color: theme == 'light' ? '#D6DCDE' : '#444',
                    visible: true,
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
                <OverlayIndicators />
            </Chart>
            <SubplotIndicators mainChart={chart1} chartOptions={subplotChartOptions} />
            <Equity mainChart={chart1} chartOptions={subplotChartOptions} />
        </div>
    );
};

export default App;
