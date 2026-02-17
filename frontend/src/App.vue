<script setup lang="ts">
import { defineAsyncComponent } from 'vue';
const AsyncHoldings = defineAsyncComponent(() =>
    import('./components/Holdings.vue')
);
</script>

<template>
    <h1>Holdings</h1>
    <Suspense>
        <template #default>
            <AsyncHoldings />
        </template>
        <template #fallback>
            <h1> not yet </h1>
        </template>
    </Suspense>
</template>

<style scoped>
</style>
