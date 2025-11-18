/**
 * Network Configuration Generator - Modern UI
 * Tile-based interface for protocol configuration
 */

const app = {
    data: {
        global: {},
        l2: {},
        l3: {},
        vxlan: {},
        acls: {},
        profiles: {}
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
                fields: ['mlag']
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
                supported: ['ios', 'nxos']
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
    renderProtocolTiles(); // Re-render to show/hide vendor-specific protocols
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

    // Generate form based on protocol
    const formContainer = document.getElementById('protocol-form-container');
    formContainer.innerHTML = generateForm(protocolPath, protocolData);
}

// Generate form HTML for protocol
function generateForm(protocolPath, protocolData) {
    // This is a simplified version - real implementation would be more comprehensive
    const [category, protocol] = protocolPath.split('.');

    let html = '<div class="form-section">';

    switch (protocol) {
        case 'vlans':
            html += `
                <h4>VLANs</h4>
                <button class="btn-add" onclick="addVlan()">+ Add VLAN</button>
                <div id="vlans-list"></div>
            `;
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
            `;
            break;

        case 'bgp':
            html += `
                <h4>BGP Configuration</h4>
                <div class="form-group">
                    <label>AS Number</label>
                    <input type="number" id="bgp_asn" min="1" max="4294967295">
                </div>
                <div class="form-group">
                    <label>Router ID</label>
                    <input type="text" id="bgp_router_id" placeholder="1.1.1.1">
                </div>
                <h5>Neighbors</h5>
                <button class="btn-add" onclick="addBgpNeighbor()">+ Add Neighbor</button>
                <div id="bgp-neighbors-list"></div>
            `;
            break;

        default:
            html += `<p>Configuration form for ${protocolData.name} coming soon...</p>`;
    }

    html += '</div>';
    return html;
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
        // Collect data from all active protocol forms
        const configData = {
            global: {
                hostname: document.getElementById('hostname')?.value || 'router1'
            },
            l2: {},
            l3: {}
        };

        const response = await fetch('/api/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                vendor: app.selectedVendor,
                config: configData
            })
        });

        const result = await response.json();

        if (response.ok) {
            showConfigPreview(result.config, result.validation);
            statusDiv.innerHTML = '<div class="success">✓ Configuration generated successfully</div>';
        } else {
            statusDiv.innerHTML = `<div class="error">✗ Error: ${result.error}</div>`;
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="error">✗ Network error: ${error.message}</div>`;
    }
}

// Show configuration preview
function showConfigPreview(config, validation) {
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
        validationDiv.innerHTML = '<div class="success">✓ No issues found</div>';
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
                alert('Configuration imported successfully!');
                // TODO: Update UI with imported data
            } catch (error) {
                alert('Error parsing JSON: ' + error.message);
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
    // Load a simple OSPF + VLAN example
    app.activeProtocols.add('l2.vlans');
    app.activeProtocols.add('l3.ospf');
    app.activeProtocols.add('l3.bgp');

    app.data = {
        global: {
            hostname: 'campus-dist1',
            domain_name: 'example.com',
            ntp_servers: ['10.0.0.1']
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
                areas: [{ id: '0.0.0.0', type: 'normal' }]
            }],
            bgp: {
                asn: 65001,
                router_id: '1.1.1.1'
            }
        }
    };

    renderProtocolTiles();
    updateActiveProtocolsList();
}

// Setup event listeners
function setupEventListeners() {
    // View switching
    document.querySelectorAll('[data-view]').forEach(btn => {
        btn.addEventListener('click', () => {
            app.currentView = btn.dataset.view;
            // Update active view
            document.querySelectorAll('.view').forEach(v => v.style.display = 'none');
            document.getElementById(app.currentView + '-view').style.display = 'block';
        });
    });
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initApp);
