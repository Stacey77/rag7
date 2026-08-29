import React, { useState } from 'react';
import {
  LayoutDashboard,
  Brain,
  BarChart3,
  Activity,
  Settings,
  Users,
  Shield,
  Database,
  Bell,
  Search,
  Menu,
  X,
  ChevronDown,
  LogOut,
  User,
  Moon,
  Sun,
  MessageSquare,
} from 'lucide-react';

type Section = 
  | 'dashboard'
  | 'models'
  | 'analytics'
  | 'monitoring'
  | 'settings'
  | 'users'
  | 'security'
  | 'data';

interface NavItem {
  id: Section;
  label: string;
  icon: React.ReactNode;
}

export const App: React.FC = () => {
  const [activeSection, setActiveSection] = useState<Section>('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [darkMode, setDarkMode] = useState(true);
  const [notifications] = useState(3);

  const navItems: NavItem[] = [
    { id: 'dashboard', label: 'Dashboard', icon: <LayoutDashboard className="w-5 h-5" /> },
    { id: 'models', label: 'Models', icon: <Brain className="w-5 h-5" /> },
    { id: 'analytics', label: 'Analytics', icon: <BarChart3 className="w-5 h-5" /> },
    { id: 'monitoring', label: 'Monitoring', icon: <Activity className="w-5 h-5" /> },
    { id: 'data', label: 'Data', icon: <Database className="w-5 h-5" /> },
    { id: 'users', label: 'Users', icon: <Users className="w-5 h-5" /> },
    { id: 'security', label: 'Security', icon: <Shield className="w-5 h-5" /> },
    { id: 'settings', label: 'Settings', icon: <Settings className="w-5 h-5" /> },
  ];

  const renderContent = () => {
    switch (activeSection) {
      case 'dashboard':
        return (
          <div>
            <h1 className="text-3xl font-bold text-white mb-6">Dashboard</h1>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {/* Metric Cards */}
              {[
                { label: 'Total Models', value: '24', change: '+12%', positive: true },
                { label: 'Active Users', value: '1,234', change: '+8%', positive: true },
                { label: 'API Calls', value: '45.2K', change: '+23%', positive: true },
                { label: 'Avg Response', value: '145ms', change: '-5%', positive: true },
              ].map((metric, idx) => (
                <div key={idx} className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
                  <p className="text-gray-400 text-sm mb-2">{metric.label}</p>
                  <div className="flex items-end justify-between">
                    <h3 className="text-3xl font-bold text-white">{metric.value}</h3>
                    <span className={`text-sm ${metric.positive ? 'text-green-400' : 'text-red-400'}`}>
                      {metric.change}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-8 grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">Recent Activity</h3>
                <div className="space-y-3">
                  {[
                    { action: 'Model deployed', model: 'GPT-4 Turbo', time: '2 min ago' },
                    { action: 'User registered', model: 'john@example.com', time: '15 min ago' },
                    { action: 'API key created', model: 'Production Key', time: '1 hour ago' },
                  ].map((activity, idx) => (
                    <div key={idx} className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                      <div>
                        <p className="text-white text-sm font-medium">{activity.action}</p>
                        <p className="text-gray-400 text-xs">{activity.model}</p>
                      </div>
                      <span className="text-xs text-gray-500">{activity.time}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
                <h3 className="text-xl font-bold text-white mb-4">System Status</h3>
                <div className="space-y-4">
                  {[
                    { service: 'API Gateway', status: 'Operational', uptime: '99.9%' },
                    { service: 'Model Inference', status: 'Operational', uptime: '99.8%' },
                    { service: 'Database', status: 'Operational', uptime: '100%' },
                  ].map((service, idx) => (
                    <div key={idx} className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-2 h-2 rounded-full bg-green-500"></div>
                        <span className="text-white text-sm">{service.service}</span>
                      </div>
                      <div className="flex items-center gap-4">
                        <span className="text-gray-400 text-xs">{service.uptime}</span>
                        <span className="text-green-400 text-xs">{service.status}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      case 'models':
        return (
          <div>
            <h1 className="text-3xl font-bold text-white mb-6">Model Management</h1>
            <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
              <p className="text-gray-300">Model management interface coming soon...</p>
            </div>
          </div>
        );

      case 'analytics':
        return (
          <div>
            <h1 className="text-3xl font-bold text-white mb-6">Analytics</h1>
            <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
              <p className="text-gray-300">Analytics dashboard coming soon...</p>
            </div>
          </div>
        );

      case 'monitoring':
        return (
          <div>
            <h1 className="text-3xl font-bold text-white mb-6">Monitoring</h1>
            <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
              <p className="text-gray-300">Monitoring interface coming soon...</p>
            </div>
          </div>
        );

      case 'data':
        return (
          <div>
            <h1 className="text-3xl font-bold text-white mb-6">Data Management</h1>
            <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
              <p className="text-gray-300">Data management interface coming soon...</p>
            </div>
          </div>
        );

      case 'users':
        return (
          <div>
            <h1 className="text-3xl font-bold text-white mb-6">User Management</h1>
            <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
              <p className="text-gray-300">User management interface coming soon...</p>
            </div>
          </div>
        );

      case 'security':
        return (
          <div>
            <h1 className="text-3xl font-bold text-white mb-6">Security</h1>
            <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
              <p className="text-gray-300">Security settings coming soon...</p>
            </div>
          </div>
        );

      case 'settings':
        return (
          <div>
            <h1 className="text-3xl font-bold text-white mb-6">Settings</h1>
            <div className="p-6 rounded-2xl bg-white/10 backdrop-blur-xl border border-white/20">
              <p className="text-gray-300">Settings interface coming soon...</p>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className={`min-h-screen ${darkMode ? 'bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900' : 'bg-gray-100'}`}>
      {/* Sidebar */}
      <aside
        className={`fixed top-0 left-0 h-screen z-40 transition-all duration-300 ${
          sidebarOpen ? 'w-64' : 'w-20'
        }`}
      >
        <div className="h-full p-4 bg-white/10 backdrop-blur-xl border-r border-white/20">
          {/* Logo */}
          <div className="flex items-center justify-between mb-8">
            {sidebarOpen ? (
              <>
                <div className="flex items-center gap-2">
                  <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center">
                    <Brain className="w-5 h-5 text-white" />
                  </div>
                  <span className="text-white font-bold text-lg">AI Platform</span>
                </div>
                <button
                  onClick={() => setSidebarOpen(false)}
                  className="text-gray-400 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </>
            ) : (
              <button
                onClick={() => setSidebarOpen(true)}
                className="mx-auto text-gray-400 hover:text-white transition-colors"
              >
                <Menu className="w-5 h-5" />
              </button>
            )}
          </div>

          {/* Navigation */}
          <nav className="space-y-2">
            {navItems.map((item) => (
              <button
                key={item.id}
                onClick={() => setActiveSection(item.id)}
                className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                  activeSection === item.id
                    ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white'
                    : 'text-gray-400 hover:text-white hover:bg-white/5'
                }`}
                title={!sidebarOpen ? item.label : undefined}
              >
                {item.icon}
                {sidebarOpen && <span className="font-medium">{item.label}</span>}
              </button>
            ))}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <div className={`transition-all duration-300 ${sidebarOpen ? 'ml-64' : 'ml-20'}`}>
        {/* Top Header */}
        <header className="sticky top-0 z-30 backdrop-blur-xl bg-white/10 border-b border-white/20">
          <div className="flex items-center justify-between px-8 py-4">
            {/* Search Bar */}
            <div className="flex-1 max-w-xl">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search..."
                  className="w-full pl-11 pr-4 py-2 rounded-lg bg-white/5 border border-white/10 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            {/* Right Actions */}
            <div className="flex items-center gap-4">
              {/* Theme Toggle */}
              <button
                onClick={() => setDarkMode(!darkMode)}
                className="p-2 rounded-lg bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-all"
              >
                {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
              </button>

              {/* Notifications */}
              <button className="relative p-2 rounded-lg bg-white/5 text-gray-400 hover:text-white hover:bg-white/10 transition-all">
                <Bell className="w-5 h-5" />
                {notifications > 0 && (
                  <span className="absolute top-0 right-0 w-5 h-5 bg-red-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                    {notifications}
                  </span>
                )}
              </button>

              {/* User Menu */}
              <div className="relative">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="flex items-center gap-3 p-2 rounded-lg bg-white/5 hover:bg-white/10 transition-all"
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white text-sm font-bold">
                    JD
                  </div>
                  <div className="text-left hidden md:block">
                    <p className="text-white text-sm font-medium">John Doe</p>
                    <p className="text-gray-400 text-xs">Admin</p>
                  </div>
                  <ChevronDown className="w-4 h-4 text-gray-400" />
                </button>

                {userMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 rounded-lg bg-white/10 backdrop-blur-xl border border-white/20 shadow-xl">
                    <div className="p-2">
                      <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 transition-all">
                        <User className="w-4 h-4" />
                        <span className="text-sm">Profile</span>
                      </button>
                      <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-gray-300 hover:text-white hover:bg-white/10 transition-all">
                        <Settings className="w-4 h-4" />
                        <span className="text-sm">Settings</span>
                      </button>
                      <div className="my-1 border-t border-white/10"></div>
                      <button className="w-full flex items-center gap-3 px-3 py-2 rounded-lg text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-all">
                        <LogOut className="w-4 h-4" />
                        <span className="text-sm">Logout</span>
                      </button>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Main Content Area */}
        <main className="p-8">
          {renderContent()}
        </main>
      </div>

      {/* AI Companion - Fixed Bottom Right */}
      <button className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 shadow-2xl flex items-center justify-center text-white hover:scale-110 transition-transform z-50">
        <MessageSquare className="w-6 h-6" />
      </button>
    </div>
  );
};

export default App;
