<template>
    <div class="container-fluid p-4 bg-light min-vh-100">
      <div class="row mb-3">
        <nav class="navbar navbar-expand-lg bg-body-tertiary shadow-sm rounded">
          <div class="container-fluid">
            <span class="navbar-brand fw-bold">Welcome, {{ student.student_name || 'Student' }}!</span>
            <div class="d-flex justify-content-end ms-auto gap-2">
              <button class="btn btn-outline-primary" @click="exportCSV">Export History (CSV)</button>
              <button class="btn btn-secondary" @click="handleLogout">Logout</button>
            </div>
          </div>
        </nav>
      </div>
  
      <div v-if="message" class="alert alert-info alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" @click="message = ''"></button>
      </div>
  
      <div class="row mb-4">
        <div class="col-12">
            <div class="card p-4 shadow-sm">
                <h4 class="mb-3 text-center">Edit Profile</h4>
                <form @submit.prevent="handleUpdateProfile">
                    <div class="row g-3">
                        
                        <div class="col-md-6">
                            <label class="form-label fw-bold">Full Name:</label>
                            <input type="text" class="form-control" v-model="student.student_name" placeholder="Full Name" required />
                        </div>

                        <div class="col-md-6">
                            <label class="form-label fw-bold">Skills:</label>
                            <input type="text" class="form-control" v-model="student.skills" placeholder="Skills (e.g. Python, SQL)" required />
                        </div>
                        
                        <div class="col-md-6">
                            <label class="form-label fw-bold">Resume Link:</label>
                            <input type="text" class="form-control" v-model="student.resume" placeholder="Google Drive / Dropbox Link" required />
                        </div>
                        
                        <div class="col-md-6">
                            <label class="form-label fw-bold">Contact Number:</label>
                            <input type="text" class="form-control" v-model="student.contact_info" placeholder="Contact Number" required />
                        </div>
                    </div>
                    <div class="mt-4 text-center">
                        <button type="submit" class="btn btn-primary px-5">Submit</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
       
  
      <div class="row mb-4">
        <div class="col-12">
          <div class="card p-3 shadow-sm">
            <div class="d-flex justify-content-between align-items-center mb-3">
              <h4 class="mb-0">Current Drives</h4>
              <input 
                type="text" 
                v-model="searchQuery" 
                placeholder="Search drive or company..." 
                class="form-control w-25" 
              />
            </div>
  
            <p v-if="filteredDrives.length === 0" class="text-muted fst-italic">No approved placement drives found.</p>
            <table v-else class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Sr. No.</th>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Eligibility</th>
                  <th>Application Deadline</th>
                  <th class="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(drive, index) in filteredDrives" :key="drive.drive_id">
                  <td>{{ index + 1 }}</td>
                  <td class="fw-bold">{{ drive.job_title }}</td>
                  <td>{{ drive.company_name }}</td>
                  <td>{{ drive.eligibility_criteria || 'N/A' }}</td>
                  <td>{{ drive.application_deadline }}</td>
                  <td class="text-end">
                    <button 
                      v-if="!drive.is_applied" 
                      class="btn btn-outline-success" 
                      @click="applyDrive(drive.drive_id)"
                    >
                      Apply
                    </button>
                    <span v-else class="badge bg-secondary">Applied</span>
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
            <h4 class="mb-3">Applied Drives</h4>
            <p v-if="applications.length === 0" class="text-muted fst-italic">You have not applied to any placement drives yet.</p>
            <table v-else class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Sr. No.</th>
                  <th>Job Title</th>
                  <th>Company</th>
                  <th>Applied Date</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(app, index) in applications" :key="app.application_id">
                  <td>{{ index + 1 }}</td>
                  <td class="fw-bold">{{ app.job_title }}</td>
                  <td>{{ app.company_name }}</td>
                  <td>{{ app.application_date }}</td>
                  <td>
                    <span :class="getStatusBadgeClass(app.status)">
                      {{ app.status }}
                    </span>
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
        student: {},
        approvedDrives: [],
        applications: [],
        searchQuery: '',
        message: ''
      }
    },
    computed: {
      filteredDrives() {
        const q = this.searchQuery.toLowerCase()
        return this.approvedDrives.filter(d => 
          d.job_title.toLowerCase().includes(q) || 
          d.company_name.toLowerCase().includes(q)
        )
      }
    },
    async created() {
      this.loadStudentData()
    },
    methods: {
      async loadStudentData() {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_URL}/api/student/dashboard`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await response.json()
  
        if (response.ok) {
          this.student = data.student
          this.approvedDrives = data.approved_drives
          this.applications = data.applications
        } else {
          this.message = data.message
        }
      },
  
      async handleUpdateProfile() {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_URL}/api/student/update_profile`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(this.student)
        })
  
        const data = await response.json()
        this.message = data.message
        if (response.ok) {
          this.loadStudentData()
        }
      },
  
      async applyDrive(driveId) {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_URL}/api/student/apply/${driveId}`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })
  
        const data = await response.json()
        this.message = data.message
        if (response.ok) {
          this.loadStudentData()
        }
      },
  
      async exportCSV() {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_URL}/api/student/export_csv`, {
          method: 'POST',
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await response.json()
        this.message = data.message
      },
  
      getStatusBadgeClass(status) {
        if (status === 'Selected') return 'badge bg-success'
        if (status === 'Shortlisted') return 'badge bg-warning text-dark'
        if (status === 'Rejected') return 'badge bg-danger'
        return 'badge bg-primary'
      },
  
      handleLogout() {
        localStorage.clear()
        this.$router.push('/login')
      }
    }
  }
  </script>
  
  