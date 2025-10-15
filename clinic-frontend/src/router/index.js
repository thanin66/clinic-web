import { createRouter, createWebHistory } from 'vue-router'
import LoginPage from '../views/LoginPage.vue'
import RegisterPage from '../views/RegisterPage.vue'
import ProfilePage from '../views/ProfilePage.vue'
import AppointmentPage from '../views/AppointmentPage.vue'

// **************** START: เพิ่ม Google Callback Component ****************
const GoogleCallback = {
    template: '<div class="d-flex justify-center align-center" style="height: 100vh;"><h3>กำลังเข้าสู่ระบบ...</h3></div>',
    mounted() {
        // 1. ดึง Token จาก Query Parameter ที่ Backend แนบมา
        const token = this.$route.query.token;
        const error = this.$route.query.error;

        if (token) {
            // 2. ถ้ามี Token ให้บันทึกและ Redirect ไปหน้า appointments
            localStorage.setItem("token", token);
            this.$router.push("/appointments");
        } else if (error) {
            // 3. ถ้ามี Error (เช่น google_auth_failed) ให้กลับไปหน้า Login
            this.$router.push({ path: "/login", query: { error: error } });
        } else {
            // 4. กรณีที่ไม่มี Token หรือ Error ให้กลับไปหน้า Login
            this.$router.push("/login");
        }
    }
};
// **************** END: เพิ่ม Google Callback Component ****************

const routes = [
    { path: '/', redirect: '/login' },
    { path: '/login', component: LoginPage },
    { path: '/register', component: RegisterPage },
    { path: '/profile', component: ProfilePage, meta: { requiresAuth: true } },
    {
        path: '/appointments',
        component: AppointmentPage,
        meta: { requiresAuth: true }
    },
    // **************** START: เพิ่ม Callback Route ****************
    {
        // Path นี้ต้องตรงกับ URL ที่ FastAPI Redirect มา (ยกเว้น Domain/Port)
        path: '/login/callback',
        component: GoogleCallback
    }
    // **************** END: เพิ่ม Callback Route ****************
]

const router = createRouter({
    history: createWebHistory(),
    routes
})

// Router guard
router.beforeEach((to, from, next) => {
    const token = localStorage.getItem('token')
    if (to.meta.requiresAuth && !token) {
        next('/login')
    } else {
        next()
    }
})

export default router