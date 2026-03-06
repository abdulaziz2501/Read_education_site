// Auth utility for READ EDUCATION
const API_URL = ''; // Same origin

const auth = {
    // Pages that don't require login
    publicRoutes: ['/', '/login', '/verify', '/index.html'],

    setToken(token) {
        if (token) localStorage.setItem('access_token', token);
    },
    getToken() {
        return localStorage.getItem('access_token');
    },
    logout() {
        localStorage.removeItem('access_token');
        // Only redirect if NOT on a public page
        if (!this.isPublicPath(window.location.pathname)) {
            window.location.href = '/login';
        }
    },
    isPublicPath(path) {
        // Normalize path: remove trailing slash, handle empty, etc.
        const normalized = path === '' ? '/' : (path.endsWith('/') && path.length > 1 ? path.slice(0, -1) : path);
        return this.publicRoutes.includes(normalized) || normalized.startsWith('/certificate/');
    },
    async fetchWithAuth(url, options = {}) {
        const token = this.getToken();
        const headers = { 'Content-Type': 'application/json', ...options.headers };
        if (token) headers['Authorization'] = `Bearer ${token}`;

        try {
            const response = await fetch(url, { ...options, headers });
            if (response.status === 401) {
                // Token is dead. Clear it.
                if (this.getToken()) {
                    localStorage.removeItem('access_token');
                }
                // Only force redirect if the CURRENT page is private
                if (!this.isPublicPath(window.location.pathname)) {
                    window.location.href = '/login';
                }
            }
            return response;
        } catch (err) {
            console.error('Fetch error:', err);
            throw err;
        }
    },
    async getUser() {
        const token = this.getToken();
        if (!token) return null;

        try {
            const response = await this.fetchWithAuth('/api/auth/me');
            if (response.ok) return await response.json();
        } catch (e) { }
        return null; // For 401 etc.
    },
    async checkAuthAndRedirect() {
        const user = await this.getUser();
        const path = window.location.pathname;

        if (!user) {
            // Not logged in: If private page, go to login
            if (!this.isPublicPath(path)) {
                window.location.href = '/login';
            }
        } else {
            // Logged in: If on login page, go to appropriate dashboard
            if (path === '/login') {
                window.location.href = user.role === 'admin' ? '/admin' : '/dashboard';
            }
        }
        return user;
    }
};
