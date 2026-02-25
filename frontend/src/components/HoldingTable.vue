<script setup lang='ts'>
import type { Holding, Buy } from '../types'

const props = defineProps<{
    holding: Holding
}>();


const calcGainsAndLosses = (buys: Buy[], price: number) => {
    const sum = (arr: number[]) => arr.reduce((acc: number, curr: number) => acc + curr, 0)
    const gains = buys.filter(b => price > b.price)
    const losses = buys.filter(b => price < b.price)
    return {
        gain: sum(gains.map(g => (price - g.price) * g.shares)),
        loss: sum(losses.map(l => (l.price - price) * l.shares))
    }
}

let { buys, cost, previous_close } = props.holding

const {gain, loss} = calcGainsAndLosses(buys, previous_close.price)

</script>

<template>
    <table>
        <thead>
            <tr>
                <th></th>
                <th class="align-right">%</th>
                <th class="align-right">$</th>
            </tr>
        </thead>

        <tbody>
            <tr>
                <td class="align-left">cost</td>
                <td class="align-right"></td>
                <td class="align-right">{{ cost.toFixed(0) }}</td>
            </tr>

            <tr>
                <td class="align-left">gain</td>
                <td class="align-right">{{ (100 * gain / cost).toFixed(1) }}</td>
                <td class="align-right">{{ gain.toFixed(0) }}</td>
            </tr>

            <tr>
                <td class="align-left">loss</td>
                <td class="align-right">{{ (100 * loss / cost).toFixed(1) }}</td>
                <td class="align-right">{{ loss.toFixed(0) }}</td>
            </tr>

            <tr>
                <td class="align-left">net</td>
                <td class="align-right">{{ (100 * (gain - loss) / cost).toFixed(1) }}</td>
                <td class="align-right">{{ (gain-loss).toFixed(0) }}</td>
            </tr>

            <tr>
                <td class="align-left">value</td>
                <td class="align-right"></td>
                <td class="align-right">{{ (cost + gain - loss).toFixed(0) }}</td>
            </tr>
        </tbody>
    </table>
</template>

<style scoped>

table {
    min-width: 350px;
    margin-left: auto;
    margin-right: auto;
    background-color: #ddd;
    font-size: small;
}

.align-right {
    text-align: right;
}

.align-left {
    text-align: left;
}

td, th {
    padding-left: 10px;
    padding-right: 10px;
    padding-top: 0.2em;
    padding-bottom: 0.2em;
}

thead tr {
    background-color: transparent;
}

tbody tr:nth-child(even) {
    background-color: #f2f2f2;
}

tbody tr:nth-child(odd) {
    background-color: #ffffff;
}
</style>
