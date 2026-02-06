import { useState, useEffect } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { 
  LayoutDashboard, Users, TrendingUp, Code, CheckCircle2, XCircle,
  Activity, Zap, Target, Award, ArrowUpRight,
  RefreshCw, Clock, Sparkles
} from 'lucide-react';
import api from '../services/api';

const COLORS = {
  primary: '#6366f1',
  secondary: '#ec4899',
  accent: '#06b6d4',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  purple: '#8b5cf6',
  pink: '#f472b6',
  blue: '#3b82f6',
  green: '#22c55e',
  yellow: '#eab308',
  orange: '#f97316',
  gray: '#6b7280'
};

// Animated Counter Component
function AnimatedCounter({ value, suffix = '', duration = 1000 }) {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const end = parseFloat(value) || 0;
    const increment = end / (duration / 16);
    let current = 0;
    
    const timer = setInterval(() => {
      current += increment;
      if (current >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(current);
      }
    }, 16);
    
    return () => clearInterval(timer);
  }, [value, duration]);
  
  return (
    <span className="counter-animate">
      {typeof value === 'number' && value % 1 !== 0 ? count.toFixed(1) : Math.floor(count)}{suffix}
    </span>
  );
}

// Live Status Indicator
function LiveIndicator() {
  return (
    <div className="live-indicator">
      <span>Live Data</span>
    </div>
  );
}

function Dashboard() {
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [loading, setLoading] = useState(true);
  const [lastUpdated, setLastUpdated] = useState(new Date());
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      const [summaryRes, trendsRes] = await Promise.all([
        api.get('/dashboard/summary'),
        api.get('/dashboard/trends')
      ]);
      setSummary(summaryRes.data);
      setTrends(trendsRes.data);
      setLastUpdated(new Date());
    } catch (err) {
      console.error('Error fetching data:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = () => {
    setRefreshing(true);
    fetchData();
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading dashboard...</p>
      </div>
    );
  }

  const maturityData = [
    { level: 'L0', name: 'Not Enabled', count: summary?.l0_count || 0 },
    { level: 'L1', name: 'Enabled', count: summary?.l1_count || 0 },
    { level: 'L2', name: 'Active', count: summary?.l2_count || 0 },
    { level: 'L3', name: 'Working', count: summary?.l3_count || 0 },
    { level: 'L4', name: 'Consistent', count: summary?.l4_count || 0 },
    { level: 'L5', name: 'Value User', count: summary?.l5_count || 0 },
  ];

  const totalUsers = summary?.total_users || 1;

  return (
    <div className="dashboard">
      <header className="header">
        <div>
          <h1>
            <LayoutDashboard size={28} />
            AI Adoption Dashboard
          </h1>
          <p className="subtitle">Real-time Copilot adoption metrics • Umang Bhardwaj's L0-L5 Framework</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <LiveIndicator />
          <button 
            className="btn btn-secondary" 
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'spinning' : ''} />
            Refresh
          </button>
        </div>
      </header>

      {/* Key Metrics */}
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon blue">
            <Users size={24} color="white" />
          </div>
          <div className="metric-label">Weekly Active Users</div>
          <div className="metric-value blue">
            <AnimatedCounter value={summary?.weekly_active_users || 0} />
          </div>
          <div className="metric-change positive">
            <ArrowUpRight size={14} />
            +12% from last week
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon green">
            <TrendingUp size={24} color="white" />
          </div>
          <div className="metric-label">Acceptance Rate</div>
          <div className="metric-value green">
            <AnimatedCounter value={summary?.acceptance_rate || 0} suffix="%" />
          </div>
          <div className="metric-change positive">
            <ArrowUpRight size={14} />
            +3.2% improvement
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon purple">
            <Award size={24} color="white" />
          </div>
          <div className="metric-label">L5 Value Users</div>
          <div className="metric-value purple">
            <AnimatedCounter value={summary?.l5_count || 0} />
          </div>
          <div className="metric-change positive">
            <ArrowUpRight size={14} />
            {((summary?.l5_count / totalUsers) * 100).toFixed(0)}% of total
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon pink">
            <Code size={24} color="white" />
          </div>
          <div className="metric-label">Total Suggestions</div>
          <div className="metric-value pink">
            <AnimatedCounter value={summary?.total_suggestions || 0} />
          </div>
          <div className="metric-change positive">
            <Sparkles size={14} />
            AI-generated code
          </div>
        </div>
      </div>

      {/* Charts Section */}
      <div className="charts-grid">
        <div className="chart-card">
          <h3>
            <Activity size={20} />
            Adoption Trends (Last 30 Days)
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={trends}>
              <defs>
                <linearGradient id="colorActive" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorAcceptance" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.success} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={COLORS.success} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(15, 15, 26, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px'
                }}
              />
              <Legend />
              <Area 
                type="monotone" 
                dataKey="active_users" 
                name="Active Users"
                stroke={COLORS.primary} 
                fillOpacity={1}
                fill="url(#colorActive)"
                strokeWidth={2}
              />
              <Area 
                type="monotone" 
                dataKey="acceptance_rate" 
                name="Acceptance %"
                stroke={COLORS.success} 
                fillOpacity={1}
                fill="url(#colorAcceptance)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>
            <Zap size={20} />
            AI Productivity Impact
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={trends.slice(-14)}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { day: 'numeric' })}
              />
              <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(15, 15, 26, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px'
                }}
              />
              <Legend />
              <Bar 
                dataKey="ai_assisted_commits" 
                name="AI Commits"
                fill={COLORS.accent}
                radius={[4, 4, 0, 0]}
              />
              <Bar 
                dataKey="suggestions_accepted" 
                name="Accepted"
                fill={COLORS.purple}
                radius={[4, 4, 0, 0]}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Maturity Distribution */}
      <div className="maturity-section">
        <h3>
          <Target size={20} style={{ color: COLORS.primary }} />
          Maturity Level Distribution
        </h3>
        <div className="maturity-bars">
          {maturityData.map((level, index) => (
            <div className="maturity-bar" key={level.level} style={{ animationDelay: `${index * 0.1}s` }}>
              <div className={`level-badge ${level.level.toLowerCase()}`}>
                {level.level}
              </div>
              <div className="level-info">
                <div className="level-name">{level.name}</div>
                <div className="level-desc">
                  {level.level === 'L0' && 'Copilot not enabled'}
                  {level.level === 'L1' && 'Enabled, minimal usage'}
                  {level.level === 'L2' && 'Regular user'}
                  {level.level === 'L3' && 'Active contributor'}
                  {level.level === 'L4' && 'Power user'}
                  {level.level === 'L5' && 'Champion user'}
                </div>
              </div>
              <div className="progress-container">
                <div className="progress-bar">
                  <div 
                    className={`progress-fill ${level.level.toLowerCase()}`}
                    style={{ width: `${(level.count / totalUsers) * 100}%` }}
                  />
                </div>
                <div className="count">{level.count}</div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* KPIs Section */}
      {summary?.kpis && (
        <div className="kpi-section">
          <h3 style={{ marginBottom: '20px', display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Target size={20} style={{ color: COLORS.primary }} />
            Key Performance Indicators
          </h3>
          <div className="kpi-grid">
            {Object.entries(summary.kpis).map(([name, kpi], index) => (
              <div 
                key={name} 
                className={`kpi-card ${kpi.achieved ? 'achieved' : 'not-achieved'}`}
                style={{ animationDelay: `${index * 0.1}s` }}
              >
                <div className="kpi-status">
                  {kpi.achieved ? <CheckCircle2 size={18} /> : <XCircle size={18} />}
                </div>
                <div className="kpi-header">
                  <div className="kpi-name">{name}</div>
                  <div className="kpi-phase">Phase {index + 1}</div>
                </div>
                <div className="kpi-values">
                  <div className="kpi-current">
                    <AnimatedCounter value={kpi.current} suffix="%" />
                  </div>
                  <div className="kpi-target">Target: {kpi.target}%</div>
                </div>
                <div className="kpi-progress">
                  <div 
                    className="kpi-progress-fill"
                    style={{ width: `${Math.min((kpi.current / kpi.target) * 100, 100)}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Quality & Language Charts */}
      <div className="charts-grid" style={{ marginTop: '30px' }}>
        <div className="chart-card">
          <h3>
            <CheckCircle2 size={20} />
            Code Quality Metrics
          </h3>
          <div className="metrics-grid" style={{ marginTop: '20px' }}>
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <div style={{ 
                fontSize: '48px', 
                fontWeight: '700', 
                color: COLORS.success,
                fontFamily: 'Space Grotesk'
              }}>
                <AnimatedCounter value={summary?.code_retention_rate || 0} suffix="%" />
              </div>
              <div style={{ color: 'rgba(255,255,255,0.6)', marginTop: '8px' }}>
                Code Retention Rate
              </div>
            </div>
            <div style={{ textAlign: 'center', padding: '20px' }}>
              <div style={{ 
                fontSize: '48px', 
                fontWeight: '700', 
                color: COLORS.warning,
                fontFamily: 'Space Grotesk'
              }}>
                <AnimatedCounter value={summary?.modification_rate || 0} suffix="%" />
              </div>
              <div style={{ color: 'rgba(255,255,255,0.6)', marginTop: '8px' }}>
                Modification Rate
              </div>
            </div>
          </div>
        </div>

        <div className="chart-card">
          <h3>
            <Award size={20} />
            Language Breakdown
          </h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={Object.entries(summary?.language_breakdown || {}).map(([name, value], i) => ({
                  name,
                  value,
                  fill: Object.values(COLORS)[i % Object.values(COLORS).length]
                }))}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={100}
                paddingAngle={5}
                dataKey="value"
                label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
              >
                {Object.entries(summary?.language_breakdown || {}).map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={Object.values(COLORS)[index % Object.values(COLORS).length]}
                  />
                ))}
              </Pie>
              <Tooltip 
                contentStyle={{ 
                  background: 'rgba(15, 15, 26, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px'
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Footer */}
      <div style={{ 
        marginTop: '30px', 
        padding: '20px', 
        background: 'rgba(255,255,255,0.03)', 
        borderRadius: '16px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'rgba(255,255,255,0.5)' }}>
          <Clock size={16} />
          Last updated: {lastUpdated.toLocaleTimeString()}
        </div>
        <div style={{ color: 'rgba(255,255,255,0.5)', fontSize: '13px' }}>
          Auto-refresh every 30 seconds
        </div>
      </div>
    </div>
  );
}

export default Dashboard;
