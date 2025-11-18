# Network Configuration Generator - Frontend UI

Modern React-based management interface for the Cisco Configuration Generator.

## Features

✅ **Device Inventory Dashboard**
- Real-time device status monitoring
- Bulk CSV import
- Advanced filtering and search
- Device connectivity testing

✅ **Configuration Deployment Interface**
- Multi-device deployment wizard
- Configuration preview and validation
- Dry-run testing
- Real-time deployment progress tracking
- Deployment logs viewer

✅ **Visual Diff Viewer**
- Side-by-side configuration comparison
- Syntax highlighting
- Risk assessment
- Affected resources tracking
- Change statistics

✅ **Interactive Timeline**
- Complete change history
- Filterable by device, user, date, action
- Visual timeline with statistics
- Detailed audit logs

## Tech Stack

- **React 18** - UI framework
- **Ant Design 5** - Component library
- **React Router 6** - Routing
- **React Query** - Data fetching and caching
- **Axios** - HTTP client
- **React Diff Viewer** - Configuration comparison
- **CodeMirror** - Code editor
- **Recharts** - Charts and visualizations
- **Day.js** - Date manipulation
- **Vite** - Build tool

## Installation

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# or with yarn
yarn install
```

## Development

```bash
# Start development server (runs on port 3000)
npm run dev

# The backend API should be running on port 5000
# Vite proxy will forward /api requests to http://localhost:5000
```

## Build for Production

```bash
# Build optimized production bundle
npm run build

# Output will be in ../static/dist/
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── Dashboard/          # Device inventory
│   │   │   ├── Dashboard.jsx
│   │   │   ├── InventoryTable.jsx
│   │   │   ├── BulkImport.jsx
│   │   │   └── AddDeviceModal.jsx
│   │   ├── Deployment/         # Deployment wizard
│   │   │   ├── DeploymentPage.jsx
│   │   │   ├── DeviceSelector.jsx
│   │   │   ├── ConfigPreview.jsx
│   │   │   └── DeploymentProgress.jsx
│   │   ├── Diff/              # Config comparison
│   │   │   ├── DiffPage.jsx
│   │   │   └── DiffViewer.jsx
│   │   ├── Timeline/          # Change history
│   │   │   ├── TimelinePage.jsx
│   │   │   └── HistoryTimeline.jsx
│   │   ├── Layout/            # App layout
│   │   │   ├── Header.jsx
│   │   │   ├── Sidebar.jsx
│   │   │   └── Footer.jsx
│   │   └── ConfigGenerator/   # Link to legacy UI
│   │       └── ConfigGeneratorPage.jsx
│   ├── services/
│   │   └── api.js             # API client
│   ├── styles/
│   │   └── main.css           # Global styles
│   ├── App.jsx                # Main app component
│   └── main.jsx               # Entry point
├── package.json
├── vite.config.js
└── index.html
```

## API Integration

The frontend connects to the Flask backend API running on port 5000.

### Available API Endpoints

**Device Management**
- `GET /api/devices` - List all devices
- `POST /api/devices` - Create device
- `POST /api/devices/bulk-import` - Bulk import from CSV
- `POST /api/devices/{id}/ping` - Test connectivity

**Configuration**
- `GET /api/devices/{id}/configs` - Get config history
- `POST /api/configs/compare-detailed` - Compare configs
- `POST /api/validate/config` - Validate configuration

**Deployment**
- `POST /api/deploy` - Deploy configuration
- `GET /api/deploy/history` - Deployment history

**Audit**
- `GET /api/changes/history` - Change history
- `GET /api/changes/history/{device_id}` - Device-specific history

## Environment Variables

Create a `.env` file in the frontend directory:

```env
VITE_API_BASE_URL=http://localhost:5000
```

## Browser Support

- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## Contributing

1. Follow React best practices
2. Use functional components with hooks
3. Keep components small and focused
4. Add PropTypes for component props
5. Write meaningful commit messages

## License

[Specify your license here]
