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
            dcb: {
                name: 'Data Center Bridging',
                icon: '🏢',
                description: 'PFC, ETS, DCBX (lossless Ethernet)',
                fields: ['dcb'],
                supported: ['nxos', 'huawei']
            },
            erps: {
                name: 'Ring Protection',
                icon: '🔄',
                description: 'ERPS G.8032 / REP',
                fields: ['erps', 'rep']
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
            dmvpn: {
                name: 'DMVPN',
                icon: '🌐',
                description: 'Dynamic Multipoint VPN (Phase 1/2/3)',
                fields: ['tunnels'],
                supported: ['ios', 'huawei']
            },
            ipsec: {
                name: 'IPsec VPN',
                icon: '🔐',
                description: 'IKEv1/IKEv2, Crypto Maps, Profiles',
                fields: ['ipsec'],
                supported: ['ios', 'huawei']
            },
            lisp: {
                name: 'LISP Mobility',
                icon: '📍',
                description: 'Locator/ID Separation Protocol',
                fields: ['lisp'],
                supported: ['ios', 'huawei']
            },
            bgp_advanced: {
                name: 'BGP Advanced',
                icon: '🎯',
                description: 'Flowspec, BMP, BGP-LS, AIGP',
                fields: ['bgp.advanced']
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
                icon: '🛣️',
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
    },
    telemetry: {
        title: 'Telemetry & Monitoring',
        protocols: {
            netflow: {
                name: 'NetFlow / IPFIX',
                icon: '📊',
                description: 'Flow collection and export',
                fields: ['telemetry.netflow']
            },
            sflow: {
                name: 'sFlow',
                icon: '📈',
                description: 'sFlow sampling',
                fields: ['telemetry.sflow'],
                supported: ['nxos', 'eos', 'junos']
            },
            gnmi: {
                name: 'gNMI',
                icon: '📡',
                description: 'gRPC Network Management',
                fields: ['telemetry.gnmi']
            },
            netconf: {
                name: 'NETCONF / RESTCONF',
                icon: '🔧',
                description: 'YANG-based configuration',
                fields: ['telemetry.netconf']
            },
            ip_sla: {
                name: 'IP SLA',
                icon: '⏱️',
                description: 'Service Level Agreement monitoring',
                fields: ['monitoring.ip_sla'],
                supported: ['ios', 'nxos']
            },
            erspan: {
                name: 'ERSPAN',
                icon: '🔍',
                description: 'Encapsulated Remote SPAN',
                fields: ['monitoring.erspan']
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
        { id: 'huawei', name: 'Huawei VRP', icon: '🔴' },
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

// NEW: Save functions for additional protocols
function saveStpData() {
    if (!app.data.l2.stp) {
        app.data.l2.stp = {};
    }

    app.data.l2.stp.mode = document.getElementById('stp_mode')?.value || 'mst';
    app.data.l2.stp.root_priority = {
        global: parseInt(document.getElementById('stp_priority')?.value) || 32768
    };

    app.data.l2.stp.guards = {
        bpduguard_default: document.getElementById('stp_bpduguard')?.checked || false,
        loopguard_default: document.getElementById('stp_loopguard')?.checked || false
    };

    console.log('STP saved:', app.data.l2.stp);
    alert('✅ STP configuration saved!');
}

function saveLagData() {
    if (!app.data.l2.lag) {
        app.data.l2.lag = [];
    }

    const bundleId = parseInt(document.getElementById('lag_bundle_id')?.value);
    const mode = document.getElementById('lag_mode')?.value || 'lacp';
    const membersStr = document.getElementById('lag_members')?.value || '';

    if (!bundleId || !membersStr) {
        alert('❌ Please fill all required fields');
        return;
    }

    const members = membersStr.split(',').map(m => m.trim());

    app.data.l2.lag.push({
        bundle_id: bundleId,
        mode: mode,
        members: members,
        description: `Bundle ${bundleId}`
    });

    console.log('LAG saved:', app.data.l2.lag);
    alert('✅ LAG configuration saved!');

    // Clear form
    document.getElementById('lag_bundle_id').value = '';
    document.getElementById('lag_members').value = '';
}

function saveInterfaceData() {
    if (!app.data.l3.interfaces) {
        app.data.l3.interfaces = [];
    }

    const ifaceName = document.getElementById('iface_name')?.value;
    const ipv4 = document.getElementById('iface_ipv4')?.value;
    const description = document.getElementById('iface_description')?.value;
    const vrf = document.getElementById('iface_vrf')?.value;
    const shutdown = document.getElementById('iface_shutdown')?.checked;

    if (!ifaceName || !ipv4) {
        alert('❌ Interface name and IP address are required');
        return;
    }

    app.data.l3.interfaces.push({
        interface: ifaceName,
        ipv4: [{ address: ipv4 }],
        description: description,
        vrf: vrf || undefined,
        shutdown: shutdown
    });

    console.log('Interface saved:', app.data.l3.interfaces);
    alert('✅ Interface configuration saved!');

    // Clear form
    document.getElementById('iface_name').value = '';
    document.getElementById('iface_ipv4').value = '';
    document.getElementById('iface_description').value = '';
}

function saveStaticRouteData() {
    if (!app.data.l3.static_routes) {
        app.data.l3.static_routes = [];
    }

    const prefix = document.getElementById('route_prefix')?.value;
    const nextHop = document.getElementById('route_next_hop')?.value;
    const distance = document.getElementById('route_distance')?.value;

    if (!prefix || !nextHop) {
        alert('❌ Destination network and next hop are required');
        return;
    }

    app.data.l3.static_routes.push({
        prefix: prefix,
        next_hop: nextHop,
        distance: distance ? parseInt(distance) : undefined
    });

    console.log('Static route saved:', app.data.l3.static_routes);
    alert('✅ Static route saved!');

    // Clear form
    document.getElementById('route_prefix').value = '';
    document.getElementById('route_next_hop').value = '';
    document.getElementById('route_distance').value = '';
}

function saveIsisData() {
    if (!app.data.l3.isis) {
        app.data.l3.isis = [];
    }

    const tag = document.getElementById('isis_tag')?.value || '1';
    const net = document.getElementById('isis_net')?.value;
    const isType = document.getElementById('isis_is_type')?.value || 'level-1-2';

    if (!net) {
        alert('❌ NET address is required');
        return;
    }

    app.data.l3.isis.push({
        tag: tag,
        net: net,
        is_type: isType
    });

    console.log('IS-IS saved:', app.data.l3.isis);
    alert('✅ IS-IS configuration saved!');
}

function saveEigrpData() {
    if (!app.data.l3.eigrp) {
        app.data.l3.eigrp = [];
    }

    const asn = parseInt(document.getElementById('eigrp_asn')?.value);
    const routerId = document.getElementById('eigrp_router_id')?.value;

    if (!asn) {
        alert('❌ AS Number is required');
        return;
    }

    app.data.l3.eigrp.push({
        asn: asn,
        router_id: routerId
    });

    console.log('EIGRP saved:', app.data.l3.eigrp);
    alert('✅ EIGRP configuration saved!');
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

        case 'stp':
            html += `
                <h4>Spanning Tree Configuration</h4>
                <div class="form-group">
                    <label>Mode</label>
                    <select id="stp_mode">
                        <option value="mst">MST (802.1s)</option>
                        <option value="rapid-pvst">Rapid-PVST+ (Cisco)</option>
                        <option value="rstp">RSTP (802.1w)</option>
                        <option value="pvst">PVST+ (Cisco)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Priority</label>
                    <input type="number" id="stp_priority" value="32768" step="4096" min="0" max="61440">
                </div>
                <details class="advanced-section">
                    <summary>Advanced Options</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="stp_bpduguard"> BPDU Guard (default)</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="stp_loopguard"> Loop Guard (default)</label>
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveStpData()" style="width: 100%;">
                    💾 Save STP Configuration
                </button>
            `;
            break;

        case 'lag':
            html += `
                <h4>Link Aggregation (LAG/LACP)</h4>
                <div class="form-group">
                    <label>Bundle ID</label>
                    <input type="number" id="lag_bundle_id" min="1" max="255" placeholder="1">
                </div>
                <div class="form-group">
                    <label>Mode</label>
                    <select id="lag_mode">
                        <option value="lacp">LACP (active)</option>
                        <option value="on">Static (on)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Member Interfaces (comma-separated)</label>
                    <input type="text" id="lag_members" placeholder="GigabitEthernet0/1,GigabitEthernet0/2">
                </div>
                <button class="btn btn-primary" onclick="saveLagData()" style="width: 100%;">
                    💾 Save LAG Configuration
                </button>
            `;
            break;

        case 'interfaces':
            html += `
                <h4>L3 Interfaces Configuration</h4>
                <div class="form-group">
                    <label>Interface Name</label>
                    <input type="text" id="iface_name" placeholder="GigabitEthernet0/0">
                </div>
                <div class="form-group">
                    <label>IPv4 Address (CIDR)</label>
                    <input type="text" id="iface_ipv4" placeholder="192.168.1.1/24">
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <input type="text" id="iface_description" placeholder="WAN Link">
                </div>
                <details class="advanced-section">
                    <summary>Advanced Options</summary>
                    <div class="form-group">
                        <label>VRF Name</label>
                        <input type="text" id="iface_vrf" placeholder="MGMT">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="iface_shutdown"> Shutdown</label>
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveInterfaceData()" style="width: 100%;">
                    💾 Save Interface Configuration
                </button>
            `;
            break;

        case 'static':
            html += `
                <h4>Static Routes Configuration</h4>
                <div class="form-group">
                    <label>Destination Network (CIDR)</label>
                    <input type="text" id="route_prefix" placeholder="10.0.0.0/8">
                </div>
                <div class="form-group">
                    <label>Next Hop IP</label>
                    <input type="text" id="route_next_hop" placeholder="192.168.1.254">
                </div>
                <div class="form-group">
                    <label>Administrative Distance (optional)</label>
                    <input type="number" id="route_distance" min="1" max="255" placeholder="1">
                </div>
                <button class="btn btn-primary" onclick="saveStaticRouteData()" style="width: 100%;">
                    💾 Save Static Route
                </button>
            `;
            break;

        case 'isis':
            html += `
                <h4>IS-IS Configuration</h4>
                <div class="form-group">
                    <label>Process Tag</label>
                    <input type="text" id="isis_tag" placeholder="1" value="1">
                </div>
                <div class="form-group">
                    <label>NET Address</label>
                    <input type="text" id="isis_net" placeholder="49.0001.0000.0000.0001.00">
                </div>
                <div class="form-group">
                    <label>IS-Type</label>
                    <select id="isis_is_type">
                        <option value="level-1-2">Level-1-2</option>
                        <option value="level-1">Level-1</option>
                        <option value="level-2-only">Level-2 Only</option>
                    </select>
                </div>
                <button class="btn btn-primary" onclick="saveIsisData()" style="width: 100%;">
                    💾 Save IS-IS Configuration
                </button>
            `;
            break;

        case 'eigrp':
            html += `
                <h4>EIGRP Configuration</h4>
                <div class="form-group">
                    <label>AS Number</label>
                    <input type="number" id="eigrp_asn" min="1" max="65535" placeholder="100">
                </div>
                <div class="form-group">
                    <label>Router ID</label>
                    <input type="text" id="eigrp_router_id" placeholder="1.1.1.1">
                </div>
                <button class="btn btn-primary" onclick="saveEigrpData()" style="width: 100%;">
                    💾 Save EIGRP Configuration
                </button>
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
