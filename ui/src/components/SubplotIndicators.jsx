import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import '../css/legends.css';
import { read_indicator_csv } from '../js/reader';
import { Chart, Series } from './Chart';

export const SubplotIndicators = (props) => {
    const { mainChart, chartOptions } = props;
    const [data, setData] = useState([]);
    const colors = useRef({});

    useEffect(() => {
        read_indicator_csv(`./data/subplot_indicators.csv`).then((res) => {
            if (res.length > 0) setData(res);
            else setData([]);
        });
    }, []);

    // Original: [{'bbands', [19.7, 19.9, ...]}, {'bbands', [21.2, 21.8, ...]}, ...]
    // Array of objects of name -> value
    // Combined: [{'bbands', [[19.7, 19.9, ...], [21.2, 21.8, ...]]}, ...]
    // Array of objects of name -> values
    const combinedInds = useMemo(() => {
        const combined = [];
        data.forEach((v) => {
            const f = combined.find((e) => e.name == v.name);
            if (f) f.values.push(v.value);
            else combined.push({ name: v.name, values: [v.value] });
        });
        return combined;
    }, [data]);

    const getRandomColor = useCallback(() => {
        var letters = '0123456789ABCDEF';
        var color = '#';
        for (var i = 0; i < 6; i++) {
            color += letters[Math.floor(Math.random() * 16)];
        }
        return color;
    }, []);

    const getIndicatorColor = useCallback((name) => {
        if (!(name in colors.current)) colors.current[name] = getRandomColor();
        return colors.current[name];
    }, []);

    return (
        <>
            {combinedInds.map((v, i) => (
                <Chart height="10%" mainChart={mainChart} {...chartOptions} key={i}>
                    <div className="legend-wrapper">
                        <div className={'legend'} key={i}>
                            {v['name']}
                        </div>
                    </div>
                    {v['values'].map((v2, i2) => (
                        <Series
                            type={'line'}
                            data={v2}
                            lastValueVisible={false}
                            priceLineVisible={false}
                            lineWidth={1}
                            color={getIndicatorColor(i2)}
                            key={i2}
                        />
                    ))}
                </Chart>
            ))}
        </>
    );
};
