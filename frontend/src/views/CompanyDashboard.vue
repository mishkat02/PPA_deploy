<template>
    <div class="container-fluid p-4 bg-light min-vh-100">
      <div class="row mb-3">
        <nav class="navbar navbar-expand-lg bg-body-tertiary shadow-sm rounded">
          <div class="container-fluid">
            <span class="navbar-brand fw-bold">Welcome, {{ company.company_name || 'Company' }}!</span>
            <div class="d-flex justify-content-end ms-auto gap-2">
              <button class="btn btn-secondary" @click="handleLogout">Logout</button>
            </div>
          </div>
        </nav>
      </div>
  
      <div v-if="message" class="alert alert-info alert-dismissible fade show" role="alert">
        {{ message }}
        <button type="button" class="btn-close" @click="message = ''"></button>
      </div>
  
      <div v-if="company.approval_status !== 'Approved'" class="alert alert-warning shadow-sm" role="alert">
        <strong>Account Status: {{ company.approval_status }}</strong> — You will be able to post placement drives once the Admin approves your company account.
      </div>
  
      <div class="row mb-4" v-if="company.approval_status === 'Approved'">
        <div class="col-12">
          <div class="card p-4 shadow-sm">
            <h4 class="mb-3 text-center">Create Drive</h4>
            <form @submit.prevent="handleCreateDrive">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-bold">Job Title:</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="newDrive.job_title" 
                    placeholder="e.g. Software Engineer" 
                    required 
                  />
                </div>
  
                <div class="col-md-6">
                  <label class="form-label fw-bold">Eligibility Criteria:</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="newDrive.eligibility_criteria" 
                    placeholder="e.g. B.Tech 7.0+ CGPA, Python" 
                    required 
                  />
                </div>
  
                <div class="col-md-6">
                  <label class="form-label fw-bold">Application Deadline:</label>
                  <input 
                    type="date" 
                    class="form-control" 
                    v-model="newDrive.application_deadline" 
                    required 
                  />
                </div>
  
                <div class="col-md-6">
                  <label class="form-label fw-bold">Job Description:</label>
                  <input 
                    type="text" 
                    class="form-control" 
                    v-model="newDrive.job_description" 
                    placeholder="Describe the role and responsibilities" 
                    required 
                  />
                </div>
              </div>
  
              <div class="mt-4 text-center">
                <button type="submit" class="btn btn-success px-5">Create Drive</button>
              </div>
            </form>
          </div>
        </div>
      </div>
  
      <div class="row mb-4">
        <div class="col-12">
          <div class="card p-3 shadow-sm">
            <h4 class="mb-3">My Placement Drives</h4>
            <p v-if="drives.length === 0" class="text-muted fst-italic">No drives created yet.</p>
            <table v-else class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Sr. No.</th>
                  <th>Job Title</th>
                  <th>Deadline</th>
                  <th>Status</th>
                  <th>Applicants</th>
                  <th class="text-end">Action</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(drive, index) in drives" :key="drive.drive_id">
                  <td>{{ index + 1 }}</td>
                  <td class="fw-bold">{{ drive.job_title }}</td>
                  <td>{{ drive.application_deadline }}</td>
                  <td>
                    <span :class="['badge', drive.drive_status === 'Approved' ? 'bg-success' : 'bg-warning text-dark']">
                      {{ drive.drive_status }}
                    </span>
                  </td>
                  <td><span class="badge bg-secondary">{{ drive.applications_count }} Applicants</span></td>
                  <td class="text-end">
                    <button class="btn btn-sm btn-outline-primary" @click="viewApplicants(drive.drive_id)">
                      View Applicants
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
  
      <div class="row mb-3" v-if="selectedDriveTitle">
        <div class="col-12">
          <div class="card p-3 shadow-sm border-dark">
            <h4 class="mb-3 text-dark">Applicants for: {{ selectedDriveTitle }}</h4>
            <p v-if="applicants.length === 0" class="text-muted fst-italic">No students have applied to this drive yet.</p>
            <table v-else class="table table-hover align-middle">
              <thead>
                <tr>
                  <th>Student Name</th>
                  <th>Skills</th>
                  <th>Contact</th>
                  <th>Status</th>
                  <th class="text-end">Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applicants" :key="app.application_id">
                  <td class="fw-bold">{{ app.student_name }}</td>
                  <td>{{ app.skills }}</td>
                  <td>{{ app.contact_info || 'N/A' }}</td>
                  <td>
                    <span :class="getStatusBadgeClass(app.status)">
                      {{ app.status }}
                    </span>
                  </td>
                  <td class="text-end">
                    <div class="btn-group btn-group-sm" role="group">
                      <button class="btn btn-outline-warning" @click="updateStatus(app.application_id, 'Shortlisted')">Shortlist</button>
                      <button class="btn btn-outline-success" @click="updateStatus(app.application_id, 'Selected')">Select</button>
                      <button class="btn btn-outline-danger" @click="updateStatus(app.application_id, 'Rejected')">Reject</button>
                    </div>
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
        company: {},
        drives: [],
        applicants: [],
        selectedDriveTitle: '',
        currentDriveId: null,
        message: '',
        newDrive: {
          job_title: '',
          job_description: '',
          eligibility_criteria: '',
          application_deadline: ''
        }
      }
    },
    async created() {
      this.loadCompanyData()
    },
    methods: {
      async loadCompanyData() {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_URL}/api/company/dashboard`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await response.json()
  
        if (response.ok) {
          this.company = data.company
          this.drives = data.drives
        } else {
          this.message = data.message
        }
      },
  
      async handleCreateDrive() {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_URL}/api/company/create_drive`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify(this.newDrive)
        })
  
        const data = await response.json()
        this.message = data.message
  
        if (response.ok) {
          this.newDrive = { job_title: '', job_description: '', eligibility_criteria: '', application_deadline: '' }
          this.loadCompanyData()
        }
      },
  
      async viewApplicants(driveId) {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_URL}/api/company/drive_applications/${driveId}`, {
          headers: { 'Authorization': `Bearer ${token}` }
        })
        const data = await response.json()
  
        if (response.ok) {
          this.currentDriveId = driveId
          this.selectedDriveTitle = data.drive_title
          this.applicants = data.applications
        }
      },
  
      async updateStatus(appId, newStatus) {
        const token = localStorage.getItem('token')
        const response = await fetch(`${API_URL}/api/company/update_app_status/${appId}`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({ status: newStatus })
        })
  
        const data = await response.json()
        this.message = data.message
  
        if (response.ok) {
          this.viewApplicants(this.currentDriveId)
        }
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
  
  