import {defineConfig, loadEnv} from 'vite'
import vue from '@vitejs/plugin-vue'
import {fileURLToPath, URL} from 'node:url'
// https://vite.dev/config/
export default defineConfig(() => {
    const env = loadEnv(process.cwd(), '')
    return {
        plugins: [vue()],
        resolve:
            {
                alias: {
                    '@':
                        fileURLToPath(new URL('./src', import.meta.url)),
                    '@assets':
                        fileURLToPath(new URL('./src/assets', import.meta.url)),
                }
                ,
            }
        ,
        define: {
            __API_URL__: JSON.stringify(env.API_URL),
            __API_KEY__: JSON.stringify(env.API_KEY),
        }
    }
})
