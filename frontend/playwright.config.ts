import {defineConfig} from '@playwright/test';
export default defineConfig({testDir:'./tests',timeout:60000,use:{baseURL:'http://127.0.0.1:3000',trace:'retain-on-failure'},workers:1,reporter:'list'});
