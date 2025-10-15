<template>
  <v-container class="py-6">
    <v-card max-width="1000" class="mx-auto pa-6">
      <h2 class="text-center mb-6">Dashboard</h2>

      <!-- Alert -->
      <v-alert v-if="errorMessage" type="error" density="compact" border="start" variant="tonal" class="mb-4">
        {{ errorMessage }}
      </v-alert>

      <!-- Buttons -->
      <div class="d-flex justify-center gap-3 flex-wrap mb-4">
        <v-btn color="primary" @click="showModal = true">เพิ่มตารางนัด</v-btn>
        <v-btn color="secondary" @click="viewProfile">Profile</v-btn>
        <v-btn color="error" @click="logout">Logout</v-btn>
        <v-btn color="info" @click="fetchAppointments" :loading="loading">รีเฟรช</v-btn>
      </div>

      <!-- Filters -->
      <v-row dense class="mb-4">
        <v-col cols="12" md="4">
          <v-text-field
            v-model="filterDate"
            label="เลือกวันที่"
            type="date"
            dense
            clearable
          ></v-text-field>
        </v-col>
        <v-col cols="12" md="4">
          <v-select
            v-model="filterSlot"
            :items="['เช้า','บ่าย']"
            label="ช่วงเวลา"
            dense
            clearable
          ></v-select>
        </v-col>
      </v-row>

      <!-- Data Table -->
        <v-data-table
          :headers="tableHeaders"
          :items="filteredAppointments"
          :loading="loading"
          density="compact"
          class="elevation-1"
        >

        <template v-slot:item.actions="{ item }">
          <v-btn
            v-if="isOwnAppointment(item.user_id)"
            color="primary"
            small
            @click="editAppointment(item)"
          >
            แก้ไข
          </v-btn>
          <v-btn
            v-if="isOwnAppointment(item.user_id)"
            color="error"
            small
            @click="confirmDelete(item)"
          >
            ลบ
          </v-btn>
        </template>

        <template v-slot:item.appointment_time="{ item }">
          {{ item.appointment_time }} ({{ item.time_slot }})
        </template>

        <template v-slot:item.reason="{ item }">
          {{ item.reason || '-' }}
        </template>
      </v-data-table>

      <!-- Create Appointment Modal -->
      <v-dialog v-model="showModal" max-width="400">
        <v-card>
          <v-card-title class="text-h6">สร้างการนัดหมาย</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="appointmentDate"
              label="วันที่"
              type="date"
              required
            />
            <v-select
              v-model="timeSlot"
              :items="['เช้า','บ่าย']"
              label="ช่วงเวลา"
              required
            />
            <v-text-field
              v-model="reason"
              label="เหตุผล"
              placeholder="เช่น ตรวจสุขภาพ"
              required
            />
            <v-select
              v-model="selectedDoctor"
              :items="doctors"
              label="เลือกหมอ"
              required
            ></v-select>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="showModal = false">ยกเลิก</v-btn>
            <v-btn color="success" @click="createAppointment" :loading="loading">ยืนยัน</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Edit Appointment -->
      <v-dialog v-model="editModal" max-width="400">
        <v-card>
          <v-card-title class="text-h6">แก้ไขการนัดหมาย</v-card-title>
          <v-card-text>
            <v-text-field
              v-model="editDate"
              label="วันที่"
              type="date"
              readonly
            />
            <v-select
              v-model="editSlot"
              :items="['เช้า','บ่าย']"
              label="ช่วงเวลา"
              required
            />
            <v-text-field
              v-model="editReason"
              label="เหตุผล"
              required
            />
            <v-select
              v-model="editDoctor"
              :items="doctors"
              label="เลือกหมอ"
              required
            />
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="editModal = false">ยกเลิก</v-btn>
            <v-btn color="success" @click="saveEdit" :loading="loading">บันทึก</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <!-- Delete Confirmation -->
      <v-dialog v-model="deleteDialog" max-width="400">
        <v-card>
          <v-card-title class="text-h6">ยืนยันการลบ</v-card-title>
          <v-card-text>
            คุณแน่ใจหรือว่าต้องการลบการนัดหมายนี้? การกระทำนี้ไม่สามารถย้อนกลับได้
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="deleteDialog = false">ยกเลิก</v-btn>
            <v-btn color="error" @click="deleteAppointment" :loading="loading">ลบ</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </v-container>
</template>

<script>
import api from '../api/axios'

export default {
  data() {
    return {
      appointments: [],
      doctors: [],
      currentUserId: null,

      showModal: false,
      appointmentDate: '',
      timeSlot: 'เช้า',
      reason: '',
      selectedDoctor: '',

      editModal: false,
      editingAppointment: null,
      editDate: '',
      editSlot: '',
      editReason: '',
      editDoctor: '',

      loading: false,
      errorMessage: '',
      deleteDialog: false,
      appointmentToDelete: null,
      filterDate: '',
      filterSlot: '',
      tableHeaders: [
        { text: 'ID', value: 'id' },
        { text: 'ผู้ใช้', value: 'user_id' },
        { text: 'วันที่', value: 'appointment_date' },
        { text: 'เวลา', value: 'appointment_time' },
        { text: 'หมอ', value: 'doctor_name' },
        { text: 'เหตุผล', value: 'reason' },
        { text: 'สถานะ', value: 'status' },
        { text: 'สร้างเมื่อ', value: 'created_at' },
        { text: 'อัปเดตล่าสุด', value: 'updated_at' },
        { text: 'Actions', value: 'actions', sortable: false },
      ]
    }
  },
  computed: {
    filteredAppointments() {
      return this.appointments.filter(a => {
        const matchDate = !this.filterDate || a.appointment_date === this.filterDate
        const matchSlot = !this.filterSlot || a.time_slot === this.filterSlot
        return matchDate && matchSlot
      })
    }
  },
  async created() {
    await this.fetchAppointments()
    await this.fetchDoctors()
    await this.fetchCurrentUser()
  },
  methods: {
    async fetchAppointments() {
      this.loading = true
      try {
        const res = await api.get('/appointments')
        this.appointments = res.data
      } catch (err) {
        console.error(err)
        this.errorMessage = "ไม่สามารถโหลดตารางนัดทั้งหมดได้"
      } finally {
        this.loading = false
      }
    },
    async fetchDoctors() {
      try {
        const res = await api.get('/doctors')
        this.doctors = res.data
      } catch (err) {
        console.error(err)
        this.errorMessage = "ไม่สามารถโหลดรายชื่อหมอได้"
      }
    },
    async fetchCurrentUser() {
      try {
        const res = await api.get('/me')
        this.currentUserId = res.data.id
      } catch (err) {
        console.error(err)
      }
    },
    isOwnAppointment(userId) { 
      return userId === this.currentUserId 
    },
    async createAppointment() {
      if (!this.appointmentDate || !this.reason || !this.selectedDoctor) {
        this.errorMessage = 'กรุณากรอกข้อมูลให้ครบ'
        return
      }
      this.loading = true
      this.errorMessage = ''
      try {
        const res = await api.post('/appointments/', {
          appointment_date: this.appointmentDate,
          time_slot: this.timeSlot,
          reason: this.reason,
          doctor_name: this.selectedDoctor
        })
        alert(`สร้างการนัดหมายสำเร็จ!\nหมอ: ${res.data.doctor_name}\nวันที่: ${res.data.appointment_date}\nเวลา: ${res.data.appointment_time}`)
        this.showModal = false
        this.appointmentDate = ''
        this.timeSlot = 'เช้า'
        this.reason = ''
        this.selectedDoctor = ''
        this.fetchAppointments()
      } catch (err) {
        console.error(err)
        if (err.response && err.response.data && err.response.data.detail) {
          this.errorMessage = err.response.data.detail
        } else {
          this.errorMessage = 'สร้างการนัดหมายไม่สำเร็จ'
        }
      } finally { this.loading = false }
    },
    editAppointment(appt) {
      this.editingAppointment = appt
      this.editDate = appt.appointment_date
      this.editSlot = appt.time_slot
      this.editReason = appt.reason
      this.editDoctor = appt.doctor_name
      this.editModal = true
    },
    async saveEdit() {
      if (!this.editingAppointment) return
      this.loading = true
      this.errorMessage = ''
      try {
        await api.put(`/appointments/${this.editingAppointment.id}`, {
          time_slot: this.editSlot,
          reason: this.editReason,
          doctor_name: this.editDoctor
        })
        alert('แก้ไขเรียบร้อย')
        this.editModal = false
        this.fetchAppointments()
      } catch (err) {
        console.error(err)
        this.errorMessage = 'ไม่สามารถแก้ไขการนัดหมายได้'
      } finally {
        this.loading = false
      }
    },

    confirmDelete(appt) {
      this.appointmentToDelete = appt
      this.deleteDialog = true
    },
    async deleteAppointment() {
      if (!this.appointmentToDelete) return
      this.loading = true
      this.errorMessage = ''
      try {
        await api.delete(`/appointments/${this.appointmentToDelete.id}`)
        alert('ลบการนัดหมายเรียบร้อย')
        this.fetchAppointments()
      } catch (err) {
        console.error(err)
        this.errorMessage = 'ไม่สามารถลบการนัดหมายได้'
      } finally {
        this.loading = false
        this.deleteDialog = false
        this.appointmentToDelete = null
      }
    },

    viewProfile() {
      this.$router.push('/profile')
    },
    logout() {
      localStorage.removeItem('token')
      this.$router.push('/login')
    }
  }
}
</script>

<style scoped>
h2 { color: #409eff; margin-bottom: 20px; }
.v-data-table { background-color: #e6f7ff; }
</style>
