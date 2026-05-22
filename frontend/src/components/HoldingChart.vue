<script setup lang='ts'>
import type { Holding, Lot, CostBasisMethod } from '../types';
import { onMounted, ref, reactive, watch } from 'vue';
import * as d3 from 'd3';

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

const drawChart = () => {

    const showCostBarTitle = (lot: Lot) => {
        return `cost: ${Number.isInteger(lot.shares) ? lot.shares : lot.shares.toFixed(3)} @ $${(lot.price).toFixed(2)} = $${(lot.shares * lot.price).toFixed(2)} on ${lot.date}`;
    }

    const sortLots = (lots: Lot[], costBasisMethod: CostBasisMethod) => {

        const fifoSorter = (left: Lot, right: Lot) => {
            if (left.date < right.date) return -1;
            if (left.date > right.date) return 1;
            if (left.order < right.order) return -1;
            if (left.order > right.order) return 1;
            return 0;
        }

        const hifoSorter = (left: Lot, right: Lot) => {
            if (left.price > right.price) return -1;
            if (left.price < right.price) return 1;
            return 0;
        }

        const sortedLots = lots.sort({
            'FIFO': fifoSorter,
            'HIFO': hifoSorter
        }[costBasisMethod]);

        let acc = 0;
        for (let lot of sortedLots) {
            lot.shares_acc = acc;
            acc += lot.shares;
        }

        return sortedLots;
    }

    let {
        lots,
        cost_per_share: costPerShare,
        id: ticker,
        max_price: maxPrice,
        min_price: minPrice,
        previous_close: previousClose,
        shares } = props.holding;

    const yLims = calcYLims(minPrice, maxPrice, previousClose && previousClose.price)

    const sortedLots = sortLots(lots, locals.costBasisMethod);

    const margins = {
        b: 60,
        t: 50,
        l: 60,
        r: 60,
    };

    // select the DOM element using the ref's value
    const svg = d3.select(chart.value);

    // clear previous renders to prevent duplicate charts on updates
    svg.selectAll('*').remove();


    // set svg dimensions
    svg.attr('width', width)
    .attr('height', height)
    .style('background-color', 'ddd');

    // define scales
    const x = d3.scaleLinear()
    .domain([0, shares])
    .range([0, width - margins.l - margins.r]);

    const y = d3.scaleLinear()
    .domain(yLims)
    .range([height - margins.t - margins.b, 0]);

    // charting area
    const chartgroup = svg.append('g')
        .attr('id', 'chartgroup')
        .attr('transform', `translate(${margins.l},${margins.t})`)

    chartgroup.append('g')
    .attr('id', 'chartbg')
    .append('rect')
        .attr('width', width - margins.l - margins.r)
        .attr('height', height - margins.t - margins.b)
        .attr('fill', '#fff')

    // bars
    if (previousClose) {
        // cost rects for profitable bars
        chartgroup.append('g')
        .attr('id', 'profitables-cost-group')
        .selectAll('rect')
            .data(sortedLots.filter(lot => lot.price < previousClose.price))
            .join('rect')
            .attr('x', lot => x(lot.shares_acc))
            .attr('y', lot => y(lot.price))
            .attr('width', lot => x(lot.shares))
            .attr('height', lot => y(yLims[0]) - y(lot.price))
            .attr('fill', 'sandybrown')
            .append('title')
                .text(showCostBarTitle);

        // cost rects for unprofitable bars
        chartgroup.append('g')
        .attr('id', 'unprofitables-cost-group')
        .selectAll('rect')
            .data(sortedLots.filter(lot => lot.price >= previousClose.price))
            .join('rect')
            .attr('x', lot => x(lot.shares_acc))
            .attr('y', y(previousClose.price))
            .attr('width', lot => x(lot.shares))
            .attr('height', y(yLims[0]) - y(previousClose.price))
            .attr('fill', 'sandybrown')
            .append('title')
                .text(showCostBarTitle);

        // gains bars
        chartgroup.append('g')
        .attr('id', 'profitables-gain-group')
        .selectAll('rect')
            .data(sortedLots.filter(lot => lot.price < previousClose.price))
            .join('rect')
            .attr('x', lot => x(lot.shares_acc))
            .attr('y', y(previousClose.price))
            .attr('width', lot => x(lot.shares))
            .attr('height', lot => y(lot.price) - y(previousClose.price))
            .attr('fill', 'lightgreen')

        // losses bars
        chartgroup.append('g')
        .attr('id', 'unprofitables-loss-group')
        .selectAll('rect')
            .data(sortedLots.filter(lot => lot.price >= previousClose.price))
            .join('rect')
            .attr('x', lot => x(lot.shares_acc))
            .attr('y', lot => y(lot.price))
            .attr('width', lot => x(lot.shares))
            .attr('height', lot => y(previousClose.price) - y(lot.price))
            .attr('fill', 'lightcoral')
            .append('title')
                .text(showCostBarTitle);

    } else {

        // cost bars
        chartgroup.append('g')
        .attr('id', 'cost-group')
        .selectAll('rect')
            .data(sortedLots)
            .join('rect')
            .attr('x', lot => x(lot.shares_acc))
            .attr('y', lot => y(lot.price))
            .attr('width', lot => x(lot.shares))
            .attr('height', lot => y(yLims[0]) - y(lot.price))
            .attr('fill', 'sandybrown')
            .append('title')
                .text(showCostBarTitle);

    }

    chartgroup.selectAll('rect').on("click", _ => {
        locals.costBasisMethod = locals.costBasisMethod === 'FIFO' ? 'HIFO' : 'FIFO'
        drawChart()
    })

    // x axis
    chartgroup.append('g')
        .attr('id', 'xaxis')
        .attr('transform', `translate(0,${height - margins.b - margins.t})`)
        .call(d3.axisBottom(x).ticks(5));

    // y axis
    chartgroup.append('g')
        .attr('id', 'yaxis')
        .call(d3.axisLeft(y).ticks(5));

    // xlabel
    chartgroup.append('g')
        .attr('id', 'xlabel')
        .attr('transform', `translate(${(width - margins.l - margins.r) / 2}, ${height - margins.t - 0.35 * margins.b})`)
        .append('text')
            .attr('class', 'xlabel')
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .text(`Cumulative number of shares (${locals.costBasisMethod})`)
            .append('title')
                .text('Click chart to toggle Cost Basis Method');


    // ylabel
    chartgroup.append('g')
        .attr('id', 'ylabel')
        .attr('transform', `translate(${-0.80 * margins.l}, ${(height - margins.b - margins.t) / 2}) rotate(-90)`)
        .append('text')
            .attr('class', 'ylabel')
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .text('Price ($)');

    // title
    chartgroup.append('g')
        .attr('id', 'title')
        .attr('transform', `translate(${(width - margins.l - margins.r) / 2}, ${-0.5 * margins.t + 3})`)
        .append('text')
            .attr('class', 'title')
            .attr('text-anchor', 'middle')
            .attr('dominant-baseline', 'middle')
            .text(ticker);

    // cost per share line
    const cpsgroup = chartgroup.append('g').attr('id', 'cpsgroup')

    cpsgroup.append('line')
        .attr('x1', x(0))
        .attr('x2', x(shares))
        .attr('y1', y(costPerShare))
        .attr('y2', y(costPerShare))
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
        .attr('y', y(costPerShare))
        .attr('dy', '0em')
        .text('cps')
        .append('title')
            .text(`cost per share: $${costPerShare.toFixed(2)}`);

    if (previousClose) {

        // previous closing price group
        const pricegroup = chartgroup.append('g').attr('id', 'pricegroup')

        // previous closing price line
        pricegroup.append('line')
            .attr('x1', x(0))
            .attr('x2', x(shares))
            .attr('y1', y(previousClose.price))
            .attr('y2', y(previousClose.price))
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
            .attr('y', y(previousClose.price))
            .attr('dy', '0em')
            .text('price')
            .append('title')
                .text(`previous-day close price: $${previousClose.price.toFixed(2)}`);

    }
};

const props = defineProps<{
    holding: Holding,
}>();
const chart = ref(null);
const locals = reactive<{
    costBasisMethod: CostBasisMethod
}>({
    costBasisMethod: 'FIFO'
});

const width = 350;
const height = 285;
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

svg {
    min-width: 350px;
    min-height: 175px;
}

</style>
