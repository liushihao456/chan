import { createChart, CrosshairMode } from 'lightweight-charts';
import React, { createContext, forwardRef, useContext, useEffect, useRef, useState } from 'react';

export const ChartContext = createContext();

export const Chart = forwardRef((props, ref) => {
    const { height, ...rest } = props;
    const [container, setContainer] = useState(false);
    const style = height ? { height: height, marginTop: '10px' } : { flexGrow: 1, height: '1px' };
    return (
        <div
            ref={(element) => setContainer(element)}
            style={{ ...style, position: 'relative' }}
        >
            {container && <ChartContainer {...rest} timeScale={height ? {visible: false} : {}} ref={ref} container={container} />}
        </div>
    );
});

export const ChartContainer = forwardRef((props, ref) => {
    const { children, container, mainChart, ...rest } = props;

    const chartApiRef = useRef({
        api() {
            if (!this._api) {
                this._api = createChart(container, {
                    ...rest,
                    width: container.clientWidth,
                    height: container.clientHeight,
                    crosshair: {
                        mode: CrosshairMode.Normal,
                    },
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
                        secondsVisible: true,
                        fixLeftEdge: true,
                        fixRightEdge: true,
                    },
                });
                this._api.timeScale().fitContent();

                if (mainChart && mainChart.current) {
                    mainChart.current.timeScale().subscribeVisibleLogicalRangeChange(timeRange => {
                        this._api.timeScale().setVisibleLogicalRange(timeRange);
                    });

                    // this._api.timeScale().subscribeVisibleLogicalRangeChange(timeRange => {
                    //     mainChart.current.timeScale().setVisibleLogicalRange(timeRange);
                    // });
                }

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

        const observer = new ResizeObserver((entries) => {
            for (const entry of entries) {
                chart.resize(entry.contentRect.width, entry.contentRect.height);
            }
        });
        observer.observe(container);
        return () => {
            observer.unobserve(container);
            chartApi.free();
        };
    }, []);

    // useEffect(() => {
    //     // if (theme == 'dark') {
    //     //     chartApiRef.current.api().priceScale().applyOptions({borderColor: '#71649C'});
    //     //     chartApiRef.current.api().timeScale().applyOptions({borderColor: '#71649C'});
    //     // }
    // }, [theme]);

    useEffect(() => {
        if (ref) ref.current = chartApiRef.current.api();
    }, []);

    useEffect(() => {
        chartApiRef.current.api().applyOptions(rest);
    }, [rest]);

    return <ChartContext.Provider value={chartApiRef.current}>{props.children}</ChartContext.Provider>;
});

export const Series = forwardRef((props, ref) => {
    const { children, data, type, ...rest } = props;
    const parent = useContext(ChartContext);
    const seriesRef = useRef({
        api() {
            if (!this._api) {
                if (type == 'area') this._api = parent.api().addAreaSeries(rest);
                else if (type == 'bar') this._api = parent.api().addBarSeries(rest);
                else if (type == 'baseline') this._api = parent.api().addBaselineSeries(rest);
                else if (type == 'candlestick') this._api = parent.api().addCandlestickSeries(rest);
                else if (type == 'histogram') this._api = parent.api().addHistogramSeries(rest);
                else if (type == 'line') this._api = parent.api().addLineSeries(rest);
                else throw Error(`${type} series is not supported.`);
                if (
                    type == 'histogram' &&
                    rest.priceFormat &&
                    rest.priceFormat.type &&
                    rest.priceFormat.type == 'volume'
                ) {
                    this._api.priceScale().applyOptions({
                        // set the positioning of the volume series
                        scaleMargins: {
                            top: 0.8, // highest point of the series will be 80% away from the top
                            bottom: 0,
                        },
                    });
                }
                this._api.setData(data);
            }
            return this._api;
        },
        free() {
            if (parent.api() && this._api) {
                try {
                    parent.api().removeSeries(this._api);
                } catch (e) {}
            }
        },
    });

    useEffect(() => {
        const series = seriesRef.current;
        if (ref) ref.current = series.api();

        return () => series.free();
    }, []);

    useEffect(() => {
        seriesRef.current.api().applyOptions(rest);
    }, [rest]);

    return <ChartContext.Provider value={seriesRef.current}>{props.children}</ChartContext.Provider>;
});
