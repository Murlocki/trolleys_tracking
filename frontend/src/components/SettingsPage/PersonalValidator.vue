<template>
    <Dialog v-model:visible="vis" modal>
        <div class="card flex justify-content-center">
            <div class="flex flex-column align-items-center">
                <div class="font-bold text-xl mb-2">{{ props.title }}</div>
                <span class="text-color-secondary mb-5"
                    >Please enter the code sent to your {{ props.yourObject }}.</span
                >
                <InputOtp v-model="val" :length="6" style="gap: 0">
                    <template #default="{ attrs, events, index }">
                        <input type="text" v-bind="attrs" v-on="events" class="custom-otp-input" />
                        <div v-if="index === 3" class="px-3">
                            <i class="pi pi-minus" />
                        </div>
                    </template>
                </InputOtp>
                <div class="flex justify-content-between mt-5 align-self-stretch">
                    <Button @click="handleResend" label="Resend Code" link class="p-0"></Button>
                    <Button @click="handleAccept" label="Submit Code"></Button>
                </div>
            </div>
        </div>
    </Dialog>
</template>

<script setup>
import { ref } from 'vue'
import Dialog from 'primevue/dialog'
import Button from 'primevue/button'
import InputOtp from 'primevue/inputotp'
const val = ref(null)
const vis = defineModel('vis')
const props = defineProps({
    title: String,
    yourObject: String,
    acceptFunction: Function,
    resendFunction: Function,
})

const handleAccept = function () {
    props.acceptFunction(val.value)
    vis.value = false
}
const handleResend = function () {
    props.resendFunction()
}
</script>

<style scoped>
.custom-otp-input {
    width: 48px;
    height: 48px;
    font-size: 24px;
    appearance: none;
    text-align: center;
    transition: all 0.2s;
    border-radius: 0;
    border: 1px solid var(--surface-400);
    background: transparent;
    outline-offset: -2px;
    outline-color: transparent;
    border-right: 0 none;
    transition: outline-color 0.3s;
    color: var(--text-color);
}

.custom-otp-input:focus {
    outline: 2px solid var(--primary-color);
}

.custom-otp-input:first-child,
.custom-otp-input:nth-child(5) {
    border-top-left-radius: 12px;
    border-bottom-left-radius: 12px;
}

.custom-otp-input:nth-child(3),
.custom-otp-input:last-child {
    border-top-right-radius: 12px;
    border-bottom-right-radius: 12px;
    border-right-width: 1px;
    border-right-style: solid;
    border-color: var(--surface-400);
}
</style>
