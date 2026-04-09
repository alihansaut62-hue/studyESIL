// Обновление количества товаров в корзине
document.querySelectorAll('.qty-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const input = this.parentElement.querySelector('input');
        let value = parseInt(input.value);
        
        if(this.classList.contains('plus')) {
            value++;
        } else if(this.classList.contains('minus') && value > 1) {
            value--;
        }
        
        input.value = value;
        updateCartItem(this.dataset.id, value);
    });
});

// Функция обновления корзины
function updateCartItem(itemId, quantity) {
    fetch('pages/update-cart.php', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            id: itemId,
            quantity: quantity
        })
    })
    .then(response => response.json())
    .then(data => {
        if(data.success) {
            location.reload();
        }
    });
}

// Таймер обратного отсчета
function startCountdown(days, hours, minutes, seconds) {
    const timer = setInterval(() => {
        if(seconds > 0) {
            seconds--;
        } else {
            if(minutes > 0) {
                minutes--;
                seconds = 59;
            } else if(hours > 0) {
                hours--;
                minutes = 59;
                seconds = 59;
            } else if(days > 0) {
                days--;
                hours = 23;
                minutes = 59;
                seconds = 59;
            } else {
                clearInterval(timer);
            }
        }
        
        // Обновление DOM
        document.querySelectorAll('.time-block').forEach((block, index) => {
            const value = [days, hours, minutes, seconds][index];
            block.innerHTML = `${value.toString().padStart(2, '0')} <span>${block.querySelector('span').textContent}</span>`;
        });
    }, 1000);
}

// Валидация форм
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function(e) {
        const password = this.querySelector('#password');
        const confirmPassword = this.querySelector('#confirm_password');
        
        if(password && confirmPassword && password.value !== confirmPassword.value) {
            e.preventDefault();
            alert('Passwords do not match!');
        }
    });
});

// Фильтры на странице магазина
document.querySelectorAll('.filter-section input').forEach(input => {
    input.addEventListener('change', function() {
        const form = document.createElement('form');
        form.method = 'GET';
        form.action = window.location.pathname;
        
        // Сбор всех выбранных фильтров
        document.querySelectorAll('.filter-section input:checked').forEach(checked => {
            const hidden = document.createElement('input');
            hidden.type = 'hidden';
            hidden.name = checked.name;
            hidden.value = checked.value;
            form.appendChild(hidden);
        });
        
        document.body.appendChild(form);
        form.submit();
    });
});