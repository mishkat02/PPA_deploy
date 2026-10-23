<template>
    <div class="container-fluid p-4 bg-light min-vh-100">
      <div class="row mb-3">
        <nav class="navbar navbar-expand-lg bg-body-tertiary shadow-sm rounded">
          <div class="container-fluid">
            <span class="navbar-brand fw-bold">Welcome, Admin!</span>
            <div class="d-flex ms-auto gap-2 align-items-center">
              <button class="btn btn-success" @click="handleLogout">Logout</button>
            </div>
          </div>
        </nav>
      </div>
  
      <div v-if="message" class="alert alert-info alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" @click="message = ''"></button>
      </div>
  
      <div class="row mb-4">
        <div class="col-md-3">
          <div class="card text-center shadow-sm border-primary">
            <div class="card-body">
              <h6 class="text-muted">Total Students</h6>
              <h3 class="text-primary">{{ stats.total_students }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center shadow-sm border-success">
            <div class="card-body">
              <h6 class="text-muted">Total Companies</h6>
              <h3 class="text-success">{{ stats.total_company }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center shadow-sm border-warning">
            <div class="card-body">
              <h6 class="text-muted">Placement Drives</h6>
              <h3 class="text-warning">{{ stats.total_drives }}</h3>
            </div>
          </div>
        </div>
        <div class="col-md-3">
          <div class="card text-center shadow-sm border-info">
            <div class="card-body">
              <h6 class="text-muted">Applications</h6>
              <h3 class="text-info">{{ stats.total_applications }}</h3>
            </div>
          </div>
        </div>
      </div>
  
      <div class="row mb-3">
        <div class="col-12">
          <div class="card p-3 shadow-sm">
            <h4>Company Applications</h4>
            <p v-if="pendingCompanies.length === 0" class="text-muted fst-italic">No pending company requests.</p>
            <table v-else class="table align-middle">
              <thead>
                <tr>
                  <th>Company Name</th>
                  <th>Website</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="comp in pendingCompanies" :key="comp.company_id">
                  <td>{{ comp.company_name }}</td>
                  <td>{{ comp.website }}</td>
                  <td class="d-flex justify-content-end gap-2">
                    <button class="btn btn-outline-success" @click="approveCompany(comp.company_id)">Approve</button>
                    <button class="btn btn-outline-danger" @click="rejectCompany(comp.company_id)">Reject</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
  
      <div class="row mb-3"> 
        <div class="col-12">
          <div class="card p-3 shadow-sm">
            <h4>Pending Drives</h4>
            <p v-if="pendingDrives.length === 0" class="text-muted fst-italic">No pending drive requests.</p>
            <table v-else class="table align-middle">
              <thead>
                <tr>
                  <th>Drive ID</th>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th class="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="p in pendingDrives" :key="p.drive_id">
                  <td>{{ p.drive_id }}</td>
                  <td>{{ p.job_title }}</td>
                  <td>{{ p.company_name }}</td>
                  <td class="text-end">
                    <button class="btn btn-outline-success me-2" @click="approveDrive(p.drive_id)">Approve</button>
                    <button class="btn btn-outline-danger" @click="rejectDrive(p.drive_id)">Reject</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
  
      <div class="row mb-3">
        <div class="col-12">
          <div class="card p-3 shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h4 class="mb-0">Manage Users </h4>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Search user by name or email..." 
                class="form-control w-25" 
              />
            </div>
            <p v-if="filteredUsers.length === 0" class="text-muted fst-italic">No users found.</p>
            <table v-else class="table align-middle">
              <thead>
                <tr>
                  <th>Username</th>
                  <th>Email</th>
                  <th>Role</th>
                  <th>Status</th>
                  <th class="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="u in filteredUsers" :key="u.id">
                  <td>{{ u.username }}</td>
                  <td>{{ u.email }}</td>
                  <td><span class="badge bg-secondary">{{ u.role }}</span></td>
                  <td>
                    <span :class="['badge', u.is_blacklisted ? 'bg-danger' : 'bg-success']">
                      {{ u.is_blacklisted ? 'Blacklisted' : 'Active' }}
                    </span>
                  </td>
                  <td class="text-end">
                    <button 
                      :class="['btn', u.is_blacklisted ? 'btn-outline-success' : 'btn-outline-danger']" 
                      @click="toggleBlacklist(u.id)"
                    >
                      {{ u.is_blacklisted ? 'Un-blacklist' : 'Blacklist' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
  
      <div class="row mb-3"> 
        <div class="col-12">
          <div class="card p-3 shadow-sm">
            <h4>Student Applications</h4>
            <p v-if="allApplications.length === 0" class="text-muted fst-italic">No applications submitted yet.</p>
            <table v-else class="table align-middle">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Company</th>
                  <th>Job Title</th>
                  <th>Application Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in allApplications" :key="a.id">
                  <td>{{ a.student_name }}</td>
                  <td>{{ a.company_name }}</td>
                  <td>{{ a.job_title }}</td>
                  <td>
                    <span class="badge bg-info text-dark">{{ a.status }}</span>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
  
    </div>
  </template>
  
  <script>
import { API_URL } from '../config'
  export default {
    data() {
      return {
        stats: { total_students: 0, total_company: 0, total_drives: 0, total_applications: 0 },
        pendingCompanies: [],
        pendingDrives: [],
        users: [],
        allApplications: [],
        searchQuery: '',
        message: ''
      }
    },
    computed: {
      filteredUsers() {
        const q = this.searchQuery.toLowerCase()
        return this.users.filter(u => 
          u.username.toLowerCase().includes(q) || 
          u.email.toLowerCase().includes(q)
        )
      }
    },
    async created() {
      this.loadAdminData()
    },
    methods: {
      async loadAdminData() {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_URL}/api/admin/dashboard`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await response.json()
  
        if (response.ok) {
          this.stats = data.stats
          this.pendingCompanies = data.pending_companies
          this.pendingDrives = data.pending_drives
          this.users = data.users
          this.allApplications = data.applications || []
        } else {
          this.message = data.message
        }
      },
  
      async approveCompany(id) {
        const token = localStorage.getItem('token')
        const res = await fetch(`${API_URL}/api/admin/approve_company/${id}`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await res.json()
        this.message = data.message
        this.loadAdminData()
      },
  
      async rejectCompany(id) {
        const token = localStorage.getItem('token')
        const res = await fetch(`${API_URL}/api/admin/reject_company/${id}`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await res.json()
        this.message = data.message
        this.loadAdminData()
      },
  
      async approveDrive(id) {
        const token = localStorage.getItem('token')
        const res = await fetch(`${API_URL}/api/admin/approve_drive/${id}`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await res.json()
        this.message = data.message
        this.loadAdminData()
      },
  
      async rejectDrive(id) {
        const token = localStorage.getItem('token')
        const res = await fetch(`${API_URL}/api/admin/reject_drive/${id}`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await res.json()
        this.message = data.message
        this.loadAdminData()
      },
  
      async toggleBlacklist(userId) {
        const token = localStorage.getItem('token')
        const res = await fetch(`${API_URL}/api/admin/blacklist_user/${userId}`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await res.json()
        this.message = data.message
        this.loadAdminData()
      },
  
      handleLogout() {
        localStorage.clear()
        this.$router.push('/login')
      }
    }
  }
  </script>
  
  <style scoped>
  </style>