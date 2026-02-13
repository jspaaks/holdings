<script setup lang='ts'>
import type { Holding, Transaction, Buy, Sell } from '../types'

import { onMounted, ref, watch } from 'vue';
import * as d3 from 'd3';

type BuyWithSharesAcc = Buy & {
    shares_acc: number;
};

const props = withDefaults(defineProps<{
    holding: Holding,
    width?: number,
    height?: number,
}>(), {width: 700, height: 300});

const chart = ref(null);

const calcStatsShares = (buys: Buy[]) => {
    const shares = buys.map((t: Transaction) => t.shares);
    const min = 0;
    const max = shares.reduce((acc, curr) => acc + curr, 0);
    let lims : [number, number];
    if (min === max) {
        lims = [min - 0.5, max + 0.5];
    } else {
        lims = [min, max];
    }
    return {min, max, lims}
}

const calcStatsPrices = (buys: Buy[]) => {
    const prices = buys.map((t: Transaction) => t.price);
    const min = Math.min(...prices);
    const max = Math.max(...prices);
    const range = max - min;
    let lims : [number, number];
    if (range === 0) {
        lims = [min - 0.5, max + 0.5];
    } else {
        lims = [min - 0.1 * range, max + 0.1 * range];
    }
    return {min, max, lims}
}

const removeBuysFifo = (buys: Buy[], sold: number) => {
    for (const b of buys) {
        if (sold <= 0) break;
        const delta = sold - b.shares > 0 ? b.shares : sold;
        b.shares -= delta;
        sold -= delta;
    }
    return buys.filter(b => b.shares !== 0);
}

const calcCumulative = (fifoed: Buy[]) => {
    let shares_acc: number = 0;
    let accumulated = [...fifoed] as BuyWithSharesAcc[];
    for (let a of accumulated) {
        a.shares_acc = shares_acc;
        shares_acc += a.shares;
    }
    return accumulated;
}

const calcEffectivePrice = (buys: Buy[], n: number) => {
    return buys
    .map(t => t.price * t.shares)
    .reduce((acc, curr) => acc + curr, 0) /  n;
}

const calcTotalSharesSold = (sells: Sell[]) => {
    return sells
    .map(t => t.shares)
    .reduce((acc, curr) => acc + curr, 0);
}

const addDerivedPropertyInvested = (fifoed: Buy[]) => {
    return {
        invested: fifoed
        .map(f => f.shares * f.price)
        .reduce((acc, curr) => acc + curr, 0)
    };
}

const transactionsByDateSorter = (a: Transaction, b: Transaction) => {
    if (a.date < b.date) {
        return -1;
    } else if (a.date == b.date) {
        return 0;
    } else {
        return 1;
    }
}

const drawChart = () => {

    const sells = props.holding.transactions
    .sort(transactionsByDateSorter)
    .filter(t => t.type === 'SELL');

    const buys = props.holding.transactions
    .sort(transactionsByDateSorter)
    .filter(t => t.type === 'BUY');

    const totalSharesSold = calcTotalSharesSold(sells);
    const fifoed = removeBuysFifo(buys, totalSharesSold);

    const data = {
        ...fifoed,
        ...addDerivedPropertyInvested(fifoed),
    };

    const buysPrime: BuyWithSharesAcc[] = calcCumulative(fifoed);
    const shares = calcStatsShares(buysPrime);
    const prices = calcStatsPrices(buysPrime);
    const effectivePrice = calcEffectivePrice(buysPrime, shares.max);

    const margins = {
        b: 70,
        t: 50,
        l: 130,
        r: 130,
    };

    // select the DOM element using the ref's value
    const svg = d3.select(chart.value);

    // clear previous renders to prevent duplicate charts on updates
    svg.selectAll('*').remove();

    if (buysPrime.length === 0) {
        svg.style('display', 'none');
        return;
    }

    // set svg dimensions
    svg.attr('width', props.width)
    .attr('height', props.height)
    .style('background-color', 'ddd');

    // define scales
    const x = d3.scaleLinear()
    .domain(shares.lims)
    .range([0, props.width - margins.l - margins.r]);

    const y = d3.scaleLinear()
    .domain(prices.lims)
    .range([props.height - margins.t - margins.b, 0]);

    // charting area
    svg.append('g')
    .attr('transform', `translate(${margins.l},${margins.t})`)
    .append('rect')
    .attr('width', props.width - margins.l - margins.r)
    .attr('height', props.height - margins.t - margins.b)
    .attr('fill', '#fff')

    // rectangles
    svg.append('g')
    .attr('transform', `translate(${margins.l},${margins.t})`)
    .selectAll('rect')
    .data(buysPrime)
    .join('rect') // 'join' handles enter, update, and exit
    .attr('x', t => x(t.shares_acc))
    .attr('y', t => y(prices.lims[0]) - y(t.price))
    .attr('width', t => x(t.shares))
    .attr('height', t => y(t.price))
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
    .attr('transform', `translate(${margins.l / 2}, ${margins. t + (props.height - margins.b - margins.t) / 2})`)
    .text('Price ($)');

    // title
    svg.append('text')
    .attr('class', 'title')
    .attr('text-anchor', 'middle')
    .attr('dominant-baseline', 'central')
    .attr('transform', `translate(${margins.l + (props.width - margins.l - margins.r) / 2}, ${margins.t / 2})`)
    .text(props.holding.ticker);

    // effective price
    svg.append('g')
    .attr('transform', `translate(${margins.l},${margins.t})`)
    .append('line')
    .attr('x1', x(shares.lims[0]))
    .attr('x2', x(shares.lims[1]))
    .attr('y1', y(effectivePrice))
    .attr('y2', y(effectivePrice))
    .style('stroke', 'black')
    .style('stroke-width', 0.5);
};



// Call drawChart when the component is first mounted
onMounted(drawChart);

// Watch for changes to the 'data' prop and redraw the chart when it updates
watch(() => props.holding.transactions, drawChart);

</script>

<template>
    <svg ref='chart'></svg>
</template>

<style scoped>
</style>
