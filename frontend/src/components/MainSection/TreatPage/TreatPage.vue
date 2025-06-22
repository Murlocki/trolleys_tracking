<template>
    <Panel :header="currentId == 0 ? '' : currentId + '.'" :toggleable="true" class="mt-3">
        <div class="p-2">{{ item.text }}</div>
        <div class="p-2">
            <treat-page v-for="child in item.children" :key="child.id" :item="child" :parentId="currentId.toString()" />
        </div>
    </Panel>
</template>

<script setup>
import {defineProps} from 'vue'
import Panel from 'primevue/panel'

const props = defineProps({
    item: {
        type: Object,
        required: true,
    },
    parentId: {
        type: String,
        required: false,
        default: '',
    },
})

const currentId = props.parentId != '' ? props.parentId + '.' + props.item.id : props.item.id
</script>
