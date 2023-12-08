import React, { useEffect, useRef, useState } from 'react';
import './App.css';
import { Chart, Series } from './components/Chart';
import { read_kline_csv } from './data/reader';

const App = (props) => {
    const { colors: { backgroundColor = 'white', lineColor = '#2962FF', textColor = 'black' } = {} } = props;
    const [chartLayoutOptions, setChartLayoutOptions] = useState({});
    const series1 = useRef(null);
    const [started, setStarted] = useState(false);

    useEffect(() => {
        read_kline_csv('./data/300340.csv', 20221010, 20221015).then((v) => series1.current.setData(v));
    }, []);

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
            <Chart layout={chartLayoutOptions}>
                <Series ref={series1} type={'candlestick'} data={[]} />
            </Chart>
        </div>
    );
};

export default App;
