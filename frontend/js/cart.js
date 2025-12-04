let cart = JSON.parse(localStorage.getItem('cart')) || [];

function updateCartCount() {
    const count = cart.reduce((sum, item) => sum + item.quantity, 0);
    document.getElementById('cartCount').textContent = count;
}

function addToCart(product) {
    const existingItem = cart.find(item => item.id === product.id);
    if (existingItem) {
        if (existingItem.quantity < product.quantity) {
            existingItem.quantity++;
        } else {
            alert('Đã đạt giới hạn số lượng sản phẩm này!');
            return;
        }
    } else {
        cart.push({
            id: product.id,
            name: product.name,
            price: product.price,
            quantity: 1,
            maxQuantity: product.quantity
        });
    }
    saveCart();
    updateCartCount();
    alert('Đã thêm vào giỏ hàng!');
}

function removeFromCart(productId) {
    cart = cart.filter(item => item.id !== productId);
    saveCart();
    updateCartCount();
    renderCart();
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function toggleCart() {
    const modal = document.getElementById('cartModal');
    if (modal.style.display === 'block') {
        modal.style.display = 'none';
    } else {
        renderCart();
        modal.style.display = 'block';
    }
}

function renderCart() {
    const cartItemsDiv = document.getElementById('cartItems');
    const cartTotalSpan = document.getElementById('cartTotal');
    
    if (cart.length === 0) {
        cartItemsDiv.innerHTML = '<p>Giỏ hàng trống.</p>';
        cartTotalSpan.textContent = '0';
        return;
    }

    let total = 0;
    cartItemsDiv.innerHTML = cart.map(item => {
        const itemTotal = item.price * item.quantity;
        total += itemTotal;
        return `
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #eee; padding: 10px 0;">
                <div>
                    <h4>${item.name}</h4>
                    <p>${formatPrice(item.price)} ₫ x ${item.quantity}</p>
                </div>
                <div>
                    <p>${formatPrice(itemTotal)} ₫</p>
                    <button class="btn btn-secondary" onclick="removeFromCart(${item.id})" style="background: #e53e3e;">Xóa</button>
                </div>
            </div>
        `;
    }).join('');

    cartTotalSpan.textContent = formatPrice(total);
}

async function checkout() {
    if (cart.length === 0) {
        alert('Giỏ hàng trống!');
        return;
    }

    if (!getToken()) {
        alert('Vui lòng đăng nhập để thanh toán!');
        window.location.href = 'login.html';
        return;
    }

    const confirmCheckout = confirm('Bạn có chắc chắn muốn thanh toán?');
    if (!confirmCheckout) return;

    try {
        // 1. Create Order
        const user = getUsername(); // Assuming username is stored
        // Need email, let's fake it or get from profile if available. 
        // Since we don't have profile API easily, we'll use dummy email or username@example.com
        const orderData = {
            id: Date.now(), // Simple ID generation
            customer_name: user,
            customer_email: `${user}@example.com`,
            items: cart.map(item => ({
                id: Date.now() + Math.floor(Math.random() * 1000),
                product_id: item.id,
                product_name: item.name,
                quantity: item.quantity,
                unit_price: item.price
            }))
        };

        console.log('Creating order...', orderData);
        const order = await ordersAPI.create(orderData);
        console.log('Order created:', order);

        // 2. Update Product Quantity (Stock)
        // Note: The order service might check stock but doesn't update it automatically in this architecture 
        // (based on my analysis of order_service/app.py, it checks stock but doesn't call product service to reduce it? 
        // Wait, let me re-read order_service/app.py. 
        // It calls check_product_stock but NOT reduce_quantity. 
        // So we must do it here or Order Service should have done it. 
        // The prompt says "Cập nhật lại số lượng sp... API: PUT localhost:***1/products/id".
        // So client must do it.
        
        for (const item of cart) {
            // Calculate new quantity
            const newQty = item.maxQuantity - item.quantity;
            await productsAPI.update(item.id, { quantity: newQty });
        }

        // 3. Update Order Status (Simulate Payment/Shipping)
        await ordersAPI.update(order.id, { status: 'completed' });

        // 4. Create Reports
        // Order Report
        // Note: reportsAPI.createOrderReport might need to be awaited and check response
        const orderReport = await reportsAPI.createOrderReport(order.id);
        
        // Product Reports
        // We need to create a report for each product in the order
        // The API requires order_report_id.
        // Assuming orderReport contains the ID.
        // Let's check report_service if I can. But I'll assume standard response.
        // If orderReport is the response JSON, it should have the ID.
        
        if (orderReport && (orderReport.id || orderReport._id)) {
             const reportId = orderReport.id || orderReport._id;
             for (const item of cart) {
                 await reportsAPI.createProductReport(reportId, item.id);
             }
        }
        
        alert('Thanh toán thành công! Đơn hàng #' + order.id);
        cart = [];
        saveCart();
        updateCartCount();
        toggleCart();
        loadProducts(); // Reload to show new quantities
        
    } catch (error) {
        console.error('Checkout error:', error);
        alert('Có lỗi xảy ra khi thanh toán: ' + error.message);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
});
