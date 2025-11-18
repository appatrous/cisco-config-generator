/**
 * Network Configuration Generator - Modern UI (FIXED VERSION)
 * Tile-based interface for protocol configuration with working forms
 */

const app = {
    data: {
        global: {
            hostname: 'router1'
        },
        l2: {},
        l3: {},
        vxlan: {},
        acls: {}
    },
    selectedVendor: 'ios',
    activeProtocols: new Set(),
    currentView: 'protocols'
};

// Protocol definitions with metadata
const protocols = {
    l2: {
        title: 'Layer 2',
        protocols: {
            vlans: {
                name: 'VLANs',
                icon: '🔷',
                description: 'VLAN configuration (802.1Q)',
                fields: ['vlans', 'trunks']
            },
            stp: {
                name: 'Spanning Tree',
                icon: '🌳',
                description: 'STP/RSTP/MSTP configuration',
                fields: ['stp']
            },
            lag: {
                name: 'Link Aggregation',
                icon: '🔗',
                description: 'LAG/LACP (802.1AX)',
                fields: ['lag']
            },
            mlag: {
                name: 'MLAG / vPC',
                icon: '⚡',
                description: 'Multi-chassis LAG',
                fields: ['mlag'],
                supported: ['nxos', 'eos', 'junos']
            },
            security: {
                name: 'L2 Security',
                icon: '🔒',
                description: 'Port Security, DHCP Snooping, DAI, 802.1X',
                fields: ['security']
            },
            discovery: {
                name: 'Discovery',
                icon: '📡',
                description: 'LLDP / CDP',
                fields: ['discovery']
            }
        }
    },
    l3: {
        title: 'Layer 3',
        protocols: {
            interfaces: {
                name: 'L3 Interfaces',
                icon: '🔌',
                description: 'Routed interfaces, SVIs, FHRP',
                fields: ['interfaces', 'vrfs']
            },
            static: {
                name: 'Static Routing',
                icon: '➡️',
                description: 'Static routes and PBR',
                fields: ['static_routes', 'pbr']
            },
            ospf: {
                name: 'OSPF',
                icon: '🦎',
                description: 'OSPFv2 / OSPFv3',
                fields: ['ospf']
            },
            isis: {
                name: 'IS-IS',
                icon: '🔺',
                description: 'IS-IS with SR support',
                fields: ['isis']
            },
            eigrp: {
                name: 'EIGRP',
                icon: '⚙️',
                description: 'EIGRP (Cisco)',
                supported: ['ios', 'nxos'],
                fields: ['eigrp']
            },
            bgp: {
                name: 'BGP',
                icon: '🌐',
                description: 'BGP with EVPN/RPKI',
                fields: ['bgp']
            },
            multicast: {
                name: 'Multicast',
                icon: '📻',
                description: 'PIM, IGMP/MLD, MSDP',
                fields: ['multicast']
            }
        }
    },
    advanced: {
        title: 'Advanced',
        protocols: {
            vxlan: {
                name: 'VXLAN / EVPN',
                icon: '☁️',
                description: 'Data Center fabric',
                fields: ['vxlan'],
                supported: ['nxos', 'eos', 'junos']
            },
            nat: {
                name: 'NAT',
                icon: '🔄',
                description: 'NAT/PAT/NAT64',
                fields: ['nat']
            },
            mpls: {
                name: 'MPLS',
                icon: '🏷️',
                description: 'MPLS / L3VPN',
                fields: ['mpls']
            },
            sr: {
                name: 'Segment Routing',
                icon: '🎯',
                description: 'SR-MPLS / SRv6',
                fields: ['segment_routing']
            },
            qos: {
                name: 'QoS',
                icon: '⚖️',
                description: 'Quality of Service',
                fields: ['qos']
            },
            bfd: {
                name: 'BFD',
                icon: '💓',
                description: 'Bidirectional Forwarding Detection',
                fields: ['bfd']
            }
        }
    }
};

// Initialize the app
function initApp() {
    renderVendorSelector();
    renderProtocolTiles();
    setupEventListeners();
    loadExample(); // Load default example
}

// Render vendor selector
function renderVendorSelector() {
    const vendors = [
        { id: 'ios', name: 'Cisco IOS/IOS-XE', icon: '🔵' },
        { id: 'nxos', name: 'Cisco NX-OS', icon: '🟦' },
        { id: 'eos', name: 'Arista EOS', icon: '🟩' },
        { id: 'junos', name: 'Juniper Junos', icon: '🟨' },
        { id: 'frr', name: 'FRRouting', icon: '🟧' }
    ];

    const container = document.getElementById('vendor-selector');
    container.innerHTML = vendors.map(v => `
        <button class="vendor-btn ${v.id === app.selectedVendor ? 'active' : ''}"
                data-vendor="${v.id}"
                onclick="selectVendor('${v.id}')">
            <span class="vendor-icon">${v.icon}</span>
            <span class="vendor-name">${v.name}</span>
        </button>
    `).join('');
}

// Select vendor
function selectVendor(vendor) {
    app.selectedVendor = vendor;
    renderVendorSelector();
    renderProtocolTiles();
}

// Render protocol tiles
function renderProtocolTiles() {
    const container = document.getElementById('protocol-tiles');
    let html = '';

    for (const [categoryKey, category] of Object.entries(protocols)) {
        html += `<div class="protocol-category">
            <h2>${category.title}</h2>
            <div class="tiles-grid">`;

        for (const [protocolKey, protocol] of Object.entries(category.protocols)) {
            const isSupported = !protocol.supported ||
                               protocol.supported.includes(app.selectedVendor);
            const isActive = app.activeProtocols.has(`${categoryKey}.${protocolKey}`);

            html += `
                <div class="protocol-tile ${isActive ? 'active' : ''} ${!isSupported ? 'disabled' : ''}"
                     data-protocol="${categoryKey}.${protocolKey}"
                     onclick="${isSupported ? `toggleProtocol('${categoryKey}.${protocolKey}')` : ''}">
                    <div class="tile-header">
                        <span class="tile-icon">${protocol.icon}</span>
                        <h3>${protocol.name}</h3>
                        ${isActive ? '<span class="active-badge">✓</span>' : ''}
                    </div>
                    <p class="tile-description">${protocol.description}</p>
                    ${!isSupported ? '<span class="unsupported-badge">Not supported on ' + app.selectedVendor.toUpperCase() + '</span>' : ''}
                </div>
            `;
        }

        html += `</div></div>`;
    }

    container.innerHTML = html;
}

// Toggle protocol activation
function toggleProtocol(protocolPath) {
    if (app.activeProtocols.has(protocolPath)) {
        app.activeProtocols.delete(protocolPath);
    } else {
        app.activeProtocols.add(protocolPath);
        showProtocolForm(protocolPath);
    }
    renderProtocolTiles();
    updateActiveProtocolsList();
}

// Show protocol configuration form
function showProtocolForm(protocolPath) {
    const [category, protocol] = protocolPath.split('.');
    const protocolData = protocols[category].protocols[protocol];

    document.getElementById('config-panel').style.display = 'block';
    document.getElementById('protocol-form-title').textContent =
        `${protocolData.icon} ${protocolData.name}`;

    const formContainer = document.getElementById('protocol-form-container');
    formContainer.innerHTML = generateForm(protocolPath, protocolData);
}

// Save form data to app.data
function saveFormData(protocolPath) {
    const [category, protocol] = protocolPath.split('.');

    // Collect form data based on protocol
    switch (protocol) {
        case 'vlans':
            saveVlanData();
            break;
        case 'ospf':
            saveOspfData();
            break;
        case 'bgp':
            saveBgpData();
            break;
        case 'interfaces':
            saveInterfacesData();
            break;
        case 'static':
            saveStaticRoutesData();
            break;
        default:
            alert(`Configuration form for ${protocol} needs implementation`);
    }

    alert(`✅ ${protocol.toUpperCase()} configuration saved!`);
}

// VLAN data functions
function addVlan() {
    if (!app.data.l2.vlans) app.data.l2.vlans = [];

    const vlanId = document.getElementById('vlan_id')?.value;
    const vlanName = document.getElementById('vlan_name')?.value;

    if (!vlanId || !vlanName) {
        alert('Please fill VLAN ID and Name');
        return;
    }

    app.data.l2.vlans.push({
        id: parseInt(vlanId),
        name: vlanName,
        state: 'active'
    });

    updateVlansList();
    document.getElementById('vlan_id').value = '';
    document.getElementById('vlan_name').value = '';
}

function updateVlansList() {
    const list = document.getElementById('vlans-list');
    if (!app.data.l2.vlans || app.data.l2.vlans.length === 0) {
        list.innerHTML = '<p class="empty-state">No VLANs configured</p>';
        return;
    }

    list.innerHTML = '<ul>' + app.data.l2.vlans.map((v, idx) => `
        <li>VLAN ${v.id} - ${v.name}
            <button class="btn-remove" onclick="removeVlan(${idx})">×</button>
        </li>
    `).join('') + '</ul>';
}

function removeVlan(index) {
    app.data.l2.vlans.splice(index, 1);
    updateVlansList();
}

function saveVlanData() {
    // Data already saved incrementally via addVlan
    console.log('VLANs saved:', app.data.l2.vlans);
}

// OSPF data functions
function saveOspfData() {
    if (!app.data.l3.ospf) app.data.l3.ospf = [];

    const processId = document.getElementById('ospf_process_id')?.value;
    const routerId = document.getElementById('ospf_router_id')?.value;
    const refBw = document.getElementById('ospf_ref_bw')?.value;
    const grEnabled = document.getElementById('ospf_gr')?.checked;

    const ospfConfig = {
        process_id: parseInt(processId) || 10,
        router_id: routerId || '',
        reference_bandwidth: parseInt(refBw) || 100000,
        graceful_restart: grEnabled || false,
        areas: [{id: '0.0.0.0', type: 'normal'}],
        interfaces: []
    };

    app.data.l3.ospf = [ospfConfig];
    console.log('OSPF saved:', app.data.l3.ospf);
}

// BGP data functions
function addBgpNeighbor() {
    if (!app.data.l3.bgp) {
        app.data.l3.bgp = {
            asn: parseInt(document.getElementById('bgp_asn')?.value) || 65000,
            router_id: document.getElementById('bgp_router_id')?.value || '',
            neighbors: []
        };
    }

    const ip = prompt('Neighbor IP:');
    const remoteAs = prompt('Remote AS:');

    if (ip && remoteAs) {
        app.data.l3.bgp.neighbors.push({
            ip: ip,
            remote_as: parseInt(remoteAs)
        });
        updateBgpNeighborsList();
    }
}

function updateBgpNeighborsList() {
    const list = document.getElementById('bgp-neighbors-list');
    if (!app.data.l3.bgp || !app.data.l3.bgp.neighbors || app.data.l3.bgp.neighbors.length === 0) {
        list.innerHTML = '<p class="empty-state">No neighbors configured</p>';
        return;
    }

    list.innerHTML = '<ul>' + app.data.l3.bgp.neighbors.map((n, idx) => `
        <li>${n.ip} (AS ${n.remote_as})
            <button class="btn-remove" onclick="removeBgpNeighbor(${idx})">×</button>
        </li>
    `).join('') + '</ul>';
}

function removeBgpNeighbor(index) {
    app.data.l3.bgp.neighbors.splice(index, 1);
    updateBgpNeighborsList();
}

function saveBgpData() {
    if (!app.data.l3.bgp) {
        app.data.l3.bgp = {};
    }

    app.data.l3.bgp.asn = parseInt(document.getElementById('bgp_asn')?.value) || 65000;
    app.data.l3.bgp.router_id = document.getElementById('bgp_router_id')?.value || '';

    console.log('BGP saved:', app.data.l3.bgp);
}

// Generate form HTML for protocol
function generateForm(protocolPath, protocolData) {
    const [category, protocol] = protocolPath.split('.');

    let html = `<div class="form-section">`;

    switch (protocol) {
        case 'vlans':
            html += `
                <h4>VLANs Configuration</h4>
                <div class="form-group">
                    <label>VLAN ID</label>
                    <input type="number" id="vlan_id" placeholder="10" min="1" max="4094">
                </div>
                <div class="form-group">
                    <label>VLAN Name</label>
                    <input type="text" id="vlan_name" placeholder="DATA">
                </div>
                <button class="btn-add" onclick="addVlan()">+ Add VLAN</button>
                <div id="vlans-list" style="margin-top: 1rem;"></div>
                <button class="btn btn-primary" onclick="saveFormData('${protocolPath}')" style="margin-top: 1rem; width: 100%;">
                    💾 Save VLAN Configuration
                </button>
            `;
            // Initialize list
            setTimeout(updateVlansList, 100);
            break;

        case 'ospf':
            html += `
                <h4>OSPF Configuration</h4>
                <div class="form-group">
                    <label>Process ID</label>
                    <input type="number" id="ospf_process_id" value="10" min="1" max="65535">
                </div>
                <div class="form-group">
                    <label>Router ID</label>
                    <input type="text" id="ospf_router_id" placeholder="1.1.1.1">
                </div>
                <div class="form-group">
                    <label>Reference Bandwidth (Mbps)</label>
                    <input type="number" id="ospf_ref_bw" value="100000" step="1000">
                </div>
                <details class="advanced-section">
                    <summary>Advanced Options</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="ospf_gr"> Graceful Restart</label>
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveFormData('${protocolPath}')" style="margin-top: 1rem; width: 100%;">
                    💾 Save OSPF Configuration
                </button>
            `;
            break;

        case 'bgp':
            html += `
                <h4>BGP Configuration</h4>
                <div class="form-group">
                    <label>AS Number</label>
                    <input type="number" id="bgp_asn" min="1" max="4294967295" placeholder="65000">
                </div>
                <div class="form-group">
                    <label>Router ID</label>
                    <input type="text" id="bgp_router_id" placeholder="1.1.1.1">
                </div>
                <h5>Neighbors</h5>
                <button class="btn-add" onclick="addBgpNeighbor()">+ Add Neighbor</button>
                <div id="bgp-neighbors-list" style="margin-top: 1rem;"></div>
                <button class="btn btn-primary" onclick="saveFormData('${protocolPath}')" style="margin-top: 1rem; width: 100%;">
                    💾 Save BGP Configuration
                </button>
            `;
            setTimeout(updateBgpNeighborsList, 100);
            break;

        case 'interfaces':
            html += `
                <h4>L3 Interfaces</h4>
                <p>Use JSON editor to configure interfaces (complex structure)</p>
                <button class="btn btn-secondary" onclick="openJsonEditor()">📝 Edit JSON</button>
            `;
            break;

        case 'static':
            html += `
                <h4>Static Routes</h4>
                <p>Use JSON editor to configure static routes</p>
                <button class="btn btn-secondary" onclick="openJsonEditor()">📝 Edit JSON</button>
            `;
            break;

        default:
            html += `
                <p>📝 Configuration form for ${protocolData.name}</p>
                <p class="help-text">Use JSON editor for advanced configuration or wait for form implementation.</p>
                <button class="btn btn-secondary" onclick="openJsonEditor()">📝 Edit JSON</button>
            `;
    }

    html += '</div>';
    return html;
}

// JSON Editor
function openJsonEditor() {
    const jsonStr = JSON.stringify(app.data, null, 2);
    const newJson = prompt('Edit configuration (JSON):', jsonStr);
    if (newJson) {
        try {
            app.data = JSON.parse(newJson);
            alert('✅ Configuration updated from JSON');
        } catch (e) {
            alert('❌ Invalid JSON: ' + e.message);
        }
    }
}

// Update active protocols list
function updateActiveProtocolsList() {
    const list = document.getElementById('active-protocols-list');
    if (app.activeProtocols.size === 0) {
        list.innerHTML = '<p class="empty-state">No protocols selected. Click on tiles to add.</p>';
        return;
    }

    let html = '<ul>';
    for (const protocolPath of app.activeProtocols) {
        const [category, protocol] = protocolPath.split('.');
        const protocolData = protocols[category].protocols[protocol];
        html += `
            <li>
                <span>${protocolData.icon} ${protocolData.name}</span>
                <button class="btn-remove" onclick="toggleProtocol('${protocolPath}')">×</button>
            </li>
        `;
    }
    html += '</ul>';
    list.innerHTML = html;
}

// Generate configuration
async function generateConfig() {
    const statusDiv = document.getElementById('generation-status');
    statusDiv.innerHTML = '<div class="spinner">⏳ Generating configuration...</div>';

    try {
        // Collect global data
        app.data.global = {
            hostname: document.getElementById('hostname')?.value || 'router1',
            domain_name: document.getElementById('domain_name')?.value || ''
        };

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vendor: app.selectedVendor,
                config: app.data
            })
        });

        const result = await response.json();

        if (response.ok && result.success) {
            showConfigPreview(result.config, result.validation, result.linting);
            statusDiv.innerHTML = '<div class="success">✅ Configuration generated successfully</div>';
        } else {
            statusDiv.innerHTML = `<div class="error">❌ Error: ${result.error || 'Unknown error'}</div>`;
            if (result.validation) {
                showValidationErrors(result.validation);
            }
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="error">❌ Network error: ${error.message}</div>`;
    }
}

// Show validation errors
function showValidationErrors(validation) {
    const validationDiv = document.getElementById('validation-results');
    let html = '';

    if (validation.errors && validation.errors.length > 0) {
        html += `<h4 class="error">❌ Errors (${validation.errors.length})</h4>`;
        html += '<ul>' + validation.errors.map(e => `<li>${e}</li>`).join('') + '</ul>';
    }

    if (validation.warnings && validation.warnings.length > 0) {
        html += `<h4 class="warning">⚠️ Warnings (${validation.warnings.length})</h4>`;
        html += '<ul>' + validation.warnings.map(w => `<li>${w}</li>`).join('') + '</ul>';
    }

    validationDiv.innerHTML = html || '<p>Validation info not available</p>';
}

// Show configuration preview
function showConfigPreview(config, validation, linting) {
    document.getElementById('preview-panel').style.display = 'block';
    document.getElementById('config-output').textContent = config;

    // Show validation results
    const validationDiv = document.getElementById('validation-results');
    if (validation.errors && validation.errors.length > 0) {
        validationDiv.innerHTML = `
            <h4 class="error">Errors (${validation.errors.length})</h4>
            <ul>${validation.errors.map(e => `<li>${e}</li>`).join('')}</ul>
        `;
    } else if (validation.warnings && validation.warnings.length > 0) {
        validationDiv.innerHTML = `
            <h4 class="warning">Warnings (${validation.warnings.length})</h4>
            <ul>${validation.warnings.map(w => `<li>${w}</li>`).join('')}</ul>
        `;
    } else {
        validationDiv.innerHTML = '<div class="success">✅ No validation issues</div>';
    }

    // Show linting results
    if (linting) {
        if (linting.errors && linting.errors.length > 0) {
            validationDiv.innerHTML += `
                <h4 class="error" style="margin-top: 1rem;">Linting Errors (${linting.errors.length})</h4>
                <ul>${linting.errors.map(e => `<li>${e}</li>`).join('')}</ul>
            `;
        } else if (linting.warnings && linting.warnings.length > 0) {
            validationDiv.innerHTML += `
                <h4 class="warning" style="margin-top: 1rem;">Linting Warnings (${linting.warnings.length})</h4>
                <ul>${linting.warnings.map(w => `<li>${w}</li>`).join('')}</ul>
            `;
        }
    }
}

// Download configuration
function downloadConfig() {
    const config = document.getElementById('config-output').textContent;
    const hostname = document.getElementById('hostname')?.value || 'router1';
    const blob = new Blob([config], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${hostname}_${app.selectedVendor}.cfg`;
    a.click();
    URL.revokeObjectURL(url);
}

// Copy to clipboard
function copyToClipboard() {
    const config = document.getElementById('config-output').textContent;
    navigator.clipboard.writeText(config).then(() => {
        alert('✅ Configuration copied to clipboard!');
    }).catch(err => {
        alert('❌ Failed to copy: ' + err);
    });
}

// Import JSON configuration
function importJson() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    input.onchange = e => {
        const file = e.target.files[0];
        const reader = new FileReader();
        reader.onload = event => {
            try {
                app.data = JSON.parse(event.target.result);
                alert('✅ Configuration imported successfully!');
                // Refresh active protocols based on loaded data
                app.activeProtocols.clear();
                if (app.data.l2 && app.data.l2.vlans) app.activeProtocols.add('l2.vlans');
                if (app.data.l3 && app.data.l3.ospf) app.activeProtocols.add('l3.ospf');
                if (app.data.l3 && app.data.l3.bgp) app.activeProtocols.add('l3.bgp');
                renderProtocolTiles();
                updateActiveProtocolsList();
            } catch (error) {
                alert('❌ Error parsing JSON: ' + error.message);
            }
        };
        reader.readAsText(file);
    };
    input.click();
}

// Export JSON configuration
function exportJson() {
    const json = JSON.stringify(app.data, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'network-config.json';
    a.click();
    URL.revokeObjectURL(url);
}

// Load example configuration
function loadExample() {
    app.activeProtocols.add('l2.vlans');
    app.activeProtocols.add('l3.ospf');
    app.activeProtocols.add('l3.bgp');

    app.data = {
        global: {
            hostname: 'campus-dist1',
            domain_name: 'example.com'
        },
        l2: {
            vlans: [
                { id: 10, name: 'DATA' },
                { id: 20, name: 'VOICE' },
                { id: 30, name: 'MGMT' }
            ]
        },
        l3: {
            ospf: [{
                process_id: 10,
                router_id: '1.1.1.1',
                reference_bandwidth: 100000,
                areas: [{ id: '0.0.0.0', type: 'normal' }],
                interfaces: []
            }],
            bgp: {
                asn: 65001,
                router_id: '1.1.1.1',
                neighbors: []
            }
        }
    };

    renderProtocolTiles();
    updateActiveProtocolsList();
}

// Setup event listeners
function setupEventListeners() {
    // Tab switching for preview
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            const tabId = btn.dataset.tab + '-tab';
            document.getElementById(tabId)?.classList.add('active');
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initApp);
