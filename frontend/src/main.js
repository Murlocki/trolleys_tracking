import { createApp } from 'vue'
import { createPinia } from 'pinia'
import PrimeVue from 'primevue/config'

import './style.css'
import App from './App.vue'
import router from './router'
import 'primeflex/primeflex.css'
import 'primeicons/primeicons.css'

import Tooltip from 'primevue/tooltip'

const pinia = createPinia()
const app = createApp(App)

app.use(pinia)
app.use(router)
app.use(PrimeVue, { ripple: true })
app.directive('tooltip', Tooltip)
app.mount('#app')