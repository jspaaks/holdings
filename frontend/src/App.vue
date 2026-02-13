<script setup lang="ts">
import { defineAsyncComponent } from 'vue';
import type { Holding } from './types' 

const AsyncHoldingChart = defineAsyncComponent(() =>
    import('./components/HoldingChart.vue')
);

const fetchDataFromLocalhost = async (url: string) => {
    try {
        const response = await fetch(`${url}/holdings`);
        
        if (!response.ok) {
            // Handle non-successful HTTP responses
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        // Parse the response body as JSON and cast it to the defined interface
        const data: Holding[] = await response.json();
        console.log(data)
        return data;

    } catch (error) {
        // Handle network errors or other issues
        console.error('Fetch problem:', error);
    }
}

const holdings = await fetchDataFromLocalhost('http://localhost:3000');
</script>

<template>
    <Suspense>
        <template #default>
            <div v-for='holding in holdings' :key='holding.ticker'>
                <AsyncHoldingChart v-bind:holding='holding'/>
            </div>
        </template>
    </Suspense>
</template>

<style scoped>
</style>
