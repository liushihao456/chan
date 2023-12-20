import React, { useEffect, useState } from 'react';
import '../css/legends.css';
import { Chart, Series } from './Chart';
import { read_csv } from '../js/reader';

export const Equity = (props) => {
    const { mainChart, chartOptions } = props;
    const [equity, setEquity] = useState([]);

    useEffect(() => {
        read_csv(`./data/equity.csv`).then((res) => {
            setEquity(
                res.map((o) => {
                    return { time: o.time, value: o.Equity / res[0].Equity };
                })
            );
        });
    }, []);

    return (
        equity.length > 0 && (
            <Chart height="15%" mainChart={mainChart} {...chartOptions}>
                <div className="legend-wrapper">
                    <div className={'legend'}>Equity</div>
                </div>
                <Series
                    type={'line'}
                    data={equity}
                    lastValueVisible={false}
                    priceLineVisible={false}
                    lineWidth={1}
                />
            </Chart>
        )
    );
};
