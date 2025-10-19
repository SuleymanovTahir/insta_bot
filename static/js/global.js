// ===== ГЛОБАЛЬНЫЕ УТИЛИТЫ =====

/**
 * Показать уведомление
 * @param {string} message - Текст сообщения
 * @param {string} type - Тип: success, error, warning, info
 * @param {number} duration - Длительность показа (мс)
 */
function showNotification(message, type = 'success', duration = 5000) {
    const container = document.getElementById('notificationContainer');
    if (!container) return;
    
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-circle',
        info: 'fa-info-circle'
    };
    
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#3b82f6'
    };
    
    notification.innerHTML = `
        <i class="fas ${icons[type]}" style="color: ${colors[type]}; font-size: 1.25rem;"></i>
        <span style="font-weight: 500; color: #111827;">${message}</span>
        <button onclick="this.parentElement.remove()" style="margin-left: auto; padding: 0.25rem; color: #6b7280; cursor: pointer; background: none; border: none;">
            <i class="fas fa-times"></i>
        </button>
    `;
    
    container.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, duration);
}

/**
 * Подтверждение действия
 * @param {string} message - Текст подтверждения
 * @returns {Promise<boolean>}
 */
async function confirmAction(message) {
    return confirm(message);
}

/**
 * Форматирование даты
 * @param {string} dateString - Дата в формате ISO
 * @returns {string} - Отформатированная дата
 */
function formatDate(dateString) {
    const date = new Date(dateString);
    const day = String(date.getDate()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const year = date.getFullYear();
    return `${day}.${month}.${year}`;
}

/**
 * Форматирование времени
 * @param {string} dateString - Дата в формате ISO
 * @returns {string} - Отформатированное время
 */
function formatTime(dateString) {
    const date = new Date(dateString);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
}

/**
 * Форматирование даты и времени
 * @param {string} dateString - Дата в формате ISO
 * @returns {string} - Отформатированная дата и время
 */
function formatDateTime(dateString) {
    return `${formatDate(dateString)} ${formatTime(dateString)}`;
}

/**
 * Debounce функция
 * @param {Function} func - Функция для debounce
 * @param {number} wait - Время задержки (мс)
 * @returns {Function}
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Копировать текст в буфер обмена
 * @param {string} text - Текст для копирования
 */
async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
        showNotification('Скопировано в буфер обмена', 'success');
    } catch (err) {
        showNotification('Ошибка копирования', 'error');
    }
}

/**
 * Загрузить данные из API
 * @param {string} url - URL эндпоинта
 * @param {object} options - Опции fetch
 * @returns {Promise<any>}
 */
async function fetchAPI(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        showNotification('Ошибка загрузки данных', 'error');
        throw error;
    }
}

/**
 * Показать loader
 */
function showLoader() {
    const loader = document.createElement('div');
    loader.id = 'globalLoader';
    loader.style.cssText = `
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    `;
    loader.innerHTML = `
        <div class="loader"></div>
    `;
    document.body.appendChild(loader);
}

/**
 * Скрыть loader
 */
function hideLoader() {
    const loader = document.getElementById('globalLoader');
    if (loader) {
        loader.remove();
    }
}

/**
 * Валидация email
 * @param {string} email
 * @returns {boolean}
 */
function validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

/**
 * Валидация телефона
 * @param {string} phone
 * @returns {boolean}
 */
function validatePhone(phone) {
    const re = /^[\d\s\+\-\(\)]+$/;
    return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

/**
 * Экспорт данных
 * @param {string} format - Формат (csv, excel, pdf)
 * @param {string} endpoint - API эндпоинт
 */
async function exportData(format, endpoint) {
    showLoader();
    try {
        const url = `${endpoint}?format=${format}`;
        window.location.href = url;
        showNotification(`Экспорт ${format.toUpperCase()} начат`, 'info');
    } catch (error) {
        showNotification('Ошибка экспорта', 'error');
    } finally {
        setTimeout(hideLoader, 1000);
    }
}

/**
 * Инициализация tooltips
 */
function initTooltips() {
    document.querySelectorAll('[data-tooltip]').forEach(element => {
        const text = element.getAttribute('data-tooltip');
        element.classList.add('tooltip');
        
        const tooltipText = document.createElement('span');
        tooltipText.className = 'tooltip-text';
        tooltipText.textContent = text;
        element.appendChild(tooltipText);
    });
}

/**
 * Анимация счётчика
 * @param {HTMLElement} element - Элемент для анимации
 * @param {number} target - Целевое значение
 * @param {number} duration - Длительность (мс)
 */
function animateCounter(element, target, duration = 1000) {
    const start = parseInt(element.textContent) || 0;
    const increment = (target - start) / (duration / 16);
    let current = start;
    
    const timer = setInterval(() => {
        current += increment;
        if ((increment > 0 && current >= target) || (increment < 0 && current <= target)) {
            element.textContent = target;
            clearInterval(timer);
        } else {
            element.textContent = Math.round(current);
        }
    }, 16);
}

// ===== ИНИЦИАЛИЗАЦИЯ ПРИ ЗАГРУЗКЕ =====
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация tooltips
    initTooltips();
    
    // Анимация счётчиков на странице
    document.querySelectorAll('[data-counter]').forEach(element => {
        const target = parseInt(element.getAttribute('data-counter'));
        animateCounter(element, target);
    });
    
    // Smooth scroll для якорных ссылок
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            if (href !== '#') {
                e.preventDefault();
                const target = document.querySelector(href);
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            }
        });
    });
});

// ===== ЭКСПОРТ ДЛЯ ИСПОЛЬЗОВАНИЯ В ДРУГИХ СКРИПТАХ =====
window.showNotification = showNotification;
window.confirmAction = confirmAction;
window.formatDate = formatDate;
window.formatTime = formatTime;
window.formatDateTime = formatDateTime;
window.debounce = debounce;
window.copyToClipboard = copyToClipboard;
window.fetchAPI = fetchAPI;
window.showLoader = showLoader;
window.hideLoader = hideLoader;
window.validateEmail = validateEmail;
window.validatePhone = validatePhone;
window.exportData = exportData;
window.animateCounter = animateCounter;