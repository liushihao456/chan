import React, { useCallback, useEffect, useRef, useState } from 'react';
import '../css/legends.css';
import { Series } from './Chart';

export const InlineIndicators = (props) => {
    const { data } = props;
    const [indicatorDisabled, setIndicatorDisabled] = useState({});
    const colors = useRef({});

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

    const legendOnClick = useCallback(
        (name) => {
            if (!indicatorDisabled[name])
                setIndicatorDisabled((v) => {
                    return {
                        ...v,
                        [name]: true,
                    };
                });
            else
                setIndicatorDisabled((v) => {
                    return {
                        ...v,
                        [name]: false,
                    };
                });
        },
        [indicatorDisabled]
    );

    return (
        data.length > 0 && (
            <>
                <div className="legend-wrapper">
                    {data
                        .filter((v) => v['value'][v['value'].length - 1]['value'] > 2)
                        .map((v) => v['name'])
                        .filter((v, i, a) => a.indexOf(v) === i)
                        .map((v, i) => (
                            <div
                                className={'legend' + (indicatorDisabled[v] ? ' off' : ' on')}
                                key={i}
                                onClick={() => legendOnClick(v)}
                                style={{ color: getIndicatorColor(v) }}
                            >
                                {v}
                            </div>
                        ))}
                </div>
                {data
                    .map((v, i) => (
                        v['value'][v['value'].length - 1]['value'] > 2 && !indicatorDisabled[v['name']] &&
                        <Series
                            type={'line'}
                            data={v['value']}
                            lastValueVisible={false}
                            priceLineVisible={false}
                            lineWidth={1}
                            color={getIndicatorColor(v['name'])}
                            key={i}
                        />
                    ))}
            </>
        )
    );
};
