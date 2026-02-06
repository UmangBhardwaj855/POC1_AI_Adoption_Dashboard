import { useState } from 'react';
import { 
  LayoutDashboard, Users, BarChart3, Settings, Brain, 
  ChevronRight, Sparkles, Zap, Activity, Github, Cpu
} from 'lucide-react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'users', label: 'Users', icon: Users },
  { id: 'metrics', label: 'Metrics', icon: BarChart3 },
  { id: 'settings', label: 'Settings', icon: Settings },
];

function Sidebar({ activePage, onNavigate, isOpen }) {
  const [isHovered, setIsHovered] = useState(null);

  return (
    <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
      {/* Logo Section */}
      <div className="sidebar-header">
        <div className="logo-container">
          <div className="logo-icon-wrapper">
            <Cpu size={24} />
          </div>
          <div className="logo-text-wrapper">
            <span className="logo-title">AI Dashboard</span>
            <span className="logo-version">v2.0 Pro</span>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav">
        <div className="nav-section-title">Navigation</div>
        {navItems.map((item, index) => (
          <button
            key={item.id}
            className={`nav-item ${activePage === item.id ? 'active' : ''}`}
            onClick={() => onNavigate(item.id)}
            onMouseEnter={() => setIsHovered(item.id)}
            onMouseLeave={() => setIsHovered(null)}
          >
            <div className="nav-icon-box">
              <item.icon size={18} />
            </div>
            <span className="nav-text">{item.label}</span>
            <ChevronRight 
              size={14} 
              className={`nav-chevron ${isHovered === item.id || activePage === item.id ? 'show' : ''}`} 
            />
          </button>
        ))}
      </nav>

      {/* Status Section */}
      <div className="sidebar-status">
        <div className="nav-section-title">System Status</div>
        <div className="status-grid">
          <div className="status-item">
            <div className="status-dot online"></div>
            <span>API Online</span>
          </div>
          <div className="status-item">
            <div className="status-dot online"></div>
            <span>DB Connected</span>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <div className="sidebar-footer">
        <div className="footer-brand">
          <Brain size={16} />
          <span>Umang's L0-L5 Framework</span>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;
