import { createChart } from 'lightweight-charts';
import React, { createContext, forwardRef, useContext, useEffect, useRef, useState } from 'react';

const Context = createContext();

export function Chart(props) {
    const [container, setContainer] = useState(false);
    return (
        <div ref={(element) => setContainer(element)} style={{ flexGrow: 1 }}>
            {container && <ChartContainer {...props} container={container} />}
        </div>
    );
}

export const ChartContainer = forwardRef((props, ref) => {
    const { children, container, layout, ...rest } = props;

    const chartApiRef = useRef({
        api() {
            if (!this._api) {
                this._api = createChart(container, {
                    ...rest,
                    layout,
                    width: container.clientWidth,
                    height: container.clientHeight,
                    grid: {
                        vertLines: {
                            style: 3,
                        },
                        horzLines: {
                            visible: false,
                        },
                    },
                    timeScale: {
                        timeVisible: true,
                        secondsVisible: false,
                    },
                });
                this._api.timeScale().fitContent();
            }
            return this._api;
        },
        free() {
            if (this._api) {
                this._api.remove();
            }
        },
    });

    useEffect(() => {
        const chartApi = chartApiRef.current;
        const chart = chartApi.api();

        const handleResize = () => {
            chart.applyOptions({
                ...rest,
                width: container.clientWidth,
            });
        };

        window.addEventListener('resize', handleResize);
        return () => {
            window.removeEventListener('resize', handleResize);
            chart.remove();
        };
    }, []);

    useEffect(() => {
        chartApiRef.current.api().applyOptions(rest);
        if (ref) ref.current = chartApiRef.current.api();
    }, []);

    useEffect(() => {
        chartApiRef.current.api().applyOptions({ layout });
    }, [layout]);

    return <Context.Provider value={chartApiRef.current}>{props.children}</Context.Provider>;
});
ChartContainer.displayName = 'ChartContainer';

export const Series = forwardRef((props, ref) => {
    const parent = useContext(Context);
    const seriesRef = useRef({
        api() {
            if (!this._api) {
                const { children, data, type, ...rest } = props;
                if (type == 'area') this._api = parent.api().addAreaSeries(rest);
                else if (type == 'bar') this._api = parent.api().addBarSeries(rest);
                else if (type == 'baseline') this._api = parent.api().addBaselineSeries(rest);
                else if (type == 'candlestick') this._api = parent.api().addCandlestickSeries(rest);
                else if (type == 'histogram') this._api = parent.api().addHistogramSeries(rest);
                else if (type == 'line') this._api = parent.api().addLineSeries(rest);
                else throw Error(`${type} series is not supported.`);
                this._api.setData(data);
            }
            return this._api;
        },
        free() {
            if (this._api) {
                parent.free();
            }
        },
    });

    useEffect(() => {
        const series = seriesRef.current;
        const { children, data, ...rest } = props;
        series.api().applyOptions(rest);
        if (ref) ref.current = series.api();

        return () => series.free();
    }, []);

    return <Context.Provider value={seriesRef.current}>{props.children}</Context.Provider>;
});
Series.displayName = 'Series';
