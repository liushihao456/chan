import { useEffect, useMemo, useRef, useState } from 'react';
import './App.css';
import { Chart, Series } from './components/Chart';
import { read_kline_csv } from './data/reader';

const initialData = [
    { time: '2018-10-11', value: 52.89 },
    { time: '2018-10-12', value: 51.65 },
    { time: '2018-10-13', value: 51.56 },
    { time: '2018-10-14', value: 50.19 },
    { time: '2018-10-15', value: 51.86 },
    { time: '2018-10-16', value: 51.25 },
];
const currentDate = new Date(initialData[initialData.length - 1].time);

const App = (props) => {
    const { colors: { backgroundColor = 'white', lineColor = '#2962FF', textColor = 'black' } = {} } = props;

    const [chartLayoutOptions, setChartLayoutOptions] = useState({});
    // The following variables illustrate how a series could be updated.
    const series1 = useRef(null);
    const [started, setStarted] = useState(false);

    // const kline = useMemo(() => read_kline_csv('../../data/300340.csv'), []);

    // The purpose of this effect is purely to show how a series could
    // be updated using the `reference` passed to the `Series` component.
    useEffect(() => {
        if (series1.current === null) {
            return;
        }

        if (started) {
            const interval = setInterval(() => {
                currentDate.setDate(currentDate.getDate() + 1);
                const next = {
                    time: currentDate.toISOString().slice(0, 10),
                    value: 53 - 2 * Math.random(),
                };
                series1.current.update(next);
            }, 1000);
            return () => clearInterval(interval);
        }
    }, [started]);

    useEffect(() => {
        setChartLayoutOptions({
            background: {
                color: backgroundColor,
            },
            textColor,
        });
    }, [backgroundColor, textColor]);

    return (
        <div className="App">
            <button type="button" onClick={() => setStarted((current) => !current)}>
                {started ? 'Stop updating' : 'Start updating series'}
            </button>
            <Chart layout={chartLayoutOptions}>
                <Series ref={series1} type={'area'} data={initialData} color={lineColor} />
            </Chart>
        </div>
    );
};

export default App;
