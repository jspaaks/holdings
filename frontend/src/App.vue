<script setup lang="ts">
import { defineAsyncComponent } from 'vue';
const AsyncHoldings = defineAsyncComponent(() =>
    import('./components/Holdings.vue')
);
</script>

<template>
    <div class="gridded">
        <Suspense>
            <template #default>
                <AsyncHoldings />
            </template>
        </Suspense>
    </div>
</template>

<style scoped>
    .gridded {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
        gap: 3px;
    }
</style>
