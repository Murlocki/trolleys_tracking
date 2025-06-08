<script setup>
import { ref } from 'vue'
import { eventStore } from '../../../store/eventStore'
const calendar = ref()

/*Настрока календаря */
const store = eventStore()
const title = ref()
const calendarOptions = ref({
    plugins: [dayGridPlugin, interactionPlugin, timeGridPlugin],
    headerToolbar: {
        center: '',
        left: '',
        right: '',
    },
    contentHeight: 'auto',
    timeZone: 'local',
    defaultTimedEventDuration: '00:00',
    initialView: 'timeGridDay',
    events: store.$state.events,
    viewClassNames: () => {
        title.value = calendar.value.getApi().view.title
    },
})
</script>
<template>
    <div style="min-height: 700px; height: fit-content" class="flex justify-content-center w-full mt-3">
        <div class="flex flex-column justify-content-center w-full md:w-10 mb-5">
            <div class="text-color text-2xl md:text-3xl lg:text-5xl h-full w-full mb-1">
                <span>Your events for {{ title }}</span>
                <div class="w-12 md:w-10 lg:w-9 border-1"></div>
            </div>
            <div style="border-radius: 16px">
            </div>
        </div>
    </div>
</template>
<style>
.grid-background {
    width: 100%;
    height: 100%;
    background-color: white;
    background-image: linear-gradient(to right, #e0e0e05e 1px, transparent 1px),
        linear-gradient(to bottom, #e0e0e05e 1px, transparent 1px);
    background-size: 200px 130px;
    background-position: -1px -1px;
}

.fc-scrollgrid {
    border-radius: 16px 16px 0px 0px !important;
}
.fc-scrollgrid > thead > tr > th {
    border-radius: 16px 16px 0px 0px !important;
}
.fc-scroller {
    border-radius: 0px 0px 16px 16px !important;
}

.fc-daygrid-event-dot {
    display: none;
}
.fc-day-today {
    background-color: var(--primary-color-text) var(--primary-color) !important;
    color: var(--primary-color) !important;
}

/*Настройки ивентов */
.fc-more-link,
.fc-daygrid-more-link,
.fc-daygrid-day-bottom {
    overflow: hidden;
}
.fc-event-title {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
/*Стили кнопок */
.fc-button {
    background-color: var(--primary-color) !important;
    color: var(--primary-color-text) !important;
    padding: 0.5rem 1rem;
    font-size: 1rem !important;
}
.fc-button-primary {
    color: var(--primary-color);
    padding: 0.5rem 1rem;
    font-size: 1rem !important;
    border-radius: 15px !important;
    cursor: pointer;
    margin-left: 5px !important;
    margin-right: 5px !important;
}
.fc-button:hover,
.fc-button:focus {
    background-color: var(--primary-color-text) !important;
    color: var(--primary-color) !important;
}
</style>
