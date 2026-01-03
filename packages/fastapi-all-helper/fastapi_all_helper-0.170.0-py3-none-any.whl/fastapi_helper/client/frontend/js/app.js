document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const errorMessage = document.getElementById('errorMessage');
    const submitBtn = loginForm.querySelector('.submit-btn');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const username = usernameInput.value.trim();
        const password = passwordInput.value;
        
        // Validation
        if (!username || !password) {
            showError('Пожалуйста, заполните все поля');
            return;
        }
        
        // Show loading state
        submitBtn.classList.add('loading');
        submitBtn.innerHTML = '<span>Загрузка...</span>';
        hideError();
        
        try {
            const response = await fetch('/admin/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: username,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (response.ok && data.success) {
                // Success - redirect to panel
                submitBtn.innerHTML = '<span>Успешно!</span><i class="fas fa-check"></i>';
                submitBtn.style.background = 'linear-gradient(135deg, #10b981, #059669)';
                
                setTimeout(() => {
                    window.location.href = data.redirect_url || '/admin/panel';
                }, 500);
            } else {
                // Error
                showError(data.message || 'Неверный логин или пароль');
                resetSubmitButton();
            }
        } catch (error) {
            console.error('Login error:', error);
            showError('Произошла ошибка. Попробуйте снова.');
            resetSubmitButton();
        }
    });
    
    function resetSubmitButton() {
        submitBtn.classList.remove('loading');
        submitBtn.innerHTML = '<span>Войти</span><i class="fas fa-arrow-right"></i>';
        submitBtn.disabled = false;
    }
    
    function showError(message) {
        const errorSpan = errorMessage.querySelector('span');
        errorSpan.textContent = message;
        errorMessage.classList.remove('hidden');
        
        // Shake animation on inputs
        usernameInput.style.animation = 'shake 0.5s ease';
        passwordInput.style.animation = 'shake 0.5s ease';
        
        setTimeout(() => {
            usernameInput.style.animation = '';
            passwordInput.style.animation = '';
        }, 500);
    }
    
    function hideError() {
        errorMessage.classList.add('hidden');
    }
    
    // Focus first input
    usernameInput.focus();
});