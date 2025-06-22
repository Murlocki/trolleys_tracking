<template>
  <Sidebar
      v-model:visible="vis"
      header="Main menu"
      class="p-sidebar-sm"
      role="region"
      :showCloseIcon="false"
      blockScroll
  >
    <template #container>
      <div class="flex flex-column h-full">
        <Button
            class="flex align-items-center justify-content-between px-4 pt-3 flex-shrink-0 border-none border-noround"
            raised text @click="router.push('/')">
          <Image :src="themeIcon" width="60"></Image>
          <span class="ml-2 text-3xl" style="font-family: 'AlbraTRIAL-Black', sans-serif">Wewatch menu</span>
        </Button>
        <Accordion :multiple="true">
          <AccordionTab v-for="elem in sidebarElements" :key="elem.id" style="height: fit-content">
            <template #header>
              <div class="flex align-items-center gap-2 w-full ml-3">
                <span :class="'pi ' + elem.icon"></span>
                <span class="font-bold white-space-nowrap text-xl">{{ elem.title }}</span>
              </div>
            </template>
            <div v-for="subElem in elem.subElements" :key="subElem.id" class="ml-3 mb-3 w-full">
              <router-link :to="subElem.link" style="text-decoration: none" class="inline-block w-12">
                <span :class="' text-color text-lg pi ' + subElem.icon"></span>
                <span class="ml-2 text-color text-lg border-bottom-1">{{ subElem.title }}</span>
              </router-link>
            </div>
          </AccordionTab>
        </Accordion>
        <div class="mt-auto">
          <hr class="mx-3 border-top-1 border-none surface-border"/>
          <Button
              class="w-12 h-12 border-none border-noround flex justify-content-start"
              @click="router.push('/home/settings')"
          >
            <div class="flex align-items-center justify-content-center w-12 mb-2 py-2">
                            <span
                                class="text-color-secondary text-4xl"
                                style="overflow: hidden; text-overflow: ellipsis; width: 70%"
                            >
                                {{ store.$state.userIdentifier }}
                            </span>
            </div>
          </Button>
        </div>
      </div>
    </template>
  </Sidebar>
</template>

<script setup>
import Sidebar from 'primevue/sidebar'
import Image from 'primevue/image'
import Button from 'primevue/button'
import {computed, defineModel, onMounted} from 'vue'
import {userSettingsStore} from '@/store/userSettingsStore.js'
import {imagePath, wemeetLogoWhite} from '@assets/index.js'
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import {useRouter} from 'vue-router'
import {getUserProfile} from "@/externalRequests/requests.js";


const router = useRouter()

const vis = defineModel('visible')
const store = userSettingsStore()
const themeIcon = computed(() => {
  if (!store.$state.darkModeOn) return imagePath
  return wemeetLogoWhite
})

const sidebarElements = [
  {
    id: 0,
    title: 'Tables',
    icon: 'pi-table',
    subElements: [
      {
        title: 'Your users',
        id: 0,
        icon: 'pi-server',
        link: '/tables/users',
      },
      {
        title: 'Your cameras',
        id: 1,
        icon: 'pi-camera',
        link: '/tables/cameras',
      },
    ],
  },
  {
    id: 1,
    title: 'Company',
    icon: 'pi-box',
    subElements: [
      {
        title: 'About',
        id: 0,
        icon: 'pi-question',
        link: '/about',
      },
      {
        title: 'Help',
        id: 1,
        icon: 'pi-question-circle',
        link: '/help',
      },
      {
        title: 'Terms of use',
        id: 2,
        icon: 'pi-file',
        link: '/treat',
      },
    ],
  },
]


onMounted(async () => {
  if (!store.isLogged) {
    return;
  }
  store.setLoading(true);
  const response = await getUserProfile(store.getJwt.value);
  console.log(response)

  if (response.status === 401 || response.status === 403) {
    await store.clearJwt()
    await router.push('/');
    console.log("Logged out")
    store.setLoading(false);
    return
  }


  const response_json = await response.json()
  if (response.status === 200) {
    store.setUserIdentifier(response_json.data.username)
    console.log("Set user identifier for user identifier.")
  }
  store.setJwtKey(response_json.token)
  store.setLoading(false);

})

</script>

<style></style>
