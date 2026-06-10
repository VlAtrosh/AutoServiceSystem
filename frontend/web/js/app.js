// ========== ГЛОБАЛЬНАЯ ФУНКЦИЯ ВХОДА ==========
window.manualLogin = async function() {
    const email = document.getElementById('login-email').value.trim();
    const password = document.getElementById('login-password').value.trim();
    const errorDiv = document.getElementById('login-error');
    
    if (errorDiv) errorDiv.textContent = '';
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: email, password: password })
        });

        if (res.ok) {
            const data = await res.json();
            localStorage.setItem('auth_token', data.access_token);
            
            const modal = document.getElementById('login-modal');
            if (modal) modal.style.display = 'none';
            
            await loadCurrentUser();
            await loadOrders();
            setupNavigation();
            setupUserProfile();
            
            showToast('Вход выполнен успешно', 'success');
        } else {
            const error = await res.json();
            if (errorDiv) errorDiv.textContent = error.detail || 'Неверный логин или пароль';
        }
    } catch (err) {
        console.error('Ошибка входа:', err);
        if (errorDiv) errorDiv.textContent = 'Ошибка подключения к серверу';
    }
};

// ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
function showLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) modal.style.display = 'flex';
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.textContent = message;
    
    // Принудительные стили прямо здесь
    toast.style.position = 'relative';
    toast.style.padding = '12px 20px';
    toast.style.borderRadius = '8px';
    toast.style.marginBottom = '10px';
    toast.style.fontSize = '14px';
    toast.style.fontWeight = '500';
    toast.style.boxShadow = '0 4px 12px rgba(0,0,0,0.15)';
    toast.style.animation = 'slideIn 0.3s ease-out';
    
    // Цвета
    if (type === 'success') {
        toast.style.backgroundColor = '#10b981';
        toast.style.color = 'white';
    } else if (type === 'error') {
        toast.style.backgroundColor = '#ef4444';
        toast.style.color = 'white';
    } else {
        toast.style.backgroundColor = '#3b82f6';
        toast.style.color = 'white';
    }
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 400);
    }, 3000);
}


function hideLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) modal.style.display = 'none';
}

async function checkTokenValidity() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        return false;
    }
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            return true;
        } else {
            localStorage.removeItem('auth_token');
            return false;
        }
    } catch (error) {
        console.error('Ошибка проверки токена:', error);
        return false;
    }
}

let currentUser = null;

async function loadCurrentUser() {
    const token = localStorage.getItem('auth_token');
    if (!token) return null;
    try {
        const res = await fetch('http://localhost:8000/api/v1/auth/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            currentUser = await res.json();
            const userNameEl = document.getElementById('user-name');
            const userRoleEl = document.getElementById('user-role');
            const userIdEl = document.getElementById('user-id');
            if (userNameEl) userNameEl.innerText = currentUser.username || currentUser.email;
            if (userRoleEl) userRoleEl.innerText = currentUser.role;
            if (userIdEl) userIdEl.innerText = currentUser.id;
            return currentUser;
        }
    } catch(e) { 
        console.log(e); 
    }
    return null;
}

function logout() {
    localStorage.removeItem('auth_token');
    currentUser = null;
    // Очищаем содержимое
    document.getElementById('content-area').innerHTML = '';
    // Показываем модальное окно
    showLoginModal();
    // Очищаем данные пользователя в сайдбаре
    document.getElementById('user-name').innerText = 'Пользователь';
    document.getElementById('user-role').innerText = '';
    document.getElementById('user-id').innerText = '';
}

// ========== МОДАЛЬНОЕ ОКНО СОЗДАНИЯ ЗАКАЗА ==========
function showCreateOrderModal() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        alert('Не авторизован');
        showLoginModal();
        return;
    }
    
    const modal = document.createElement('div');
    modal.id = 'create-order-modal';
    modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); display:flex; align-items:center; justify-content:center; z-index:10001;';
    modal.innerHTML = `
        <div style="background:white; border-radius:24px; width:400px; max-width:90%; padding:32px;">
            <h3 style="margin-bottom:20px;"> Новый заказ</h3>
            <div style="margin-bottom:16px;">
                <label style="display:block; margin-bottom:6px; font-weight:500;">ID автомобиля</label>
                <input type="text" id="order-car-id" placeholder="Введите ID автомобиля" style="width:100%; padding:12px; border:1px solid #e2e8f0; border-radius:12px;">
            </div>
            <div style="margin-bottom:16px;">
                <label style="display:block; margin-bottom:6px; font-weight:500;">Информация об авто</label>
                <input type="text" id="order-car" placeholder="BMW X5, 2022" style="width:100%; padding:12px; border:1px solid #e2e8f0; border-radius:12px;">
            </div>
            <div style="display:flex; gap:12px;">
                <button id="submit-order-btn" style="flex:1; padding:12px; background:#4f46e5; color:white; border:none; border-radius:12px; cursor:pointer;">Создать</button>
                <button id="cancel-order-btn" style="flex:1; padding:12px; background:#f1f5f9; border:none; border-radius:12px; cursor:pointer;">Отмена</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    document.getElementById('submit-order-btn').onclick = async () => {
        const carId = document.getElementById('order-car-id').value.trim();
        const carInfo = document.getElementById('order-car').value.trim();
        
        if (!carId || !carInfo) {
            alert('Заполните все поля');
            return;
        }
        
        try {
            const res = await fetch('http://localhost:8000/api/v1/orders/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ car_id: carId, car_info: carInfo })
            });
            
            if (res.ok) {
                alert('✅ Заказ создан!');
                modal.remove();
                location.reload();
            } else {
                const err = await res.json();
                alert('❌ Ошибка: ' + (err.detail || 'Неизвестная ошибка'));
            }
        } catch {
            alert('❌ Ошибка подключения к серверу');
        }
    };
    
    document.getElementById('cancel-order-btn').onclick = () => modal.remove();
}

// ========== ЗАГРУЗКА ЗАКАЗОВ ==========
async function loadOrders() {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    const content = document.getElementById('content-area');
    content.innerHTML = '<div class="loading">Загрузка заказов...</div>';
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/orders/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const orders = await res.json();
        
        if (!orders.length) {
            content.innerHTML = `
                <div class="empty-state">
                    <p>Пока нет заказов</p>
                    <button onclick="showCreateOrderForm()" class="btn btn-primary">Создать первый заказ</button>
                </div>`;
            return;
        }
        
        let html = '<div class="cards-grid">';
        for (const order of orders) {
            html += `
                <div class="order-card" onclick="showOrderDetails('${order.id}')">
                    <div class="order-header">
                        <span class="order-number">#${order.number || order.id.slice(0, 8)}</span>
                        <span class="order-status status-${order.status || 'new'}">${(order.status || 'Новый').toUpperCase()}</span>
                    </div>
                    <div class="order-car">${order.car_info || order.car_id}</div>
                    <div class="order-total">${(order.total || 0).toLocaleString()} ₽</div>
                    <div class="order-footer">Нажмите для просмотра деталей</div>
                </div>`;
        }
        html += '</div>';
        content.innerHTML = html;
    } catch(err) {
        content.innerHTML = '<div class="error-message">Ошибка загрузки заказов. Проверьте подключение.</div>';
    }
}

// ========== ЗАПИСЬ НА РЕМОНТ ==========
async function showAppointmentForm() {
    document.getElementById('page-title').textContent = 'Запись на ремонт';
    const content = document.getElementById('content-area');
    
    content.innerHTML = `
        <div style="max-width: 520px; margin: 0 auto;">
            <div class="order-card">
                <h3> Запись на ремонт</h3>
                <div class="form-group">
                    <label>Ваше имя *</label>
                    <input type="text" id="appointment-name" class="form-input" placeholder="Иван Петров">
                </div>
                <div class="form-group">
                    <label>Телефон *</label>
                    <input type="tel" id="appointment-phone" class="form-input" placeholder="+7 (999) 123-45-67">
                </div>
                <div class="form-group">
                    <label>Автомобиль *</label>
                    <input type="text" id="appointment-car" class="form-input" placeholder="BMW X5, 2022">
                </div>
                <div class="form-group">
                    <label>Желаемая дата</label>
                    <input type="date" id="appointment-date" class="form-input">
                </div>
                <div class="form-group">
                    <label>Описание проблемы</label>
                    <textarea id="appointment-desc" class="form-input" rows="4" placeholder="Опишите неисправность..."></textarea>
                </div>
                <button id="submit-appointment" class="btn btn-primary">✉️ Отправить заявку</button>
            </div>
        </div>
    `;
    
    document.getElementById('submit-appointment').addEventListener('click', async () => {
        const name = document.getElementById('appointment-name').value.trim();
        const phone = document.getElementById('appointment-phone').value.trim();
        const car = document.getElementById('appointment-car').value.trim();
        const date = document.getElementById('appointment-date').value;
        const desc = document.getElementById('appointment-desc').value.trim();
        
        if (!name || !phone || !car) {
            showToast('Заполните обязательные поля: имя, телефон, автомобиль', 'error');
            return;
        }
        
        const token = localStorage.getItem('auth_token');
        
        try {
            const res = await fetch('http://localhost:8000/api/v1/appointments/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({
                    client_name: name,
                    phone: phone,
                    car_info: car,
                    appointment_date: date || null,
                    description: desc || null
                })
            });
            
            if (res.ok) {
                showToast('✅ Заявка успешно отправлена! С вами свяжутся в ближайшее время.', 'success');
                document.getElementById('appointment-name').value = '';
                document.getElementById('appointment-phone').value = '';
                document.getElementById('appointment-car').value = '';
                document.getElementById('appointment-date').value = '';
                document.getElementById('appointment-desc').value = '';
            } else {
                const error = await res.json();
                showToast('❌ Ошибка: ' + (error.detail || 'Не удалось отправить заявку'), 'error');
            }
        } catch(err) {
            console.error(err);
            showToast('❌ Ошибка подключения к серверу', 'error');
        }
    });
}

// ========== КЛИЕНТЫ ==========
async function loadClients() {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка...</div>';
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/clients/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const clients = await res.json();
        
        if (!clients.length) {
            content.innerHTML = `
                <div style="text-align:center; padding:60px;">
                    <div style="font-size:48px;">👥</div>
                    <div style="color:#64748b;">Нет клиентов</div>
                    <button onclick="showAddClientForm()" class="btn-primary">+ Добавить клиента</button>
                </div>
            `;
            return;
        }
        
        let html = '<div class="cards-grid">';
        for (const client of clients) {
            html += `
                <div class="order-card" style="cursor: pointer;" onclick="showClientDetails('${client.id}')">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <strong>${client.last_name || ''} ${client.first_name || ''}</strong><br>
                            <span style="color:#64748b;"> ${client.email || client.user_id}</span><br>
                            <span> ${client.phone || '—'}</span><br>
                            <span style="font-size:12px;"> Скидка: ${client.discount || 0}% |  Статус: ${client.status || 'активен'}</span>
                        </div>
                        <span style="font-size:32px;"></span>
                    </div>
                    <div style="margin-top: 12px; font-size: 12px; color: #4f46e5;">Нажмите для деталей →</div>
                </div>
            `;
        }
        html += '</div>';
        html += `<div style="text-align:center; margin-top:20px;"><button onclick="showAddClientForm()" class="btn-primary">+ Добавить клиента</button></div>`;
        content.innerHTML = html;
        
    } catch(err) {
        console.error(err);
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки клиентов</div>';
    }
}

// ========== ИСПОЛНИТЕЛИ ==========
async function loadWorkers() {
    document.getElementById('page-title').textContent = 'Исполнители';
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка...</div>';
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/mechanics/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const workers = await res.json();
        
        if (!workers.length) {
            content.innerHTML = '<div style="padding:40px;text-align:center;">Нет исполнителей</div>';
            return;
        }
        
        let html = '<div class="cards-grid">';
        for (const w of workers) {
            html += `
                <div class="order-card">
                    <div style="display:flex; justify-content:space-between;">
                        <div>
                            <strong>${w.first_name || w.user_id || 'Механик'}</strong><br>
                            <span>${w.specialization || 'Механик'}</span><br>
                            <span style="font-size:12px;">Статус: ${w.status || 'свободен'}</span>
                        </div>
                        <span style="font-size:32px;"></span>
                    </div>
                </div>
            `;
        }
        html += '</div>';
        content.innerHTML = html;
    } catch(e) {
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки исполнителей</div>';
    }
}

// ========== СПРАВОЧНИК РАБОТ ==========
async function loadWorksReference() {
    document.getElementById('page-title').textContent = 'Справочник работ';
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка работ...</div>';
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/works/?skip=0&limit=100', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const works = await response.json();
            
            if (!works.length) {
                content.innerHTML = '<div style="padding:40px;text-align:center;">Нет работ</div>';
                return;
            }
            
            let html = '<div class="cards-grid">';
            for (const work of works) {
                html += `
                    <div class="order-card">
                        <div class="order-header">
                            <span class="order-number">${work.name}</span>
                            <span class="order-status status-accepted">${work.price_per_hour} ₽/час</span>
                        </div>
                        <div class="order-car">Код: ${work.code}</div>
                        <div class="order-car">Категория: ${work.category || '—'}</div>
                    </div>
                `;
            }
            html += '</div>';
            content.innerHTML = html;
        } else {
            content.innerHTML = `<div style="padding:40px;text-align:center;">Ошибка: ${response.status}</div>`;
        }
    } catch (err) {
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки работ</div>';
    }
}

// ========== СПРАВОЧНИК ЗАПЧАСТЕЙ ==========
async function loadPartsReference() {
    document.getElementById('page-title').textContent = 'Справочник запчастей';
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка запчастей...</div>';
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    try {
        const response = await fetch('http://localhost:8000/api/v1/parts/?skip=0&limit=100', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (response.ok) {
            const parts = await response.json();
            
            if (!parts.length) {
                content.innerHTML = '<div style="padding:40px;text-align:center;">Нет запчастей</div>';
                return;
            }
            
            let html = '<div class="cards-grid">';
            for (const part of parts) {
                html += `
                    <div class="order-card">
                        <div class="order-header">
                            <span class="order-number">${part.name}</span>
                            <span class="order-status status-accepted">${part.price} ₽</span>
                        </div>
                        <div class="order-car">Артикул: ${part.article || part.code}</div>
                        <div class="order-car">Остаток: ${part.quantity || 0} шт.</div>
                    </div>
                `;
            }
            html += '</div>';
            content.innerHTML = html;
        } else {
            content.innerHTML = `<div style="padding:40px;text-align:center;">Ошибка: ${response.status}</div>`;
        }
    } catch (err) {
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки запчастей</div>';
    }
}

// ========== АВТОМОБИЛИ ==========
async function loadCars() {
    document.getElementById('page-title').textContent = 'Автомобили';
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка...</div>';
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    try {
        // Определяем роль пользователя
        const isAdmin = currentUser?.role === 'director';
        
        // Если админ - запрашиваем все авто, если нет - только свои
        const url = isAdmin ? 'http://localhost:8000/api/v1/cars/all' : 'http://localhost:8000/api/v1/cars/';
        
        const res = await fetch(url, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const cars = await res.json();
        
        if (!cars.length) {
            content.innerHTML = `
                <div style="text-align:center; padding:60px;">
                    <div style="font-size:48px;"></div>
                    <div style="color:#64748b;">Нет автомобилей</div>
                    <button onclick="showAddCarForm()" class="btn-primary" style="margin-top:20px;">+ Добавить автомобиль</button>
                </div>
            `;
            return;
        }
        
        let html = '<div class="cards-grid">';
        for (const car of cars) {
            html += `
                <div class="order-card" style="cursor: pointer;" onclick="showCarDetails('${car.id}')">
                    <div class="order-header">
                        <span class="order-number">${car.brand} ${car.model}</span>
                        <span class="order-status status-accepted">${car.year || '—'}</span>
                    </div>
                    <div class="order-car"> ${car.license_plate || 'без номера'}</div>
                    <div class="order-car"> ${car.color || '—'}</div>
                    <div class="order-car">👤 Владелец: ${car.owner_name || car.client_id || '—'}</div>
                    <div style="margin-top: 12px; font-size: 12px; color: #4f46e5;">Нажмите для деталей →</div>
                </div>
            `;
        }
        html += '</div>';
        html += `<div style="text-align:center; margin-top:20px;">
                    <button onclick="showAddCarForm()" class="btn-primary">+ Добавить автомобиль</button>
                </div>`;
        content.innerHTML = html;
        
    } catch(e) {
        console.error(e);
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки автомобилей</div>';
    }
}

// ========== ФОРМА ДОБАВЛЕНИЯ АВТОМОБИЛЯ ==========

// ========== ФОРМА ДОБАВЛЕНИЯ КЛИЕНТА ==========
function showAddClientForm() {
    const content = document.getElementById('content-area');
    content.innerHTML = `
        <div style="max-width: 500px; margin: 0 auto;">
            <div class="order-card">
                <h3 style="margin-bottom:20px;"> Новый клиент</h3>
                
                <div class="form-group">
                    <label>Логин (username) *</label>
                    <input type="text" id="client-username" class="form-input" placeholder="ivan_petrov">
                </div>
                
                <div class="form-group">
                    <label>Email *</label>
                    <input type="email" id="client-email" class="form-input" placeholder="ivan@example.com">
                </div>
                
                <div class="form-group">
                    <label>Имя</label>
                    <input type="text" id="client-firstname" class="form-input" placeholder="Иван">
                </div>
                
                <div class="form-group">
                    <label>Фамилия</label>
                    <input type="text" id="client-lastname" class="form-input" placeholder="Петров">
                </div>
                
                <div class="form-group">
                    <label>Телефон</label>
                    <input type="tel" id="client-phone" class="form-input" placeholder="+7 999 123 45 67">
                </div>
                
                <div class="form-group">
                    <label>Пароль *</label>
                    <input type="password" id="client-password" class="form-input" placeholder="******">
                </div>
                
                <div class="form-group">
                    <label>Скидка (%)</label>
                    <input type="number" id="client-discount" class="form-input" placeholder="0" value="0">
                </div>
                
                <div style="display:flex; gap:12px; margin-top:20px;">
                    <button onclick="saveClient()" class="btn-primary" style="background:#4f46e5;">Сохранить</button>
                    <button onclick="loadClients()" class="btn-primary" style="background:#64748b;">Отмена</button>
                </div>
            </div>
        </div>
    `;
}

// ========== УДАЛЕНИЕ КЛИЕНТА ==========
async function deleteClient(clientId, userId) {
    if (!confirm('Вы уверены, что хотите удалить этого клиента? Будут удалены также все связанные заказы и автомобили.')) {
        return;
    }
    
    const token = localStorage.getItem('auth_token');
    
    try {
        // 1. Удаляем клиента
        const clientRes = await fetch(`http://localhost:8000/api/v1/clients/${clientId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!clientRes.ok) {
            alert('❌ Ошибка удаления клиента');
            return;
        }
        
        // 2. Удаляем пользователя
        const userRes = await fetch(`http://localhost:8000/api/v1/users/${userId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (userRes.ok || userRes.status === 404) {
            alert('✅ Клиент успешно удалён!');
            loadClients();
        } else {
            alert('⚠️ Клиент удалён, но не удалось удалить пользователя');
            loadClients();
        }
        
    } catch(err) {
        console.error(err);
        alert('❌ Ошибка подключения к серверу');
    }
}


async function saveClient() {
    const token = localStorage.getItem('auth_token');
    
    const username = document.getElementById('client-username').value.trim();
    const email = document.getElementById('client-email').value.trim();
    const password = document.getElementById('client-password').value.trim();
    const firstName = document.getElementById('client-firstname').value.trim();
    const lastName = document.getElementById('client-lastname').value.trim();
    const phone = document.getElementById('client-phone').value.trim();
    const discount = parseInt(document.getElementById('client-discount').value) || 0;
    
    // Валидация на фронтенде
    if (!username || !email || !password) {
        alert('❌ Заполните обязательные поля: логин, email, пароль');
        return;
    }
    
    if (username.length < 3) {
        alert('❌ Логин должен содержать минимум 3 символа');
        return;
    }
    
    if (password.length < 6) {
        alert('❌ Пароль должен содержать минимум 6 символов');
        return;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('❌ Некорректный формат email. Пример: name@domain.com');
        return;
    }
    
    if (phone && !/^[\d\s\+\(\)-]+$/.test(phone)) {
        alert('❌ Некорректный формат телефона');
        return;
    }
    
    try {
        const registerRes = await fetch('http://localhost:8000/api/v1/auth/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                first_name: firstName,
                last_name: lastName,
                phone: phone,
                role: 'client'
            })
        });
        
        if (!registerRes.ok) {
            const error = await registerRes.json();
            
            // Обработка конкретных ошибок от бэкенда
            if (error.detail) {
                if (Array.isArray(error.detail)) {
                    // Pydantic validation errors
                    const errorMsg = error.detail.map(e => {
                        if (e.msg === 'String should have at least 6 characters') {
                            return 'Пароль должен быть не менее 6 символов';
                        }
                        if (e.msg === 'value is not a valid email address') {
                            return 'Некорректный формат email';
                        }
                        return `${e.loc.join('.')}: ${e.msg}`;
                    }).join('\n');
                    alert('❌ ' + errorMsg);
                } else if (typeof error.detail === 'string') {
                    if (error.detail.includes('Username already registered')) {
                        alert('❌ Пользователь с таким логином уже существует');
                    } else if (error.detail.includes('Email already registered')) {
                        alert('❌ Пользователь с таким email уже существует');
                    } else {
                        alert('❌ ' + error.detail);
                    }
                }
            } else {
                alert('❌ Ошибка регистрации. Проверьте правильность заполнения полей.');
            }
            return;
        }
        
        alert('✅ Клиент успешно создан!');
        loadClients();
        
    } catch(err) {
        console.error(err);
        alert('❌ Ошибка подключения к серверу');
    }
}

function showAddCarForm() {
    const content = document.getElementById('content-area');
    content.innerHTML = `
        <div style="max-width: 500px; margin: 0 auto;">
            <div class="order-card">
                <h3 style="margin-bottom:20px;"> Новый автомобиль</h3>
                <div class="form-group"><label>Марка</label><input type="text" id="car-brand" class="form-input" placeholder="BMW"></div>
                <div class="form-group"><label>Модель</label><input type="text" id="car-model" class="form-input" placeholder="X5"></div>
                <div class="form-group"><label>Год</label><input type="number" id="car-year" class="form-input" placeholder="2022"></div>
                <div class="form-group"><label>Госномер</label><input type="text" id="car-plate" class="form-input" placeholder="А123ВС77"></div>
                <div class="form-group"><label>Цвет</label><input type="text" id="car-color" class="form-input" placeholder="Черный"></div>
                <div class="form-group"><label>VIN</label><input type="text" id="car-vin" class="form-input" placeholder="WBAXX123456789012"></div>
                <div style="display:flex; gap:12px; margin-top:20px;">
                    <button onclick="saveCar()" class="btn-primary" style="background:#4f46e5;">Сохранить</button>
                    <button onclick="loadCars()" class="btn-primary" style="background:#64748b;">Отмена</button>
                </div>
            </div>
        </div>
    `;
}

async function saveCar() {
    const token = localStorage.getItem('auth_token');
    const carData = {
        brand: document.getElementById('car-brand').value,
        model: document.getElementById('car-model').value,
        year: parseInt(document.getElementById('car-year').value),
        license_plate: document.getElementById('car-plate').value,
        color: document.getElementById('car-color').value,
        vin: document.getElementById('car-vin').value
    };
    
    if (!carData.brand || !carData.model || !carData.year || !carData.license_plate) {
        alert('Заполните обязательные поля');
        return;
    }
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/cars/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(carData)
        });
        if (res.ok) {
            alert('✅ Автомобиль добавлен!');
            loadCars();
        } else {
            alert('❌ Ошибка добавления');
        }
    } catch {
        alert('❌ Ошибка подключения');
    }
}

// ========== РЕДАКТИРОВАНИЕ И УДАЛЕНИЕ АВТОМОБИЛЯ ==========
async function editCar(carId) {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/cars/${carId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const car = await res.json();
        
        const newBrand = prompt('Введите марку:', car.brand);
        if (!newBrand) return;
        const newModel = prompt('Введите модель:', car.model);
        if (!newModel) return;
        const newYear = prompt('Введите год:', car.year);
        const newPlate = prompt('Введите госномер:', car.license_plate);
        
        const updateRes = await fetch(`http://localhost:8000/api/v1/cars/${carId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
                brand: newBrand,
                model: newModel,
                year: parseInt(newYear),
                license_plate: newPlate
            })
        });
        
        if (updateRes.ok) {
            alert('✅ Автомобиль обновлён');
            showCarDetails(carId);
        } else {
            alert('❌ Ошибка обновления');
        }
    } catch(err) {
        alert('❌ Ошибка');
    }
}

async function deleteCar(carId) {
    if (!confirm('Удалить автомобиль?')) return;
    
    const token = localStorage.getItem('auth_token');
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/cars/${carId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            alert('✅ Автомобиль удалён');
            loadCars();
        } else {
            alert('❌ Ошибка удаления');
        }
    } catch(err) {
        alert('❌ Ошибка');
    }
}

// ========== ДЕТАЛЬНАЯ КАРТОЧКА АВТОМОБИЛЯ ==========
async function showCarDetails(carId) {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка деталей автомобиля...</div>';
    
    try {
        const isAdmin = currentUser?.role === 'director';
        
        const res = await fetch(`http://localhost:8000/api/v1/cars/${carId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const car = await res.json();
        
        // Проверка доступа: если не админ и машина не его - ошибка
        if (!isAdmin && car.client_id !== currentUser?.id) {
            content.innerHTML = `
                <div style="text-align:center; padding:60px;">
                    <div style="font-size:48px;"></div>
                    <div style="color:#ef4444;">У вас нет доступа к этому автомобилю</div>
                    <button onclick="loadCars()" class="btn-primary" style="margin-top:20px;">← Назад</button>
                </div>
            `;
            return;
        }
        
        // Получаем информацию о владельце (логин клиента)
        let ownerInfo = car.client_id || '—';
        if (car.client_id) {
            try {
                const userRes = await fetch(`http://localhost:8000/api/v1/auth/users/${car.client_id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (userRes.ok) {
                    const user = await userRes.json();
                    ownerInfo = user.username || user.email;
                }
            } catch(e) {
                console.error('Ошибка получения владельца:', e);
            }
        }
        
        // Получаем заказы для этого автомобиля
        let ordersHtml = '<div style="margin-top: 20px;"><h3>История заказов</h3><div style="color: #64748b;">Загрузка...</div></div>';
        
        try {
            const ordersRes = await fetch('http://localhost:8000/api/v1/orders/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const orders = await ordersRes.json();
            const carOrders = orders.filter(o => o.car_id === carId || o.car_info?.includes(car.brand));

            
            if (carOrders.length > 0) {
                ordersHtml = `
                    <div style="margin-top: 20px;">
                        <h3>История заказов (${carOrders.length})</h3>
                        <div class="cards-grid" style="grid-template-columns: 1fr;">
                            ${carOrders.map(order => `
                                <div class="order-card" style="cursor: pointer;" onclick="showOrderDetails('${order.id}')">
                                    <div class="order-header">
                                        <span class="order-number">Заказ #${order.number || order.id.slice(0, 8)}</span>
                                        <span class="order-status status-${order.status}">${order.status || 'новый'}</span>
                                    </div>
                                    <div class="order-car"> Сумма: ${(order.total || 0).toLocaleString()} ₽</div>
                                    <div class="order-car"> ${new Date(order.created_at).toLocaleDateString()}</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            } else {
                ordersHtml = '<div style="margin-top: 20px;"><h3>История заказов</h3><div style="color: #64748b;">Нет заказов для этого автомобиля</div></div>';
            }
        } catch(e) {
            ordersHtml = '<div style="margin-top: 20px;"><h3>История заказов</h3><div style="color: #64748b;">Ошибка загрузки</div></div>';
        }
        
        const html = `
            <div style="max-width: 800px; margin: 0 auto;">
                <div class="order-card" style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2 style="margin: 0;"> ${car.brand} ${car.model}</h2>
                        <button onclick="loadCars()" class="btn-primary" style="background: #64748b;">← Назад к списку</button>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
                        <div><strong> Марка:</strong><br>${car.brand}</div>
                        <div><strong> Модель:</strong><br>${car.model}</div>
                        <div><strong> Год выпуска:</strong><br>${car.year || '—'}</div>
                        <div><strong> Госномер:</strong><br>${car.license_plate || '—'}</div>
                        <div><strong> VIN номер:</strong><br>${car.vin || '—'}</div>
                        <div><strong> Цвет:</strong><br>${car.color || '—'}</div>
                        <div><strong> Владелец:</strong><br>${ownerInfo}</div>
                        <div><strong> ID автомобиля:</strong><br><span style="font-size: 11px;">${car.id}</span></div>
                    </div>
                    
                    ${ordersHtml}
                    
                    <div style="display: flex; gap: 12px; margin-top: 20px;">
                        <button onclick="editCar('${car.id}')" class="btn-primary" style="background: #f59e0b;"> Редактировать</button>
                        <button onclick="deleteCar('${car.id}')" class="btn-primary" style="background: #ef4444;"> Удалить</button>
                    </div>
                </div>
            </div>
        `;
        
        content.innerHTML = html;
        
    } catch(err) {
        console.error(err);
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки деталей автомобиля</div>';
    }
}

// ========== НОВАЯ ФОРМА СОЗДАНИЯ ЗАКАЗА ==========
async function showCreateOrderForm() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        alert('Не авторизован');
        return;
    }
    
    // Получаем список клиентов
    const clientsRes = await fetch('http://localhost:8000/api/v1/clients/', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const clients = await clientsRes.json();
    window.currentClients = clients;
    
    // Получаем список работ
    const worksRes = await fetch('http://localhost:8000/api/v1/works/', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const works = await worksRes.json();
    
    // Получаем список механиков
    const mechanicsRes = await fetch('http://localhost:8000/api/v1/mechanics/', {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const mechanics = await mechanicsRes.json();
    
    const content = document.getElementById('content-area');
    content.innerHTML = `
        <div style="max-width: 600px; margin: 0 auto;">
            <div class="order-card">
                <h3> Новый заказ-наряд</h3>
                
                <div class="form-group">
                    <label>Клиент</label>
                    <select id="order-client" class="form-input">
                        <option value="">Выберите клиента</option>
                        ${clients.map(c => `<option value="${c.id}">${c.last_name || ''} ${c.first_name || ''} (${c.email})</option>`).join('')}
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Автомобиль</label>
                    <select id="order-car" class="form-input">
                        <option value="">Сначала выберите клиента</option>
                    </select>
                </div>
                
                <div class="form-group">
                    <label>Работы</label>
                    <select id="order-works" class="form-input" multiple size="5">
                        ${works.map(w => `<option value="${w.id}">${w.name} - ${w.price_per_hour} ₽/час</option>`).join('')}
                    </select>
                    <small>Зажмите Ctrl для выбора нескольких работ</small>
                </div>
                
                <div class="form-group">
                    <label>Механик</label>
                    <select id="order-mechanic" class="form-input">
                        <option value="">Выберите механика</option>
                        ${mechanics.map(m => `<option value="${m.id}">${m.first_name || ''} ${m.last_name || ''} (${m.specialization || 'Механик'})</option>`).join('')}
                    </select>
                </div>
                
                <div style="display:flex; gap:12px; margin-top:20px;">
                    <button onclick="createOrderWithDetails()" class="btn-primary">Создать заказ</button>
                    <button onclick="loadOrders()" class="btn-primary" style="background:#64748b;">Отмена</button>
                </div>
            </div>
        </div>
    `;
    
    // Загрузка автомобилей при выборе клиента
    document.getElementById('order-client').onchange = async () => {
        const clientId = document.getElementById('order-client').value;
        const selectedClient = window.currentClients.find(c => c.id === clientId);
        const userId = selectedClient.user_id;
        if (userId) {
            const carsRes = await fetch(`http://localhost:8000/api/v1/cars/all`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const allCars = await carsRes.json();
            const clientCars = allCars.filter(c => c.client_id === userId);
            
            const carSelect = document.getElementById('order-car');
            carSelect.innerHTML = '<option value="">Выберите автомобиль</option>';
            clientCars.forEach(car => {
                carSelect.innerHTML += `<option value="${car.id}">${car.brand} ${car.model} (${car.license_plate})</option>`;
            });
        }
    };
}

async function createOrderWithDetails() {
    const token = localStorage.getItem('auth_token');
    
    const clientId = document.getElementById('order-client').value;
    const carId = document.getElementById('order-car').value;
    const carInfo = document.getElementById('order-car').options[document.getElementById('order-car').selectedIndex]?.text;
    const worksSelect = document.getElementById('order-works');
    const selectedWorks = Array.from(worksSelect.selectedOptions).map(opt => opt.value);
    const mechanicId = document.getElementById('order-mechanic').value;

    console.log('carId:', carId);
    console.log('selectedWorks:', selectedWorks);
    console.log('mechanicId:', mechanicId);
    
    if (!carId) {
        alert('Выберите автомобиль');
        return;
    }
    
    try {
        // 1. Создаём заказ, НО без client_id (бэкенд сам подставит из car)
        const orderRes = await fetch('http://localhost:8000/api/v1/orders/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify({ car_id: carId, car_info: carInfo })
        });
        
        if (!orderRes.ok) {
            const err = await orderRes.json();
            alert('Ошибка создания заказа: ' + JSON.stringify(err));
            return;
        }
        
        const order = await orderRes.json();
        
        // 2. Добавляем работы
        for (const workId of selectedWorks) {
            await fetch(`http://localhost:8000/api/v1/orders/${order.id}/add-work?work_id=${workId}&hours=1`, {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
        }
        
        // 3. Назначаем механика
        if (mechanicId) {
            await fetch(`http://localhost:8000/api/v1/orders/${order.id}/assign-mechanic?mechanic_id=${mechanicId}`, {
                method: 'PATCH',
                headers: { 'Authorization': `Bearer ${token}` }
            });
        }
        
        alert('✅ Заказ создан!');
        loadOrders();
        
    } catch(err) {
        console.error(err);
        alert('❌ Ошибка создания заказа');
    }
}


// ========== СОЗДАНИЕ ЗАКАЗА ДЛЯ КОНКРЕТНОГО АВТО ==========
function showCreateOrderModalForCar(carId, carInfo) {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        alert('Не авторизован');
        showLoginModal();
        return;
    }
    
    const modal = document.createElement('div');
    modal.id = 'create-order-modal';
    modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); display:flex; align-items:center; justify-content:center; z-index:10001;';
    modal.innerHTML = `
        <div style="background:white; border-radius:24px; width:400px; max-width:90%; padding:32px;">
            <h3 style="margin-bottom:20px;"> Новый заказ</h3>
            <div style="margin-bottom:16px;">
                <label style="display:block; margin-bottom:6px; font-weight:500;">ID автомобиля</label>
                <input type="text" id="order-car-id" value="${carId}" readonly style="width:100%; padding:12px; border:1px solid #e2e8f0; border-radius:12px; background:#f1f5f9;">
            </div>
            <div style="margin-bottom:16px;">
                <label style="display:block; margin-bottom:6px; font-weight:500;">Информация об авто</label>
                <input type="text" id="order-car" value="${carInfo}" readonly style="width:100%; padding:12px; border:1px solid #e2e8f0; border-radius:12px; background:#f1f5f9;">
            </div>
            <div style="display:flex; gap:12px;">
                <button id="submit-order-btn" style="flex:1; padding:12px; background:#4f46e5; color:white; border:none; border-radius:12px; cursor:pointer;">Создать заказ</button>
                <button id="cancel-order-btn" style="flex:1; padding:12px; background:#f1f5f9; border:none; border-radius:12px; cursor:pointer;">Отмена</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    document.getElementById('submit-order-btn').onclick = async () => {
        const carIdVal = document.getElementById('order-car-id').value;
        const carInfoVal = document.getElementById('order-car').value;
        
        try {
            const res = await fetch('http://localhost:8000/api/v1/orders/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ car_id: carIdVal, car_info: carInfoVal })
            });
            
            if (res.ok) {
                alert('✅ Заказ создан!');
                modal.remove();
                location.reload();
            } else {
                const err = await res.json();
                alert('❌ Ошибка: ' + (err.detail || 'Неизвестная ошибка'));
            }
        } catch {
            alert('❌ Ошибка подключения к серверу');
        }
    };
    
    document.getElementById('cancel-order-btn').onclick = () => modal.remove();
}

// ========== ОТВЯЗКА АВТОМОБИЛЯ ОТ КЛИЕНТА ==========
async function detachCarFromClient(carId) {
    if (!confirm('Отвязать автомобиль от клиента?')) return;
    
    const token = localStorage.getItem('auth_token');
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/cars/${carId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ client_id: null })  // ← null, а не пустая строка
        });
        
        if (res.ok) {
            alert('✅ Автомобиль отвязан');
            location.reload();
        } else {
            const error = await res.json();
            alert('❌ Ошибка: ' + (error.detail || 'Неизвестная ошибка'));
        }
    } catch(err) {
        alert('❌ Ошибка подключения');
    }
}



// ========== ДЕТАЛЬНАЯ КАРТОЧКА КЛИЕНТА ==========
async function showClientDetails(clientId) {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка деталей клиента...</div>';
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/clients/${clientId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const client = await res.json();
        
        // Используем данные напрямую из client (они уже есть в ответе API)
        const userInfo = {
            username: client.username || client.user_id,
            email: client.email || '—',
            phone: client.phone || '—',
            role: client.role || 'client'
        };
        
        // Получаем заказы клиента
        let ordersHtml = '<div style="margin-top: 20px;"><h3> Заказы клиента</h3><div style="color: #64748b;">Загрузка...</div></div>';
        
        try {
            const ordersRes = await fetch('http://localhost:8000/api/v1/orders/', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const orders = await ordersRes.json();
            const clientOrders = orders.filter(o => o.client_id === client.id);
            
            
            
            if (clientOrders.length > 0) {
                ordersHtml = `
                    <div style="margin-top: 20px;">
                        <h3>Заказы клиента (${clientOrders.length})</h3>
                        <div class="cards-grid" style="grid-template-columns: 1fr;">
                            ${clientOrders.map(order => `
                                <div class="order-card" style="cursor: pointer;" onclick="showOrderDetails('${order.id}')">
                                    <div class="order-header">
                                        <span class="order-number">Заказ #${order.number || order.id.slice(0, 8)}</span>
                                        <span class="order-status status-${order.status}">${order.status || 'новый'}</span>
                                    </div>
                                    <div class="order-car"> ${order.car_info || order.car_id}</div>
                                    <div class="order-car"> ${(order.total || 0).toLocaleString()} ₽</div>
                                </div>
                            `).join('')}
                        </div>
                    </div>
                `;
            } else {
                ordersHtml = '<div style="margin-top: 20px;"><h3>Заказы клиента</h3><div style="color: #64748b;">Нет заказов</div></div>';
            }
        } catch(e) {
            ordersHtml = '<div style="margin-top: 20px;"><h3>Заказы клиента</h3><div style="color: #64748b;">Ошибка загрузки</div></div>';
        }
        
        // Получаем автомобили клиента
        let carsHtml = '<div style="margin-top: 20px;"><h3> Автомобили клиента</h3><div style="color: #64748b;">Загрузка...</div></div>';
        
        try {
            const carsRes = await fetch('http://localhost:8000/api/v1/cars/all', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const cars = await carsRes.json();
            const clientCars = cars.filter(c => c.client_id === client.user_id);
            
            if (clientCars.length > 0) {
                carsHtml = `
                        <div style="margin-top: 20px;">
                            <h3> Автомобили клиента (${clientCars.length})</h3>
                            <div class="cards-grid" style="grid-template-columns: 1fr;">
                                ${clientCars.map(car => `
                                    <div class="order-card">
                                        <div style="display: flex; justify-content: space-between; align-items: center;">
                                            <div style="flex: 1; cursor: pointer;" onclick="showCarDetails('${car.id}')">
                                                <div class="order-header">
                                                    <span class="order-number">${car.brand} ${car.model}</span>
                                                    <span class="order-status status-accepted">${car.year || '—'}</span>
                                                </div>
                                                <div class="order-car"> ${car.license_plate || 'без номера'}</div>
                                            </div>
                                            <button onclick="event.stopPropagation(); detachCarFromClient('${car.id}')" 
                                                    class="btn-primary" style="background: #ffac4d; padding: 6px 12px; font-size: 12px;">
                                                 Отвязать
                                            </button>
                                        </div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    `;
            } else {
                carsHtml = '<div style="margin-top: 20px;"><h3> Автомобили клиента</h3><div style="color: #64748b;">Нет автомобилей</div></div>';
            }
        } catch(e) {
            carsHtml = '<div style="margin-top: 20px;"><h3> Автомобили клиента</h3><div style="color: #64748b;">Ошибка загрузки</div></div>';
        }
        
        const html = `
            <div style="max-width: 800px; margin: 0 auto;">
                <div class="order-card" style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2 style="margin: 0;"> ${userInfo.username}</h2>
                        <div style="display: flex; gap: 12px;">
                            <button onclick="deleteClient('${client.id}', '${client.user_id}')" class="btn-primary" style="background: #ef4444;"> Удалить клиента</button>
                            <button onclick="showAttachCarToClient('${client.id}', '${client.user_id}')" class="btn-primary" style="background: #10b981;"> Привязать авто</button>
                            <button onclick="loadClients()" class="btn-primary" style="background: #64748b;">← Назад к списку</button>
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
                        <div><strong> Логин:</strong><br>${userInfo.username}</div>
                        <div><strong> Email:</strong><br>${userInfo.email}</div>
                        <div><strong> Телефон:</strong><br>${userInfo.phone}</div>
                        <div><strong> Роль:</strong><br>${userInfo.role}</div>
                        <div><strong> Скидка:</strong><br>${client.discount || 0}%</div>
                        <div><strong> Статус:</strong><br>${client.status || 'активен'}</div>
                        <div><strong> ID:</strong><br><span style="font-size: 11px;">${client.id}</span></div>
                    </div>
                    
                    ${carsHtml}
                    ${ordersHtml}
                </div>
            </div>
        `;

        content.innerHTML = html;
        
    } catch(err) {
        console.error(err);
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки деталей клиента</div>';
    }
}


async function showOrderDetails(orderId) {
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка деталей заказа...</div>';
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/orders/${orderId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const order = await res.json();
        
        let mechanicInfo = 'Не назначен';
        if (order.mechanic_id) {
            try {
                // Получаем механика по ID
                const mechRes = await fetch(`http://localhost:8000/api/v1/mechanics/${order.mechanic_id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (mechRes.ok) {
                    const mechanic = await mechRes.json();
                    // Получаем данные пользователя по user_id из механика
                    const userRes = await fetch(`http://localhost:8000/api/v1/auth/users/${mechanic.user_id}`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (userRes.ok) {
                        const user = await userRes.json();
                        mechanicInfo = `${user.username || user.email} (${mechanic.specialization || 'Механик'})`;
                    } else {
                        mechanicInfo = `${mechanic.first_name || ''} ${mechanic.last_name || ''} (${mechanic.specialization || 'Механик'})`;
                    }
                }
            } catch(e) {
                console.error('Ошибка получения механика:', e);
            }
        }
                
        const statusMap = {
            'new': ' Новый',
            'accepted': ' Принят',
            'in_progress': ' В работе',
            'completed': ' Выполнен',
            'cancelled': ' Отменён'
        };
        
        // Получаем имя клиента
        let clientName = 'Не указан';
        if (order.client_id) {
            try {
                // Сначала получаем клиента по ID (из таблицы clients)
                const clientRes = await fetch(`http://localhost:8000/api/v1/clients/${order.client_id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (clientRes.ok) {
                    const client = await clientRes.json();
                    // Теперь получаем пользователя по user_id
                    const userRes = await fetch(`http://localhost:8000/api/v1/auth/users/${client.user_id}`, {
                        headers: { 'Authorization': `Bearer ${token}` }
                    });
                    if (userRes.ok) {
                        const user = await userRes.json();
                        // Показываем username (логин)
                        clientName = user.username || user.email;
                    } else {
                        clientName = client.user_id;
                    }
                }
            } catch(e) {
                console.error('Ошибка получения клиента:', e);
                clientName = order.client_id.slice(0, 8) + '...';
            }
        }

        const statusText = statusMap[order.status] || order.status;
        
        const html = `
            <div style="max-width: 800px; margin: 0 auto;">
                <div class="order-card" style="margin-bottom: 20px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                        <h2 style="margin: 0;">Заказ-наряд #${order.number || order.id}</h2>
                        <button onclick="loadOrders()" class="btn-primary" style="background: #64748b;">← Назад</button>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-bottom: 20px;">
                        <div><strong> Дата создания:</strong><br>${new Date(order.created_at).toLocaleString()}</div>
                        <div><strong> Статус:</strong><br>${statusText}</div>
                        <div><strong> Автомобиль:</strong><br>${order.car_info || order.car_id}</div>
                        <div><strong> Клиент:</strong><br>${clientName}</div>
                        <div><strong> Механик:</strong><br>${mechanicInfo}</div>
                        <div><strong> Общая сумма:</strong><br><span style="font-size: 24px; color: #4f46e5;">${(order.total || 0).toLocaleString()} ₽</span></div>
                    </div>
                    
                    <h3> Список работ</h3>
                    <div id="order-works-list" style="margin-bottom: 20px;">
                        <div style="padding: 20px; text-align: center; color: #64748b;">Загрузка работ...</div>
                    </div>
                    
                    <div style="display: flex; gap: 12px; align-items: center; margin-top: 20px;">
                        <select id="work-select" class="form-input" style="flex: 1;">
                            <option value="">Выберите работу</option>
                        </select>
                        <button onclick="addSelectedWorkToOrder('${order.id}')" class="btn-primary" style="background: #4f46e5;"> Добавить</button>
                    </div>
                    
                    <div style="display: flex; gap: 12px; margin-top: 20px;">
                        <button onclick="deleteOrder('${order.id}')" class="btn-primary" style="background: #ef4444;"> Удалить заказ</button>
                        <div style="display: flex; gap: 12px; align-items: center; margin-top: 12px;">
                            <select id="order-status-select" class="form-input" style="flex: 1; background: white;">
                                <option value="accepted"> Принят</option>
                                <option value="diagnostics"> Диагностика</option>
                                <option value="waiting_approval"> Ждёт согласования</option>
                                <option value="in_progress"> В работе</option>
                                <option value="ready"> Готов</option>
                                <option value="completed"> Выполнен</option>
                            </select>
                            <button onclick="updateOrderStatusFromSelect('${order.id}')" class="btn-primary" style="background: #10b981;">Изменить статус</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        content.innerHTML = html;
        
        const statusSelect = document.getElementById('order-status-select');
        if (statusSelect && order.status) {
            statusSelect.value = order.status;
        }

        // Загружаем список работ в select
        const worksSelect = document.getElementById('work-select');
        if (worksSelect) {
            const worksRes = await fetch('http://localhost:8000/api/v1/works/?skip=0&limit=100', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            const works = await worksRes.json();
            worksSelect.innerHTML = '<option value="">Выберите работу</option>';
            works.forEach(work => {
                worksSelect.innerHTML += `<option value="${work.id}">${work.name} - ${work.price_per_hour} ₽/час</option>`;
            });
        }
        
        await loadOrderWorks(orderId);
        
    } catch(err) {
        console.error(err);
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки деталей заказа</div>';
    }
}

async function loadOrderWorks(orderId) {
    const token = localStorage.getItem('auth_token');
    const worksContainer = document.getElementById('order-works-list');
    if (!worksContainer) return;
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/orders/${orderId}`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const order = await res.json();
        
        if (order.items && order.items.length > 0) {
            let html = '<div class="cards-grid" style="grid-template-columns: 1fr;">';
            for (const item of order.items) {
                html += `
                    <div class="order-card">
                        <div class="order-header">
                            <span class="order-number">${item.name}</span>
                            <span class="order-status status-accepted">${item.price} ₽</span>
                        </div>
                        <div class="order-car">Количество: ${item.quantity} час(ов)</div>
                        <div class="order-car">Итого: ${item.total} ₽</div>
                    </div>
                `;
            }
            html += '</div>';
            worksContainer.innerHTML = html;
        } else {
            worksContainer.innerHTML = `
                <div class="cards-grid" style="grid-template-columns: 1fr;">
                    <div class="order-card">
                        <div class="order-header">
                            <span class="order-number">Нет добавленных работ</span>
                            <span class="order-status status-accepted">—</span>
                        </div>
                        <div class="order-car">Добавьте работы через кнопку выше</div>
                    </div>
                </div>
            `;
        }
    } catch(err) {
        console.error(err);
        worksContainer.innerHTML = '<div style="padding:20px;text-align:center;color:red;">Ошибка загрузки работ</div>';
    }
}

async function changeOrderStatus(orderId) {
    const newStatus = prompt('Введите новый статус (accepted, diagnostics, waiting_approval, in_progress, ready, completed):', 'accepted');
    if (!newStatus) return;
    
    const token = localStorage.getItem('auth_token');
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/orders/${orderId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ new_status: newStatus })
        });
        
        if (res.ok) {
            const result = await res.json();
            alert('✅ Статус изменён на: ' + result.status);
            location.reload();
        } else {
            const error = await res.json();
            alert('❌ Ошибка: ' + JSON.stringify(error));
        }
    } catch(err) {
        alert('❌ Ошибка: ' + err.message);
    }
}

async function deleteOrder(orderId) {
    if (!confirm('Удалить этот заказ?')) return;
    
    const token = localStorage.getItem('auth_token');
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/orders/${orderId}`, {
            method: 'DELETE',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            alert('✅ Заказ удалён');
            loadOrders();
        } else {
            alert('❌ Ошибка удаления');
        }
    } catch(err) {
        alert('❌ Ошибка подключения');
    }
}

async function updateOrderStatusFromSelect(orderId) {
    const select = document.getElementById('order-status-select');
    const newStatus = select.value;
    
    const token = localStorage.getItem('auth_token');
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/orders/${orderId}/status`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ new_status: newStatus })
        });
        
        if (res.ok) {
            alert('✅ Статус изменён');
            showOrderDetails(orderId);
        } else {
            const error = await res.json();
            alert('❌ Ошибка: ' + (error.detail || 'Неизвестная ошибка'));
        }
    } catch(err) {
        alert('❌ Ошибка подключения');
    }
}


async function searchGlobal() {
    const query = document.getElementById('global-search').value.trim().toLowerCase();
    if (!query || query.length < 2) {
        // Если запрос пустой или слишком короткий - показываем текущий раздел
        const currentPage = getCurrentPage();
        loadCurrentPageContent(currentPage);
        return;
    }
    
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;"> Поиск...</div>';
    
    try {
        // Получаем данные из всех разделов
        const [orders, cars, clients, works, parts, mechanics] = await Promise.all([
            fetch('http://localhost:8000/api/v1/orders/', { headers: { 'Authorization': `Bearer ${token}` } }).then(r => r.json()),
            fetch('http://localhost:8000/api/v1/cars/all', { headers: { 'Authorization': `Bearer ${token}` } }).then(r => r.json()),
            fetch('http://localhost:8000/api/v1/clients/', { headers: { 'Authorization': `Bearer ${token}` } }).then(r => r.json()),
            fetch('http://localhost:8000/api/v1/works/', { headers: { 'Authorization': `Bearer ${token}` } }).then(r => r.json()),
            fetch('http://localhost:8000/api/v1/parts/', { headers: { 'Authorization': `Bearer ${token}` } }).then(r => r.json()),
            fetch('http://localhost:8000/api/v1/mechanics/', { headers: { 'Authorization': `Bearer ${token}` } }).then(r => r.json())
        ]);
        
        // Получаем имена пользователей для клиентов
        const clientNames = {};
        for (const client of clients) {
            try {
                const userRes = await fetch(`http://localhost:8000/api/v1/auth/users/${client.user_id}`, {
                    headers: { 'Authorization': `Bearer ${token}` }
                });
                if (userRes.ok) {
                    const user = await userRes.json();
                    clientNames[client.id] = `${user.last_name || ''} ${user.first_name || ''}`.trim() || user.username;
                    clientNames[client.user_id] = clientNames[client.id];
                }
            } catch(e) {}
        }
        
        // Фильтруем заказы
        const filteredOrders = orders.filter(order => {
            const clientName = clientNames[order.client_id] || '';
            return order.number?.toLowerCase().includes(query) ||
                   order.car_info?.toLowerCase().includes(query) ||
                   order.id?.toLowerCase().includes(query) ||
                   clientName.toLowerCase().includes(query) ||
                   order.status?.toLowerCase().includes(query);
        });
        
        // Фильтруем автомобили
        const filteredCars = cars.filter(car => {
            const ownerName = clientNames[car.client_id] || '';
            return car.brand?.toLowerCase().includes(query) ||
                   car.model?.toLowerCase().includes(query) ||
                   car.license_plate?.toLowerCase().includes(query) ||
                   ownerName.toLowerCase().includes(query);
        });
        
        // Фильтруем клиентов
        const filteredClients = clients.filter(client => {
            const name = clientNames[client.id] || '';
            return name.toLowerCase().includes(query) ||
                   client.email?.toLowerCase().includes(query) ||
                   client.phone?.toLowerCase().includes(query);
        });
        
        // Фильтруем работы
        const filteredWorks = works.filter(work => {
            return work.name?.toLowerCase().includes(query) ||
                   work.code?.toLowerCase().includes(query) ||
                   work.category?.toLowerCase().includes(query);
        });
        
        // Фильтруем запчасти
        const filteredParts = parts.filter(part => {
            return part.name?.toLowerCase().includes(query) ||
                   part.article?.toLowerCase().includes(query) ||
                   part.category?.toLowerCase().includes(query);
        });
        
        // Фильтруем исполнителей
        const filteredMechanics = mechanics.filter(mechanic => {
            return mechanic.first_name?.toLowerCase().includes(query) ||
                   mechanic.last_name?.toLowerCase().includes(query) ||
                   mechanic.specialization?.toLowerCase().includes(query);
        });
        
        let html = `<div style="margin-bottom: 24px;">
                        <h3> Результаты поиска по запросу: "${query}"</h3>
                    </div>`;
        
        // Заказы
        if (filteredOrders.length > 0) {
            html += `<h4 style="margin: 20px 0 12px;"> Заказы (${filteredOrders.length})</h4>`;
            html += '<div class="cards-grid">';
            for (const order of filteredOrders.slice(0, 5)) {
                const clientName = clientNames[order.client_id] || '—';
                html += `
                    <div class="order-card" onclick="showOrderDetails('${order.id}')">
                        <div class="order-header">
                            <span class="order-number">#${order.number || order.id.slice(0, 8)}</span>
                            <span class="order-status status-${order.status}">${order.status || 'Новый'}</span>
                        </div>
                        <div class="order-car"> ${order.car_info || order.car_id}</div>
                        <div class="order-car"> ${clientName}</div>
                        <div class="order-total">${(order.total || 0).toLocaleString()} ₽</div>
                    </div>`;
            }
            html += '</div>';
            if (filteredOrders.length > 5) {
                html += `<div style="text-align:center; margin: 12px;"><button onclick="searchAndShowAll('orders', '${query}')" class="btn-primary">Показать все ${filteredOrders.length} заказов →</button></div>`;
            }
        }
        
        // Автомобили
        if (filteredCars.length > 0) {
            html += `<h4 style="margin: 20px 0 12px;"> Автомобили (${filteredCars.length})</h4>`;
            html += '<div class="cards-grid">';
            for (const car of filteredCars.slice(0, 5)) {
                const ownerName = clientNames[car.client_id] || '—';
                html += `
                    <div class="order-card" onclick="showCarDetails('${car.id}')">
                        <div class="order-header">
                            <span class="order-number">${car.brand} ${car.model}</span>
                            <span class="order-status status-accepted">${car.year || '—'}</span>
                        </div>
                        <div class="order-car"> ${car.license_plate || 'без номера'}</div>
                        <div class="order-car"> Владелец: ${ownerName}</div>
                    </div>`;
            }
            html += '</div>';
            if (filteredCars.length > 5) {
                html += `<div style="text-align:center; margin: 12px;"><button onclick="searchAndShowAll('cars', '${query}')" class="btn-primary">Показать все ${filteredCars.length} автомобилей →</button></div>`;
            }
        }
        
        // Клиенты
        if (filteredClients.length > 0) {
            html += `<h4 style="margin: 20px 0 12px;"> Клиенты (${filteredClients.length})</h4>`;
            html += '<div class="cards-grid">';
            for (const client of filteredClients.slice(0, 5)) {
                const name = clientNames[client.id] || client.user_id;
                html += `
                    <div class="order-card" onclick="showClientDetails('${client.id}')">
                        <div style="display:flex; justify-content:space-between;">
                            <div>
                                <strong>${name}</strong><br>
                                <span> ${client.email || '—'}</span><br>
                                <span> ${client.phone || '—'}</span>
                            </div>
                            <span style="font-size:32px;"></span>
                        </div>
                    </div>`;
            }
            html += '</div>';
            if (filteredClients.length > 5) {
                html += `<div style="text-align:center; margin: 12px;"><button onclick="searchAndShowAll('clients', '${query}')" class="btn-primary">Показать все ${filteredClients.length} клиентов →</button></div>`;
            }
        }
        
        if (filteredOrders.length === 0 && filteredCars.length === 0 && filteredClients.length === 0 && filteredWorks.length === 0 && filteredParts.length === 0 && filteredMechanics.length === 0) {
            html += `<div class="empty-state"><p> Ничего не найдено по запросу "${query}"</p><button onclick="loadOrders()" class="btn-primary">Очистить поиск</button></div>`;
        }
        
        content.innerHTML = html;
        
    } catch(err) {
        console.error(err);
        content.innerHTML = '<div style="padding:40px;text-align:center;">❌ Ошибка поиска</div>';
    }
}

function getCurrentPage() {
    const active = document.querySelector('.nav-item.active, .submenu-item.active');
    if (active) return active.dataset.page;
    return 'orders';
}

function loadCurrentPageContent(page) {
    if (page === 'orders') loadOrders();
    else if (page === 'cars') loadCars();
    else if (page === 'clients') loadClients();
    else if (page === 'workers') loadWorkers();
    else if (page === 'works-ref') loadWorksReference();
    else if (page === 'parts-ref') loadPartsReference();
    else if (page === 'reports') loadReports();
    else if (page === 'crm') loadCRM();
}

async function searchAndShowAll(type, query) {
    document.getElementById('global-search').value = query;
    if (type === 'orders') {
        await searchGlobal();
        document.getElementById('page-title').innerText = 'Результаты поиска: Заказы';
    } else if (type === 'cars') {
        await searchGlobal();
        document.getElementById('page-title').innerText = 'Результаты поиска: Автомобили';
    } else if (type === 'clients') {
        await searchGlobal();
        document.getElementById('page-title').innerText = 'Результаты поиска: Клиенты';
    }
}


// ========== ПРИВЯЗКА АВТОМОБИЛЯ К КЛИЕНТУ ==========
async function showAttachCarToClient(clientId, userId) {
    const token = localStorage.getItem('auth_token');
    
    try {
        const carsRes = await fetch('http://localhost:8000/api/v1/cars/all', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const allCars = await carsRes.json();
        
        const clientCarsRes = await fetch('http://localhost:8000/api/v1/cars/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const clientCars = await clientCarsRes.json();
        const clientCarIds = clientCars.filter(c => c.client_id === userId).map(c => c.id);
        
        const availableCars = allCars.filter(c => !clientCarIds.includes(c.id));
        
        if (availableCars.length === 0) {
            alert('Нет доступных автомобилей для привязки. Все автомобили уже привязаны к клиентам.');
            return;
        }
        
        const modal = document.createElement('div');
        modal.id = 'attach-car-modal';
        modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); display:flex; align-items:center; justify-content:center; z-index:10001;';
        
        let carsListHtml = '<select id="car-select" style="width:100%; padding:12px; border-radius:12px; margin-bottom:16px;">';
        for (const car of availableCars) {
            carsListHtml += `<option value="${car.id}">${car.brand} ${car.model} - ${car.license_plate || 'без номера'}</option>`;
        }
        carsListHtml += '</select>';
        
        modal.innerHTML = `
            <div style="background:white; border-radius:24px; width:400px; max-width:90%; padding:32px;">
                <h3 style="margin-bottom:20px;"> Привязать автомобиль</h3>
                <div style="margin-bottom:16px;">
                    <label style="display:block; margin-bottom:6px;">Выберите автомобиль:</label>
                    ${carsListHtml}
                </div>
                <div style="display:flex; gap:12px;">
                    <button id="attach-submit-btn" class="btn-primary">Привязать</button>
                    <button id="attach-cancel-btn" class="btn-primary" style="background:#64748b;">Отмена</button>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        
        document.getElementById('attach-submit-btn').onclick = async () => {
            const carId = document.getElementById('car-select').value;
            
            const updateRes = await fetch(`http://localhost:8000/api/v1/cars/${carId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ client_id: userId })
            });
            
            if (updateRes.ok) {
                alert('✅ Автомобиль успешно привязан к клиенту!');
                modal.remove();
                showClientDetails(clientId);
            } else if (updateRes.status === 403) {
                alert('❌ Этот автомобиль уже принадлежит другому клиенту.');
                modal.remove();
            } else {
                const error = await updateRes.json();
                alert('❌ Ошибка: ' + (error.detail || 'Неизвестная ошибка'));
                modal.remove();
            }
        };
        
        document.getElementById('attach-cancel-btn').onclick = () => modal.remove();
        
    } catch(err) {
        console.error(err);
        alert('Ошибка загрузки списка автомобилей');
    }
}

async function addSelectedWorkToOrder(orderId) {
    const workId = document.getElementById('work-select').value;
    if (!workId) {
        alert('Выберите работу');
        return;
    }
    
    const hours = prompt('Введите количество часов:', '1');
    if (!hours) return;
    
    const token = localStorage.getItem('auth_token');
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/orders/${orderId}/add-work?work_id=${workId}&hours=${hours}`, {
            method: 'POST',
            headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (res.ok) {
            alert('✅ Работа добавлена');
            showOrderDetails(orderId);
        } else {
            alert('❌ Ошибка добавления работы');
        }
    } catch(err) {
        alert('❌ Ошибка подключения');
    }
}

async function addWorkToOrder(orderId) {
    const workId = prompt('Введите ID работы (например: w1):', 'w1');
    if (!workId) return;
    
    const hours = parseFloat(prompt('Введите количество часов:', '1'));
    if (isNaN(hours)) return;
    
    const token = localStorage.getItem('auth_token');
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/orders/${orderId}/add-work?work_id=${workId}&hours=${hours}`, {
            method: 'POST',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (res.ok) {
            alert('✅ Работа добавлена');
            showOrderDetails(orderId);
        } else {
            alert('❌ Ошибка добавления работы');
        }
    } catch(err) {
        alert('❌ Ошибка подключения');
    }
}

// ========== ОТЧЁТЫ ==========
function loadReports() {
    document.getElementById('page-title').textContent = 'Отчёты';
    const content = document.getElementById('content-area');
    content.innerHTML = `
        <div style="max-width:500px;">
            <div class="order-card">
                <h3>Отчёт по выручке</h3>
                <div class="form-group">
                    <label>С даты</label>
                    <input type="date" id="report-from" class="form-input">
                </div>
                <div class="form-group">
                    <label>По дату</label>
                    <input type="date" id="report-to" class="form-input">
                </div>
                <button id="get-report" class="btn-primary">Сформировать</button>
                <div id="report-result" style="margin-top:20px;"></div>
            </div>
        </div>
    `;
    
    document.getElementById('get-report')?.addEventListener('click', () => {
        document.getElementById('report-result').innerHTML = `
            <div style="background:#f0fdf4; padding:16px; border-radius:12px;">
                <div style="font-size:24px;"> 150 000 ₽</div>
                <div> Заказов: 15</div>
                <div> Средний чек: 10 000 ₽</div>
            </div>
        `;
    });
}

// ========== CRM ДОСКА ==========
function loadCRM() {
    document.getElementById('page-title').textContent = 'CRM - Управление клиентами';
    const content = document.getElementById('content-area');
    content.innerHTML = `
        <div class="crm-board">
            <div class="crm-column">
                <div class="crm-column-header"> Позвонить</div>
                <div class="crm-cards">
                    <div class="crm-card">Иван Петров<br>BMW X5<br>+7 999 123-45-67</div>
                    <div class="crm-card">Сергей Иванов<br>Toyota Camry<br>+7 999 234-56-78</div>
                </div>
            </div>
            <div class="crm-column">
                <div class="crm-column-header"> Запись</div>
                <div class="crm-cards">
                    <div class="crm-card">Анна Сидорова<br>Kia Rio<br>+7 999 345-67-89</div>
                </div>
            </div>
            <div class="crm-column">
                <div class="crm-column-header"> В работе</div>
                <div class="crm-cards">
                    <div class="crm-card">Дмитрий Козлов<br>Mercedes E200<br>+7 999 456-78-90</div>
                </div>
            </div>
        </div>
    `;
}

// ========== НАВИГАЦИЯ ==========
function setupNavigation() {
    document.querySelectorAll('.nav-item[data-page]').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            if (page === 'crm') loadCRM();
            else if (page === 'cars') loadCars();
            else if (page === 'reports') loadReports();
            else loadOrders();
        });
    });
    
    document.querySelectorAll('.submenu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.preventDefault();
            const page = item.dataset.page;
            
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            document.querySelectorAll('.submenu-item').forEach(i => i.classList.remove('active'));
            
            const parent = item.closest('.has-submenu');
            if (parent) parent.classList.add('active');
            item.classList.add('active');
            
            if (page === 'orders') loadOrders();
            else if (page === 'appointment') showAppointmentForm();
            else if (page === 'clients') loadClients();
            else if (page === 'workers') loadWorkers();
            else if (page === 'works-ref') loadWorksReference();
            else if (page === 'parts-ref') loadPartsReference();
            
            document.getElementById('page-title').innerText = item.innerText.trim();
        });
    });
}

// ========== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ==========
function setupUserProfile() {
    const userDropdown = document.getElementById('user-dropdown');
    const userCard = document.getElementById('user-profile-btn');
    
    if (userCard && userDropdown) {
        userCard.addEventListener('click', (e) => {
            e.stopPropagation();
            // Показываем/скрываем меню
            if (userDropdown.style.display === 'flex') {
                userDropdown.style.display = 'none';
            } else {
                userDropdown.style.display = 'flex';
            }
        });
        
        // Закрываем меню при клике вне
        document.addEventListener('click', (e) => {
            if (!userCard.contains(e.target) && !userDropdown.contains(e.target)) {
                userDropdown.style.display = 'none';
            }
        });
    }
    
    const profileItem = document.getElementById('dropdown-profile');
        if (profileItem) {
            profileItem.onclick = () => {
                if (currentUser) {
                    const userInfoHtml = `
                        <div style="background: #f1f5f9; border-radius: 12px; padding: 12px; margin-bottom: 10px;">
                            <div><strong>Логин:</strong> ${currentUser.username || currentUser.email}</div>
                            <div><strong>Email:</strong> ${currentUser.email}</div>
                            <div><strong>Роль:</strong> ${currentUser.role}</div>
                            <div><strong>ID:</strong> ${currentUser.id}</div>
                        </div>
                    `;
                    alert(` ${currentUser.username}\n ${currentUser.email}\n ${currentUser.role}\n🆔 ${currentUser.id}`);
                } else {
                    alert('Не авторизован');
                }
                document.getElementById('user-dropdown').style.display = 'none';
            };
        }
    
    const logoutItem = document.getElementById('dropdown-logout');
    if (logoutItem) {
        logoutItem.onclick = () => {
            logout();
            document.getElementById('user-dropdown').style.display = 'none';
        };
    }
}
// ========== ИНИЦИАЛИЗАЦИЯ ==========
document.addEventListener('DOMContentLoaded', async () => {
    showLoginModal();
    
    const searchInput = document.getElementById('global-search');
    if (searchInput) {
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim();
            if (query.length > 2 || query.length === 0) {
                searchGlobal();
            }
        });
    }

    const createBtn = document.getElementById('create-order-btn');
    if (createBtn) {
        createBtn.onclick = () => {
            const token = localStorage.getItem('auth_token');
            if (!token) {
                alert('Сначала авторизуйтесь');
                showLoginModal();
                return;
            }
            showCreateOrderForm();
        };
    }
    
    const token = localStorage.getItem('auth_token');
    if (token) {
        const isValid = await checkTokenValidity();
        if (isValid) {
            await loadCurrentUser();
            setupNavigation();
            setupUserProfile();
            await loadOrders();
            hideLoginModal();
        }
    }
});