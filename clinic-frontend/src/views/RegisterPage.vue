<template>
  <v-container class="d-flex justify-center align-center" style="height: 100vh;">
    <v-card width="400" class="pa-6">
      <h2 class="text-center mb-4">สมัครสมาชิก</h2>

      <!--error -->
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
          v-model="username"
          label="ชื่อผู้ใช้"
          :rules="[rules.username]"
          prepend-icon="mdi-account"
          clearable
        />

        <v-text-field
          v-model="email"
          label="อีเมล"
          :rules="[rules.email]"
          prepend-icon="mdi-email"
          clearable
        />
        
        <v-text-field
          v-model="password"
          label="รหัสผ่าน"
          type="password"
          :rules="[rules.password]"
          prepend-icon="mdi-lock"
          clearable
        />

        <v-btn
          :disabled="!isValid || loading"
          color="primary"
          block
          class="mt-4"
          @click="register"
        >
          {{ loading ? 'กำลังสมัคร...' : 'สมัครสมาชิก' }}
        </v-btn>

        <div class="text-center mt-4">
          <small>มีบัญชีแล้ว? 
            <RouterLink to="/login">เข้าสู่ระบบ</RouterLink>
          </small>
        </div>
      </v-form>
    </v-card>
  </v-container>
</template>

<script>
import api from "../api/axios";

export default {
  name: "RegisterPage",
  data() {
    return {
      username: "",
      email: "",
      password: "",
      errorMessage: "",
      loading: false,
      isValid: false,
      rules: {
        username: v => (!!v && /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z0-9]{3,20}$/.test(v)) 
                || 'Username ต้องมี 3-20 ตัวอักษรและตัวเลข, ต้องมีทั้งตัวอักษรและตัวเลข',
        password: v => (!!v && v.length >= 6) || 'Password ต้องมีอย่างน้อย 6 ตัวอักษร',
        email: v => !!v && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v) || 'กรุณากรอกอีเมลให้ถูกต้อง'
      },
    };
  },
  methods: {
    async register() {
      this.errorMessage = "";
      const form = this.$refs.form;

      const valid = await form.validate();
      if (!valid) return;

      this.loading = true;
      try {
        await api.post("/register", {
          username: this.username,
          email: this.email,
          password: this.password,
        });

        this.loading = false;
        alert("✅ สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ");
        this.$router.push("/login");
      } catch (err) {
        console.error("Register error:", err);

        this.loading = false;

        const backendMsg =
          err?.detail ||
          err?.response?.data?.detail ||
          err?.message ||
          "เกิดข้อผิดพลาดระหว่างสมัครสมาชิก";
        if (typeof backendMsg === "string" && backendMsg.includes("value_error")) {
          this.errorMessage = "กรุณากรอกข้อมูลให้ถูกต้อง";
        } else {
          this.errorMessage = backendMsg;
        }
      }
    },
  },
};
</script>

<style scoped>
.v-card {
  border-radius: 12px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.15);
}
h2 {
  color: #409eff;
}
</style>
