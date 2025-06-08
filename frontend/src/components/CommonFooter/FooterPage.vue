<template>
    <div class="surface-600 h-full" style="flex-grow: 1; overflow-y: auto">
        <div class="surface-600 flex justify-content-center py-4 mt-2">
            <div class="flex justify-content-between align-items-center flex-wrap md:flex-nowrap w-10 lg:w-5">
                <div class="flex flex-column justify-content-center" style="width: 125px">
                    <p class="font-semibold text-primary-reverse text-center m-0">Wewatch Inc(c)</p>
                    <div class="flex justify-content-center">
                        <div v-for="item in socialsPath" :key="item.id">
                            <a href=""><img :src="item.path" alt="Custom Icon" style="width: 30px; height: 30px" /></a>
                        </div>
                    </div>
                </div>
                <div v-for="item in links" :key="item.id" style="width: 125px">
                    <router-link :to="item.link" class="active-link text-color-secondary flex justify-content-center">
                        <span>{{ item.name }}</span>
                    </router-link>
                </div>
            </div>
        </div>
    </div>
</template>

<script setup>
const links = [
    { id: 1, name: 'About us', link: '/about' },
    { id: 2, name: 'Help', link: '/help' },
    { id: 3, name: 'Treat', link: '/treat' },
]
const socialsPath = [
    {
        id: 1,
        path: '/src/assets/icons/social/discord.svg',
    },
    {
        id: 2,
        path: '/src/assets/icons/social/instagram.svg',
    },
    {
        id: 3,
        path: '/src/assets/icons/social/reddit.svg',
    },
    {
        id: 4,
        path: '/src/assets/icons/social/twitter.svg',
    },
]
</script>

<style>
.active-link {
    font-weight: bold;
    color: #333;
    text-decoration: none;
}

.active-link:hover {
    text-decoration: none;
}
</style>
