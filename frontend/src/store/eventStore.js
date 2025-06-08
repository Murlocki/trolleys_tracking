import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
export const eventStore = defineStore('eventStore', () => {
    const events = ref([
        {
            title: 'event 1',
            start: '2024-07-08',
            end: '2024-07-09',
            startHasHours: false,
            endHasHours: false,
            description: 'aaddddds',
            eventId: 14,
            backgroundColor: '#ff0000',
            borderColor: '#ff0000',
            textColor: '#000000',
        },
        {
            title: 'event 2',
            start: '2024-07-10T23:30:00',
            end: '',
            startHasHours: true,
            endHasHours: false,
            description: 'aaddddds',
            eventId: 12,
            backgroundColor: '#ff0000',
            borderColor: '#ffffff',
            textColor: '#000000',
        },
        {
            title: 'event 2',
            start: '2024-07-10T23:30:00',
            end: '',
            startHasHours: true,
            endHasHours: false,
            description: 'aaddddds',
            eventId: 16,
            backgroundColor: '#ff0000',
            borderColor: '#ffffff',
            textColor: '#000000',
        },
        {
            title: 'event 2',
            start: '2024-07-10T23:30:00',
            end: '',
            startHasHours: true,
            endHasHours: false,
            description: 'aaddddds',
            eventId: 17,
            backgroundColor: '#ff0000',
            borderColor: '#ffffff',
            textColor: '#000000',
        },
        {
            title: 'event 2',
            start: '2024-07-10T23:30:00',
            end: '',
            startHasHours: true,
            endHasHours: false,
            description: 'aaddddds',
            eventId: 18,
            backgroundColor: '#ff0000',
            borderColor: '#ffffff',
            textColor: '#000000',
        },
        {
            title: 'event 2',
            start: '2024-07-10T23:30:00',
            end: '',
            startHasHours: true,
            endHasHours: false,
            description: 'aaddddds',
            eventId: 19,
            backgroundColor: '#ff0000',
            borderColor: '#ffffff',
            textColor: '#000000',
        },
        {
            title: 'event 3',
            start: '2024-07-06',
            end: '',
            startHasHours: false,
            endHasHours: false,
            description: 'aaddddds',
            eventId: 13,
            backgroundColor: '#ff0000',
            borderColor: '#ff0000',
            textColor: '#000000',
        },
        {
            title: 'event 4',
            start: '2024-07-06',
            end: '',
            startHasHours: false,
            endHasHours: false,
            description: 'aaddddds',
            eventId: 15,
            backgroundColor: '#ff0000',
            borderColor: '#ff0000',
            textColor: '#000000',
        },
    ])

    const updateEvent = function (newEvent, currentEventId) {
        const index = events.value.findIndex((it) => it.eventId == currentEventId)
        if (index != -1) {
            events.value[index] = { ...events.value[index], ...newEvent }
            events.value = [...events.value]
        }
        console.log(events.value[index])
        console.log(events.value)
        /*Тут дальше типо запрос будет к тебе */
    }

    const createEvent = function (newEvent) {
        const eventId = Math.max(...events.value.map((item) => item.eventId)) + 1

        newEvent.id = eventId
        events.value.push(newEvent)
        /*Ну тут типо тоже должен быть запрос */
    }

    return { events, updateEvent, createEvent }
})
