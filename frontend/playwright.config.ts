import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./tests',timeout:60000,use:{baseURL:'http://127.0.0.1:3000',storageState:{cookies:[],origins:[{origin:'http://127.0.0.1:3000',localStorage:[{name:'ayudachain.guidance-language',value:'en'}]}]},trace:'retain-on-failure'},workers:1,reporter:'list'});
