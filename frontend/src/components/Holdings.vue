<script setup lang="ts">
import type { Holding } from '../types';
import HoldingChart from './HoldingChart.vue';
import HoldingTable from './HoldingTable.vue';

const fetchDataFromLocalhost = async (url: string) => {
    try {
        const response = await fetch(`${url}/holdings`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data: Holding[] = await response.json();
        return data;
    } catch (error) {
        console.error('Fetch problem:', error);
    }
}

const holdings = await fetchDataFromLocalhost('http://localhost:3000');
</script>

<template>
    <div v-for='holding in holdings' :key='holding.id'>
        <HoldingChart v-bind:holding='holding'/>
        <HoldingTable v-bind:holding='holding'/>
    </div>
</template>

<style scoped>
    div {
        margin: 0;
        display: flex;
        place-items: center;
        background-color: #ddd;
        min-width: 600px;
    }
</style>
