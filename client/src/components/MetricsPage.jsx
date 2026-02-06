import { useState, useEffect } from 'react';
import {
  LineChart, Line, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from 'recharts';
import { 
  BarChart3, TrendingUp, Code, GitPullRequest, 
  Check, Shield, Bug, RefreshCw, Activity, Zap, 
  Target, Award, Sparkles, ArrowUpRight
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
  blue: '#3b82f6'
};

// Animated Counter
function AnimatedCounter({ value, suffix = '' }) {
  const [count, setCount] = useState(0);
  
  useEffect(() => {
    const end = parseFloat(value) || 0;
    const duration = 1000;
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
  }, [value]);
  
  return (
    <span>
      {typeof value === 'number' && value % 1 !== 0 ? count.toFixed(1) : Math.floor(count)}{suffix}
    </span>
  );
}

function MetricsPage() {
  const [activeTab, setActiveTab] = useState('adoption');
  const [adoptionMetrics, setAdoptionMetrics] = useState(null);
  const [productivityMetrics, setProductivityMetrics] = useState(null);
  const [qualityMetrics, setQualityMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    fetchMetrics();
  }, []);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      setRefreshing(true);
      const [adoption, productivity, quality] = await Promise.all([
        api.get('/metrics/adoption'),
        api.get('/metrics/productivity'),
        api.get('/metrics/quality')
      ]);
      
      setAdoptionMetrics(adoption.data);
      setProductivityMetrics(productivity.data);
      setQualityMetrics(quality.data);
    } catch (err) {
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading metrics...</p>
      </div>
    );
  }

  const tabs = [
    { id: 'adoption', label: 'Adoption', icon: TrendingUp, color: COLORS.primary },
    { id: 'productivity', label: 'Productivity', icon: Zap, color: COLORS.success },
    { id: 'quality', label: 'Quality', icon: Shield, color: COLORS.purple },
  ];

  return (
    <div className="metrics-page">
      <header className="header">
        <div>
          <h1>
            <BarChart3 size={28} />
            Detailed Metrics
          </h1>
          <p className="subtitle">Comprehensive AI adoption analytics • Umang's L0-L5 Framework</p>
        </div>
        <button 
          className="btn btn-secondary" 
          onClick={fetchMetrics}
          disabled={refreshing}
        >
          <RefreshCw size={16} className={refreshing ? 'spinning' : ''} />
          Refresh
        </button>
      </header>

      <div className="premium-tabs">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`premium-tab ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
            style={{ '--tab-color': tab.color }}
          >
            <tab.icon size={18} />
            <span>{tab.label}</span>
            {activeTab === tab.id && <div className="tab-indicator" />}
          </button>
        ))}
      </div>

      <div className="tab-content">
        {activeTab === 'adoption' && (
          <AdoptionTab data={adoptionMetrics} />
        )}

        {activeTab === 'productivity' && (
          <ProductivityTab data={productivityMetrics} />
        )}

        {activeTab === 'quality' && (
          <QualityTab data={qualityMetrics} />
        )}
      </div>
    </div>
  );
}

function AdoptionTab({ data }) {
  if (!data) return <p>No adoption data available</p>;

  return (
    <div className="tab-panel">
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon blue">
            <Activity size={24} color="white" />
          </div>
          <div className="metric-label">Weekly Active Users (WAU)</div>
          <div className="metric-value blue">
            <AnimatedCounter value={data.summary?.wau || 0} />
          </div>
          <div className="metric-change positive">
            <ArrowUpRight size={14} />
            Active developers
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon green">
            <Target size={24} color="white" />
          </div>
          <div className="metric-label">Monthly Active Users (MAU)</div>
          <div className="metric-value green">
            <AnimatedCounter value={data.summary?.mau || 0} />
          </div>
          <div className="metric-change positive">
            <ArrowUpRight size={14} />
            Monthly reach
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon yellow">
            <Zap size={24} color="white" />
          </div>
          <div className="metric-label">Activation Rate</div>
          <div className="metric-value yellow">
            <AnimatedCounter value={data.summary?.activation_rate || 0} suffix="%" />
          </div>
          <div className="metric-change positive">
            <Sparkles size={14} />
            Enabled users
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon purple">
            <Code size={24} color="white" />
          </div>
          <div className="metric-label">Avg Prompts/User</div>
          <div className="metric-value purple">
            <AnimatedCounter value={data.summary?.avg_prompts_per_user || 0} />
          </div>
          <div className="metric-change positive">
            <ArrowUpRight size={14} />
            Daily average
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>
            <TrendingUp size={20} />
            Active Users Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data.trends || []}>
              <defs>
                <linearGradient id="colorActiveUsers" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0}/>
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
                fill="url(#colorActiveUsers)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>
            <Code size={20} />
            Prompts & Suggestions
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.trends?.slice(-14) || []}>
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
              <Bar dataKey="prompts" name="Prompts" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
              <Bar dataKey="suggestions" name="Suggestions" fill={COLORS.success} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function ProductivityTab({ data }) {
  if (!data) return <p>No productivity data available</p>;

  return (
    <div className="tab-panel">
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon blue">
            <GitPullRequest size={24} color="white" />
          </div>
          <div className="metric-label">AI-Assisted Commits</div>
          <div className="metric-value blue">
            <AnimatedCounter value={data.summary?.total_ai_commits || 0} />
          </div>
          <div className="metric-change positive">
            <ArrowUpRight size={14} />
            Total commits
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon green">
            <Code size={24} color="white" />
          </div>
          <div className="metric-label">AI-Assisted PRs</div>
          <div className="metric-value green">
            <AnimatedCounter value={data.summary?.total_ai_prs || 0} />
          </div>
          <div className="metric-change positive">
            <ArrowUpRight size={14} />
            Pull requests
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon yellow">
            <Check size={24} color="white" />
          </div>
          <div className="metric-label">Avg Acceptance Rate</div>
          <div className="metric-value yellow">
            <AnimatedCounter value={data.summary?.avg_acceptance_rate || 0} suffix="%" />
          </div>
          <div className="metric-change positive">
            <Sparkles size={14} />
            AI suggestions
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon purple">
            <Zap size={24} color="white" />
          </div>
          <div className="metric-label">Lines Generated</div>
          <div className="metric-value purple">
            <AnimatedCounter value={data.summary?.total_lines_generated || 0} />
          </div>
          <div className="metric-change positive">
            <ArrowUpRight size={14} />
            AI-generated code
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>
            <GitPullRequest size={20} />
            AI-Assisted Development
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.trends?.slice(-14) || []}>
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
              <Bar dataKey="ai_commits" name="AI Commits" fill={COLORS.primary} radius={[4, 4, 0, 0]} />
              <Bar dataKey="ai_prs" name="AI PRs" fill={COLORS.success} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>
            <Check size={20} />
            Code Acceptance Rate
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.trends || []}>
              <defs>
                <linearGradient id="colorAcceptanceRate" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={COLORS.purple} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={COLORS.purple} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
              />
              <YAxis domain={[0, 100]} tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
              <Tooltip 
                formatter={(value) => `${value?.toFixed(1)}%`}
                contentStyle={{ 
                  background: 'rgba(15, 15, 26, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="acceptance_rate" 
                name="Acceptance Rate"
                stroke={COLORS.purple}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

function QualityTab({ data }) {
  if (!data) return <p>No quality data available</p>;

  return (
    <div className="tab-panel">
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon green">
            <Shield size={24} color="white" />
          </div>
          <div className="metric-label">Code Retention Rate</div>
          <div className="metric-value green">
            <AnimatedCounter value={data.summary?.avg_retention_rate || 0} suffix="%" />
          </div>
          <div className="metric-change positive">
            <ArrowUpRight size={14} />
            Code kept
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon yellow">
            <Activity size={24} color="white" />
          </div>
          <div className="metric-label">Modification Rate</div>
          <div className="metric-value yellow">
            <AnimatedCounter value={data.summary?.avg_modification_rate || 0} suffix="%" />
          </div>
          <div className="metric-change neutral">
            <Sparkles size={14} />
            Code modified
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon red">
            <Bug size={24} color="white" />
          </div>
          <div className="metric-label">Bug Rate</div>
          <div className="metric-value red">
            <AnimatedCounter value={data.summary?.avg_bug_rate || 0} suffix="%" />
          </div>
          <div className="metric-change negative">
            <ArrowUpRight size={14} />
            Lower is better
          </div>
        </div>
        <div className="metric-card">
          <div className="metric-icon purple">
            <GitPullRequest size={24} color="white" />
          </div>
          <div className="metric-label">PR Rejection Rate</div>
          <div className="metric-value purple">
            <AnimatedCounter value={data.summary?.avg_pr_rejection_rate || 0} suffix="%" />
          </div>
          <div className="metric-change negative">
            <ArrowUpRight size={14} />
            Lower is better
          </div>
        </div>
      </div>

      <div className="charts-grid">
        <div className="chart-card">
          <h3>
            <Shield size={20} />
            Code Quality Trend
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data.trends || []}>
              <defs>
                <linearGradient id="colorRetention" x1="0" y1="0" x2="0" y2="1">
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
              <YAxis domain={[0, 100]} tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
              <Tooltip 
                formatter={(value) => `${value?.toFixed(1)}%`}
                contentStyle={{ 
                  background: 'rgba(15, 15, 26, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px'
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="retention_rate" 
                name="Retention Rate"
                stroke={COLORS.success}
                strokeWidth={2}
                dot={false}
              />
              <Line 
                type="monotone" 
                dataKey="modification_rate" 
                name="Modification Rate"
                stroke={COLORS.warning}
                strokeWidth={2}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="chart-card">
          <h3>
            <Bug size={20} />
            Bug & PR Rejection Rate
          </h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data.trends?.slice(-14) || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" />
              <XAxis 
                dataKey="date" 
                tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }}
                tickFormatter={(date) => new Date(date).toLocaleDateString('en-US', { day: 'numeric' })}
              />
              <YAxis tick={{ fill: 'rgba(255,255,255,0.5)', fontSize: 11 }} />
              <Tooltip 
                formatter={(value) => `${value?.toFixed(1)}%`}
                contentStyle={{ 
                  background: 'rgba(15, 15, 26, 0.95)', 
                  border: '1px solid rgba(255,255,255,0.1)',
                  borderRadius: '12px'
                }}
              />
              <Legend />
              <Bar dataKey="bug_rate" name="Bug Rate %" fill={COLORS.danger} radius={[4, 4, 0, 0]} />
              <Bar dataKey="pr_rejection_rate" name="PR Rejection %" fill={COLORS.purple} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default MetricsPage;
