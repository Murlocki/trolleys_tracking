import {createRouter, createWebHistory} from 'vue-router'
import EnterPage from '../components/MainSection/EnterPage/EnterPage.vue'
import MainContainer from '../components/MainSection/EnterPage/MainContainer.vue'
import AboutPage from '../components/MainSection/AboutPage/AboutPage.vue'
import HelpPage from '../components/MainSection/HelpPage/HelpPage.vue'
import TreatPageMain from "@/components/MainSection/TreatPage/TreatPageMain.vue";
import UserView from "@/components/UserView/UserView.vue";
import CameraGroupTable from "@/components/CameraView/Groups/CameraGroupTable.vue";

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
                component: UserView,
            },
            {
                path: 'cameras',
                component: CameraGroupTable,
            },
        ],
    }
]
const router = new createRouter({
    history: createWebHistory(),
    routes,
})

export default router
