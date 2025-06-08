import { createRouter, createWebHistory, useRouter } from 'vue-router'
import EnterPage from '../components/MainSection/EnterPage/EnterPage.vue'
import MainContainer from '../components/MainSection/EnterPage/MainContainer.vue'
import AboutPage from '../components/MainSection/AboutPage/AboutPage.vue'
import HelpPage from '../components/MainSection/HelpPage/HelpPage.vue'
import LoggedPage from '../components/MainSection/CalendarPage/LoggedPage.vue'
import Homepage from '../components/MainSection/HomePage/Homepage.vue'
import Settings from '../components/SettingsPage/Settings.vue'
import UserPage from '../components/MainSection/UserPage/UserPage.vue'
import { userSettingsStore } from '../store/userSettingsStore'
const routes = [
    {
        path: '/users/:id',
        component: UserPage,
    },
    {
        path: '',
        component: EnterPage,
        children: [
            {
                path: '',
                component: MainContainer,
            },
            {
                path: 'about',
                component: AboutPage,
            },
            {
                path: 'help',
                component: HelpPage,
            },
        ],
    },
    {
        path: '/home',
        component: LoggedPage,
        beforeEnter: (to, from) => {
            const store = userSettingsStore()
            const router = useRouter()
            if (!store.$state.isLoggged) {
                router.push('')
                return false
            }
        },
        children: [
            {
                path: '',
                component: Homepage,
            },
            {
                path: 'settings',
                component: Settings,
            },
        ],
    },
]
const router = new createRouter({
    history: createWebHistory(),
    routes,
})

export default router
