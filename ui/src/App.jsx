import React, { useMemo, useRef, useState } from 'react';
import './App.css';
import { Chart} from './components/Chart';
import { Equity } from './components/Equity';
import { Kline } from './components/Kline';
import { OverlayIndicators } from './components/OverlayIndicators';
import { SubplotIndicators } from './components/SubplotIndicators';
import { TickChart } from './components/TickChart';
import './css/colors.css';

const App = () => {
    const [theme, setTheme] = useState('dark');
    const chart1 = useRef();

    // useEffect(() => {
    //     read_predicts_csv(`./tickdata/predicts.csv`).then((res) => {
    //         setInds(x => [...x, {name: 'predicts', value: res}]);
    //     });
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
                <OverlayIndicators />
                {
                    // <TickChart />
                }
            </Chart>
            <SubplotIndicators mainChart={chart1} chartOptions={chartOptions} />
            <Equity mainChart={chart1} chartOptions={chartOptions} />
        </div>
    );
};

export default App;
