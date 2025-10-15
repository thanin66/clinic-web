<template>
  <v-container class="d-flex justify-center align-center" style="height: 100vh;">
    <v-progress-circular indeterminate color="primary" class="mr-2"></v-progress-circular>
    <h3 class="ml-2">กำลังเข้าสู่ระบบด้วย Google...</h3>
  </v-container>
</template>

<script>
export default {
  name: 'GoogleCallbackPage',
  mounted() {
    // 1. ดึง Query Parameter ที่ชื่อ 'token'
    const token = this.$route.query.token;
    const error = this.$route.query.error;

    if (token) {
      // 2. ถ้ามี token ให้บันทึกและไปหน้า Dashboard
      localStorage.setItem("token", token);
      this.$router.push("/appointments");
    } else if (error) {
      // 3. ถ้ามี error
      alert("การล็อกอินด้วย Google ล้มเหลว โปรดลองอีกครั้ง");
      this.$router.push("/login");
    } else {
      // 4. กรณีที่ไม่ปกติ
      alert("เกิดข้อผิดพลาดในการล็อกอิน");
      this.$router.push("/login");
    }
  }
}
</script>