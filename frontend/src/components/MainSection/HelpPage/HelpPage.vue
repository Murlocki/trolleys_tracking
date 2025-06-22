<template>
    <div
        class="flex flex-column align-content-center w-10 mx-5 mt-2 pt-3 border-round-lg shadow-5 border-solid border-200"
        style="min-height: 80vh"
    >
        <p class="text-center font-semibold text-2xl">Most asked questions</p>
        <div class="flex justify-content-center">
            <Accordion :activeIndex="0" style="width: 90%">
                <AccordionTab v-for="item in helpPageText" :key="item.id" :header="item.header">
                    <p class="m-0 text-sm md:text-base">
                        {{ item.text }}
                    </p>
                </AccordionTab>
            </Accordion>
        </div>
    </div>
</template>

<script setup>
import Accordion from 'primevue/accordion'
import AccordionTab from 'primevue/accordiontab'
import {helpPageText} from '@assets/index.js'
</script>

<style></style>
