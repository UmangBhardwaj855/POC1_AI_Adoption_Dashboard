import { useState } from 'react';
import { 
  Settings as SettingsIcon, 
  Github, 
  RefreshCw, 
  Check, 
  AlertCircle,
  Users,
  Database,
  Key
} from 'lucide-react';
import api from '../services/api';

function SettingsPage() {
  const [token, setToken] = useState('');
  const [org, setOrg] = useState('');
  const [syncUsers, setSyncUsers] = useState(true);
  const [syncMetrics, setSyncMetrics] = useState(true);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(false);
  const [testing, setTesting] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const testConnection = async () => {
    if (!token || !org) {
      setError('Please enter both token and organization name');
      return;
    }

    setTesting(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.get(`/github/test-connection?token=${token}&org=${org}`);
      setResult({
        type: 'test',
        ...response.data
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Connection failed');
    } finally {
      setTesting(false);
    }
  };

  const handleSync = async () => {
    if (!token || !org) {
      setError('Please enter both token and organization name');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await api.post('/github/sync', {
        token,
        org,
        sync_users: syncUsers,
        sync_metrics: syncMetrics,
        days
      });
      setResult({
        type: 'sync',
        ...response.data
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Sync failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="settings-page">
      <header className="header">
        <h1>
          <SettingsIcon size={28} />
          Settings
        </h1>
        <p className="subtitle">Configure GitHub integration and sync data</p>
      </header>

      <div className="settings-content">
        <div className="settings-card">
          <h2>
            <Github size={24} />
            GitHub Copilot Integration
          </h2>
          <p className="card-description">
            Connect to your GitHub organization to import users and sync Copilot usage metrics.
          </p>

          <div className="form-group">
            <label>
              <Key size={16} />
              GitHub Personal Access Token
            </label>
            <input
              type="password"
              value={token}
              onChange={(e) => setToken(e.target.value)}
              placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
            />
            <span className="help-text">
              Required scopes: <code>read:org</code>, <code>copilot</code>
            </span>
          </div>

          <div className="form-group">
            <label>
              <Github size={16} />
              Organization Name
            </label>
            <input
              type="text"
              value={org}
              onChange={(e) => setOrg(e.target.value)}
              placeholder="e.g., xoriant"
            />
          </div>

          <div className="form-group">
            <label>Sync Options</label>
            <div className="checkbox-group">
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={syncUsers}
                  onChange={(e) => setSyncUsers(e.target.checked)}
                />
                <Users size={16} />
                Sync Users from Organization
              </label>
              <label className="checkbox-label">
                <input
                  type="checkbox"
                  checked={syncMetrics}
                  onChange={(e) => setSyncMetrics(e.target.checked)}
                />
                <Database size={16} />
                Sync Copilot Metrics (Enterprise only)
              </label>
            </div>
          </div>

          <div className="form-group">
            <label>Days of History</label>
            <select value={days} onChange={(e) => setDays(Number(e.target.value))}>
              <option value={7}>Last 7 days</option>
              <option value={14}>Last 14 days</option>
              <option value={30}>Last 30 days</option>
              <option value={60}>Last 60 days</option>
              <option value={90}>Last 90 days</option>
            </select>
          </div>

          {error && (
            <div className="alert alert-error">
              <AlertCircle size={20} />
              {error}
            </div>
          )}

          {result && (
            <div className="alert alert-success">
              <Check size={20} />
              {result.type === 'test' ? (
                <span>Connected successfully! Found {result.members_count} members.</span>
              ) : (
                <span>
                  Sync complete! {result.users_synced} users synced
                  {result.metrics_synced > 0 && `, ${result.metrics_synced} days of metrics`}
                </span>
              )}
            </div>
          )}

          <div className="button-group">
            <button 
              className="btn btn-secondary"
              onClick={testConnection}
              disabled={testing || loading}
            >
              {testing ? (
                <>
                  <RefreshCw size={16} className="spinning" />
                  Testing...
                </>
              ) : (
                <>
                  <Check size={16} />
                  Test Connection
                </>
              )}
            </button>

            <button 
              className="btn btn-primary"
              onClick={handleSync}
              disabled={loading || testing}
            >
              {loading ? (
                <>
                  <RefreshCw size={16} className="spinning" />
                  Syncing...
                </>
              ) : (
                <>
                  <RefreshCw size={16} />
                  Sync Data
                </>
              )}
            </button>
          </div>
        </div>

        <div className="settings-card info-card">
          <h3>How to get a GitHub Token</h3>
          <ol>
            <li>Go to <a href="https://github.com/settings/tokens" target="_blank" rel="noreferrer">GitHub Settings → Developer settings → Personal access tokens</a></li>
            <li>Click "Generate new token (classic)"</li>
            <li>Select scopes: <code>read:org</code> and <code>copilot</code></li>
            <li>Click "Generate token" and copy it</li>
          </ol>
          
          <h3>Requirements</h3>
          <ul>
            <li>You must be an organization admin</li>
            <li>Organization must have GitHub Copilot Business/Enterprise</li>
            <li>Copilot metrics require Enterprise license</li>
          </ul>
        </div>
      </div>

      <style>{`
        .settings-page {
          padding: 24px;
        }
        
        .settings-content {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 24px;
          max-width: 1200px;
        }
        
        @media (max-width: 900px) {
          .settings-content {
            grid-template-columns: 1fr;
          }
        }
        
        .settings-card {
          background: white;
          border-radius: 12px;
          padding: 24px;
          box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        
        .settings-card h2 {
          display: flex;
          align-items: center;
          gap: 12px;
          margin: 0 0 8px 0;
          font-size: 20px;
          color: #202124;
        }
        
        .card-description {
          color: #5f6368;
          margin-bottom: 24px;
        }
        
        .form-group {
          margin-bottom: 20px;
        }
        
        .form-group label {
          display: flex;
          align-items: center;
          gap: 8px;
          margin-bottom: 8px;
          font-weight: 500;
          color: #202124;
        }
        
        .form-group input[type="text"],
        .form-group input[type="password"],
        .form-group select {
          width: 100%;
          padding: 12px;
          border: 1px solid #dadce0;
          border-radius: 8px;
          font-size: 14px;
          transition: border-color 0.2s;
        }
        
        .form-group input:focus,
        .form-group select:focus {
          outline: none;
          border-color: #4285f4;
        }
        
        .help-text {
          font-size: 12px;
          color: #5f6368;
          margin-top: 4px;
          display: block;
        }
        
        .help-text code {
          background: #f1f3f4;
          padding: 2px 6px;
          border-radius: 4px;
        }
        
        .checkbox-group {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }
        
        .checkbox-label {
          display: flex;
          align-items: center;
          gap: 8px;
          cursor: pointer;
          font-weight: normal !important;
        }
        
        .checkbox-label input {
          width: 18px;
          height: 18px;
          cursor: pointer;
        }
        
        .alert {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px 16px;
          border-radius: 8px;
          margin-bottom: 20px;
        }
        
        .alert-error {
          background: #fce8e6;
          color: #c5221f;
        }
        
        .alert-success {
          background: #e6f4ea;
          color: #137333;
        }
        
        .button-group {
          display: flex;
          gap: 12px;
        }
        
        .btn {
          display: flex;
          align-items: center;
          gap: 8px;
          padding: 12px 24px;
          border: none;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 500;
          cursor: pointer;
          transition: all 0.2s;
        }
        
        .btn:disabled {
          opacity: 0.6;
          cursor: not-allowed;
        }
        
        .btn-primary {
          background: #4285f4;
          color: white;
        }
        
        .btn-primary:hover:not(:disabled) {
          background: #3367d6;
        }
        
        .btn-secondary {
          background: #f1f3f4;
          color: #202124;
        }
        
        .btn-secondary:hover:not(:disabled) {
          background: #e8eaed;
        }
        
        .spinning {
          animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
        
        .info-card {
          background: #f8f9fa;
        }
        
        .info-card h3 {
          margin: 0 0 12px 0;
          font-size: 16px;
          color: #202124;
        }
        
        .info-card h3:not(:first-child) {
          margin-top: 24px;
        }
        
        .info-card ol, .info-card ul {
          margin: 0;
          padding-left: 20px;
          color: #5f6368;
        }
        
        .info-card li {
          margin-bottom: 8px;
        }
        
        .info-card a {
          color: #4285f4;
        }
        
        .info-card code {
          background: #e8eaed;
          padding: 2px 6px;
          border-radius: 4px;
          font-size: 13px;
        }
      `}</style>
    </div>
  );
}

export default SettingsPage;
