<script setup lang="ts">
import { defineAsyncComponent } from 'vue';
const AsyncHoldings = defineAsyncComponent(() =>
    import('./components/HoldingCharts.vue')
);
</script>

<template>
    <div class="flexed">
        <Suspense>
            <template #default>
                <AsyncHoldings />
            </template>
        </Suspense>
    </div>
</template>

<style scoped>
    .flexed {
        display: flex;
        flex-wrap: wrap;
        gap: 2px;
    }
</style>
