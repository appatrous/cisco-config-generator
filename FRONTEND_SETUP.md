# Frontend UI Setup Guide

## 🎨 New Management Interface

This guide explains how to set up and run the new React-based management interface that complements the existing configuration generator.

## ✨ New Features

### 1. **Device Inventory Dashboard** 📊
- Real-time device status monitoring (reachable/unreachable)
- Bulk CSV import functionality
- Advanced filtering (platform, status, location)
- Search by hostname, IP, or location
- Quick actions: Ping, Deploy, View History

### 2. **Deployment Interface** 🚀
- **Step 1**: Select multiple devices
- **Step 2**: Preview and validate configuration
- **Step 3**: Deploy with real-time progress tracking
- Dry-run mode for testing
- Live deployment logs
- Rollback capabilities

### 3. **Visual Diff Viewer** 🔄
- Side-by-side configuration comparison
- Syntax highlighting
- Risk assessment (CRITICAL/HIGH/MEDIUM/LOW)
- Change statistics (additions/deletions)
- Affected resources tracking (interfaces, VLANs, routing)

### 4. **Interactive Timeline** 📜
- Complete change history with visual timeline
- Filter by device, user, date range, action type
- Statistics dashboard (total changes, deployments, success/failed)
- Grouped by date with relative timestamps
- Detailed audit logs

## 📦 Installation

### Prerequisites

- Node.js 18+ and npm (or yarn)
- Python 3.8+ with Flask backend running

### Step 1: Install Frontend Dependencies

```bash
cd frontend
npm install
```

### Step 2: Start Backend API

In a separate terminal:

```bash
cd ..
python app_modern.py
```

The backend will run on `http://localhost:5000`

### Step 3: Start Frontend Development Server

```bash
cd frontend
npm run dev
```

The frontend will run on `http://localhost:3000` and proxy API requests to port 5000.

## 🌐 Accessing the Applications

- **New Management UI**: http://localhost:3000
- **Legacy Config Generator**: http://localhost:5000/modern
- **API Documentation**: http://localhost:5000/api

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│          Frontend (React + Vite)                │
│              Port 3000                          │
│                                                 │
│  ┌────────────┐  ┌─────────────┐  ┌──────────┐│
│  │ Dashboard  │  │ Deployment  │  │   Diff   ││
│  └────────────┘  └─────────────┘  └──────────┘│
│  ┌────────────┐  ┌─────────────┐              │
│  │  Timeline  │  │   Layout    │              │
│  └────────────┘  └─────────────┘              │
└───────────────────┬─────────────────────────────┘
                    │ HTTP/REST API
                    ↓
┌─────────────────────────────────────────────────┐
│          Backend (Flask + Extensions)           │
│              Port 5000                          │
│                                                 │
│  ┌────────────────┐  ┌──────────────────────┐  │
│  │  Device API    │  │  Deployment API      │  │
│  └────────────────┘  └──────────────────────┘  │
│  ┌────────────────┐  ┌──────────────────────┐  │
│  │  Config API    │  │  Validation API      │  │
│  └────────────────┘  └──────────────────────┘  │
│  ┌────────────────┐                            │
│  │  Audit API     │                            │
│  └────────────────┘                            │
└───────────────────┬─────────────────────────────┘
                    │
                    ↓
┌─────────────────────────────────────────────────┐
│       Core Services (Netmiko, NAPALM)           │
│                                                 │
│  • SSH Connection Management                   │
│  • Configuration Deployment                    │
│  • Backup & Rollback                           │
│  • Validation & Compliance                     │
└─────────────────────────────────────────────────┘
```

## 🔌 API Integration

The frontend automatically connects to the backend API. All API calls are proxied through Vite's dev server.

### Configuration

Edit `frontend/vite.config.js` if you need to change the API URL:

```javascript
export default defineConfig({
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  }
})
```

## 📚 Backend API Endpoints Used

### Device Management
- `GET /api/devices` - List all devices
- `POST /api/devices` - Create device
- `PUT /api/devices/{id}` - Update device
- `DELETE /api/devices/{id}` - Delete device
- `POST /api/devices/bulk-import` - Bulk import CSV
- `POST /api/devices/{id}/ping` - Test connectivity
- `POST /api/devices/pull-config` - Pull running config via SSH

### Configuration Management
- `GET /api/devices/{id}/configs` - Get config history
- `GET /api/configs/{id}` - Get specific config version
- `POST /api/configs` - Create new config
- `POST /api/configs/compare-detailed` - Compare two configs
- `POST /api/configs/merge` - Merge configurations
- `POST /api/configs/rollback` - Generate rollback config

### Deployment
- `POST /api/deploy` - Deploy config to devices
- `GET /api/deploy/status/{task_id}` - Get deployment status
- `GET /api/deploy/history` - Deployment history
- `POST /api/deploy/rollback/{id}` - Rollback deployment

### Validation & Compliance
- `POST /api/validate/config` - Validate configuration
- `POST /api/validate/compliance` - Check compliance

### Audit & History
- `GET /api/changes/history` - Get change history
- `GET /api/changes/history/{device_id}` - Device-specific history
- `POST /api/changes/record` - Record a change

## 🚀 Production Deployment

### Build for Production

```bash
cd frontend
npm run build
```

This creates optimized static files in `../static/dist/`

### Serve from Flask

The Flask backend can serve the built frontend:

```python
# app_modern.py (already configured)
@app.route('/')
def serve_frontend():
    return send_from_directory('static/dist', 'index.html')
```

### Environment Variables

Create `.env` in the frontend directory:

```env
VITE_API_BASE_URL=https://your-production-domain.com
```

## 🎨 Customization

### Theme Colors

Edit `frontend/src/main.jsx`:

```javascript
<ConfigProvider
  theme={{
    token: {
      colorPrimary: '#1890ff',  // Change primary color
      borderRadius: 6,           // Change border radius
    },
  }}
>
```

### Add New Pages

1. Create component in `frontend/src/components/YourFeature/`
2. Add route in `frontend/src/App.jsx`
3. Add menu item in `frontend/src/components/Layout/Sidebar.jsx`

## 🧪 Testing

### Run Frontend Tests

```bash
cd frontend
npm test
```

### Manual Testing Checklist

- [ ] Device inventory loads and displays correctly
- [ ] Bulk import CSV works
- [ ] Device ping functionality works
- [ ] Deployment wizard completes all steps
- [ ] Configuration validation shows results
- [ ] Diff viewer displays changes correctly
- [ ] Timeline loads history with filters
- [ ] All navigation links work

## 🐛 Troubleshooting

### Frontend won't start
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### API calls failing
- Check backend is running on port 5000
- Check browser console for CORS errors
- Verify API endpoints in Network tab

### Build errors
```bash
# Clear Vite cache
rm -rf frontend/node_modules/.vite
npm run dev
```

## 📖 Related Documentation

- [Main README](../README.md) - Project overview
- [API Documentation](../docs/api_spec.md) - Backend API specs
- [Architecture](../docs/architecture.md) - System architecture

## 💡 Tips

1. **Hot Reload**: Changes to React components auto-refresh
2. **DevTools**: Install React Developer Tools browser extension
3. **API Inspection**: Use browser Network tab to debug API calls
4. **State Management**: React Query handles caching and refetching
5. **Component Library**: Ant Design provides pre-built components

## 🤝 Contributing

When adding new features:

1. Create component in appropriate directory
2. Connect to API via `services/api.js`
3. Use React Query for data fetching
4. Follow existing code style
5. Update this documentation

---

**Built with ❤️ for Network Engineers**
