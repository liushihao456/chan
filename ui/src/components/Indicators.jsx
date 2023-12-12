import React, { useEffect, useRef, useState } from 'react';
import { read_indicator_csv } from '../data/reader';
import { Series } from './Chart';

export const Indicators = (props) => {
    const { freq } = props;
    const [data, setData] = useState({});

    useEffect(() => {
        if (!(freq in data))
            read_indicator_csv(`./data/indicators/${freq}.csv`).then((res) => {
                if (res.length > 0)
                    setData((d) => {
                        return { [freq]: res, ...d };
                    });
            });
    }, [freq]);

    return (
        freq in data &&
        data[freq].map(
            (v, i) =>
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
        )
    );
};
