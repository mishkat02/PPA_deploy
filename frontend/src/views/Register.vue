<template>
    <div class="box">
      <div class="form-container">
        <form @submit.prevent="handleRegister">
          <h1>Register</h1>
  
          <p v-if="message" :class="isError ? 'error-text' : 'success-text'">{{ message }}</p>
  
          <label>Username:</label>
          <input type="text" v-model="username" placeholder="Username" required />
  
          <label>Email:</label>
          <input type="email" v-model="email" placeholder="Email" required />
  
          <label>Password:</label>
          <input type="password" v-model="password" placeholder="Password" required />
  
          <label>Role:</label>
          <select v-model="role" class="custom-select">
            <option value="Student">Student</option>
            <option value="Company">Company</option>
          </select>
  
          <div v-if="role === 'Student'">
            <label>Skills:</label>
            <input type="text" v-model="skills" placeholder="Python, SQL" />
          </div>
  
          <div v-if="role === 'Company'">
            <label>Company Name:</label>
            <input type="text" v-model="company_name" placeholder="TechCorp" />
            <label>Website:</label>
            <input type="text" v-model="website" placeholder="www.techcorp.com" />
          </div>
  
          <button type="submit">Submit</button>
        </form>
  
        <p class="link-text">
          Already registered? <router-link to="/login">Login here</router-link>
        </p>
      </div>
    </div>
  </template>
  
  <script>
import { API_URL } from '../config'
  export default {
    data() {
      return {
        username: '',
        email: '',
        password: '',
        role: 'Student',
        skills: '',
        company_name: '',
        website: '',
        message: '',
        isError: false
      }
    },
    methods: {
      async handleRegister() {
        const response = await fetch(`${API_URL}/api/register`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            role: this.role,
            username: this.username,
            email: this.email,
            password: this.password,
            skills: this.skills,
            company_name: this.company_name,
            website: this.website
          })
        })
  
        const data = await response.json()
        this.message = data.message
  
        if (response.ok) {
          this.isError = false
          setTimeout(() => {
            this.$router.push('/login')
          }, 1000)
        } else {
          this.isError = true
        }
      }
    }
  }
  </script>
  
  <style scoped>
  .box { display: flex; justify-content: center; align-items: center; min-height: 80vh; }
  .form-container { background: white; padding: 30px; border-radius: 12px; border: 1px solid #ccc; width: 100%; max-width: 400px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
  h1 { text-align: center; margin-bottom: 20px; }
  label { display: block; margin-bottom: 5px; }
  input, .custom-select { width: 100%; padding: 10px; margin-bottom: 15px; border: 1px solid #ccc; border-radius: 5px; box-sizing: border-box; }
  button { width: 100%; padding: 10px; background-color: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; }
  .error-text { color: red; text-align: center; }
  .success-text { color: green; text-align: center; }
  .link-text { text-align: center; margin-top: 15px; }
  </style>