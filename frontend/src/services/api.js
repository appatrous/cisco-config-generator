import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if exists
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized
      localStorage.removeItem('auth_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ========== DEVICE MANAGEMENT ==========

export const deviceAPI = {
  // Get all devices
  getAll: (params) => api.get('/devices', { params }),

  // Get device by ID
  getById: (id) => api.get(`/devices/${id}`),

  // Create device
  create: (data) => api.post('/devices', data),

  // Update device
  update: (id, data) => api.put(`/devices/${id}`, data),

  // Delete device
  delete: (id) => api.delete(`/devices/${id}`),

  // Bulk import from CSV
  bulkImport: (file) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/devices/bulk-import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },

  // Test connectivity
  ping: (id) => api.post(`/devices/${id}/ping`),

  // Pull running config
  pullConfig: (id, credentials) =>
    api.post(`/devices/pull-config`, { ...credentials, device_id: id }),

  // Export to CSV
  exportCSV: () => api.get('/devices/export', { responseType: 'blob' }),
}

// ========== CONFIGURATION MANAGEMENT ==========

export const configAPI = {
  // Get config history for device
  getHistory: (deviceId) => api.get(`/devices/${deviceId}/configs`),

  // Get specific config version
  getVersion: (configId) => api.get(`/configs/${configId}`),

  // Create new config version
  create: (data) => api.post('/configs', data),

  // Compare two configs
  compare: (config1Id, config2Id) =>
    api.post('/configs/compare-detailed', {
      config_id_1: config1Id,
      config_id_2: config2Id,
    }),

  // Merge configs
  merge: (baseConfig, overlayConfig, strategy = 'overlay') =>
    api.post('/configs/merge', {
      base_config: baseConfig,
      overlay_config: overlayConfig,
      strategy,
    }),

  // Generate rollback config
  generateRollback: (targetConfig, currentConfig) =>
    api.post('/configs/rollback', {
      target_config: targetConfig,
      current_config: currentConfig,
    }),
}

// ========== DEPLOYMENT ==========

export const deploymentAPI = {
  // Deploy config to devices
  deploy: (deviceIds, configId, dryRun = false) =>
    api.post('/deploy', {
      device_ids: deviceIds,
      config_id: configId,
      dry_run: dryRun,
    }),

  // Get deployment status
  getStatus: (taskId) => api.get(`/deploy/status/${taskId}`),

  // Get deployment history
  getHistory: (params) => api.get('/deploy/history', { params }),

  // Get device deployment history
  getDeviceHistory: (deviceId) => api.get(`/devices/${deviceId}/deployments`),

  // Cancel deployment
  cancel: (taskId) => api.post(`/deploy/cancel/${taskId}`),

  // Rollback deployment
  rollback: (deploymentId) => api.post(`/deploy/rollback/${deploymentId}`),
}

// ========== VALIDATION & COMPLIANCE ==========

export const validationAPI = {
  // Validate configuration
  validate: (config, vendor = 'cisco') =>
    api.post('/validate/config', { config, vendor }),

  // Check compliance
  checkCompliance: (config, standards = ['pci_dss', 'hipaa']) =>
    api.post('/validate/compliance', { config, standards }),
}

// ========== AUDIT & HISTORY ==========

export const auditAPI = {
  // Get change history
  getHistory: (params) => api.get('/changes/history', { params }),

  // Get device history
  getDeviceHistory: (deviceId, params) =>
    api.get(`/changes/history/${deviceId}`, { params }),

  // Record change
  recordChange: (change) => api.post('/changes/record', change),
}

// ========== CONFIG GENERATION (LEGACY) ==========

export const generatorAPI = {
  // Generate config
  generate: (data) => api.post('/generate', data),

  // Validate schema
  validate: (data) => api.post('/validate', data),

  // Multi-vendor generation
  generateMulti: (vendors, config) =>
    api.post('/generate-multi', { vendors, config }),
}

export default api
