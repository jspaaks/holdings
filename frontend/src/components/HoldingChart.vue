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
        t: 60,
        l: 100,
        r: 200,
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
    svg.append('g')
    .attr('transform', `translate(${margins.l},${margins.t})`)
    .append('rect')
    .attr('width', props.width - margins.l - margins.r)
    .attr('height', props.height - margins.t - margins.b)
    .attr('fill', '#fff')

    // bars
    svg.append('g')
    .attr('transform', `translate(${margins.l},${margins.t})`)
    .selectAll('rect')
    .data(buys)
    .join('rect') // 'join' handles enter, update, and exit
    .attr('x', t => x(t.shares_acc))
    .attr('y', t => y(t.price))
    .attr('width', t => x(t.shares))
    .attr('height', t => y(yLims[0]) - y(t.price))
    .attr('fill', 'steelblue');

    // x axis
    svg.append('g')
    .attr('transform', `translate(${margins.l},${props.height - margins.b})`)
    .call(d3.axisBottom(x));

    // y axis
    svg.append('g')
    .attr('transform', `translate(${margins.l},${margins.t})`)
    .call(d3.axisLeft(y));

    // xlabel
    svg.append('text')
    .attr('class', 'x-label')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'central')
    .attr('transform', `translate(${margins.l + (props.width - margins.l - margins.r) / 2}, ${props.height - margins.b / 2})`)
    .text('Net cumulative number of shares');

    // ylabel
    svg.append('text')
    .attr('class', 'y-label')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'central')
    .attr('transform', `translate(${margins.l / 2}, ${margins. t + (props.height - margins.b - margins.t) / 2}) rotate(-90)`)
    .text('Price ($)');

    // title
    svg.append('text')
    .attr('class', 'title')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'central')
    .attr('transform', `translate(${margins.l + (props.width - margins.l - margins.r) / 2}, ${margins.t / 2})`)
    .text(ticker);

    // cost per share
    svg.append('g')
    .attr('transform', `translate(${margins.l},${margins.t})`)
    .append('line')
    .attr('x1', x(0))
    .attr('x2', x(shares))
    .attr('y1', y(cost_per_share))
    .attr('y2', y(cost_per_share))
    .style('stroke', 'black')
    .style('stroke-width', 1)
    .style('stroke-dasharray', '7, 5');

    // cost text
    svg.append('text')
    .attr('text-anchor', 'start')
    .attr('dominant-baseline', 'central')
    .attr('x', props.width - 0.8 * margins.r)
    .attr('y', margins.t)
    .attr('dy', '2em')
    .text('cost:');

    svg.append('text')
    .attr('text-anchor', 'end')
    .attr('dominant-baseline', 'central')
    .attr('x', props.width - 0.1 * margins.r)
    .attr('y', margins.t)
    .attr('dy', '2em')
    .text(`$${cost.toFixed(2)}`);

    if (previous_close) {

        // previous closing price
        svg.append('g')
        .attr('transform', `translate(${margins.l},${margins.t})`)
        .append('line')
        .attr('x1', x(0))
        .attr('x2', x(shares))
        .attr('y1', y(previous_close.price))
        .attr('y2', y(previous_close.price))
        .style('stroke', 'black')
        .style('stroke-width', 1)
        .style('stroke-dasharray', '15, 3');

        const {gain, loss} = calcGainsAndLosses(buys, previous_close.price)

        // gain text
        svg.append('text')
        .attr('text-anchor', 'start')
        .attr('dominant-baseline', 'central')
        .attr('x', props.width - 0.8 * margins.r)
        .attr('y', margins.t)
        .attr('dy', '4em')
        .text('gain:');

        svg.append('text')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'central')
        .attr('x', props.width - 0.1 * margins.r)
        .attr('y', margins.t)
        .attr('dy', '4em')
        .text(`$${gain.toFixed(2)}`);

        // loss text
        svg.append('text')
        .attr('text-anchor', 'start')
        .attr('dominant-baseline', 'central')
        .attr('x', props.width - 0.8 * margins.r)
        .attr('y', margins.t)
        .attr('dy', '6em')
        .text(`loss:`);

        svg.append('text')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'central')
        .attr('x', props.width - 0.1 * margins.r)
        .attr('y', margins.t)
        .attr('dy', '6em')
        .text(`$${loss.toFixed(2)}`);

        // net text
        svg.append('text')
        .attr('text-anchor', 'start')
        .attr('dominant-baseline', 'central')
        .attr('x', props.width - 0.8 * margins.r)
        .attr('y', margins.t)
        .attr('dy', '8em')
        .text(`net:`);

        svg.append('text')
        .attr('text-anchor', 'end')
        .attr('dominant-baseline', 'central')
        .attr('x', props.width - 0.1 * margins.r)
        .attr('y', margins.t)
        .attr('dy', '8em')
        .text(`$${(cost + gain - loss).toFixed(2)}`);
    }

};



onMounted(drawChart);

watch(() => props.holding, drawChart);

</script>

<template>
    <svg ref='chart'></svg>
</template>

<style scoped>
</style>
