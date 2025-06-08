import {defineConfig, loadEnv} from 'vite'
import vue from '@vitejs/plugin-vue'
import {fileURLToPath, URL} from 'node:url'

export default defineConfig(() => {
    const env = loadEnv(process.cwd(), '')
    return {
        plugins: [vue()],
        resolve: {
            alias: {
                '@': fileURLToPath(new URL('./src', import.meta.url)),
                '@assets': fileURLToPath(new URL('./src/assets', import.meta.url)),
            },
        },
        define: {
            __AUTH_URL__: JSON.stringify(env.AUTH_URL),
            __USER_URL__: JSON.stringify(env.USER_URL),
            __SESSION_URL__: JSON.stringify(env.SESSION_URL),
            __CAMERA_URL__: JSON.stringify(env.CAMERA_URL),
            __CAMERA_READER_URL__: JSON.stringify(env.CAMERA_READER_URL),
            __API_KEY__: JSON.stringify(env.API_KEY),
        },
    }
})
