// User page functions
let allProducts = [];

// Load products on page load
document.addEventListener('DOMContentLoaded', async () => {
    checkUserAuth();
    await loadProducts();
});

function checkUserAuth() {
    const username = getUsername();
    const token = getToken();
    
    if (username && token) {
        document.getElementById('userInfo').textContent = `Xin chào, ${username}`;
        document.getElementById('loginBtn').style.display = 'none';
        document.getElementById('logoutBtn').style.display = 'inline-block';
    } else {
        document.getElementById('userInfo').textContent = '';
        document.getElementById('loginBtn').style.display = 'inline-block';
        document.getElementById('logoutBtn').style.display = 'none';
    }
}

function logout() {
    removeToken();
    window.location.href = 'index.html';
}

async function loadProducts() {
    const loading = document.getElementById('loading');
    const errorDiv = document.getElementById('errorMessage');
    const productsGrid = document.getElementById('productsGrid');

    try {
        loading.style.display = 'block';
        errorDiv.style.display = 'none';
        
        const products = await productsAPI.getAll();
        allProducts = products;
        
        displayProducts(products);
        loading.style.display = 'none';
    } catch (error) {
        loading.style.display = 'none';
        errorDiv.textContent = 'Không thể tải sản phẩm. Vui lòng thử lại sau.';
        errorDiv.style.display = 'block';
        productsGrid.innerHTML = '';
        console.error('Error loading products:', error);
    }
}

function displayProducts(products) {
    const productsGrid = document.getElementById('productsGrid');
    
    if (!products || products.length === 0) {
        productsGrid.innerHTML = '<p style="text-align:center; color:white; padding:40px;">Không có sản phẩm nào.</p>';
        return;
    }

    productsGrid.innerHTML = products.map(product => `
        <div class="product-card">
            <div style="background: #667eea; height: 200px; border-radius: 5px; display: flex; align-items: center; justify-content: center; color: white; font-size: 3rem; margin-bottom: 15px;">
                🛍️
            </div>
            <h3>${product.name}</h3>
            <p class="price">${formatPrice(product.price)} ₫</p>
            <p class="quantity">Còn lại: ${product.quantity} sản phẩm</p>
            ${product.description ? `<p class="description">${product.description}</p>` : ''}
        </div>
    `).join('');
}

function filterProducts() {
    const searchInput = document.getElementById('searchInput').value.toLowerCase();
    const filtered = allProducts.filter(product => 
        product.name.toLowerCase().includes(searchInput) ||
        (product.description && product.description.toLowerCase().includes(searchInput))
    );
    displayProducts(filtered);
}

function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN').format(price);
}

