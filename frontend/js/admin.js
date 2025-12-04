// Admin page functions
let orderItemCounter = 0;
let allProductsForOrder = [];

// Initialize admin page
document.addEventListener('DOMContentLoaded', async () => {
    checkAdminAuth();
    await loadProductsForAdmin();
    await loadOrders();
    await loadReports();
});

function checkAdminAuth() {
    const token = getToken();
    const username = getUsername();
    
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    if (username) {
        document.getElementById('adminInfo').textContent = `Xin chào, ${username} (Admin)`;
    }

    // Verify token
    authAPI.verifyToken(token).catch(() => {
        removeToken();
        window.location.href = 'login.html';
    });
}

function logout() {
    removeToken();
    window.location.href = 'index.html';
}

// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Remove active class from all buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}Tab`).classList.add('active');
    event.target.classList.add('active');

    // Load data if needed
    if (tabName === 'orders') {
        loadOrders();
    } else if (tabName === 'reports') {
        loadReports();
    }
}

// ==================== PRODUCTS MANAGEMENT ====================

async function loadProductsForAdmin() {
    try {
        const products = await productsAPI.getAll();
        allProductsForOrder = products;
        displayProductsTable(products);
    } catch (error) {
        document.getElementById('productsTableBody').innerHTML = 
            '<tr><td colspan="7" class="text-center">Lỗi tải dữ liệu</td></tr>';
        console.error('Error loading products:', error);
    }
}

function displayProductsTable(products) {
    const tbody = document.getElementById('productsTableBody');
    
    if (!products || products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Không có sản phẩm nào</td></tr>';
        return;
    }

    tbody.innerHTML = products.map(product => `
        <tr>
            <td>${product.id}</td>
            <td>${product.name}</td>
            <td>${product.description || '-'}</td>
            <td>${formatPrice(product.price)} ₫</td>
            <td>${product.quantity}</td>
            <td>${product.updated_at ? new Date(product.updated_at).toLocaleString('vi-VN') : '-'}</td>
            <td>
                <button class="btn btn-primary" onclick="showEditProductModal(${product.id})">Sửa</button>
                <button class="btn btn-danger" onclick="deleteProductConfirm(${product.id})">Xóa</button>
            </td>
        </tr>
    `).join('');
}

function showAddProductModal() {
    document.getElementById('addProductModal').style.display = 'block';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

async function addProduct(event) {
    event.preventDefault();
    
    const product = {
        id: parseInt(document.getElementById('productId').value),
        name: document.getElementById('productName').value,
        description: document.getElementById('productDescription').value,
        price: parseFloat(document.getElementById('productPrice').value),
        quantity: parseInt(document.getElementById('productQuantity').value)
    };

    try {
        await productsAPI.create(product);
        closeModal('addProductModal');
        await loadProductsForAdmin();
        // Reset form
        document.getElementById('addProductModal').querySelector('form').reset();
    } catch (error) {
        alert('Lỗi thêm sản phẩm: ' + error.message);
    }
}

function showEditProductModal(productId) {
    const product = allProductsForOrder.find(p => p.id === productId);
    if (!product) return;

    document.getElementById('editProductId').value = product.id;
    document.getElementById('editProductName').value = product.name;
    document.getElementById('editProductDescription').value = product.description || '';
    document.getElementById('editProductPrice').value = product.price;
    document.getElementById('editProductQuantity').value = product.quantity;
    
    document.getElementById('editProductModal').style.display = 'block';
}

async function updateProduct(event) {
    event.preventDefault();
    
    const id = parseInt(document.getElementById('editProductId').value);
    const product = {
        name: document.getElementById('editProductName').value,
        description: document.getElementById('editProductDescription').value,
        price: parseFloat(document.getElementById('editProductPrice').value),
        quantity: parseInt(document.getElementById('editProductQuantity').value)
    };

    try {
        await productsAPI.update(id, product);
        closeModal('editProductModal');
        await loadProductsForAdmin();
    } catch (error) {
        alert('Lỗi cập nhật sản phẩm: ' + error.message);
    }
}

async function deleteProductConfirm(productId) {
    const amount = prompt('Nhập số lượng cần xóa (hoặc số lớn hơn để xóa hết):');
    if (!amount || isNaN(amount)) return;

    try {
        await productsAPI.delete(productId, parseInt(amount));
        await loadProductsForAdmin();
    } catch (error) {
        alert('Lỗi xóa sản phẩm: ' + error.message);
    }
}

// ==================== ORDERS MANAGEMENT ====================

async function loadOrders() {
    try {
        const orders = await ordersAPI.getAll();
        displayOrdersTable(orders);
    } catch (error) {
        document.getElementById('ordersTableBody').innerHTML = 
            '<tr><td colspan="7" class="text-center">Lỗi tải dữ liệu</td></tr>';
        console.error('Error loading orders:', error);
    }
}

function displayOrdersTable(orders) {
    const tbody = document.getElementById('ordersTableBody');
    
    if (!orders || orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Không có đơn hàng nào</td></tr>';
        return;
    }

    tbody.innerHTML = orders.map(order => `
        <tr>
            <td>${order.id}</td>
            <td>${order.customer_name}</td>
            <td>${order.customer_email}</td>
            <td>${formatPrice(order.total_amount || 0)} ₫</td>
            <td><span class="status-badge ${order.status}">${order.status}</span></td>
            <td>${order.created_at ? new Date(order.created_at).toLocaleString('vi-VN') : '-'}</td>
            <td>
                <button class="btn btn-primary" onclick="viewOrderDetails(${order.id})">Xem</button>
                <button class="btn btn-secondary" onclick="showUpdateStatusModal(${order.id}, '${order.status}')">Cập Nhật TT</button>
                <button class="btn btn-danger" onclick="deleteOrderConfirm(${order.id})">Xóa</button>
            </td>
        </tr>
    `).join('');
}

function showUpdateStatusModal(orderId, currentStatus) {
    document.getElementById('statusOrderId').value = orderId;
    document.getElementById('newStatus').value = currentStatus;
    document.getElementById('updateStatusModal').style.display = 'block';
}

async function updateOrderStatus(event) {
    event.preventDefault();
    const orderId = document.getElementById('statusOrderId').value;
    const newStatus = document.getElementById('newStatus').value;

    try {
        await ordersAPI.update(orderId, { status: newStatus });
        closeModal('updateStatusModal');
        await loadOrders();
        alert('Cập nhật trạng thái thành công!');
    } catch (error) {
        alert('Lỗi cập nhật trạng thái: ' + error.message);
    }
}

async function viewOrderDetails(orderId) {
    try {
        const order = await ordersAPI.getById(orderId);
        const modal = document.getElementById('orderDetailsModal');
        const content = document.getElementById('orderDetailsContent');
        
        content.innerHTML = `
            <p><strong>ID:</strong> ${order.id}</p>
            <p><strong>Khách hàng:</strong> ${order.customer_name}</p>
            <p><strong>Email:</strong> ${order.customer_email}</p>
            <p><strong>Ngày tạo:</strong> ${new Date(order.created_at).toLocaleString('vi-VN')}</p>
            <p><strong>Trạng thái:</strong> <span class="status-badge ${order.status}">${order.status}</span></p>
            <hr>
            <h3>Sản phẩm:</h3>
            <table class="data-table" style="width: 100%;">
                <thead>
                    <tr>
                        <th>Sản phẩm</th>
                        <th>Đơn giá</th>
                        <th>Số lượng</th>
                        <th>Thành tiền</th>
                    </tr>
                </thead>
                <tbody>
                    ${order.items ? order.items.map(item => `
                        <tr>
                            <td>${item.product_name}</td>
                            <td>${formatPrice(item.unit_price)} ₫</td>
                            <td>${item.quantity}</td>
                            <td>${formatPrice(item.unit_price * item.quantity)} ₫</td>
                        </tr>
                    `).join('') : '<tr><td colspan="4">Không có sản phẩm</td></tr>'}
                </tbody>
                <tfoot>
                    <tr>
                        <td colspan="3" style="text-align: right; font-weight: bold;">Tổng cộng:</td>
                        <td style="font-weight: bold;">${formatPrice(order.total_amount)} ₫</td>
                    </tr>
                </tfoot>
            </table>
        `;
        
        modal.style.display = 'block';
    } catch (error) {
        alert('Lỗi tải chi tiết đơn hàng: ' + error.message);
    }
}

async function deleteOrderConfirm(orderId) {
    if (!confirm('Bạn có chắc muốn xóa đơn hàng này?')) return;

    try {
        await ordersAPI.delete(orderId);
        await loadOrders();
    } catch (error) {
        alert('Lỗi xóa đơn hàng: ' + error.message);
    }
}

// ==================== REPORTS MANAGEMENT ====================

async function loadReports() {
    try {
        const [orderReports, productReports] = await Promise.all([
            reportsAPI.getAllOrderReports(),
            reportsAPI.getAllProductReports()
        ]);

        displayOrderReportsTable(orderReports);
        displayProductReportsTable(productReports);
        calculateStatistics(orderReports, productReports);
    } catch (error) {
        console.error('Error loading reports:', error);
    }
}

function displayOrderReportsTable(reports) {
    const tbody = document.getElementById('orderReportsTableBody');
    
    if (!reports || reports.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Chưa có báo cáo đơn hàng</td></tr>';
        return;
    }

    tbody.innerHTML = reports.map(report => `
        <tr>
            <td>${report.id || report.order_id}</td>
            <td>${report.order_id}</td>
            <td>${formatPrice(report.total_revenue)} ₫</td>
            <td>${formatPrice(report.total_cost)} ₫</td>
            <td class="profit">${formatPrice(report.total_profit)} ₫</td>
            <td>${report.created_at ? new Date(report.created_at).toLocaleString('vi-VN') : '-'}</td>
            <td>
                <button class="btn btn-danger" onclick="deleteOrderReportConfirm(${report.id || report.order_id})">Xóa</button>
            </td>
        </tr>
    `).join('');
}

function displayProductReportsTable(reports) {
    const tbody = document.getElementById('productReportsTableBody');
    
    if (!reports || reports.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">Chưa có báo cáo sản phẩm</td></tr>';
        return;
    }

    tbody.innerHTML = reports.map(report => `
        <tr>
            <td>${report.id}</td>
            <td>${report.product_id}</td>
            <td>${report.total_sold}</td>
            <td>${formatPrice(report.revenue)} ₫</td>
            <td>${formatPrice(report.cost)} ₫</td>
            <td class="profit">${formatPrice(report.profit)} ₫</td>
            <td>
                <button class="btn btn-danger" onclick="deleteProductReportConfirm(${report.id})">Xóa</button>
            </td>
        </tr>
    `).join('');
}

function calculateStatistics(orderReports, productReports) {
    let totalRevenue = 0;
    let totalCost = 0;
    let totalOrders = 0;

    if (orderReports) {
        orderReports.forEach(report => {
            totalRevenue += report.total_revenue || 0;
            totalCost += report.total_cost || 0;
            totalOrders++;
        });
    }

    const totalProfit = totalRevenue - totalCost;

    document.getElementById('totalRevenue').textContent = formatPrice(totalRevenue) + ' ₫';
    document.getElementById('totalCost').textContent = formatPrice(totalCost) + ' ₫';
    document.getElementById('totalProfit').textContent = formatPrice(totalProfit) + ' ₫';
    document.getElementById('totalOrders').textContent = totalOrders;
}

async function generateOrderReport() {
    const orderId = prompt('Nhập ID đơn hàng cần tạo báo cáo:');
    if (!orderId) return;

    try {
        await reportsAPI.createOrderReport(parseInt(orderId));
        alert('Tạo báo cáo thành công!');
        await loadReports();
    } catch (error) {
        alert('Lỗi tạo báo cáo: ' + error.message);
    }
}

async function deleteOrderReportConfirm(id) {
    if (!confirm('Bạn có chắc muốn xóa báo cáo này?')) return;

    try {
        await reportsAPI.deleteOrderReport(id);
        await loadReports();
    } catch (error) {
        alert('Lỗi xóa báo cáo: ' + error.message);
    }
}

async function deleteProductReportConfirm(id) {
    if (!confirm('Bạn có chắc muốn xóa báo cáo này?')) return;

    try {
        await reportsAPI.deleteProductReport(id);
        await loadReports();
    } catch (error) {
        alert('Lỗi xóa báo cáo: ' + error.message);
    }
}

// Utility functions
function formatPrice(price) {
    return new Intl.NumberFormat('vi-VN').format(price || 0);
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        if (event.target === modal) {
            modal.style.display = 'none';
        }
    });
}

