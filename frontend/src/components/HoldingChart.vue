<script setup lang='ts'>
import type { Holding, Buy } from '../types'

import { onMounted, ref, watch } from 'vue';
import * as d3 from 'd3';

const props = withDefaults(defineProps<{
    holding: Holding,
    width?: number,
    height?: number,
}>(), {width: 500, height: 275});

const chart = ref(null);

const calcYLims = (min_price: number, max_price: number, previous_close_price?: number) => {
    const factor = 0.1;
    let lims: [number, number] = [min_price, max_price];
    if (previous_close_price && previous_close_price < min_price) {
        lims[0] = previous_close_price;
    }
    if (previous_close_price && previous_close_price > max_price) {
        lims[1] = previous_close_price;
    }
    if (lims[0] == lims[1]) {
        lims[0] = min_price - 0.5;
        lims[1] = min_price + 0.5;
    } else {
        const buffer = factor * (lims[1] - lims[0]);
        lims[0] = lims[0] - buffer > 0 ? lims[0] - buffer : 0;
        lims[1] = lims[1] + buffer;
    }
    return lims
}

const calcGainsAndLosses = (buys: Buy[], price: number) => {
    const sum = (arr: number[]) => arr.reduce((acc: number, curr: number) => acc + curr, 0)
    const gains = buys.filter(b => price > b.price)
    const losses = buys.filter(b => price < b.price)
    return {
        gain: sum(gains.map(g => (price - g.price) * g.shares)),
        loss: sum(losses.map(l => (l.price - price) * l.shares))
    }
}

const drawChart = () => {

    let {
        buys,
        cost,
        cost_per_share,
        id: ticker,
        max_price,
        min_price,
        previous_close,
        shares } = props.holding;

    const yLims = calcYLims(min_price, max_price, previous_close && previous_close.price)

    const margins = {
        b: 60,
        t: 50,
        l: 100,
        r: 230,
    };

    // select the DOM element using the ref's value
    const svg = d3.select(chart.value);

    // clear previous renders to prevent duplicate charts on updates
    svg.selectAll('*').remove();

    // set svg dimensions
    svg.attr('width', props.width)
    .attr('height', props.height)
    .style('background-color', 'ddd');

    // define scales
    const x = d3.scaleLinear()
    .domain([0, shares])
    .nice()
    .range([0, props.width - margins.l - margins.r]);

    const y = d3.scaleLinear()
    .domain(yLims)
    .range([props.height - margins.t - margins.b, 0]);

    // charting area
    const chartgroup = svg.append('g')
    .attr('id', 'chartgroup')
    .attr('transform', `translate(${margins.l},${margins.t})`)

    chartgroup.append('g')
    .attr('id', 'chartbg')
    .append('rect')
    .attr('width', props.width - margins.l - margins.r)
    .attr('height', props.height - margins.t - margins.b)
    .attr('fill', '#fff')

    // bars
    chartgroup.append('g')
    .attr('id', 'barsgroup')
    .selectAll('rect')
    .data(buys)
    .join('rect') // 'join' handles enter, update, and exit
    .attr('x', t => x(t.shares_acc))
    .attr('y', t => y(t.price))
    .attr('width', t => x(t.shares))
    .attr('height', t => y(yLims[0]) - y(t.price))
    .attr('fill', 'steelblue');

    // x axis
    chartgroup.append('g')
    .attr('id', 'xaxis')
    .attr('transform', `translate(0,${props.height - margins.b - margins.t})`)
    .call(d3.axisBottom(x).ticks(5));

    // y axis
    chartgroup.append('g')
    .attr('id', 'yaxis')
    .call(d3.axisLeft(y).ticks(5));

    // xlabel
    chartgroup.append('g')
    .attr('id', 'xlabel')
    .attr('transform', `translate(${(props.width - margins.l - margins.r) / 2}, ${props.height - margins.t - 0.35 * margins.b})`)
    .append('text')
    .attr('class', 'xlabel')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .text('Net cumulative number of shares');

    // ylabel
    chartgroup.append('g')
    .attr('id', 'ylabel')
    .attr('transform', `translate(${-0.5 * margins.l}, ${(props.height - margins.b - margins.t) / 2}) rotate(-90)`)
    .append('text')
    .attr('class', 'ylabel')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .text('Price ($)');

    // title
    chartgroup.append('g')
    .attr('id', 'title')
    .attr('transform', `translate(${(props.width - margins.l - margins.r) / 2}, ${-0.5 * margins.t + 3})`)
    .append('text')
    .attr('class', 'title')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'middle')
    .text(ticker);

    // cost per share line
    const cpsgroup = chartgroup.append('g')
    .attr('id', 'cpsgroup')

    cpsgroup.append('line')
    .attr('x1', x(0))
    .attr('x2', x(shares))
    .attr('y1', y(cost_per_share))
    .attr('y2', y(cost_per_share))
    .style('stroke', 'black')
    .style('stroke-width', 1)
    .style('stroke-dasharray', '7, 5');

    // cost per share text
    cpsgroup.append('text')
    .attr('class', 'chart-annotation')
    .attr('text-anchor', 'start')
    .attr('dominant-baseline', 'middle')
    .attr('x', x(shares))
    .attr('dx', '0.5em')
    .attr('y', y(cost_per_share))
    .attr('dy', '0em')
    .text('cps');

    // table group
    const tablegroup = svg.append('g')
    .attr('id', 'tablegroup')
    .attr('transform', `translate(${props.width - margins.r},${margins.t + 40})`)

    // '%' text
    tablegroup.append('text')
    .attr('class', 'table-elem')
    .attr('text-anchor', 'start')
    .attr('dominant-baseline', 'middle')
    .attr('x', 0.575 * margins.r)
    .attr('y', 0)
    .attr('dy', '0em')
    .text('%');

    // '$' text
    tablegroup.append('text')
    .attr('class', 'table-elem')
    .attr('text-anchor', 'start')
    .attr('dominant-baseline', 'middle')
    .attr('x', 0.85 * margins.r)
    .attr('y', 0)
    .attr('dy', '0em')
    .text('$');

    // cost text
    tablegroup.append('text')
    .attr('class', 'table-elem')
    .attr('text-anchor', 'end')
    .attr('dominant-baseline', 'middle')
    .attr('x', 0.4 * margins.r)
    .attr('y', 0)
    .attr('dy', '1.5em')
    .text('cost');

    // cost absolute number
    tablegroup.append('text')
    .attr('class', 'table-elem')
    .attr('text-anchor', 'end')
    .attr('dominant-baseline', 'middle')
    .attr('x', 0.9 * margins.r)
    .attr('y', 0)
    .attr('dy', '1.5em')
    .text(`${cost.toFixed(0)}`);

    if (previous_close) {

        // previous closing price group
        const pricegroup = chartgroup.append('g')
        .attr('id', 'pricegroup')

        // previous closing price line
        pricegroup.append('line')
        .attr('x1', x(0))
        .attr('x2', x(shares))
        .attr('y1', y(previous_close.price))
        .attr('y2', y(previous_close.price))
        .style('stroke', 'black')
        .style('stroke-width', 1)
        .style('stroke-dasharray', '15, 3');

        // previous closing price text
        pricegroup.append('text')
        .attr('class', 'chart-annotation')
        .attr('text-anchor', 'start')
        .attr('dominant-baseline', 'middle')
        .attr('x', x(shares))
        .attr('dx', '0.5em')
        .attr('y', y(previous_close.price))
        .attr('dy', '0em')
        .text('price');

        const {gain, loss} = calcGainsAndLosses(buys, previous_close.price)

        // gain text
        tablegroup.append('text')
        .attr('class', 'table-elem')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0.4 * margins.r)
        .attr('y', 0)
        .attr('dy', '3em')
        .text('gain');

        // gain percent
        tablegroup.append('text')
        .attr('class', 'table-elem')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0.625 * margins.r)
        .attr('y', 0)
        .attr('dy', '3em')
        .text(`${(100 * gain / cost).toFixed(1)}`);

        // gain absolute number
        tablegroup.append('text')
        .attr('class', 'table-elem')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0.9 * margins.r)
        .attr('y', 0)
        .attr('dy', '3em')
        .text(`${gain.toFixed(0)}`);

        // loss text
        tablegroup.append('text')
        .attr('class', 'table-elem')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0.4 * margins.r)
        .attr('y', 0)
        .attr('dy', '4.5em')
        .text(`loss`);

        // loss percent
        tablegroup.append('text')
        .attr('class', 'table-elem')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0.625 * margins.r)
        .attr('y', 0)
        .attr('dy', '4.5em')
        .text(`${(100 * loss / cost).toFixed(1)}`);

        // loss absolute number
        tablegroup.append('text')
        .attr('class', 'table-elem')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0.9 * margins.r)
        .attr('y', 0)
        .attr('dy', '4.5em')
        .text(`${loss.toFixed(0)}`);

        // net text
        tablegroup.append('text')
        .attr('class', 'table-elem')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0.4 * margins.r)
        .attr('y', 0)
        .attr('dy', '6em')
        .text(`net`);

        // net absolute number
        tablegroup.append('text')
        .attr('class', 'table-elem')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'middle')
        .attr('x', 0.9 * margins.r)
        .attr('y', 0)
        .attr('dy', '6em')
        .text(`${(cost + gain - loss).toFixed(0)}`);
    }
};



onMounted(drawChart);

watch(() => props.holding, drawChart);

</script>

<template>
    <svg ref='chart'></svg>
</template>

<style>

.chart-annotation {
    font-size: small;
}
.table-elem {
    font-size: small;
}
.xlabel, .ylabel {
    font-size: medium;
}
</style>
