// ========== ГЛОБАЛЬНАЯ ФУНКЦИЯ ВХОДА (вызывается из HTML) ==========
window.manualLogin = async function() {
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const errorDiv = document.getElementById('login-error');
    
    if (errorDiv) errorDiv.textContent = '';
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/user/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
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
            
            alert('Вход выполнен успешно!');
        } else {
            const error = await res.json();
            if (errorDiv) errorDiv.textContent = error.detail || 'Неверный email или пароль';
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

function hideLoginModal() {
    const modal = document.getElementById('login-modal');
    if (modal) modal.style.display = 'none';
}

async function checkTokenValidity() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        showLoginModal();
        return false;
    }
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/user/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            hideLoginModal();
            return true;
        } else {
            localStorage.removeItem('auth_token');
            showLoginModal();
            return false;
        }
    } catch (error) {
        console.error('Ошибка проверки токена:', error);
        showLoginModal();
        return false;
    }
}

let currentUser = null;

async function loadCurrentUser() {
    const token = localStorage.getItem('auth_token');
    if (!token) return null;
    try {
        const res = await fetch('http://localhost:8000/api/v1/user/me', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (res.ok) {
            currentUser = await res.json();
            const userNameEl = document.getElementById('user-name');
            const userRoleEl = document.getElementById('user-role');
            const userIdEl = document.getElementById('user-id');
            if (userNameEl) userNameEl.innerText = currentUser.name;
            if (userRoleEl) userRoleEl.innerText = currentUser.role;
            if (userIdEl) userIdEl.innerText = currentUser.id;
            return currentUser;
        }
    } catch(e) { console.log(e); }
    return null;
}

function logout() {
    localStorage.removeItem('auth_token');
    alert('Вы вышли из системы');
    location.reload();
}

// ========== МОДАЛЬНОЕ ОКНО СОЗДАНИЯ ЗАКАЗА ==========
function showCreateOrderModal() {
    const token = localStorage.getItem('auth_token');
    if (!token) {
        alert('Не авторизован');
        return;
    }
    
    const userId = currentUser?.id || 'client1';
    
    const modal = document.createElement('div');
    modal.id = 'create-order-modal';
    modal.style.cssText = 'position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); display:flex; align-items:center; justify-content:center; z-index:10001;';
    modal.innerHTML = `
        <div style="background:white; border-radius:24px; width:400px; max-width:90%; padding:32px;">
            <h3 style="margin-bottom:20px;">➕ Новый заказ</h3>
            <div style="margin-bottom:16px;">
                <label style="display:block; margin-bottom:6px; font-weight:500;">Автомобиль</label>
                <input type="text" id="order-car" placeholder="BMW X5, 2022" style="width:100%; padding:12px; border:1px solid #e2e8f0; border-radius:12px;">
            </div>
            <div style="margin-bottom:24px;">
                <label style="display:block; margin-bottom:6px; font-weight:500;">Клиент ID</label>
                <input type="text" id="order-client-id" value="${userId}" readonly style="width:100%; padding:12px; border:1px solid #e2e8f0; border-radius:12px; background:#f1f5f9;">
            </div>
            <div style="display:flex; gap:12px;">
                <button id="submit-order-btn" style="flex:1; padding:12px; background:#4f46e5; color:white; border:none; border-radius:12px; cursor:pointer;">Создать</button>
                <button id="cancel-order-btn" style="flex:1; padding:12px; background:#f1f5f9; border:none; border-radius:12px; cursor:pointer;">Отмена</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    
    document.getElementById('submit-order-btn').onclick = async () => {
        const carInfo = document.getElementById('order-car').value.trim();
        
        if (!carInfo) {
            alert('Введите автомобиль');
            return;
        }
        
        try {
            const res = await fetch('http://localhost:8000/api/v1/order/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
                body: JSON.stringify({ client_id: userId, car_info: carInfo })
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
    if (!content) return;
    
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка заказов...</div>';
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/order/orders', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const orders = await res.json();
        
        if (orders.length === 0) {
            content.innerHTML = '<div style="padding:40px;text-align:center;">Нет заказов</div>';
            return;
        }
        
        content.innerHTML = `<div class="cards-grid">${orders.map(order => `
            <div class="order-card">
                <div class="order-header">
                    <span class="order-number">#${order.number}</span>
                    <span class="order-status status-${order.status}">${order.status}</span>
                </div>
                <div class="order-car">🚗 ${order.car_info}</div>
                <div class="order-total">${(order.total || 0).toLocaleString()} ₽</div>
            </div>
        `).join('')}</div>`;
    } catch {
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки заказов</div>';
    }
}

// ========== ЗАПИСЬ НА РЕМОНТ ==========
function showAppointmentForm() {
    document.getElementById('page-title').textContent = 'Запись на ремонт';
    const content = document.getElementById('content-area');
    content.innerHTML = `
        <div style="max-width: 500px;">
            <div class="order-card" style="border-left-color: #10b981;">
                <h3 style="margin-bottom: 20px;">📅 Запись на ремонт</h3>
                <div class="form-group">
                    <label>Ваше имя</label>
                    <input type="text" id="appointment-name" class="form-input" placeholder="Иван Петров" style="margin-top:5px;">
                </div>
                <div class="form-group" style="margin-top:15px;">
                    <label>Телефон</label>
                    <input type="tel" id="appointment-phone" class="form-input" placeholder="+7 (999) 123-45-67" style="margin-top:5px;">
                </div>
                <div class="form-group" style="margin-top:15px;">
                    <label>Автомобиль</label>
                    <input type="text" id="appointment-car" class="form-input" placeholder="BMW X5, 2022" style="margin-top:5px;">
                </div>
                <div class="form-group" style="margin-top:15px;">
                    <label>Желаемая дата</label>
                    <input type="date" id="appointment-date" class="form-input" style="margin-top:5px;">
                </div>
                <div class="form-group" style="margin-top:15px;">
                    <label>Описание проблемы</label>
                    <textarea id="appointment-desc" class="form-input" rows="3" placeholder="Опишите неисправность..." style="margin-top:5px;"></textarea>
                </div>
                <button id="submit-appointment" class="btn btn-primary" style="width:100%; margin-top:20px; background:#10b981;">Отправить заявку</button>
            </div>
        </div>
    `;
    
    document.getElementById('submit-appointment')?.addEventListener('click', () => {
        const name = document.getElementById('appointment-name')?.value;
        const phone = document.getElementById('appointment-phone')?.value;
        const car = document.getElementById('appointment-car')?.value;
        if (!name || !phone || !car) {
            alert('❌ Заполните имя, телефон и автомобиль');
            return;
        }
        alert('✅ Заявка отправлена! Скоро с вами свяжутся.');
        showAppointmentForm();
    });
}

// ========== КЛИЕНТЫ ==========
async function loadClients() {
    document.getElementById('page-title').textContent = 'Клиенты';
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка...</div>';
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/order/orders', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const orders = await res.json();
        const clients = {};
        orders.forEach(o => { clients[o.client_id] = (clients[o.client_id] || 0) + 1; });
        
        if (Object.keys(clients).length === 0) {
            content.innerHTML = '<div style="padding:40px;text-align:center;">Нет клиентов</div>';
            return;
        }
        content.innerHTML = `<div class="cards-grid">${Object.entries(clients).map(([id, count]) => `
            <div class="order-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><strong>${id}</strong><br><span style="color:#64748b;">Заказов: ${count}</span></div>
                    <span style="font-size:32px;">👤</span>
                </div>
            </div>
        `).join('')}</div>`;
    } catch {
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки</div>';
    }
}

// ========== ИСПОЛНИТЕЛИ ==========
async function loadWorkers() {
    document.getElementById('page-title').textContent = 'Исполнители';
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка...</div>';
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    content.innerHTML = `
        <div class="cards-grid">
            <div class="order-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><strong>mechanic1</strong><br><span style="color:#64748b;">Механик</span><br><span style="font-size:12px; color:#94a3b8;">ID: mech_001</span></div>
                    <span style="font-size:32px;">🔧</span>
                </div>
            </div>
            <div class="order-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><strong>mechanic2</strong><br><span style="color:#64748b;">Механик</span><br><span style="font-size:12px; color:#94a3b8;">ID: mech_002</span></div>
                    <span style="font-size:32px;">🔧</span>
                </div>
            </div>
            <div class="order-card">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div><strong>mechanic3</strong><br><span style="color:#64748b;">Механик</span><br><span style="font-size:12px; color:#94a3b8;">ID: mech_003</span></div>
                    <span style="font-size:32px;">🔧</span>
                </div>
            </div>
        </div>
    `;
}

// ========== СПРАВОЧНИК РАБОТ ==========
async function loadWorksReference() {
    document.getElementById('page-title').textContent = 'Справочник работ';
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка...</div>';
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/reference/works', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const works = await res.json();
        
        if (works.length === 0) {
            content.innerHTML = '<div style="padding:40px;text-align:center;">Нет работ</div>';
            return;
        }
        
        content.innerHTML = `<div class="cards-grid">${works.map(work => `
            <div class="order-card">
                <div class="order-header">
                    <span class="order-number">${work.name}</span>
                    <span class="order-status status-accepted">${work.price_per_hour} ₽/час</span>
                </div>
                <div class="order-car">ID: ${work.id}</div>
            </div>
        `).join('')}</div>`;
    } catch {
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки</div>';
    }
}

// ========== СПРАВОЧНИК ЗАПЧАСТЕЙ ==========
async function loadPartsReference() {
    document.getElementById('page-title').textContent = 'Справочник запчастей';
    const content = document.getElementById('content-area');
    content.innerHTML = '<div style="padding:40px;text-align:center;">Загрузка...</div>';
    const token = localStorage.getItem('auth_token');
    if (!token) return;
    
    try {
        const res = await fetch('http://localhost:8000/api/v1/reference/parts', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const parts = await res.json();
        
        if (parts.length === 0) {
            content.innerHTML = '<div style="padding:40px;text-align:center;">Нет запчастей</div>';
            return;
        }
        
        content.innerHTML = `<div class="cards-grid">${parts.map(part => `
            <div class="order-card">
                <div class="order-header">
                    <span class="order-number">${part.name}</span>
                    <span class="order-status status-ready">${part.price} ₽</span>
                </div>
                <div class="order-car">Артикул: ${part.article}</div>
            </div>
        `).join('')}</div>`;
    } catch {
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки</div>';
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
        const res = await fetch('http://localhost:8000/api/v1/cars/', {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const cars = await res.json();
        
        if (cars.length === 0) {
            content.innerHTML = `
                <div style="text-align:center; padding:60px;">
                    <div style="font-size:48px; margin-bottom:16px;">🚗</div>
                    <div style="font-size:18px; color:#64748b;">Нет автомобилей</div>
                    <button onclick="showAddCarForm()" class="btn-add">Добавить автомобиль</button>
                </div>
            `;
            return;
        }
        
        content.innerHTML = `
            <div class="cards-grid">
                ${cars.map(car => `
                    <div class="order-card">
                        <div class="order-header">
                            <span class="order-number">${car.brand} ${car.model}</span>
                            <span class="order-status status-accepted">${car.year}</span>
                        </div>
                        <div class="order-car">
                            <div>🚗 ${car.license_plate}</div>
                            <div>🎨 ${car.color}</div>
                            <div style="font-size:12px; color:#94a3b8; margin-top:5px;">🔢 VIN: ${car.vin}</div>
                        </div>
                        <div class="car-actions">
                            <button onclick="editCar('${car.id}')" class="btn-edit">Редактировать</button>
                            <button onclick="deleteCar('${car.id}')" class="btn-delete">Удалить</button>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div style="text-align:center; margin-top:20px;">
                <button onclick="showAddCarForm()" class="btn-add">Добавить автомобиль</button>
            </div>
        `;
    } catch {
        content.innerHTML = '<div style="padding:40px;text-align:center;">Ошибка загрузки</div>';
    }
}

function showAddCarForm() {
    const content = document.getElementById('content-area');
    content.innerHTML = `
        <div style="max-width: 500px; margin: 0 auto;">
            <div class="order-card">
                <h3 style="margin-bottom:20px;">Новый автомобиль</h3>
                <div class="form-group"><label>Марка</label><input type="text" id="car-brand" class="form-input" placeholder="BMW"></div>
                <div class="form-group"><label>Модель</label><input type="text" id="car-model" class="form-input" placeholder="X5"></div>
                <div class="form-group"><label>Год</label><input type="number" id="car-year" class="form-input" placeholder="2022"></div>
                <div class="form-group"><label>Госномер</label><input type="text" id="car-plate" class="form-input" placeholder="А123ВС77"></div>
                <div class="form-group"><label>Цвет</label><input type="text" id="car-color" class="form-input" placeholder="Черный"></div>
                <div class="form-group"><label>VIN</label><input type="text" id="car-vin" class="form-input" placeholder="WBAXX123456789012"></div>
                <div style="display:flex; gap:12px; margin-top:20px;">
                    <button onclick="saveCar()" class="btn-edit">Сохранить</button>
                    <button onclick="loadCars()" class="btn-delete">Отмена</button>
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
            alert('Автомобиль добавлен!');
            loadCars();
        } else {
            alert('Ошибка');
        }
    } catch {
        alert('Ошибка подключения');
    }
}

async function editCar(carId) {
    const token = localStorage.getItem('auth_token');
    const res = await fetch(`http://localhost:8000/api/v1/cars/${carId}`, {
        headers: { 'Authorization': `Bearer ${token}` }
    });
    const car = await res.json();
    
    const content = document.getElementById('content-area');
    content.innerHTML = `
        <div style="max-width: 500px; margin: 0 auto;">
            <div class="order-card">
                <h3 style="margin-bottom:20px;">Редактировать автомобиль</h3>
                <div class="form-group"><label>Марка</label><input type="text" id="car-brand" class="form-input" value="${car.brand}"></div>
                <div class="form-group"><label>Модель</label><input type="text" id="car-model" class="form-input" value="${car.model}"></div>
                <div class="form-group"><label>Год</label><input type="number" id="car-year" class="form-input" value="${car.year}"></div>
                <div class="form-group"><label>Госномер</label><input type="text" id="car-plate" class="form-input" value="${car.license_plate}"></div>
                <div class="form-group"><label>Цвет</label><input type="text" id="car-color" class="form-input" value="${car.color}"></div>
                <div class="form-group"><label>VIN</label><input type="text" id="car-vin" class="form-input" value="${car.vin}"></div>
                <div style="display:flex; gap:12px; margin-top:20px;">
                    <button onclick="updateCar('${carId}')" class="btn-edit">Сохранить</button>
                    <button onclick="loadCars()" class="btn-delete">Отмена</button>
                </div>
            </div>
        </div>
    `;
}

async function updateCar(carId) {
    const token = localStorage.getItem('auth_token');
    const carData = {
        brand: document.getElementById('car-brand').value,
        model: document.getElementById('car-model').value,
        year: parseInt(document.getElementById('car-year').value),
        license_plate: document.getElementById('car-plate').value,
        color: document.getElementById('car-color').value,
        vin: document.getElementById('car-vin').value
    };
    
    try {
        const res = await fetch(`http://localhost:8000/api/v1/cars/${carId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json', 'Authorization': `Bearer ${token}` },
            body: JSON.stringify(carData)
        });
        if (res.ok) {
            alert('Автомобиль обновлён!');
            loadCars();
        } else {
            alert('Ошибка');
        }
    } catch {
        alert('Ошибка подключения');
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
            alert('Автомобиль удалён!');
            loadCars();
        } else {
            alert('Ошибка');
        }
    } catch {
        alert('Ошибка подключения');
    }
}

// ========== ОТЧЁТЫ ==========
function loadReports() {
    document.getElementById('page-title').textContent = 'Отчёты';
    const today = new Date().toISOString().slice(0, 10);
    const content = document.getElementById('content-area');
    content.innerHTML = `
        <div style="max-width:500px;">
            <div class="order-card">
                <h3 style="margin-bottom:16px;">Отчёт по выручке</h3>
                <div class="form-group" style="margin-bottom:12px;">
                    <label>С даты</label>
                    <input type="date" id="report-from" class="form-input" value="${today}" style="margin-top:5px;">
                </div>
                <div class="form-group" style="margin-bottom:20px;">
                    <label>По дату</label>
                    <input type="date" id="report-to" class="form-input" value="${today}" style="margin-top:5px;">
                </div>
                <button id="get-report" class="btn-edit" style="width:100%;">Сформировать</button>
                <div id="report-result" style="margin-top:20px;"></div>
            </div>
        </div>
    `;
    
    document.getElementById('get-report')?.addEventListener('click', async () => {
        const from = document.getElementById('report-from').value;
        const to = document.getElementById('report-to').value;
        const token = localStorage.getItem('auth_token');
        const resultDiv = document.getElementById('report-result');
        resultDiv.innerHTML = '<div style="padding:20px;text-align:center;">Загрузка...</div>';
        
        try {
            const res = await fetch(`http://localhost:8000/api/v1/report/revenue?from_date=${from}&to_date=${to}`, {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (res.ok) {
                const data = await res.json();
                resultDiv.innerHTML = `
                    <div style="background:#f0fdf4; padding:16px; border-radius:12px; margin-top:16px;">
                        <div style="font-size:24px; font-weight:700;">💰 ${data.total_revenue?.toLocaleString()} ₽</div>
                        <div style="margin-top:8px;">📋 Заказов: ${data.orders_count}</div>
                        <div>📈 Средний чек: ${data.avg_check?.toLocaleString()} ₽</div>
                    </div>
                `;
            } else {
                resultDiv.innerHTML = '<div style="color:red;">Ошибка загрузки отчёта</div>';
            }
        } catch {
            resultDiv.innerHTML = '<div style="color:red;">Ошибка подключения</div>';
        }
    });
}

// ========== CRM ДОСКА ==========
function loadCRM() {
    document.getElementById('page-title').textContent = 'CRM - Управление клиентами';
    const content = document.getElementById('content-area');
    
    const columns = [
        { name: 'Позвонить', color: '#fef3c7', textColor: '#d97706', icon: '📞' },
        { name: 'Запись', color: '#dbeafe', textColor: '#1e40af', icon: '📅' },
        { name: 'В работе', color: '#e0e7ff', textColor: '#4338ca', icon: '🔧' },
        { name: 'Выполнен', color: '#d1fae5', textColor: '#059669', icon: '✅' },
        { name: 'Отказ', color: '#fee2e2', textColor: '#dc2626', icon: '❌' }
    ];
    
    const cards = {
        'Позвонить': [
            { id: 1, name: 'Иван Петров', car: 'BMW X5', phone: '+7 999 123-45-67', date: '2026-05-10' },
            { id: 2, name: 'Сергей Иванов', car: 'Toyota Camry', phone: '+7 999 234-56-78', date: '2026-05-11' }
        ],
        'Запись': [
            { id: 3, name: 'Анна Сидорова', car: 'Kia Rio', phone: '+7 999 345-67-89', date: '2026-05-15' }
        ],
        'В работе': [
            { id: 4, name: 'Дмитрий Козлов', car: 'Mercedes E200', phone: '+7 999 456-78-90', date: '2026-05-18' }
        ],
        'Выполнен': [
            { id: 5, name: 'Ольга Смирнова', car: 'Hyundai Solaris', phone: '+7 999 567-89-01', date: '2026-05-05' }
        ],
        'Отказ': [
            { id: 6, name: 'Павел Новиков', car: 'Volkswagen Passat', phone: '+7 999 678-90-12', date: '2026-05-03' }
        ]
    };
    
    let html = `<div class="crm-board">`;
    
    columns.forEach(col => {
        const columnCards = cards[col.name] || [];
        html += `
            <div class="crm-column">
                <div class="crm-column-header" style="background: ${col.color}; color: ${col.textColor};">
                    ${col.icon} ${col.name} <span style="font-size: 11px; background: rgba(0,0,0,0.1); padding: 2px 8px; border-radius: 20px;">${columnCards.length}</span>
                </div>
                <div class="crm-cards">
                    ${columnCards.map(card => `
                        <div class="crm-card" onclick="alert('Клиент: ${card.name}\\nАвто: ${card.car}\\nТелефон: ${card.phone}\\nДата: ${card.date}')">
                            <div class="crm-card-title">${card.name}</div>
                            <div class="crm-card-info">🚗 ${card.car}</div>
                            <div class="crm-card-info">📞 ${card.phone}</div>
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });
    
    html += `</div>`;
    content.innerHTML = html;
}

// ========== НАВИГАЦИЯ ==========
function setupNavigation() {
    document.querySelectorAll('.nav-item:not(.has-submenu)').forEach(item => {
        item.removeEventListener('click', item._listener);
        const handler = (e) => {
            e.preventDefault();
            document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
            document.querySelectorAll('.submenu-item').forEach(i => i.classList.remove('active'));
            item.classList.add('active');
            
            const page = item.dataset.page;
            if (page === 'crm') loadCRM();
            else if (page === 'cars') loadCars();
            else if (page === 'reports') loadReports();
            else loadOrders();
        };
        item._listener = handler;
        item.addEventListener('click', handler);
    });
    
    document.querySelectorAll('.submenu-item').forEach(item => {
        item.removeEventListener('click', item._listener);
        const handler = (e) => {
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
        };
        item._listener = handler;
        item.addEventListener('click', handler);
    });
}

// ========== ПРОФИЛЬ ПОЛЬЗОВАТЕЛЯ ==========
function setupUserProfile() {
    const userDropdown = document.getElementById('user-dropdown');
    const userCard = document.getElementById('user-profile-btn');
    
    if (userCard && userDropdown) {
        userCard.addEventListener('mouseenter', () => {
            userDropdown.style.display = 'flex';
        });
        
        userCard.addEventListener('mouseleave', () => {
            setTimeout(() => {
                if (!userDropdown.matches(':hover')) {
                    userDropdown.style.display = 'none';
                }
            }, 100);
        });
        
        userDropdown.addEventListener('mouseleave', () => {
            userDropdown.style.display = 'none';
        });
        
        userDropdown.addEventListener('mouseenter', () => {
            userDropdown.style.display = 'flex';
        });
    }
    
    const profileItem = document.getElementById('dropdown-profile');
    if (profileItem) {
        profileItem.onclick = () => {
            if (!currentUser) {
                alert('Не авторизован');
                return;
            }
            alert(`👤 ${currentUser.name}\n📧 ${currentUser.email}\n🎭 ${currentUser.role}\n🆔 ${currentUser.id}`);
        };
    }
    
    const logoutItem = document.getElementById('dropdown-logout');
    if (logoutItem) {
        logoutItem.onclick = () => {
            logout();
        };
    }
}

// ========== ИНИЦИАЛИЗАЦИЯ ==========
document.addEventListener('DOMContentLoaded', async () => {
    const isValid = await checkTokenValidity();
    
    if (isValid) {
        await loadCurrentUser();
        setupNavigation();
        setupUserProfile();
        
        const createBtn = document.getElementById('create-order-btn');
        if (createBtn) {
            createBtn.onclick = () => {
                const token = localStorage.getItem('auth_token');
                if (!token) {
                    alert('Сначала авторизуйтесь');
                    return;
                }
                showCreateOrderModal();
            };
        }
        
        await loadOrders();
    }
});