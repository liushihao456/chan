import React, { useCallback, useEffect, useState } from 'react';
import '../css/legends.css';
import { read_indicator_csv } from '../data/reader';
import { Series } from './Chart';

export const Indicators = (props) => {
    const { freq } = props;
    const [data, setData] = useState({});
    const [indicatorDisabled, setIndicatorDisabled] = useState({});

    useEffect(() => {
        if (!(freq in data))
            read_indicator_csv(`./data/indicators/${freq}.csv`).then((res) => {
                if (res.length > 0)
                    setData((d) => {
                        return { [freq]: res, ...d };
                    });
            });
    }, [freq]);

    const legendOnClick = useCallback(
        (name) => {
            console.log(name);
            console.log(indicatorDisabled[name]);
            if (!indicatorDisabled[name])
                setIndicatorDisabled((v) => {
                    return {
                        ...v,
                        [name]: true,
                    };
                });
            else
                setIndicatorDisabled((v) => {
                    console.log(`setting ${name} to false`);
                    return {
                        ...v,
                        [name]: false,
                    };
                });
        },
        [indicatorDisabled]
    );

    console.log(indicatorDisabled);

    return (
        freq in data && (
            <>
                <div className="legend-wrapper">
                    {data[freq]
                        .map((v) => v['name'])
                        .filter((v, i, a) => a.indexOf(v) === i)
                        .map((v, i) => (
                            <div
                                className={'legend' + (indicatorDisabled[v] ? ' off' : '')}
                                key={i}
                                onClick={() => legendOnClick(v)}
                            >
                                {v}
                            </div>
                        ))}
                </div>
                {data[freq].map(
                    (v, i) =>
                        !indicatorDisabled[v['name']] &&
                        v['value'][v['value'].length - 1]['value'] > 2 && (
                            <Series
                                type={'line'}
                                data={v['value']}
                                lastValueVisible={false}
                                priceLineVisible={false}
                                lineWidth={1}
                                key={i}
                            />
                        )
                )}
            </>
        )
    );
};
