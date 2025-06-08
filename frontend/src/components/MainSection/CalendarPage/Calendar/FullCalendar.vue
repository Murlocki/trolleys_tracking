<script setup>
import Button from 'primevue/button'
import EventForm from '../EventForm/EventForm.vue'

/*Настройка диалоговой формы */
import Dialog from 'primevue/dialog'
const visibleForm = ref(false)

import { ref } from 'vue'
import { eventStore } from '../../../../store/eventStore'
const calendar = ref()

/*Обрабатываем клики на дни */
const prevView = ref(['dayGridMonth'])
const handleNonDayClick = function (arg) {
    console.log(arg)
    if (calendar.value.getApi().view.type == 'dayGridMonth') prevView.value = []
    prevView.value = [...prevView.value, calendar.value.getApi().view.type]
    calendar.value.getApi().changeView('timeGridDay')
    calendar.value.getApi().gotoDate(arg.dateStr)
}
const returnPrevView = function () {
    const prevViewType = prevView.value.slice(-1)
    prevView.value = [...prevView.value.slice(0, -1)]
    calendar.value.getApi().changeView(prevViewType)
}

const handleDateClick = function (arg) {
    if (calendar.value.getApi().view.type != 'timeGridDay') {
        handleNonDayClick(arg)
    }
}

/*Открытие формы изменения ивента */
const currentEvent = ref({})
const openForm = ref(false)
const editingMode = ref(false)
const handleEventClick = function (info) {
    if (calendar.value.getApi().view.type == 'timeGridDay') {
        editingMode.value = info.event ? true : false
        currentEvent.value = info.event

        openForm.value = true
        visibleForm.value = true
    }
}

/*Перетаскивание события */
const formatDate = function (date, hasHours) {
    const dateFormat = new Date(date.toString().split('GMT')[0] + ' UTC').toISOString()
    return hasHours ? dateFormat.slice(0, 19) : dateFormat.slice(0, 10)
}
const formatEndDate = function (end) {
    end.setDate(end.value.getDate() + 1)
    end.toUTCString()
    return end
}
const handleEventDrop = function (info) {
    // Handle event drop
    console.log('Event dropped:', info)

    const startDateFormat = formatDate(info.event.start, info.event.extendedProps.startHasHours)
    const endDateFormat = info.event.end
        ? formatDate(
              info.event.extendedProps.endHasHours ? info.event.end : formatEndDate(info.event.end),
              info.event.extendedProps.endHasHours,
          )
        : ''

    const updatedEvent = {
        title: info.event.title,
        start: startDateFormat,
        end: endDateFormat,
        startHasHours: info.event.extendedProps.startHasHours,
        endHasHours: info.event.extendedProps.endHasHours,
        description: info.event.extendedProps.description,
        eventId: info.event.extendedProps.eventId,
        backgroundColor: info.event.backgroundColor,
        borderColor: info.event.borderColor,
        textColor: info.event.textColor,
    }
    store.updateEvent(updatedEvent, updatedEvent.eventId)

    console.log(store.$state.events)
    console.log(calendarOptions.value.events)
}

/*Настрока календаря */
const store = eventStore()

const calendarOptions = ref({
    plugins: [dayGridPlugin, interactionPlugin, timeGridPlugin],
    headerToolbar: {
        left: 'prev,next',
        right: 'timeGridWeek,timeGridDay,dayGridMonth',
    },
    nowIndicator: true,
    contentHeight: 'auto',
    timeZone: 'local',
    defaultTimedEventDuration: '00:00',
    initialView: 'dayGridMonth',
    dateClick: handleDateClick,
    editable: true,
    eventClick: handleEventClick,
    eventDrop: handleEventDrop,
    dayMaxEventRows: 3,
    events: store.$state.events,
    viewClassNames: () => {
        title.value = calendar.value.getApi().view.title
    },
})

const title = ref()
</script>
<template>
    <div style="min-height: 700px" class="flex flex-column justify-content-center w-full md:w-10">
        <div class="flex justify-content-between mb-3 align-items-center">
            <span class="text-center text-lg lg:text-2xl font-bold vertical-align-middle" style="height: fit-content">{{
                calendar ? title : ''
            }}</span>
            <div>
                <Button
                    v-if="calendar && calendar.getApi().view.type != 'dayGridMonth'"
                    icon="pi pi-arrow-left"
                    class="border-circle mr-2"
                    v-tooltip.bottom="'Back'"
                    @click="returnPrevView"
                ></Button>
                <Button
                    icon="pi pi-plus"
                    class="border-circle"
                    v-tooltip.bottom="'Add new event'"
                    @click="handleEventClick"
                ></Button>
            </div>
        </div>
        <Dialog
            v-model:visible="visibleForm"
            modal
            dismissableMask
            header="Event form"
            :class="'w-10 md:w-6 lg:w-4 flex justify-content-center p-dialog-content bg-primary-reverse'"
        >
            <event-form
                class="bg-primary-reverse"
                style="height: fit-content"
                :event="currentEvent"
                v-model:dialog-visible="visibleForm"
                :editing-mode="editingMode"
            ></event-form>
        </Dialog>
        <div style="border-radius: 16px">
        </div>
    </div>
</template>
<style>
.fc-scrollgrid {
    border-radius: 16px 16px 0px 0px !important;
}
.fc-scrollgrid > thead > tr > th {
    border-radius: 16px 16px 0px 0px !important;
}
.fc-scroller {
    border-radius: 0px 0px 16px 16px !important;
}

/*Подсветка выходных */
.fc-day-sat,
.fc-day-sun {
    color: red;
}
.fc-daygrid-event-dot {
    display: none;
}
/* .fc-day-today {
    background-color: var(--primary-color) !important;
    color: var(--primary-color-text) !important;
} */

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

.p-dialog {
    background-color: var(--primary-color-text);
    color: var(--primary-color);
}

.p-dialog .p-dialog-header {
    background-color: var(--primary-color-text);
    color: var(--primary-color);
}

.p-dialog .p-dialog-content {
    background-color: var(--primary-color-text);
    color: var(--primary-color);
}
</style>
