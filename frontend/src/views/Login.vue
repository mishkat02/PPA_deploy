<template>
    <div class="box">
      <div class="form-container">
        <form @submit.prevent="handleLogin">
          <h1>Login</h1>
  
          <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  
          <label>Email:</label>
          <input type="email" v-model="email" placeholder="Email" required />
  
          <label>Password:</label>
          <input type="password" v-model="password" placeholder="Password" required />
  
          <button type="submit">Submit</button>
        </form>
  
        <p class="link">
          New user? <router-link to="/register">Register here</router-link>
        </p>
      </div>
    </div>
  </template>
  
  <script>
import { API_URL } from '../config'
  export default {
    data() {
      return {
        email: '',
        password: '',
        errorMessage: ''
      }
    },
    created() {
      const token = localStorage.getItem('token')
      const userStr = localStorage.getItem('user')
  
      if (token && userStr) {
        const user = JSON.parse(userStr)
        if (user.role === 'Admin') this.$router.push('/admin')
        else if (user.role === 'Company') this.$router.push('/company')
        else if (user.role === 'Student') this.$router.push('/student')
      }
    },
    methods: {
      async handleLogin() {
        const response = await fetch(`${API_URL}/api/login`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: this.email, password: this.password })
        })
  
        const data = await response.json()
  
        if (response.ok) {
          localStorage.setItem('token', data.token)
          localStorage.setItem('user', JSON.stringify(data.user))
  
          if (data.user.role === 'Admin') this.$router.push('/admin')
          else if (data.user.role === 'Company') this.$router.push('/company')
          else this.$router.push('/student')
        } else {
          this.errorMessage = data.message
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .box { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
  .form-container { background: white; padding: 30px; border-radius: 12px; border: 1px solid #ccc; width: 100%; max-width: 400px; }
  h1 { text-align: center; margin-bottom: 20px; }
  label { display: block; margin-bottom: 5px; }
  input { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
  button { width: 100%; padding: 10px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
  .error { color: red; text-align: center; }
  .link { text-align: center; margin-top: 15px; }
  </style>