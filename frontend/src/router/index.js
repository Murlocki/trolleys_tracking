import { createRouter, createWebHistory, useRouter } from 'vue-router'
import EnterPage from '../components/MainSection/EnterPage/EnterPage.vue'
import MainContainer from '../components/MainSection/EnterPage/MainContainer.vue'
import AboutPage from '../components/MainSection/AboutPage/AboutPage.vue'
import HelpPage from '../components/MainSection/HelpPage/HelpPage.vue'
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
    }
]
const router = new createRouter({
    history: createWebHistory(),
    routes,
})

export default router
