import React from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  LayoutDashboard, 
  Users, 
  BarChart3, 
  MessageSquare,
  MessageCircle,
  Settings,
  LogOut,
  Filter
} from 'lucide-react';

interface ManagerLayoutProps {
  user: { role: string; name: string } | null;
}

export default function ManagerLayout({ user }: ManagerLayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();

  const menuItems = [
    { icon: LayoutDashboard, label: 'Панель управления', path: '/manager/dashboard' },
    { icon: MessageSquare, label: 'Сообщения', path: '/manager/messages' },
    { icon: MessageCircle, label: 'Чат', path: '/manager/chat' },
    { icon: Users, label: 'Клиенты', path: '/manager/clients' },
    { icon: BarChart3, label: 'Аналитика', path: '/manager/analytics' },
    { icon: Filter, label: 'Воронка продаж', path: '/manager/funnel' },
    { icon: Settings, label: 'Настройки', path: '/manager/settings' },
  ];

  const handleLogout = () => {
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-6 border-b border-gray-200">
          <h1 className="text-2xl text-pink-600">Beauty Salon CRM</h1>
          <p className="text-sm text-gray-500 mt-1">Менеджер</p>
        </div>

        <nav className="flex-1 overflow-y-auto p-4">
          <ul className="space-y-1">
            {menuItems.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;
              
              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? 'bg-pink-50 text-pink-600'
                        : 'text-gray-700 hover:bg-gray-50'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.label}</span>
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="p-4 border-t border-gray-200">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-10 h-10 bg-pink-600 rounded-full flex items-center justify-center text-white">
              {user?.name.charAt(0) || 'M'}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm truncate">{user?.name || 'Менеджер'}</p>
              <p className="text-xs text-gray-500">{user?.role || 'manager'}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <LogOut className="w-4 h-4" />
            <span>Выйти</span>
          </button>
        </div>
      </aside>

      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}
