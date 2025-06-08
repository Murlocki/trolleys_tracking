<template>
    <Calendar
        id="calendar-24h"
        v-model="date"
        :showTime="props.hasHours"
        hourFormat="24"
        :placeholder="eventStartDate.toString()"
        :showOnFocus="false"
        showIcon
        ref="ca"
        inline
    >
    </Calendar>
</template>

<script setup>
import Calendar from 'primevue/calendar'
import { defineProps, ref } from 'vue'
const props = defineProps({
    hasHours: Boolean,
})
const date = defineModel('date')
const eventStartDate = ref(date.value)
const ca = ref()
</script>

<style></style>
