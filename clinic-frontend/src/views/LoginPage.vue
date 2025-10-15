<template>
  <v-container class="d-flex justify-center align-center" style="height: 100vh;">
    <v-card width="400" class="pa-6">
      <h2 class="text-center mb-4">เข้าสู่ระบบ</h2>

      <v-alert
        v-if="errorMessage"
        type="error"
        density="compact"
        border="start"
        variant="tonal"
        class="mb-4"
      >
        {{ errorMessage }}
      </v-alert>

      <v-form ref="form" v-model="isValid" lazy-validation>
        <v-text-field
          v-model="email"
          label="อีเมล"
          :rules="[rules.email]"
          prepend-icon="mdi-email"
          clearable
          block
        />
        <v-text-field
          v-model="password"
          label="รหัสผ่าน"
          type="password"
          :rules="[rules.password]"
          prepend-icon="mdi-lock"
          clearable
          block
        />
        <v-btn
          color="primary"
          block
          class="mt-4"
          @click="login"
        >
          {{ loading ? 'กำลังเข้าสู่ระบบ...' : 'เข้าสู่ระบบ' }}
        </v-btn>

        <v-divider class="my-4" />
        <v-btn
          color="red"
          block
          class="mt-2 text-white"
          prepend-icon="mdi-google"
          @click="loginWithGoogle"
          :disabled="loading"
        >
          ล็อกอินด้วย Google
        </v-btn>
        <div class="text-center mt-3">
          <small>
            ยังไม่มีบัญชี? <RouterLink to="/register">สมัครที่นี่</RouterLink>
          </small>
        </div>
      </v-form>
    </v-card>
  </v-container>
</template>

<script>
import api from "../api/axios";

export default {
  name: "LoginPage",
  data() {
    return {
      email: "",
      password: "",
      errorMessage: "",
      loading: false,
      isValid: false,
      rules: {
        email: v => !!v && /^[^\\s@]+@[^\\s@]+\\.[^\\s@]+$/.test(v) || 'กรุณากรอกอีเมลให้ถูกต้อง',
        password: v => !!v && v.length >= 6 || 'Password ต้องมีอย่างน้อย 6 ตัวอักษร',
      },
    };
  },
  mounted() {
    // โค้ดสำหรับแสดง Error หากถูก Redirect มาจาก Google (กรณี Auth Fail)
    if (this.$route.query.error === 'google_auth_failed') {
      this.errorMessage = 'การล็อกอินด้วย Google ล้มเหลว โปรดลองอีกครั้ง';
    }
  },
  methods: {
    // ฟังก์ชัน login เดิม

  async login() {
    this.errorMessage = "";
    const form = this.$refs.form;
    const valid = await form.validate();
    if (!valid) return;

    this.loading = true;
    try {
      const res = await api.post("/login", {
        email: this.email,
        password: this.password
      });

      if(res.data && res.data.access_token) {
        localStorage.setItem("token", res.data.access_token);
        this.$router.push("/appointments");
      } else {
        this.errorMessage = "ไม่สามารถเข้าสู่ระบบได้ โปรดลองอีกครั้ง";
      }
    } catch (err) {
      console.error("Login error:", err);
      this.loading = false;

      const backendMsg = err.response?.data?.detail || err.message || "เกิดข้อผิดพลาดในการเข้าสู่ระบบ";
      this.errorMessage = backendMsg.includes("Incorrect") 
          ? "อีเมลหรือรหัสผ่านไม่ถูกต้อง" 
          : backendMsg;
    } finally {
      this.loading = false;
    }
  },

    // Google Login
    loginWithGoogle() {
      // Redirect ไปที่ backend
      const googleLoginUrl = `${api.defaults.baseURL}/auth/google/login`;
      window.location.href = googleLoginUrl;
    }
  },
};
</script>