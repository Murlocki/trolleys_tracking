import { createRouter, createWebHistory, useRouter } from 'vue-router'
import EnterPage from '../components/MainSection/EnterPage/EnterPage.vue'
import MainContainer from '../components/MainSection/EnterPage/MainContainer.vue'
import AboutPage from '../components/MainSection/AboutPage/AboutPage.vue'
import HelpPage from '../components/MainSection/HelpPage/HelpPage.vue'
import TreatPageMain from "@/components/MainSection/TreatPage/TreatPageMain.vue";
import UserTable from "@/components/UserTables/UserTable.vue";
import CameraTable from "@/components/CameraView/CameraTable.vue";
const routes = [
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
            {
                path: 'treat',
                component: TreatPageMain,
            },
        ],
    },
    {
        path: '/tables',
        component: EnterPage,
        children: [
            {
                path: 'users',
                component: UserTable,
            },
            {
                path: 'cameras',
                component: CameraTable,
            },
        ],
    }
]
const router = new createRouter({
    history: createWebHistory(),
    routes,
})

export default router
