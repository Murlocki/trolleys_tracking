<template>
    <div class="mt-5">
        <Panel v-for="item in treatPageText" :key="item.id" :header="showedId(item) + item.header" :toggleable="true">
            <div class="p-2">{{ item.text }}</div>
            <div class="p-2">
                <treat-page
                    v-for="child in item.children"
                    :key="child.id"
                    :item="child"
                    :parentId="item.id.toString()"
                />
            </div>
        </Panel>
    </div>
</template>

<script setup>
import TreatPage from './TreatPage.vue'
import treatPageText from '@assets/treatPage/treatPage.json'
import Panel from 'primevue/panel'

const showedId = (it) => (it.id == 0 ? '' : it.id + '. ')
</script>

<style></style>
