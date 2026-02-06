import { useState, useEffect } from 'react';
import { 
  Users, Search, Plus, Edit2, Trash2, Filter, RefreshCw, 
  User, Mail, Briefcase, Award, Calendar, Activity,
  ChevronDown, MoreHorizontal, CheckCircle, XCircle, Sparkles
} from 'lucide-react';
import api from '../services/api';

const MATURITY_LEVELS = [
  { level: 0, name: 'L0 - Not Enabled', badge: 'l0', color: '#6b7280' },
  { level: 1, name: 'L1 - Enabled', badge: 'l1', color: '#ef4444' },
  { level: 2, name: 'L2 - Active', badge: 'l2', color: '#f59e0b' },
  { level: 3, name: 'L3 - Working', badge: 'l3', color: '#06b6d4' },
  { level: 4, name: 'L4 - Consistent', badge: 'l4', color: '#10b981' },
  { level: 5, name: 'L5 - Value User', badge: 'l5', color: '#6366f1' },
];

// Generate avatar initials
function getInitials(name) {
  return name.split(/[._-]/).map(n => n[0]?.toUpperCase()).slice(0, 2).join('');
}

// Generate random avatar color
function getAvatarColor(name) {
  const colors = ['#6366f1', '#ec4899', '#06b6d4', '#10b981', '#f59e0b', '#8b5cf6', '#ef4444'];
  let hash = 0;
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash);
  }
  return colors[Math.abs(hash) % colors.length];
}

function UsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [filterLevel, setFilterLevel] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState(null);
  const [refreshing, setRefreshing] = useState(false);
  const [viewMode, setViewMode] = useState('table'); // 'table' or 'cards'
  const [formData, setFormData] = useState({
    github_username: '',
    email: '',
    team: '',
    maturity_level: 0,
    is_active: true
  });

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setRefreshing(true);
      const params = new URLSearchParams();
      if (filterLevel !== '') params.append('maturity_level', filterLevel);
      
      const res = await api.get(`/users?${params}`);
      setUsers(res.data);
    } catch (err) {
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingUser) {
        await api.put(`/users/${editingUser.id}`, formData);
      } else {
        await api.post('/users', formData);
      }
      setShowModal(false);
      setEditingUser(null);
      resetForm();
      fetchUsers();
    } catch (err) {
      console.error('Error saving user:', err);
    }
  };

  const handleEdit = (user) => {
    setEditingUser(user);
    setFormData({
      github_username: user.github_username,
      email: user.email || '',
      team: user.team || '',
      maturity_level: user.maturity_level,
      is_active: user.is_active
    });
    setShowModal(true);
  };

  const handleDelete = async (userId) => {
    if (confirm('Are you sure you want to delete this user?')) {
      try {
        await api.delete(`/users/${userId}`);
        fetchUsers();
      } catch (err) {
        console.error('Error deleting user:', err);
      }
    }
  };

  const resetForm = () => {
    setFormData({
      github_username: '',
      email: '',
      team: '',
      maturity_level: 0,
      is_active: true
    });
  };

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.github_username.toLowerCase().includes(search.toLowerCase()) ||
                          (user.email || '').toLowerCase().includes(search.toLowerCase()) ||
                          (user.team || '').toLowerCase().includes(search.toLowerCase());
    return matchesSearch;
  });

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <p>Loading users...</p>
      </div>
    );
  }

  return (
    <div className="users-page">
      <header className="header">
        <div>
          <h1>
            <Users size={28} />
            User Management
          </h1>
          <p className="subtitle">Manage and track {users.length} developers across AI adoption levels</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div className="stats-badges">
            {MATURITY_LEVELS.map(level => {
              const count = users.filter(u => u.maturity_level === level.level).length;
              return count > 0 && (
                <span key={level.level} className={`mini-badge l${level.level}`}>
                  {level.badge.toUpperCase()}: {count}
                </span>
              );
            })}
          </div>
        </div>
      </header>

      <div className="page-header">
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <div className="search-box">
            <Search size={18} />
            <input
              type="text"
              placeholder="Search users, emails, teams..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="filter-box">
            <Filter size={16} />
            <select
              value={filterLevel}
              onChange={(e) => {
                setFilterLevel(e.target.value);
                fetchUsers();
              }}
            >
              <option value="">All Levels</option>
              {MATURITY_LEVELS.map(level => (
                <option key={level.level} value={level.level}>{level.name}</option>
              ))}
            </select>
            <ChevronDown size={16} />
          </div>
          <button 
            className="btn btn-secondary" 
            onClick={fetchUsers}
            disabled={refreshing}
          >
            <RefreshCw size={16} className={refreshing ? 'spinning' : ''} />
          </button>
        </div>
        <button className="btn btn-primary" onClick={() => { resetForm(); setEditingUser(null); setShowModal(true); }}>
          <Plus size={18} />
          Add User
          <Sparkles size={14} />
        </button>
      </div>

      <div className="card users-card">
        <table className="data-table premium-table">
          <thead>
            <tr>
              <th>User</th>
              <th>Team</th>
              <th>Maturity Level</th>
              <th>Status</th>
              <th>Joined</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map((user, index) => (
              <tr key={user.id} style={{ animationDelay: `${index * 0.03}s` }}>
                <td>
                  <div className="user-cell">
                    <div 
                      className="user-avatar"
                      style={{ backgroundColor: getAvatarColor(user.github_username) }}
                    >
                      {getInitials(user.github_username)}
                    </div>
                    <div className="user-info">
                      <div className="user-name">{user.github_username}</div>
                      <div className="user-email">
                        <Mail size={12} />
                        {user.email || 'No email'}
                      </div>
                    </div>
                  </div>
                </td>
                <td>
                  <div className="team-cell">
                    <Briefcase size={14} />
                    {user.team || 'Unassigned'}
                  </div>
                </td>
                <td>
                  <span className={`badge level-badge l${user.maturity_level}`}>
                    <Award size={12} />
                    L{user.maturity_level} - {MATURITY_LEVELS[user.maturity_level]?.name.split(' - ')[1]}
                  </span>
                </td>
                <td>
                  <span className={`status-badge ${user.is_active ? 'active' : 'inactive'}`}>
                    {user.is_active ? <CheckCircle size={14} /> : <XCircle size={14} />}
                    {user.is_active ? 'Active' : 'Inactive'}
                  </span>
                </td>
                <td>
                  <div className="date-cell">
                    <Calendar size={14} />
                    {new Date(user.created_at).toLocaleDateString('en-US', { 
                      month: 'short', 
                      day: 'numeric', 
                      year: 'numeric' 
                    })}
                  </div>
                </td>
                <td>
                  <div className="actions-cell">
                    <button 
                      className="action-btn edit" 
                      onClick={() => handleEdit(user)}
                      title="Edit user"
                    >
                      <Edit2 size={16} />
                    </button>
                    <button 
                      className="action-btn delete" 
                      onClick={() => handleDelete(user.id)}
                      title="Delete user"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {filteredUsers.length === 0 && (
          <div className="empty-state">
            <Users size={48} />
            <h3>No users found</h3>
            <p>Try adjusting your search or filter criteria</p>
          </div>
        )}
      </div>

      {/* Results count */}
      <div className="results-footer">
        <Activity size={16} />
        Showing {filteredUsers.length} of {users.length} users
      </div>

      {/* User Modal */}
      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal premium-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div className="modal-icon">
                {editingUser ? <Edit2 size={24} /> : <Plus size={24} />}
              </div>
              <div>
                <h3>{editingUser ? 'Edit User' : 'Add New User'}</h3>
                <p>{editingUser ? 'Update user details and maturity level' : 'Add a new developer to track'}</p>
              </div>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>
                  <User size={16} />
                  GitHub Username *
                </label>
                <input
                  type="text"
                  value={formData.github_username}
                  onChange={(e) => setFormData({ ...formData, github_username: e.target.value })}
                  placeholder="e.g., john_doe"
                  required
                />
              </div>
              <div className="form-group">
                <label>
                  <Mail size={16} />
                  Email
                </label>
                <input
                  type="email"
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="e.g., john@company.com"
                />
              </div>
              <div className="form-group">
                <label>
                  <Briefcase size={16} />
                  Team
                </label>
                <input
                  type="text"
                  value={formData.team}
                  onChange={(e) => setFormData({ ...formData, team: e.target.value })}
                  placeholder="e.g., Backend, Frontend, DevOps"
                />
              </div>
              <div className="form-group">
                <label>
                  <Award size={16} />
                  Maturity Level
                </label>
                <select
                  value={formData.maturity_level}
                  onChange={(e) => setFormData({ ...formData, maturity_level: parseInt(e.target.value) })}
                >
                  {MATURITY_LEVELS.map(level => (
                    <option key={level.level} value={level.level}>{level.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                  />
                  <span className="checkmark"></span>
                  <Activity size={16} />
                  Active User
                </label>
              </div>
              <div className="modal-actions">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>
                  Cancel
                </button>
                <button type="submit" className="btn btn-primary">
                  <Sparkles size={16} />
                  {editingUser ? 'Update User' : 'Create User'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default UsersPage;
