import React from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import { Phone, Mail, Instagram, Menu, X } from 'lucide-react';

export default function PublicLayout() {
  const location = useLocation();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  const menuItems = [
    { label: 'Главная', path: '/' },
    { label: 'Прайс-лист', path: '/price-list' },
    { label: 'О нас', path: '/about' },
    { label: 'Контакты', path: '/contacts' },
    { label: 'FAQ', path: '/faq' },
  ];

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-20">
            {/* Logo */}
            <Link to="/" className="flex items-center gap-3">
              <div className="w-12 h-12 bg-gradient-to-br from-pink-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-white text-xl">✨</span>
              </div>
              <div>
                <h1 className="text-xl text-gray-900">Luxury Beauty Salon</h1>
                <p className="text-xs text-gray-500">Красота и совершенство</p>
              </div>
            </Link>

            {/* Desktop Navigation */}
            <nav className="hidden md:flex items-center gap-8">
              {menuItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`transition-colors ${
                    location.pathname === item.path
                      ? 'text-pink-600'
                      : 'text-gray-700 hover:text-pink-600'
                  }`}
                >
                  {item.label}
                </Link>
              ))}
            </nav>

            {/* Contact Info & CTA */}
            <div className="hidden lg:flex items-center gap-4">
              <div className="flex items-center gap-2 text-gray-600">
                <Phone className="w-4 h-4" />
                <span className="text-sm">+971 50 123 4567</span>
              </div>
              <Link
                to="/cabinet"
                className="px-6 py-2.5 bg-gradient-to-r from-pink-500 to-purple-600 text-white rounded-full hover:shadow-lg transition-shadow"
              >
                Войти
              </Link>
            </div>

            {/* Mobile Menu Button */}
            <button
              className="md:hidden p-2"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="md:hidden border-t border-gray-200 bg-white">
            <nav className="px-4 py-4 space-y-2">
              {menuItems.map((item) => (
                <Link
                  key={item.path}
                  to={item.path}
                  className={`block px-4 py-3 rounded-lg ${
                    location.pathname === item.path
                      ? 'bg-pink-50 text-pink-600'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item.label}
                </Link>
              ))}
              <Link
                to="/cabinet"
                className="block px-4 py-3 bg-gradient-to-r from-pink-500 to-purple-600 text-white text-center rounded-lg"
                onClick={() => setMobileMenuOpen(false)}
              >
                Личный кабинет
              </Link>
            </nav>
          </div>
        )}
      </header>

      {/* Main Content */}
      <main className="flex-1">
        <Outlet />
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* About */}
            <div>
              <h3 className="text-lg mb-4">Luxury Beauty Salon</h3>
              <p className="text-gray-400 text-sm">
                Премиальные услуги красоты в самом сердце города. 
                Профессиональные мастера и индивидуальный подход.
              </p>
            </div>

            {/* Quick Links */}
            <div>
              <h3 className="text-lg mb-4">Быстрые ссылки</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/price-list" className="hover:text-white">Прайс-лист</Link></li>
                <li><Link to="/about" className="hover:text-white">О нас</Link></li>
                <li><Link to="/cooperation" className="hover:text-white">Сотрудничество</Link></li>
                <li><Link to="/faq" className="hover:text-white">FAQ</Link></li>
              </ul>
            </div>

            {/* Contacts */}
            <div>
              <h3 className="text-lg mb-4">Контакты</h3>
              <ul className="space-y-3 text-sm text-gray-400">
                <li className="flex items-center gap-2">
                  <Phone className="w-4 h-4" />
                  <span>+971 50 123 4567</span>
                </li>
                <li className="flex items-center gap-2">
                  <Mail className="w-4 h-4" />
                  <span>info@luxurybeauty.ae</span>
                </li>
                <li className="flex items-center gap-2">
                  <Instagram className="w-4 h-4" />
                  <span>@luxurybeauty_dubai</span>
                </li>
              </ul>
            </div>

            {/* Working Hours */}
            <div>
              <h3 className="text-lg mb-4">Часы работы</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li>Пн-Пт: 9:00 - 21:00</li>
                <li>Сб-Вс: 10:00 - 20:00</li>
              </ul>
            </div>
          </div>

          <div className="border-t border-gray-800 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-gray-400">
            <p>© 2025 Luxury Beauty Salon. Все права защищены.</p>
            <div className="flex gap-6">
              <Link to="/privacy-policy" className="hover:text-white">Политика конфиденциальности</Link>
              <Link to="/terms" className="hover:text-white">Условия использования</Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
