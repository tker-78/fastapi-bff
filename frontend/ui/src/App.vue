<script setup lang="ts">
  import { apiClient } from './axios'
  import { ref } from 'vue'

  const data = ref(null)
  const LOGIN_URL = 'http://localhost:8000/api/login'
  const LOGOUT_URL = 'http://localhost:8000/api/logout'

  async function login () {
    window.location.href = LOGIN_URL
  }

  async function logout () {
    window.location.href = LOGOUT_URL
  }

  async function getProtectedData () {
    const res = await apiClient.get("/api/protected")
    data.value = res.data
    console.log(res)
  }

  async function getProtectedByRoleData () {
    const res = await apiClient.get("/api/protected-by-role")
    data.value = res.data
  }
</script>

<template>
  <main>
    <h1>FastAPI BFF</h1>
    <p>
      Visit <a href="https://github.com/tker-78/fastapi-bff/" target="_blank" rel="noopener">tker-78's GitHub repository.</a> to read the
      documentation
    </p>
    <button @click="login">login</button>
    <button @click="logout">logout</button>
    <button @click="getProtectedData">Get Protected Data</button>
    <button @click="getProtectedByRoleData">Get Protected By Role Data</button>
    <pre>{{ data }}</pre>
  </main>
</template>

<style scoped></style>
