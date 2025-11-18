// API Configuration
const API_BASE_URL = window.location.origin; // Use relative URL for nginx gateway
// const API_BASE_URL = 'http://localhost'; // Fallback

// Get JWT token from localStorage
function getToken() {
    return localStorage.getItem('jwt_token');
}

// Save JWT token to localStorage
function saveToken(token) {
    localStorage.setItem('jwt_token', token);
}

// Remove JWT token from localStorage
function removeToken() {
    localStorage.removeItem('jwt_token');
    localStorage.removeItem('username');
}

// Get username from localStorage
function getUsername() {
    return localStorage.getItem('username');
}

// Save username to localStorage
function saveUsername(username) {
    localStorage.setItem('username', username);
}

// API Request helper
async function apiRequest(endpoint, options = {}) {
    const token = getToken();
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    if (token && endpoint !== '/login' && endpoint !== '/register') {
        headers['Authorization'] = token;
    }

    const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
    
    try {
        const response = await fetch(url, {
            ...options,
            headers
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || 'Request failed');
        }

        return data;
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Auth API
const authAPI = {
    async login(username, password) {
        return apiRequest('/login', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    },

    async register(username, password) {
        return apiRequest('/register', {
            method: 'POST',
            body: JSON.stringify({ username, password })
        });
    },

    async verifyToken(token) {
        return apiRequest('/auth/verify', {
            method: 'POST',
            headers: {
                'Authorization': token
            }
        });
    }
};

// Products API
const productsAPI = {
    async getAll() {
        return apiRequest('/products');
    },

    async getById(id) {
        return apiRequest(`/products/${id}`);
    },

    async create(product) {
        return apiRequest('/products', {
            method: 'POST',
            body: JSON.stringify(product)
        });
    },

    async update(id, product) {
        return apiRequest(`/products/${id}`, {
            method: 'PUT',
            body: JSON.stringify(product)
        });
    },

    async delete(id, amount) {
        return apiRequest(`/products/${id}`, {
            method: 'DELETE',
            body: JSON.stringify({ amount })
        });
    }
};

// Orders API
const ordersAPI = {
    async getAll() {
        return apiRequest('/orders');
    },

    async getById(id) {
        return apiRequest(`/orders/${id}`);
    },

    async create(order) {
        return apiRequest('/orders', {
            method: 'POST',
            body: JSON.stringify(order)
        });
    },

    async update(id, order) {
        return apiRequest(`/orders/${id}`, {
            method: 'PUT',
            body: JSON.stringify(order)
        });
    },

    async delete(id) {
        return apiRequest(`/orders/${id}`, {
            method: 'DELETE'
        });
    }
};

// Reports API
const reportsAPI = {
    async getAllOrderReports() {
        return apiRequest('/reports/orders');
    },

    async getOrderReportById(id) {
        return apiRequest(`/reports/orders/${id}`);
    },

    async createOrderReport(orderId) {
        return apiRequest('/reports/orders', {
            method: 'POST',
            body: JSON.stringify({ order_id: orderId })
        });
    },

    async deleteOrderReport(id) {
        return apiRequest(`/reports/orders/${id}`, {
            method: 'DELETE'
        });
    },

    async getAllProductReports() {
        return apiRequest('/reports/products');
    },

    async getProductReportById(id) {
        return apiRequest(`/reports/products/${id}`);
    },

    async createProductReport(orderReportId, productId) {
        return apiRequest('/reports/products', {
            method: 'POST',
            body: JSON.stringify({
                order_report_id: orderReportId,
                product_id: productId
            })
        });
    },

    async deleteProductReport(id) {
        return apiRequest(`/reports/products/${id}`, {
            method: 'DELETE'
        });
    },

    async getProductStatistics(productId) {
        return apiRequest(`/reports/products/${productId}/statistics`);
    }
};

