// Authentication functions
async function handleLogin(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const errorDiv = document.getElementById('errorMessage');

    errorDiv.style.display = 'none';

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            const data = await response.json();
            if (data.token) {
                saveToken(data.token);
                saveUsername(data.username || username);
                window.location.href = 'admin.html';
            } else {
                errorDiv.textContent = 'Không nhận được token từ server.';
                errorDiv.style.display = 'block';
            }
        } else {
            const error = await response.json().catch(() => ({ error: 'Đăng nhập thất bại' }));
            errorDiv.textContent = error.error || 'Đăng nhập thất bại. Vui lòng kiểm tra lại thông tin.';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'Lỗi kết nối. Vui lòng thử lại sau.';
        errorDiv.style.display = 'block';
        console.error('Login error:', error);
    }
}

async function handleRegister(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;
    const errorDiv = document.getElementById('errorMessage');
    const successDiv = document.getElementById('successMessage');

    errorDiv.style.display = 'none';
    successDiv.style.display = 'none';

    if (password !== confirmPassword) {
        errorDiv.textContent = 'Mật khẩu xác nhận không khớp!';
        errorDiv.style.display = 'block';
        return;
    }

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ username, password })
        });

        if (response.ok || response.redirected) {
            successDiv.textContent = 'Đăng ký thành công! Đang chuyển đến trang đăng nhập...';
            successDiv.style.display = 'block';
            setTimeout(() => {
                window.location.href = 'login.html';
            }, 2000);
        } else {
            const error = await response.text().catch(() => 'Đăng ký thất bại');
            errorDiv.textContent = error || 'Đăng ký thất bại. Tên đăng nhập có thể đã tồn tại.';
            errorDiv.style.display = 'block';
        }
    } catch (error) {
        errorDiv.textContent = 'Lỗi kết nối. Vui lòng thử lại sau.';
        errorDiv.style.display = 'block';
        console.error('Register error:', error);
    }
}

// Check if user is logged in
function checkAuth() {
    const token = getToken();
    if (!token) {
        // Redirect to login if on protected page
        if (window.location.pathname.includes('admin.html')) {
            window.location.href = 'login.html';
        }
        return false;
    }
    return true;
}

