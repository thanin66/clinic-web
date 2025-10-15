<template>
  <v-container class="py-6">
    <v-card max-width="900" class="mx-auto pa-6">
      <h2 class="text-center mb-6">User Profile</h2>

      <!-- Alert -->
      <v-alert v-if="errorMessage" type="error" density="compact" border="start" variant="tonal" class="mb-4">
        {{ errorMessage }}
      </v-alert>

      <!-- Display Mode -->
      <div v-if="!isEditing">
        <v-row dense>
          <v-col cols="12" md="4">
            <v-card outlined class="pa-4 mb-4">
              <h3>ข้อมูล ส่วนตัว</h3>
              <p><strong>Username:</strong> {{ user.username }}</p>
              <p><strong>ชื่อ:</strong> {{ user.first_name || '-' }}</p>
              <p><strong>นามสกุล:</strong> {{ user.last_name || '-' }}</p>
              <p><strong>วันเกิด:</strong> {{ user.date_of_birth || '-' }}</p>
              <p><strong>ที่อยู่:</strong> {{ user.address || '-' }}</p>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card outlined class="pa-4 mb-4">
              <h3>ช่องทางการติดต่อ</h3>
              <p><strong>อีเมล:</strong> {{ user.email }}</p>
              <p><strong>เบอร์โทร:</strong> {{ user.phone_number || '-' }}</p>
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card outlined class="pa-4 mb-4">
              <h3>ข้อมูลทางการแพทย์</h3>
              <p><strong>การแพ้:</strong> {{ user.allergies || 'ไม่มีข้อมูล' }}</p>
              <p><strong>โรคประจำตัว:</strong> {{ user.chronic_conditions || 'ไม่มีข้อมูล' }}</p>
              <p><strong>ยาที่ใช้:</strong> {{ user.current_medications || 'ไม่มีข้อมูล' }}</p>
            </v-card>
          </v-col>
        </v-row>
      </div>

      <!-- Edit Mode -->
      <v-form v-else ref="form" v-model="isValid" lazy-validation>
        <v-row dense>
          <v-col cols="12" md="4">
            <v-card outlined class="pa-4 mb-4">
              <h3>แก้ไขข้อมูล ส่วนตัว</h3>
              <v-text-field v-model="editedUser.first_name" label="ชื่อ" />
              <v-text-field v-model="editedUser.last_name" label="นามสกุล" />
              <v-text-field v-model="editedUser.date_of_birth" label="วันเกิด" type="date" />
              <v-textarea v-model="editedUser.address" label="ที่อยู่" />
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card outlined class="pa-4 mb-4">
              <h3>แก้ไขช่องทางการติดต่อ</h3>
              <v-text-field v-model="editedUser.phone_number" label="เบอร์โทร" />
            </v-card>
          </v-col>

          <v-col cols="12" md="4">
            <v-card outlined class="pa-4 mb-4">
              <h3>แก้ไขข้อมูลทางการแพทย์</h3>
              <v-text-field v-model="editedUser.allergies" label="การแพ้" />
              <v-text-field v-model="editedUser.chronic_conditions" label="โรคประจำตัว" />
              <v-text-field v-model="editedUser.current_medications" label="ยาที่ใช้" />
            </v-card>
          </v-col>
        </v-row>

        <div class="d-flex justify-center gap-3 mt-4 flex-wrap">
          <v-btn color="success" @click="saveProfile" :loading="loading">บันทึก</v-btn>
          <v-btn color="error" @click="cancelEdit">ยกเลิก</v-btn>
        </div>
      </v-form>

      <!-- Action Buttons -->
      <div class="d-flex justify-center gap-3 mt-6 flex-wrap">
        <v-btn v-if="!isEditing" color="primary" @click="isEditing = true">แก้ไขข้อมูล</v-btn>
        <v-btn color="error" @click="confirmDelete = true">ลบผู้ใช้</v-btn>
        <v-btn color="secondary" @click="goDashboard">กลับ appointments</v-btn>
      </div>

      <!-- Delete Confirmation Dialog -->
      <v-dialog v-model="confirmDelete" max-width="400">
        <v-card>
          <v-card-title class="text-h6">ยืนยันการลบ</v-card-title>
          <v-card-text>
            คุณแน่ใจหรือว่าต้องการลบผู้ใช้นี้? การกระทำนี้ไม่สามารถย้อนกลับได้
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey" text @click="confirmDelete = false">ยกเลิก</v-btn>
            <v-btn color="error" @click="deleteUser" :loading="loading">ลบผู้ใช้</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>
  </v-container>
</template>

<script>
import api from '../api/axios'
import { useRouter } from 'vue-router'

export default {
  setup() {
    const router = useRouter()
    return { router }
  },
  data() {
    return {
      user: {},
      editedUser: {},
      isEditing: false,
      isValid: false,
      loading: false,
      errorMessage: "", 
      confirmDelete: false
    }
  },
  async created() {
    await this.fetchUser()
  },
  methods: {
    async fetchUser() {
      const token = localStorage.getItem('token')
      if (!token) return this.router.push('/login')

      try {
        const res = await api.get('/me', { headers: { Authorization: `Bearer ${token}` } })
        this.user = res.data
        this.editedUser = { ...res.data }

        // แปลงวันเกิดเป็น YYYY-MM-DD
        if (this.editedUser.date_of_birth)
          this.editedUser.date_of_birth = this.editedUser.date_of_birth.split('T')[0]
      } catch (err) {
        console.error(err)
        this.errorMessage = "ไม่สามารถโหลดข้อมูลผู้ใช้ได้"
        localStorage.removeItem('token')
        this.router.push('/login')
      }
    },
    cancelEdit() {
      this.editedUser = { ...this.user }
      if (this.editedUser.date_of_birth)
        this.editedUser.date_of_birth = this.editedUser.date_of_birth.split('T')[0]
      this.isEditing = false
    },
  async saveProfile() {
    const token = localStorage.getItem('token')
    this.loading = true
    this.errorMessage = ""

    try {
      const payload = { ...this.editedUser }

      // ✅ ถ้า date_of_birth เป็น string ว่าง ให้ลบออก
      if (!payload.date_of_birth) {
        delete payload.date_of_birth
      } else {
        const d = new Date(payload.date_of_birth)
        if (isNaN(d)) throw new Error("วันเกิดไม่ถูกต้อง")
        const yyyy = d.getFullYear()
        const mm = String(d.getMonth() + 1).padStart(2, '0')
        const dd = String(d.getDate()).padStart(2, '0')
        payload.date_of_birth = `${yyyy}-${mm}-${dd}`
      }

      console.log("Sending update:", payload)
      const res = await api.put('/me/profile', payload, { headers: { Authorization: `Bearer ${token}` } })

      this.user = res.data
      this.isEditing = false
      alert('บันทึกข้อมูลเรียบร้อย')
    } catch (err) {
      console.error(err)
      this.errorMessage = err?.data?.detail || 'บันทึกข้อมูลไม่สำเร็จ'
    } finally {
      this.loading = false
    }
  },
    async deleteUser() {
      const token = localStorage.getItem('token')
      this.loading = true
      try {
        await api.delete('/me', { headers: { Authorization: `Bearer ${token}` } })
        alert('ลบผู้ใช้เรียบร้อย')
        localStorage.removeItem('token')
        this.router.push('/login')
      } catch (err) {
        console.error(err)
        this.errorMessage = err?.response?.data?.detail || 'ไม่สามารถลบผู้ใช้ได้'
      } finally {
        this.loading = false
        this.confirmDelete = false
      }
    },
    goDashboard() {
      this.router.push('/appointments')
    }
  }
}
</script>

<style scoped>
h2 { color: #409eff; }
h3 { color: #31706c; }
</style>
