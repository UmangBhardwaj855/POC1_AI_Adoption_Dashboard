import { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './components/Dashboard';
import UsersPage from './components/UsersPage';
import MetricsPage from './components/MetricsPage';
import SettingsPage from './components/SettingsPage';
import { Menu, X } from 'lucide-react';
import './index.css';

// AI-themed background videos (free to use)
const VIDEO_SOURCES = [
  'https://cdn.pixabay.com/video/2020/05/25/40130-424930032_large.mp4', // Neural network
  'https://cdn.pixabay.com/video/2021/02/21/65804-515513498_large.mp4', // Data flow
  'https://cdn.pixabay.com/video/2020/02/28/32671-394813081_large.mp4', // Tech particles
];

function App() {
  const [activePage, setActivePage] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const renderPage = () => {
    switch (activePage) {
      case 'dashboard':
        return <Dashboard />;
      case 'users':
        return <UsersPage />;
      case 'metrics':
        return <MetricsPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <Dashboard />;
    }
  };

  const handleNavigate = (page) => {
    setActivePage(page);
    setSidebarOpen(false); // Close sidebar on mobile after navigation
  };

  return (
    <div className="app">
      {/* AI Video Background */}
      <div className="video-background">
        <video autoPlay muted loop playsInline className="bg-video">
          <source src={VIDEO_SOURCES[0]} type="video/mp4" />
        </video>
        <div className="video-overlay"></div>
        <div className="video-gradient"></div>
      </div>

      {/* Animated Particles */}
      <div className="particles">
        {[...Array(50)].map((_, i) => (
          <div 
            key={i} 
            className="particle" 
            style={{
              left: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 20}s`,
              animationDuration: `${15 + Math.random() * 20}s`,
            }}
          />
        ))}
      </div>

      {/* Glowing Orbs */}
      <div className="orbs">
        <div className="orb orb-1"></div>
        <div className="orb orb-2"></div>
        <div className="orb orb-3"></div>
      </div>

      {/* Mobile Menu Button */}
      <button 
        className="mobile-menu-btn"
        onClick={() => setSidebarOpen(!sidebarOpen)}
        aria-label="Toggle menu"
      >
        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      {/* Mobile Overlay */}
      <div 
        className={`mobile-overlay ${sidebarOpen ? 'active' : ''}`}
        onClick={() => setSidebarOpen(false)}
      />

      <Sidebar 
        activePage={activePage} 
        onNavigate={handleNavigate}
        isOpen={sidebarOpen}
      />
      <main className="main-content">
        {renderPage()}
      </main>
    </div>
  );
}

export default App;
