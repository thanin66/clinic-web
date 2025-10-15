// axios.js
import axios from "axios";
import router from "../router"; // ต้อง import router ของ Vue

const api = axios.create({
    baseURL: 'http://127.0.0.1:8000', // backend FastAPI
    headers: { 'Content-Type': 'application/json' },
    timeout: 10000,  // 10 วินาที
});

// ---------- ดักทุก request เพื่อแนบ token ----------
api.interceptors.request.use(config => {
    const token = localStorage.getItem('token');
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
});

// ---------- ดักทุก response เพื่อจัดการ error ----------
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response) {
            // ถ้า 401 ให้ลบ token และ redirect ไป login
            if (error.response.status === 401) {
                localStorage.removeItem("token");
                router.push("/login");
            }
            // ส่ง error object กลับไปให้ component
            return Promise.reject(error.response);
        }
        return Promise.reject(error);
    }
);

export default api;
