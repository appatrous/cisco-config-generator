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
            },
            lacp_advanced: {
                name: 'LACP Advanced',
                icon: '🔗',
                description: 'Advanced LACP configuration (min-links, load-balance)',
                fields: ['lacp_advanced']
            },
            mst: {
                name: 'MST',
                icon: '🌲',
                description: 'Multiple Spanning Tree (802.1s)',
                fields: ['mst']
            },
            udld: {
                name: 'UDLD',
                icon: '🔍',
                description: 'UniDirectional Link Detection',
                fields: ['udld']
            },
            storm_control: {
                name: 'Storm Control',
                icon: '⛈️',
                description: 'Broadcast/Multicast/Unicast storm control',
                fields: ['storm_control']
            },
            flexlinks: {
                name: 'FlexLinks',
                icon: '🔄',
                description: 'Layer 2 backup links',
                fields: ['flexlinks']
            },
            stp_protection: {
                name: 'STP Protection',
                icon: '🛡️',
                description: 'PortFast, BPDU Guard, Root Guard, Loop Guard',
                fields: ['stp_protection']
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
            },
            route_maps: {
                name: 'Route Maps',
                icon: '🗺️',
                description: 'Route-map match/set conditions',
                fields: ['route_maps']
            },
            prefix_lists: {
                name: 'Prefix Lists',
                icon: '📋',
                description: 'IP/IPv6 prefix filtering',
                fields: ['prefix_lists']
            },
            vrf_lite: {
                name: 'VRF-Lite',
                icon: '🔀',
                description: 'VRF without MPLS, route leaking',
                fields: ['vrf_lite']
            },
            ipv6_advanced: {
                name: 'IPv6 Advanced',
                icon: '🌐',
                description: 'DHCPv6, SLAAC, ND, First-Hop Security',
                fields: ['ipv6_advanced']
            },
            route_filtering: {
                name: 'Route Filtering',
                icon: '🚦',
                description: 'Distribute-lists for OSPF/EIGRP/BGP',
                fields: ['route_filtering']
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
            },
            flexvpn: {
                name: 'FlexVPN',
                icon: '🔐',
                description: 'IKEv2-based VPN (Hub-Spoke)',
                fields: ['flexvpn'],
                supported: ['ios']
            },
            getvpn: {
                name: 'GET VPN',
                icon: '🔒',
                description: 'Group Encrypted Transport VPN',
                fields: ['getvpn'],
                supported: ['ios']
            },
            l2tpv3: {
                name: 'L2TPv3',
                icon: '🌐',
                description: 'Layer 2 Tunneling Protocol v3',
                fields: ['l2tpv3']
            },
            otv: {
                name: 'OTV',
                icon: '☁️',
                description: 'Overlay Transport Virtualization',
                fields: ['otv'],
                supported: ['nxos']
            },
            sdwan: {
                name: 'SD-WAN',
                icon: '🛰️',
                description: 'SD-WAN (Viptela/Meraki)',
                fields: ['sdwan']
            }
        }
    },
    security: {
        title: 'Security',
        protocols: {
            copp: {
                name: 'Control Plane Policing',
                icon: '🛡️',
                description: 'CoPP for DoS protection',
                fields: ['copp']
            },
            iacls: {
                name: 'Infrastructure ACLs',
                icon: '🔐',
                description: 'Management plane protection (iACLs)',
                fields: ['iacls']
            },
            ipv6_acls: {
                name: 'IPv6 ACLs',
                icon: '🌐',
                description: 'IPv6 Access Control Lists',
                fields: ['ipv6_acls']
            },
            time_based_acls: {
                name: 'Time-based ACLs',
                icon: '⏰',
                description: 'Time-range based access control',
                fields: ['time_based_acls']
            },
            trustsec: {
                name: 'TrustSec',
                icon: '🏷️',
                description: 'CTS/SGT Software-Defined Segmentation',
                fields: ['trustsec'],
                supported: ['ios', 'nxos']
            },
            nbar: {
                name: 'NBAR2 / AVC',
                icon: '🔍',
                description: 'Application Visibility and Control',
                fields: ['nbar'],
                supported: ['ios']
            }
        }
    },
    management: {
        title: 'Management',
        protocols: {
            ssh: {
                name: 'SSH Configuration',
                icon: '🔑',
                description: 'SSH server settings and algorithms',
                fields: ['ssh']
            },
            lines: {
                name: 'Console / VTY',
                icon: '💻',
                description: 'Console and VTY line configuration',
                fields: ['lines']
            },
            banners: {
                name: 'Banners',
                icon: '📢',
                description: 'Login, MOTD, Exec banners',
                fields: ['banners']
            },
            archive: {
                name: 'Archive / Rollback',
                icon: '💾',
                description: 'Configuration archive and rollback',
                fields: ['archive']
            },
            smart_licensing: {
                name: 'Smart Licensing',
                icon: '📜',
                description: 'Cisco Smart Licensing',
                fields: ['smart_licensing'],
                supported: ['ios', 'nxos']
            },
            dns: {
                name: 'DNS Client',
                icon: '🌐',
                description: 'DNS client configuration',
                fields: ['dns']
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

function saveDmvpnData() {
    if (!app.data.l3.tunnels) {
        app.data.l3.tunnels = [];
    }

    const tunnelId = parseInt(document.getElementById('dmvpn_tunnel_id')?.value);
    const phase = document.getElementById('dmvpn_phase')?.value;
    const source = document.getElementById('dmvpn_source')?.value;
    const ip = document.getElementById('dmvpn_ip')?.value;

    if (!tunnelId && tunnelId !== 0) {
        alert('❌ Tunnel ID is required');
        return;
    }
    if (!phase || !source || !ip) {
        alert('❌ All required fields must be filled');
        return;
    }

    const dmvpnConfig = {
        tunnel_id: tunnelId,
        mode: 'gre-multipoint',
        source: source
    };

    // Description and VRF
    const description = document.getElementById('dmvpn_description')?.value;
    if (description) dmvpnConfig.description = description;

    const vrf = document.getElementById('dmvpn_vrf')?.value;
    if (vrf) dmvpnConfig.vrf = vrf;

    // Destination (for P2P tunnels)
    const destination = document.getElementById('dmvpn_destination')?.value;
    if (destination) dmvpnConfig.destination = destination;

    // IP Addresses
    dmvpnConfig.ipv4 = [{ address: ip }];

    const ipv6 = document.getElementById('dmvpn_ipv6')?.value;
    if (ipv6) {
        dmvpnConfig.ipv6 = [{ address: ipv6 }];
    }

    // Tunnel key
    const tunnelKey = document.getElementById('dmvpn_tunnel_key')?.value;
    if (tunnelKey) dmvpnConfig.key = parseInt(tunnelKey);

    // MTU and bandwidth
    const mtu = document.getElementById('dmvpn_mtu')?.value;
    if (mtu) dmvpnConfig.mtu = parseInt(mtu);

    const tcpMss = document.getElementById('dmvpn_tcp_mss')?.value;
    if (tcpMss) dmvpnConfig.tcp_mss = parseInt(tcpMss);

    const bandwidth = document.getElementById('dmvpn_bandwidth')?.value;
    if (bandwidth) dmvpnConfig.bandwidth = parseInt(bandwidth);

    // Keepalive
    const keepaliveInterval = document.getElementById('dmvpn_keepalive_interval')?.value;
    const keepaliveRetries = document.getElementById('dmvpn_keepalive_retries')?.value;
    if (keepaliveInterval || keepaliveRetries) {
        dmvpnConfig.keepalive = {
            interval: parseInt(keepaliveInterval) || 10,
            retries: parseInt(keepaliveRetries) || 3
        };
    }

    // NHRP Configuration
    dmvpnConfig.nhrp = {
        enabled: true,
        network_id: parseInt(document.getElementById('dmvpn_nhrp_network_id')?.value) || 1
    };

    const nhrpAuth = document.getElementById('dmvpn_nhrp_auth')?.value;
    if (nhrpAuth) dmvpnConfig.nhrp.authentication = nhrpAuth;

    const holdtime = document.getElementById('dmvpn_nhrp_holdtime')?.value;
    if (holdtime) dmvpnConfig.nhrp.holdtime = parseInt(holdtime);

    const regTimeout = document.getElementById('dmvpn_registration_timeout')?.value;
    if (regTimeout) dmvpnConfig.nhrp.registration_timeout = parseInt(regTimeout);

    // DMVPN Phase 2/3 features
    if (parseInt(phase) >= 2) {
        dmvpnConfig.nhrp.shortcut = document.getElementById('dmvpn_nhrp_shortcut')?.checked || false;
    }
    if (parseInt(phase) === 3) {
        dmvpnConfig.nhrp.redirect = document.getElementById('dmvpn_nhrp_redirect')?.checked || false;
    }

    // IPsec Profile
    const ipsecProfile = document.getElementById('dmvpn_ipsec_profile')?.value;
    if (ipsecProfile) dmvpnConfig.ipsec_profile = ipsecProfile;

    // QoS settings
    const tosReflect = document.getElementById('dmvpn_tos_reflect')?.checked;
    const tosValue = document.getElementById('dmvpn_tos_value')?.value;
    const dscp = document.getElementById('dmvpn_dscp')?.value;

    if (tosReflect || tosValue || dscp) {
        dmvpnConfig.qos = {};
        if (tosReflect) dmvpnConfig.qos.tos_reflect = true;
        if (tosValue) dmvpnConfig.qos.tos_value = parseInt(tosValue);
        if (dscp) dmvpnConfig.qos.dscp = dscp;
    }

    // Routing protocols
    const ospfEnabled = document.getElementById('dmvpn_ospf_enabled')?.checked;
    const eigrpEnabled = document.getElementById('dmvpn_eigrp_enabled')?.checked;

    if (ospfEnabled || eigrpEnabled) {
        dmvpnConfig.routing = {};

        if (ospfEnabled) {
            const ospfProcess = document.getElementById('dmvpn_ospf_process')?.value;
            const ospfArea = document.getElementById('dmvpn_ospf_area')?.value;
            if (ospfProcess && ospfArea) {
                dmvpnConfig.routing.ospf = {
                    process_id: parseInt(ospfProcess),
                    area: ospfArea,
                    network_type: document.getElementById('dmvpn_ospf_network_type')?.value || 'point-to-point'
                };
                const ospfCost = document.getElementById('dmvpn_ospf_cost')?.value;
                if (ospfCost) dmvpnConfig.routing.ospf.cost = parseInt(ospfCost);
            }
        }

        if (eigrpEnabled) {
            const eigrpAsn = document.getElementById('dmvpn_eigrp_asn')?.value;
            if (eigrpAsn) {
                dmvpnConfig.routing.eigrp = {
                    asn: parseInt(eigrpAsn),
                    split_horizon: !document.getElementById('dmvpn_eigrp_split_horizon')?.checked
                };
            }
        }
    }

    // Multicast
    const pimEnabled = document.getElementById('dmvpn_pim_enabled')?.checked;
    if (pimEnabled) {
        dmvpnConfig.multicast = {
            pim_mode: document.getElementById('dmvpn_pim_mode')?.value || 'sparse-mode',
            pim_nbma_mode: document.getElementById('dmvpn_pim_nbma')?.checked || false
        };
    }

    app.data.l3.tunnels.push(dmvpnConfig);
    console.log('DMVPN saved:', app.data.l3.tunnels);
    alert('✅ DMVPN configuration saved!');
}

function saveIpsecData() {
    if (!app.data.l3.ipsec) {
        app.data.l3.ipsec = { crypto_maps: [], ikev2_profiles: [], transform_sets: [] };
    }

    const mapName = document.getElementById('ipsec_map_name')?.value;
    const sequence = parseInt(document.getElementById('ipsec_sequence')?.value);
    const peer = document.getElementById('ipsec_peer')?.value;
    const psk = document.getElementById('ipsec_psk')?.value;

    if (!mapName || !sequence || !peer || !psk) {
        alert('❌ All required fields must be filled');
        return;
    }

    const ipsecConfig = {
        crypto_map: {
            name: mapName,
            sequence: sequence,
            peer: peer
        },
        ikev2_profile: {
            version: parseInt(document.getElementById('ipsec_ike_version')?.value) || 2,
            encryption: document.getElementById('ipsec_ike_encryption')?.value || 'aes-256',
            hash: document.getElementById('ipsec_ike_hash')?.value || 'sha256',
            dh_group: parseInt(document.getElementById('ipsec_ike_dh')?.value) || 14,
            lifetime: parseInt(document.getElementById('ipsec_ike_lifetime')?.value) || 86400,
            psk: psk
        },
        transform_set: {
            name: document.getElementById('ipsec_transform_name')?.value || 'ESP-AES256-SHA256',
            esp_encryption: document.getElementById('ipsec_esp_encryption')?.value || 'esp-aes-256',
            esp_auth: document.getElementById('ipsec_esp_auth')?.value || 'esp-sha256-hmac',
            lifetime: parseInt(document.getElementById('ipsec_sa_lifetime')?.value) || 3600,
            pfs: document.getElementById('ipsec_pfs')?.checked || false,
            pfs_group: parseInt(document.getElementById('ipsec_pfs_group')?.value) || 14
        },
        acl: {
            source_network: document.getElementById('ipsec_src_network')?.value || '',
            destination_network: document.getElementById('ipsec_dst_network')?.value || ''
        }
    };

    if (!app.data.l3.ipsec.crypto_maps) app.data.l3.ipsec.crypto_maps = [];
    app.data.l3.ipsec.crypto_maps.push(ipsecConfig);
    console.log('IPsec saved:', app.data.l3.ipsec);
    alert('✅ IPsec configuration saved!');
}

function saveVxlanData() {
    if (!app.data.vxlan) {
        app.data.vxlan = {};
    }

    app.data.vxlan.enabled = document.getElementById('vxlan_enabled')?.checked || false;
    app.data.vxlan.source_interface = document.getElementById('vxlan_source')?.value || '';
    app.data.vxlan.multicast_group = document.getElementById('vxlan_mcast')?.value || '';

    app.data.vxlan.evpn = {
        enabled: document.getElementById('vxlan_evpn_enabled')?.checked || false,
        rd: document.getElementById('vxlan_rd')?.value || 'auto',
        rt: document.getElementById('vxlan_rt')?.value || '',
        anycast_gateway: document.getElementById('vxlan_anycast_gateway')?.checked || false,
        anycast_mac: document.getElementById('vxlan_anycast_mac')?.value || ''
    };

    console.log('VXLAN saved:', app.data.vxlan);
    alert('✅ VXLAN configuration saved!');
}

function saveBgpAdvancedData() {
    if (!app.data.l3.bgp) {
        app.data.l3.bgp = {};
    }
    if (!app.data.l3.bgp.advanced) {
        app.data.l3.bgp.advanced = {};
    }

    app.data.l3.bgp.advanced.flowspec = {
        enabled: document.getElementById('bgp_flowspec_enabled')?.checked || false,
        validation: document.getElementById('bgp_flowspec_validation')?.value || 'local'
    };

    app.data.l3.bgp.advanced.bmp = {
        enabled: document.getElementById('bgp_bmp_enabled')?.checked || false,
        servers: [{
            ip: document.getElementById('bgp_bmp_server')?.value || '',
            port: parseInt(document.getElementById('bgp_bmp_port')?.value) || 5000
        }],
        monitoring: {
            route_monitoring: document.getElementById('bgp_bmp_route_monitoring')?.checked || false,
            stats_reporting: document.getElementById('bgp_bmp_stats_reporting')?.checked || false
        }
    };

    app.data.l3.bgp.advanced.link_state = {
        enabled: document.getElementById('bgp_ls_enabled')?.checked || false,
        redistribute: {
            ospf: document.getElementById('bgp_ls_redistribute_ospf')?.checked || false,
            isis: document.getElementById('bgp_ls_redistribute_isis')?.checked || false
        }
    };

    app.data.l3.bgp.advanced.aigp = {
        enabled: document.getElementById('bgp_aigp_enabled')?.checked || false
    };

    app.data.l3.bgp.advanced.orr = {
        enabled: document.getElementById('bgp_orr_enabled')?.checked || false
    };

    app.data.l3.bgp.advanced.graceful_shutdown = {
        enabled: document.getElementById('bgp_graceful_shutdown')?.checked || false
    };

    app.data.l3.bgp.advanced.additional = {
        add_path: document.getElementById('bgp_add_path')?.checked || false,
        diverse_path: {
            max_paths: parseInt(document.getElementById('bgp_max_paths')?.value) || 8
        }
    };

    console.log('BGP Advanced saved:', app.data.l3.bgp.advanced);
    alert('✅ BGP Advanced configuration saved!');
}

function saveNetflowData() {
    if (!app.data.l3.telemetry) {
        app.data.l3.telemetry = { enabled: true };
    }
    if (!app.data.l3.telemetry.netflow) {
        app.data.l3.telemetry.netflow = {};
    }

    const exporterName = document.getElementById('netflow_exporter_name')?.value;
    const collectorIp = document.getElementById('netflow_collector_ip')?.value;

    if (!exporterName || !collectorIp) {
        alert('❌ Exporter name and collector IP are required');
        return;
    }

    app.data.l3.telemetry.netflow = {
        enabled: document.getElementById('netflow_enabled')?.checked || false,
        exporters: [{
            name: exporterName,
            destination: collectorIp,
            port: parseInt(document.getElementById('netflow_collector_port')?.value) || 9995,
            source: document.getElementById('netflow_source')?.value || ''
        }],
        monitors: [{
            name: document.getElementById('netflow_monitor_name')?.value || 'FLOW-MONITOR-1',
            record: document.getElementById('netflow_record')?.value || 'netflow-original',
            exporter: exporterName,
            cache_timeout: {
                active: parseInt(document.getElementById('netflow_cache_active')?.value) || 60,
                inactive: parseInt(document.getElementById('netflow_cache_inactive')?.value) || 15
            }
        }],
        samplers: [{
            name: document.getElementById('netflow_sampler_name')?.value || '',
            rate: parseInt(document.getElementById('netflow_sampling_rate')?.value) || 1000
        }]
    };

    console.log('NetFlow saved:', app.data.l3.telemetry.netflow);
    alert('✅ NetFlow configuration saved!');
}

function saveSflowData() {
    if (!app.data.l3.telemetry) {
        app.data.l3.telemetry = { enabled: true };
    }

    const collectorIp = document.getElementById('sflow_collector_ip')?.value;

    if (!collectorIp) {
        alert('❌ Collector IP is required');
        return;
    }

    app.data.l3.telemetry.sflow = {
        enabled: document.getElementById('sflow_enabled')?.checked || false,
        collectors: [{
            name: 'COLLECTOR-1',
            ip: collectorIp,
            port: parseInt(document.getElementById('sflow_collector_port')?.value) || 6343
        }],
        agent_address: document.getElementById('sflow_agent_ip')?.value || '',
        sampling_rate: parseInt(document.getElementById('sflow_sampling_rate')?.value) || 4096,
        counter_poll_interval: parseInt(document.getElementById('sflow_counter_poll')?.value) || 20
    };

    console.log('sFlow saved:', app.data.l3.telemetry.sflow);
    alert('✅ sFlow configuration saved!');
}

function saveGnmiData() {
    if (!app.data.l3.telemetry) {
        app.data.l3.telemetry = { enabled: true };
    }

    app.data.l3.telemetry.gnmi = {
        enabled: document.getElementById('gnmi_enabled')?.checked || false,
        port: parseInt(document.getElementById('gnmi_port')?.value) || 57400,
        secure_server: document.getElementById('gnmi_secure')?.checked || false,
        certificate: document.getElementById('gnmi_certificate')?.value || '',
        subscriptions: [{
            id: parseInt(document.getElementById('gnmi_sub_id')?.value) || 100,
            encoding: document.getElementById('gnmi_encoding')?.value || 'encode-kvgpb',
            receivers: [{
                ip: document.getElementById('gnmi_receiver_ip')?.value || '',
                port: parseInt(document.getElementById('gnmi_receiver_port')?.value) || 57500
            }],
            interval: parseInt(document.getElementById('gnmi_interval')?.value) || 30000
        }]
    };

    console.log('gNMI saved:', app.data.l3.telemetry.gnmi);
    alert('✅ gNMI configuration saved!');
}

function saveNetconfData() {
    if (!app.data.l3.telemetry) {
        app.data.l3.telemetry = { enabled: true };
    }

    app.data.l3.telemetry.netconf = {
        enabled: document.getElementById('netconf_enabled')?.checked || false,
        ssh_port: parseInt(document.getElementById('netconf_port')?.value) || 830,
        acl: document.getElementById('netconf_acl')?.value || ''
    };

    app.data.l3.telemetry.restconf = {
        enabled: document.getElementById('restconf_enabled')?.checked || false,
        port: parseInt(document.getElementById('restconf_port')?.value) || 443,
        acl: document.getElementById('restconf_acl')?.value || ''
    };

    console.log('NETCONF/RESTCONF saved:', app.data.l3.telemetry);
    alert('✅ NETCONF/RESTCONF configuration saved!');
}

function saveIpSlaData() {
    if (!app.data.l3.monitoring) {
        app.data.l3.monitoring = { enabled: true };
    }
    if (!app.data.l3.monitoring.ip_sla) {
        app.data.l3.monitoring.ip_sla = { enabled: true, probes: [] };
    }

    const id = parseInt(document.getElementById('ipsla_id')?.value);
    const type = document.getElementById('ipsla_type')?.value;
    const target = document.getElementById('ipsla_target')?.value;

    if (!id || !type || !target) {
        alert('❌ SLA ID, type, and target are required');
        return;
    }

    const probe = {
        id: id,
        type: type,
        target: target,
        source: document.getElementById('ipsla_source')?.value || '',
        frequency: parseInt(document.getElementById('ipsla_frequency')?.value) || 60,
        timeout: parseInt(document.getElementById('ipsla_timeout')?.value) || 5000,
        threshold: parseInt(document.getElementById('ipsla_threshold')?.value) || 100,
        vrf: document.getElementById('ipsla_vrf')?.value || '',
        tos: parseInt(document.getElementById('ipsla_tos')?.value) || 0,
        schedule: {
            start_time: document.getElementById('ipsla_start')?.value || 'now',
            life: document.getElementById('ipsla_life')?.value || 'forever',
            recurring: document.getElementById('ipsla_recurring')?.checked || false
        }
    };

    app.data.l3.monitoring.ip_sla.probes.push(probe);
    console.log('IP SLA saved:', app.data.l3.monitoring.ip_sla);
    alert('✅ IP SLA configuration saved!');
}

function saveErspanData() {
    if (!app.data.l3.monitoring) {
        app.data.l3.monitoring = { enabled: true };
    }
    if (!app.data.l3.monitoring.erspan) {
        app.data.l3.monitoring.erspan = { enabled: true, sessions: [] };
    }

    const sessionId = parseInt(document.getElementById('erspan_session_id')?.value);
    const erspanId = parseInt(document.getElementById('erspan_id')?.value);
    const destIp = document.getElementById('erspan_dest_ip')?.value;

    if (!sessionId || !erspanId || !destIp) {
        alert('❌ Session ID, ERSPAN ID, and destination IP are required');
        return;
    }

    const session = {
        id: sessionId,
        erspan_id: erspanId,
        destination_ip: destIp,
        origin_ip: document.getElementById('erspan_origin_ip')?.value || '',
        sources: [{
            type: document.getElementById('erspan_source_type')?.value || 'interface',
            interface: document.getElementById('erspan_source')?.value || '',
            direction: document.getElementById('erspan_direction')?.value || 'both'
        }],
        vrf: document.getElementById('erspan_vrf')?.value || 'default',
        ttl: parseInt(document.getElementById('erspan_ttl')?.value) || 255,
        dscp: parseInt(document.getElementById('erspan_dscp')?.value) || 0,
        mtu: parseInt(document.getElementById('erspan_mtu')?.value) || 1500
    };

    app.data.l3.monitoring.erspan.sessions.push(session);
    console.log('ERSPAN saved:', app.data.l3.monitoring.erspan);
    alert('✅ ERSPAN configuration saved!');
}

function saveLispData() {
    if (!app.data.l3.lisp) {
        app.data.l3.lisp = {};
    }

    app.data.l3.lisp = {
        enabled: document.getElementById('lisp_enabled')?.checked || false,
        instance_id: parseInt(document.getElementById('lisp_instance_id')?.value) || 0,
        role: document.getElementById('lisp_role')?.value || 'xtr',
        eid: {
            prefix: document.getElementById('lisp_eid_prefix')?.value || '',
            rloc: {
                address: document.getElementById('lisp_rloc')?.value || '',
                priority: parseInt(document.getElementById('lisp_rloc_priority')?.value) || 1,
                weight: parseInt(document.getElementById('lisp_rloc_weight')?.value) || 100
            }
        },
        map_server: document.getElementById('lisp_map_server')?.value || '',
        map_resolver: document.getElementById('lisp_map_resolver')?.value || '',
        authentication_key: document.getElementById('lisp_auth_key')?.value || ''
    };

    console.log('LISP saved:', app.data.l3.lisp);
    alert('✅ LISP configuration saved!');
}

function saveNatData() {
    if (!app.data.l3.nat) {
        app.data.l3.nat = {};
    }

    const natType = document.getElementById('nat_type')?.value;

    if (!natType) {
        alert('❌ NAT type is required');
        return;
    }

    app.data.l3.nat = {
        type: natType,
        inside_interface: document.getElementById('nat_inside_if')?.value || '',
        outside_interface: document.getElementById('nat_outside_if')?.value || '',
        pool: {
            name: document.getElementById('nat_pool_name')?.value || '',
            start: document.getElementById('nat_pool_start')?.value || '',
            end: document.getElementById('nat_pool_end')?.value || '',
            netmask: document.getElementById('nat_pool_netmask')?.value || ''
        },
        static_mappings: [{
            inside_local: document.getElementById('nat_inside_local')?.value || '',
            inside_global: document.getElementById('nat_inside_global')?.value || ''
        }]
    };

    console.log('NAT saved:', app.data.l3.nat);
    alert('✅ NAT configuration saved!');
}

function saveMplsData() {
    if (!app.data.l3.mpls) {
        app.data.l3.mpls = {};
    }

    app.data.l3.mpls = {
        enabled: document.getElementById('mpls_enabled')?.checked || false,
        ldp_router_id: document.getElementById('mpls_ldp_router_id')?.value || '',
        l3vpn: {
            vrf_name: document.getElementById('mpls_vrf_name')?.value || '',
            rd: document.getElementById('mpls_rd')?.value || '',
            rt_export: document.getElementById('mpls_rt_export')?.value || '',
            rt_import: document.getElementById('mpls_rt_import')?.value || ''
        },
        te: {
            enabled: document.getElementById('mpls_te_enabled')?.checked || false,
            tunnel_interface: document.getElementById('mpls_te_tunnel')?.value || '',
            bandwidth: parseInt(document.getElementById('mpls_te_bandwidth')?.value) || 0
        }
    };

    console.log('MPLS saved:', app.data.l3.mpls);
    alert('✅ MPLS configuration saved!');
}

function saveSrData() {
    if (!app.data.l3.segment_routing) {
        app.data.l3.segment_routing = {};
    }

    const srType = document.getElementById('sr_type')?.value || 'sr-mpls';

    app.data.l3.segment_routing = {
        enabled: document.getElementById('sr_enabled')?.checked || false,
        type: srType
    };

    if (srType === 'sr-mpls') {
        app.data.l3.segment_routing.sr_mpls = {
            srgb_start: parseInt(document.getElementById('sr_srgb_start')?.value) || 16000,
            srgb_end: parseInt(document.getElementById('sr_srgb_end')?.value) || 23999,
            node_sid: parseInt(document.getElementById('sr_node_sid')?.value) || 100
        };
    } else if (srType === 'srv6') {
        app.data.l3.segment_routing.srv6 = {
            locator_name: document.getElementById('srv6_locator_name')?.value || '',
            locator_prefix: document.getElementById('srv6_locator_prefix')?.value || '',
            behavior: document.getElementById('srv6_behavior')?.value || 'end'
        };
    }

    console.log('Segment Routing saved:', app.data.l3.segment_routing);
    alert('✅ Segment Routing configuration saved!');
}

function saveQosData() {
    if (!app.data.l3.qos) {
        app.data.l3.qos = { policies: [] };
    }

    const policyName = document.getElementById('qos_policy_name')?.value;

    if (!policyName) {
        alert('❌ Policy name is required');
        return;
    }

    const policy = {
        name: policyName,
        classes: [{
            name: document.getElementById('qos_class_name')?.value || 'class-default',
            match_dscp: document.getElementById('qos_match_dscp')?.value || '',
            priority_bandwidth: parseInt(document.getElementById('qos_priority_bw')?.value) || 0,
            police: {
                rate: parseInt(document.getElementById('qos_police_rate')?.value) || 0,
                burst: parseInt(document.getElementById('qos_police_burst')?.value) || 0
            },
            shape_rate: parseInt(document.getElementById('qos_shape_rate')?.value) || 0,
            queue_limit: parseInt(document.getElementById('qos_queue_limit')?.value) || 64,
            random_detect: document.getElementById('qos_random_detect')?.value || ''
        }]
    };

    app.data.l3.qos.policies.push(policy);
    console.log('QoS saved:', app.data.l3.qos);
    alert('✅ QoS configuration saved!');
}

function saveBfdData() {
    if (!app.data.l3.bfd) {
        app.data.l3.bfd = {};
    }

    app.data.l3.bfd = {
        enabled: document.getElementById('bfd_enabled')?.checked || false,
        interval: parseInt(document.getElementById('bfd_interval')?.value) || 50,
        multiplier: parseInt(document.getElementById('bfd_multiplier')?.value) || 3,
        template: {
            name: document.getElementById('bfd_template_name')?.value || '',
            echo_mode: document.getElementById('bfd_echo_mode')?.value || 'disabled',
            authentication: document.getElementById('bfd_authentication')?.checked || false
        }
    };

    console.log('BFD saved:', app.data.l3.bfd);
    alert('✅ BFD configuration saved!');
}

function saveSecurityData() {
    if (!app.data.l2.security) {
        app.data.l2.security = {};
    }

    // Port Security
    const portSecurity = {
        enabled: document.getElementById('security_port_security')?.checked || false,
        default_max_macs: parseInt(document.getElementById('security_max_macs')?.value) || 2,
        violation_action: document.getElementById('security_violation')?.value || 'restrict',
        sticky: document.getElementById('security_port_sticky')?.checked || false
    };

    const agingTime = document.getElementById('security_port_aging_time')?.value;
    if (agingTime) portSecurity.aging_time = parseInt(agingTime);

    const agingType = document.getElementById('security_port_aging_type')?.value;
    if (agingType) portSecurity.aging_type = agingType;

    // DHCP Snooping
    const dhcpSnooping = {
        enabled: document.getElementById('security_dhcp_snooping')?.checked || false
    };

    const dhcpVlans = document.getElementById('security_dhcp_vlans')?.value;
    if (dhcpVlans) {
        dhcpSnooping.vlans = dhcpVlans.split(',').map(v => v.trim()).filter(v => v);
    }

    const dhcpTrusted = document.getElementById('security_dhcp_trusted')?.value;
    if (dhcpTrusted) {
        dhcpSnooping.trusted_interfaces = dhcpTrusted.split(',').map(i => i.trim()).filter(i => i);
    }

    dhcpSnooping.verify_mac = document.getElementById('security_dhcp_verify_mac')?.checked || false;

    dhcpSnooping.option_82 = {
        enabled: document.getElementById('security_dhcp_option82')?.checked || false
    };

    const rateLimit = document.getElementById('security_dhcp_rate_limit')?.value;
    if (rateLimit) dhcpSnooping.rate_limit = parseInt(rateLimit);

    const dbEnabled = document.getElementById('security_dhcp_database')?.checked;
    if (dbEnabled) {
        dhcpSnooping.database = {
            persistent: true,
            file: document.getElementById('security_dhcp_database_file')?.value || 'flash:dhcp_snooping.db'
        };
    }

    // DAI (Dynamic ARP Inspection)
    const dai = {
        enabled: document.getElementById('security_dai')?.checked || false
    };

    const daiVlans = document.getElementById('security_dai_vlans')?.value;
    if (daiVlans) {
        dai.vlans = daiVlans.split(',').map(v => v.trim()).filter(v => v);
    }

    const daiTrusted = document.getElementById('security_dai_trusted')?.value;
    if (daiTrusted) {
        dai.trusted_interfaces = daiTrusted.split(',').map(i => i.trim()).filter(i => i);
    }

    dai.validate = {
        src_mac: document.getElementById('security_dai_validate_src_mac')?.checked || false,
        dst_mac: document.getElementById('security_dai_validate_dst_mac')?.checked || false,
        ip: document.getElementById('security_dai_validate_ip')?.checked || false
    };

    const arpAcl = document.getElementById('security_dai_arp_acl')?.value;
    if (arpAcl) dai.arp_acl = arpAcl;

    const daiRateLimit = document.getElementById('security_dai_rate_limit')?.value;
    if (daiRateLimit) dai.rate_limit = parseInt(daiRateLimit);

    // 802.1X
    const dot1x = {
        enabled: document.getElementById('security_dot1x')?.checked || false,
        system_auth_control: document.getElementById('security_dot1x_system_auth')?.checked || false,
        mab: document.getElementById('security_dot1x_mab')?.checked || false
    };

    const reauthInterval = document.getElementById('security_dot1x_reauth')?.value;
    if (reauthInterval) dot1x.reauth_interval = parseInt(reauthInterval);

    const quietPeriod = document.getElementById('security_dot1x_quiet')?.value;
    if (quietPeriod) dot1x.quiet_period = parseInt(quietPeriod);

    const txPeriod = document.getElementById('security_dot1x_tx_period')?.value;
    if (txPeriod) dot1x.tx_period = parseInt(txPeriod);

    const maxReauth = document.getElementById('security_dot1x_max_reauth')?.value;
    if (maxReauth) dot1x.max_reauth_req = parseInt(maxReauth);

    const guestVlan = document.getElementById('security_dot1x_guest_vlan')?.value;
    if (guestVlan) dot1x.guest_vlan = parseInt(guestVlan);

    const criticalVlan = document.getElementById('security_dot1x_critical_vlan')?.value;
    if (criticalVlan) dot1x.critical_vlan = parseInt(criticalVlan);

    // IP Source Guard
    const ipsg = {
        enabled: document.getElementById('security_ipsg')?.checked || false
    };

    const ipsgInterfaces = document.getElementById('security_ipsg_interfaces')?.value;
    if (ipsgInterfaces) {
        ipsg.bindings = ipsgInterfaces.split(',').map(iface => ({
            interface: iface.trim(),
            enabled: true
        })).filter(b => b.interface);
    }

    // MACsec
    const macsec = {
        enabled: document.getElementById('security_macsec')?.checked || false
    };

    const macsecPolicy = document.getElementById('security_macsec_policy')?.value;
    if (macsecPolicy) macsec.policy = macsecPolicy;

    const macsecCipher = document.getElementById('security_macsec_cipher')?.value;
    if (macsecCipher) macsec.cipher_suite = macsecCipher;

    const macsecInterfaces = document.getElementById('security_macsec_interfaces')?.value;
    if (macsecInterfaces) {
        macsec.per_interface = macsecInterfaces.split(',').map(iface => ({
            interface: iface.trim(),
            enabled: true
        })).filter(i => i.interface);
    }

    app.data.l2.security = {
        port_security: portSecurity,
        dhcp_snooping: dhcpSnooping,
        dai: dai,
        dot1x: dot1x,
        ipsg: ipsg,
        macsec: macsec
    };

    console.log('Security saved:', app.data.l2.security);
    alert('✅ L2 Security configuration saved!');
}

function saveDcbData() {
    if (!app.data.l2.dcb) {
        app.data.l2.dcb = {};
    }

    app.data.l2.dcb = {
        enabled: document.getElementById('dcb_enabled')?.checked || false,
        pfc: {
            enabled: document.getElementById('dcb_pfc_enabled')?.checked || false,
            priorities: document.getElementById('dcb_pfc_priorities')?.value || ''
        },
        ets: {
            enabled: document.getElementById('dcb_ets_enabled')?.checked || false,
            tc0_bandwidth: parseInt(document.getElementById('dcb_ets_tc0')?.value) || 25,
            tc1_bandwidth: parseInt(document.getElementById('dcb_ets_tc1')?.value) || 25,
            tc2_bandwidth: parseInt(document.getElementById('dcb_ets_tc2')?.value) || 25,
            tc3_bandwidth: parseInt(document.getElementById('dcb_ets_tc3')?.value) || 25
        },
        dcbx: {
            version: document.getElementById('dcb_dcbx_version')?.value || 'ieee'
        }
    };

    console.log('DCB saved:', app.data.l2.dcb);
    alert('✅ DCB configuration saved!');
}

function saveErpsData() {
    if (!app.data.l2.erps) {
        app.data.l2.erps = { rings: [] };
    }

    const ringId = parseInt(document.getElementById('erps_ring_id')?.value);
    const controlVlan = parseInt(document.getElementById('erps_control_vlan')?.value);

    if (!ringId || !controlVlan) {
        alert('❌ Ring ID and Control VLAN are required');
        return;
    }

    const ring = {
        enabled: document.getElementById('erps_enabled')?.checked || false,
        ring_id: ringId,
        control_vlan: controlVlan,
        port0: document.getElementById('erps_port0')?.value || '',
        port1: document.getElementById('erps_port1')?.value || '',
        rpl_role: document.getElementById('erps_rpl_role')?.value || 'none',
        guard_timer: parseInt(document.getElementById('erps_guard_timer')?.value) || 500,
        holdoff_timer: parseInt(document.getElementById('erps_holdoff_timer')?.value) || 0,
        wtr_timer: parseInt(document.getElementById('erps_wtr_timer')?.value) || 300
    };

    app.data.l2.erps.rings.push(ring);
    console.log('ERPS saved:', app.data.l2.erps);
    alert('✅ ERPS configuration saved!');
}

function saveDiscoveryData() {
    if (!app.data.l2.discovery) {
        app.data.l2.discovery = {};
    }

    app.data.l2.discovery = {
        lldp: {
            enabled: document.getElementById('lldp_enabled')?.checked || true,
            timer: parseInt(document.getElementById('lldp_timer')?.value) || 30,
            holdtime: parseInt(document.getElementById('lldp_holdtime')?.value) || 120,
            med: document.getElementById('lldp_med')?.checked || false
        },
        cdp: {
            enabled: document.getElementById('cdp_enabled')?.checked || false,
            timer: parseInt(document.getElementById('cdp_timer')?.value) || 60,
            holdtime: parseInt(document.getElementById('cdp_holdtime')?.value) || 180
        }
    };

    console.log('Discovery saved:', app.data.l2.discovery);
    alert('✅ Discovery protocols configuration saved!');
}

function saveMlagData() {
    if (!app.data.l2.mlag) {
        app.data.l2.mlag = {};
    }

    const domainId = parseInt(document.getElementById('mlag_domain_id')?.value);

    if (!domainId) {
        alert('❌ Domain ID is required');
        return;
    }

    app.data.l2.mlag = {
        enabled: document.getElementById('mlag_enabled')?.checked || false,
        domain_id: domainId,
        keepalive: {
            destination: document.getElementById('mlag_keepalive_ip')?.value || '',
            source: document.getElementById('mlag_keepalive_src')?.value || '',
            vrf: document.getElementById('mlag_keepalive_vrf')?.value || ''
        },
        peer_link: document.getElementById('mlag_peer_link')?.value || '',
        role: document.getElementById('mlag_role')?.value || 'primary',
        peer_gateway: document.getElementById('mlag_peer_gateway')?.checked || false,
        peer_switch: document.getElementById('mlag_peer_switch')?.checked || false,
        anycast_vtep: document.getElementById('mlag_anycast_vtep')?.checked || false
    };

    console.log('MLAG saved:', app.data.l2.mlag);
    alert('✅ MLAG/vPC configuration saved!');
}

function saveMulticastData() {
    if (!app.data.l3.multicast) {
        app.data.l3.multicast = {};
    }

    app.data.l3.multicast = {
        pim: {
            enabled: document.getElementById('multicast_pim_enabled')?.checked || false,
            mode: document.getElementById('multicast_pim_mode')?.value || 'sparse-mode',
            rp_address: document.getElementById('multicast_rp_address')?.value || ''
        },
        igmp: {
            version: parseInt(document.getElementById('multicast_igmp_version')?.value) || 3,
            snooping: {
                enabled: document.getElementById('multicast_igmp_snooping')?.checked || false,
                vlans: document.getElementById('multicast_igmp_vlans')?.value || ''
            }
        },
        msdp: {
            enabled: document.getElementById('multicast_msdp')?.checked || false,
            peer: document.getElementById('multicast_msdp_peer')?.value || ''
        },
        ssm: {
            enabled: document.getElementById('multicast_ssm')?.checked || false,
            range: document.getElementById('multicast_ssm_range')?.value || '232.0.0.0/8'
        }
    };

    console.log('Multicast saved:', app.data.l3.multicast);
    alert('✅ Multicast configuration saved!');
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

        case 'dmvpn':
            html += `
                <h4>DMVPN Configuration</h4>
                <div class="form-group">
                    <label>Tunnel ID</label>
                    <input type="number" id="dmvpn_tunnel_id" min="0" max="9999" placeholder="0" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <input type="text" id="dmvpn_description" placeholder="DMVPN Tunnel to Branch">
                </div>
                <div class="form-group">
                    <label>DMVPN Phase</label>
                    <select id="dmvpn_phase" required>
                        <option value="">Select Phase...</option>
                        <option value="1">Phase 1 (Hub-and-Spoke)</option>
                        <option value="2">Phase 2 (Spoke-to-Spoke)</option>
                        <option value="3">Phase 3 (Hierarchical)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>VRF Name</label>
                    <input type="text" id="dmvpn_vrf" placeholder="MGMT">
                </div>
                <div class="form-group">
                    <label>Tunnel Source</label>
                    <input type="text" id="dmvpn_source" placeholder="GigabitEthernet0/0 or IP address" required>
                </div>
                <div class="form-group">
                    <label>Tunnel Destination (for P2P)</label>
                    <input type="text" id="dmvpn_destination" placeholder="1.1.1.1">
                </div>
                <div class="form-group">
                    <label>Tunnel IPv4 Address (CIDR)</label>
                    <input type="text" id="dmvpn_ip" placeholder="10.0.0.1/24" required>
                </div>
                <div class="form-group">
                    <label>Tunnel IPv6 Address</label>
                    <input type="text" id="dmvpn_ipv6" placeholder="2001:db8::1/64">
                </div>
                <details class="advanced-section">
                    <summary>NHRP Configuration</summary>
                    <div class="form-group">
                        <label>NHRP Network ID</label>
                        <input type="number" id="dmvpn_nhrp_network_id" placeholder="1">
                    </div>
                    <div class="form-group">
                        <label>NHRP Authentication</label>
                        <input type="text" id="dmvpn_nhrp_auth" placeholder="secret123">
                    </div>
                    <div class="form-group">
                        <label>NHRP Holdtime (seconds)</label>
                        <input type="number" id="dmvpn_nhrp_holdtime" placeholder="600">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="dmvpn_nhrp_shortcut"> Enable NHRP Shortcut (Phase 2/3)</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="dmvpn_nhrp_redirect"> Enable NHRP Redirect (Phase 3)</label>
                    </div>
                    <div class="form-group">
                        <label>NHRP NHS Server IP (Hub only)</label>
                        <input type="text" id="dmvpn_nhs_ip" placeholder="10.0.0.1">
                    </div>
                    <div class="form-group">
                        <label>NHRP Registration Timeout</label>
                        <input type="number" id="dmvpn_registration_timeout" placeholder="60">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Tunnel Advanced Settings</summary>
                    <div class="form-group">
                        <label>Tunnel Key</label>
                        <input type="number" id="dmvpn_tunnel_key" placeholder="100">
                    </div>
                    <div class="form-group">
                        <label>MTU</label>
                        <input type="number" id="dmvpn_mtu" placeholder="1400">
                    </div>
                    <div class="form-group">
                        <label>TCP MSS</label>
                        <input type="number" id="dmvpn_tcp_mss" placeholder="1360">
                    </div>
                    <div class="form-group">
                        <label>Bandwidth (kbps)</label>
                        <input type="number" id="dmvpn_bandwidth" placeholder="1000">
                    </div>
                    <div class="form-group">
                        <label>Keepalive Interval (seconds)</label>
                        <input type="number" id="dmvpn_keepalive_interval" placeholder="10">
                    </div>
                    <div class="form-group">
                        <label>Keepalive Retries</label>
                        <input type="number" id="dmvpn_keepalive_retries" placeholder="3">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>IPsec & QoS Settings</summary>
                    <div class="form-group">
                        <label>IPsec Profile Name</label>
                        <input type="text" id="dmvpn_ipsec_profile" placeholder="IPSEC-PROFILE">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="dmvpn_tos_reflect"> TOS Reflect</label>
                    </div>
                    <div class="form-group">
                        <label>TOS Value</label>
                        <input type="number" id="dmvpn_tos_value" placeholder="0" min="0" max="255">
                    </div>
                    <div class="form-group">
                        <label>DSCP Value</label>
                        <input type="text" id="dmvpn_dscp" placeholder="ef">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Routing Protocol on Tunnel</summary>
                    <div class="form-group">
                        <label>Enable OSPF on Tunnel</label>
                        <input type="checkbox" id="dmvpn_ospf_enabled">
                    </div>
                    <div class="form-group">
                        <label>OSPF Process ID</label>
                        <input type="number" id="dmvpn_ospf_process" placeholder="1">
                    </div>
                    <div class="form-group">
                        <label>OSPF Area</label>
                        <input type="text" id="dmvpn_ospf_area" placeholder="0">
                    </div>
                    <div class="form-group">
                        <label>OSPF Network Type</label>
                        <select id="dmvpn_ospf_network_type">
                            <option value="point-to-point">Point-to-Point</option>
                            <option value="broadcast">Broadcast</option>
                            <option value="point-to-multipoint">Point-to-Multipoint</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>OSPF Cost</label>
                        <input type="number" id="dmvpn_ospf_cost" placeholder="100">
                    </div>
                    <div class="form-group">
                        <label>Enable EIGRP on Tunnel</label>
                        <input type="checkbox" id="dmvpn_eigrp_enabled">
                    </div>
                    <div class="form-group">
                        <label>EIGRP ASN</label>
                        <input type="number" id="dmvpn_eigrp_asn" placeholder="100">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="dmvpn_eigrp_split_horizon"> Disable EIGRP Split Horizon</label>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Multicast Settings</summary>
                    <div class="form-group">
                        <label>Enable PIM</label>
                        <input type="checkbox" id="dmvpn_pim_enabled">
                    </div>
                    <div class="form-group">
                        <label>PIM Mode</label>
                        <select id="dmvpn_pim_mode">
                            <option value="sparse-mode">Sparse Mode</option>
                            <option value="dense-mode">Dense Mode</option>
                            <option value="sparse-dense-mode">Sparse-Dense Mode</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="dmvpn_pim_nbma"> Enable PIM NBMA Mode</label>
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveDmvpnData()" style="width: 100%;">
                    💾 Save DMVPN Configuration
                </button>
            `;
            break;

        case 'ipsec':
            html += `
                <h4>IPsec VPN Configuration</h4>
                <div class="form-group">
                    <label>Crypto Map Name</label>
                    <input type="text" id="ipsec_map_name" placeholder="CRYPTO-MAP" required>
                </div>
                <div class="form-group">
                    <label>Description</label>
                    <input type="text" id="ipsec_map_description" placeholder="Site-to-Site VPN to Branch">
                </div>
                <div class="form-group">
                    <label>Sequence Number</label>
                    <input type="number" id="ipsec_sequence" min="1" max="65535" placeholder="10" required>
                </div>
                <div class="form-group">
                    <label>Peer IP Address</label>
                    <input type="text" id="ipsec_peer" placeholder="203.0.113.1" required>
                </div>
                <div class="form-group">
                    <label>Interface to Apply Crypto Map</label>
                    <input type="text" id="ipsec_interface" placeholder="GigabitEthernet0/0">
                </div>
                <div class="form-group">
                    <label>Pre-Shared Key</label>
                    <input type="password" id="ipsec_psk" placeholder="Enter PSK" required>
                </div>
                <div class="form-group">
                    <label><input type="checkbox" id="ipsec_reverse_route"> Enable Reverse Route Injection</label>
                </div>
                <details class="advanced-section">
                    <summary>IKE Configuration</summary>
                    <div class="form-group">
                        <label>IKE Version</label>
                        <select id="ipsec_ike_version">
                            <option value="2">IKEv2 (Recommended)</option>
                            <option value="1">IKEv1</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>IKEv2 Profile Name</label>
                        <input type="text" id="ipsec_ikev2_profile_name" placeholder="IKEV2-PROFILE">
                    </div>
                    <div class="form-group">
                        <label>IKEv2 Keyring Name</label>
                        <input type="text" id="ipsec_ikev2_keyring" placeholder="IKEV2-KEYRING">
                    </div>
                    <div class="form-group">
                        <label>Match FVRF</label>
                        <input type="text" id="ipsec_match_fvrf" placeholder="any">
                    </div>
                    <div class="form-group">
                        <label>IKE Encryption</label>
                        <select id="ipsec_ike_encryption">
                            <option value="aes-256">AES-256</option>
                            <option value="aes-192">AES-192</option>
                            <option value="aes-128">AES-128</option>
                            <option value="3des">3DES</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>IKE Hash</label>
                        <select id="ipsec_ike_hash">
                            <option value="sha512">SHA-512</option>
                            <option value="sha256">SHA-256</option>
                            <option value="sha1">SHA-1</option>
                            <option value="md5">MD5</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>PRF (Pseudo-Random Function)</label>
                        <select id="ipsec_ike_prf">
                            <option value="sha512">SHA-512</option>
                            <option value="sha384">SHA-384</option>
                            <option value="sha256">SHA-256</option>
                            <option value="sha1">SHA-1</option>
                            <option value="md5">MD5</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>IKE DH Group</label>
                        <select id="ipsec_ike_dh">
                            <option value="21">Group 21 (521-bit ECC)</option>
                            <option value="20">Group 20 (384-bit ECC)</option>
                            <option value="19">Group 19 (256-bit ECC)</option>
                            <option value="16">Group 16 (4096-bit)</option>
                            <option value="15">Group 15 (3072-bit)</option>
                            <option value="14">Group 14 (2048-bit)</option>
                            <option value="5">Group 5 (1536-bit)</option>
                            <option value="2">Group 2 (1024-bit)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>IKE Lifetime (seconds)</label>
                        <input type="number" id="ipsec_ike_lifetime" placeholder="86400">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Dead Peer Detection (DPD)</summary>
                    <div class="form-group">
                        <label>DPD Interval (seconds)</label>
                        <input type="number" id="ipsec_dpd_interval" placeholder="10" min="2" max="3600">
                    </div>
                    <div class="form-group">
                        <label>DPD Retries</label>
                        <input type="number" id="ipsec_dpd_retries" placeholder="3" min="2" max="60">
                    </div>
                    <div class="form-group">
                        <label>DPD Action on Failure</label>
                        <select id="ipsec_dpd_action">
                            <option value="clear">Clear (Recommended)</option>
                            <option value="restart">Restart</option>
                        </select>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>IPsec Transform Set</summary>
                    <div class="form-group">
                        <label>Transform Set Name</label>
                        <input type="text" id="ipsec_transform_name" placeholder="ESP-AES256-SHA256">
                    </div>
                    <div class="form-group">
                        <label>ESP Encryption</label>
                        <select id="ipsec_esp_encryption">
                            <option value="esp-aes-256-gcm">ESP-AES-256-GCM</option>
                            <option value="esp-aes-256">ESP-AES-256</option>
                            <option value="esp-aes-192">ESP-AES-192</option>
                            <option value="esp-aes-128-gcm">ESP-AES-128-GCM</option>
                            <option value="esp-aes-128">ESP-AES-128</option>
                            <option value="esp-3des">ESP-3DES</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>ESP Authentication</label>
                        <select id="ipsec_esp_auth">
                            <option value="esp-sha512-hmac">ESP-SHA512-HMAC</option>
                            <option value="esp-sha256-hmac">ESP-SHA256-HMAC</option>
                            <option value="esp-sha-hmac">ESP-SHA-HMAC</option>
                            <option value="esp-md5-hmac">ESP-MD5-HMAC</option>
                            <option value="">None (for GCM modes)</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Transform Mode</label>
                        <select id="ipsec_transform_mode">
                            <option value="tunnel">Tunnel (Recommended)</option>
                            <option value="transport">Transport</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>IPsec Lifetime (seconds)</label>
                        <input type="number" id="ipsec_sa_lifetime" placeholder="3600">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="ipsec_pfs"> Perfect Forward Secrecy (PFS)</label>
                    </div>
                    <div class="form-group">
                        <label>PFS DH Group</label>
                        <select id="ipsec_pfs_group">
                            <option value="21">Group 21 (521-bit ECC)</option>
                            <option value="20">Group 20 (384-bit ECC)</option>
                            <option value="19">Group 19 (256-bit ECC)</option>
                            <option value="16">Group 16</option>
                            <option value="14">Group 14</option>
                            <option value="5">Group 5</option>
                        </select>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Global IPsec Settings</summary>
                    <div class="form-group">
                        <label>Fragmentation</label>
                        <select id="ipsec_fragmentation">
                            <option value="before-encryption">Before Encryption (Recommended)</option>
                            <option value="after-encryption">After Encryption</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>DF-Bit Policy</label>
                        <select id="ipsec_df_bit">
                            <option value="clear">Clear DF-bit</option>
                            <option value="copy">Copy DF-bit</option>
                            <option value="set">Set DF-bit</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="ipsec_nat_transparency"> Enable NAT Transparency (NAT-T)</label>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Traffic Selectors (ACL)</summary>
                    <div class="form-group">
                        <label>Source Network</label>
                        <input type="text" id="ipsec_src_network" placeholder="192.168.1.0/24">
                    </div>
                    <div class="form-group">
                        <label>Destination Network</label>
                        <input type="text" id="ipsec_dst_network" placeholder="192.168.2.0/24">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveIpsecData()" style="width: 100%;">
                    💾 Save IPsec Configuration
                </button>
            `;
            break;

        case 'vxlan':
            html += `
                <h4>VXLAN / EVPN Configuration</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="vxlan_enabled"> Enable VXLAN</label>
                </div>
                <div class="form-group">
                    <label>Source Interface (VTEP)</label>
                    <input type="text" id="vxlan_source" placeholder="Loopback0">
                </div>
                <div class="form-group">
                    <label>Multicast Group (or 'static' for ingress-replication)</label>
                    <input type="text" id="vxlan_mcast" placeholder="239.0.0.1 or static">
                </div>
                <details class="advanced-section">
                    <summary>VXLAN Network Identifier (VNI) Mappings</summary>
                    <div id="vni-list"></div>
                    <button type="button" class="btn btn-secondary" onclick="addVniMapping()">+ Add VNI</button>
                </details>
                <details class="advanced-section">
                    <summary>EVPN Configuration</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="vxlan_evpn_enabled"> Enable EVPN</label>
                    </div>
                    <div class="form-group">
                        <label>Route Distinguisher (RD)</label>
                        <input type="text" id="vxlan_rd" placeholder="auto or 1:1">
                    </div>
                    <div class="form-group">
                        <label>Route Target (RT)</label>
                        <input type="text" id="vxlan_rt" placeholder="1:1">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="vxlan_anycast_gateway"> Anycast Gateway</label>
                    </div>
                    <div class="form-group">
                        <label>Anycast Gateway MAC</label>
                        <input type="text" id="vxlan_anycast_mac" placeholder="0000.1111.2222">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveVxlanData()" style="width: 100%;">
                    💾 Save VXLAN Configuration
                </button>
            `;
            break;

        case 'bgp_advanced':
            html += `
                <h4>BGP Advanced Features</h4>
                <details class="advanced-section" open>
                    <summary>BGP-Flowspec (DDoS Mitigation)</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_flowspec_enabled"> Enable BGP-Flowspec</label>
                    </div>
                    <div class="form-group">
                        <label>Flowspec Validation Mode</label>
                        <select id="bgp_flowspec_validation">
                            <option value="local">Local</option>
                            <option value="strict">Strict</option>
                        </select>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>BGP-BMP (Monitoring Protocol)</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_bmp_enabled"> Enable BGP-BMP</label>
                    </div>
                    <div class="form-group">
                        <label>BMP Server IP</label>
                        <input type="text" id="bgp_bmp_server" placeholder="10.0.0.100">
                    </div>
                    <div class="form-group">
                        <label>BMP Server Port</label>
                        <input type="number" id="bgp_bmp_port" placeholder="5000">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_bmp_route_monitoring"> Route Monitoring</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_bmp_stats_reporting"> Statistics Reporting</label>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>BGP-LS (Link-State for SDN)</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_ls_enabled"> Enable BGP-LS</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_ls_redistribute_ospf"> Redistribute OSPF</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_ls_redistribute_isis"> Redistribute IS-IS</label>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Other Advanced Features</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_aigp_enabled"> AIGP (Accumulated IGP Metric)</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_orr_enabled"> ORR (Optimal Route Reflection)</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_graceful_shutdown"> Graceful Shutdown (RFC 8326)</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="bgp_add_path"> Additional-Paths</label>
                    </div>
                    <div class="form-group">
                        <label>Maximum Paths</label>
                        <input type="number" id="bgp_max_paths" placeholder="8" min="1" max="64">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveBgpAdvancedData()" style="width: 100%;">
                    💾 Save BGP Advanced Configuration
                </button>
            `;
            break;

        case 'netflow':
            html += `
                <h4>NetFlow / IPFIX Configuration</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="netflow_enabled"> Enable NetFlow/IPFIX</label>
                </div>
                <div class="form-group">
                    <label>Flow Exporter Name</label>
                    <input type="text" id="netflow_exporter_name" placeholder="EXPORTER-1" required>
                </div>
                <div class="form-group">
                    <label>Collector IP Address</label>
                    <input type="text" id="netflow_collector_ip" placeholder="10.0.0.100" required>
                </div>
                <div class="form-group">
                    <label>Collector Port</label>
                    <input type="number" id="netflow_collector_port" placeholder="9995">
                </div>
                <div class="form-group">
                    <label>Source Interface</label>
                    <input type="text" id="netflow_source" placeholder="Loopback0">
                </div>
                <details class="advanced-section">
                    <summary>Flow Monitor Settings</summary>
                    <div class="form-group">
                        <label>Monitor Name</label>
                        <input type="text" id="netflow_monitor_name" placeholder="FLOW-MONITOR-1">
                    </div>
                    <div class="form-group">
                        <label>Flow Record</label>
                        <select id="netflow_record">
                            <option value="netflow-original">NetFlow Original</option>
                            <option value="netflow ipv4 original-input">NetFlow IPv4 Input</option>
                            <option value="netflow ipv4 original-output">NetFlow IPv4 Output</option>
                            <option value="ipfix">IPFIX</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Cache Timeout Active (seconds)</label>
                        <input type="number" id="netflow_cache_active" placeholder="60">
                    </div>
                    <div class="form-group">
                        <label>Cache Timeout Inactive (seconds)</label>
                        <input type="number" id="netflow_cache_inactive" placeholder="15">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Sampling</summary>
                    <div class="form-group">
                        <label>Sampler Name</label>
                        <input type="text" id="netflow_sampler_name" placeholder="SAMPLER-1">
                    </div>
                    <div class="form-group">
                        <label>Sampling Rate (1 out of N)</label>
                        <input type="number" id="netflow_sampling_rate" placeholder="1000">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveNetflowData()" style="width: 100%;">
                    💾 Save NetFlow Configuration
                </button>
            `;
            break;

        case 'sflow':
            html += `
                <h4>sFlow Configuration</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="sflow_enabled"> Enable sFlow</label>
                </div>
                <div class="form-group">
                    <label>Collector IP Address</label>
                    <input type="text" id="sflow_collector_ip" placeholder="10.0.0.100" required>
                </div>
                <div class="form-group">
                    <label>Collector Port</label>
                    <input type="number" id="sflow_collector_port" placeholder="6343">
                </div>
                <div class="form-group">
                    <label>Agent IP Address</label>
                    <input type="text" id="sflow_agent_ip" placeholder="10.0.0.1">
                </div>
                <div class="form-group">
                    <label>Sampling Rate</label>
                    <input type="number" id="sflow_sampling_rate" placeholder="4096">
                </div>
                <div class="form-group">
                    <label>Counter Poll Interval (seconds)</label>
                    <input type="number" id="sflow_counter_poll" placeholder="20">
                </div>
                <button class="btn btn-primary" onclick="saveSflowData()" style="width: 100%;">
                    💾 Save sFlow Configuration
                </button>
            `;
            break;

        case 'gnmi':
            html += `
                <h4>gNMI (gRPC Network Management Interface)</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="gnmi_enabled"> Enable gNMI</label>
                </div>
                <div class="form-group">
                    <label>gNMI Server Port</label>
                    <input type="number" id="gnmi_port" placeholder="57400">
                </div>
                <div class="form-group">
                    <label><input type="checkbox" id="gnmi_secure"> Secure Server (TLS)</label>
                </div>
                <div class="form-group">
                    <label>Trustpoint Certificate</label>
                    <input type="text" id="gnmi_certificate" placeholder="GNMI-CERT">
                </div>
                <details class="advanced-section">
                    <summary>Telemetry Subscriptions (Dial-Out)</summary>
                    <div class="form-group">
                        <label>Subscription ID</label>
                        <input type="number" id="gnmi_sub_id" placeholder="100">
                    </div>
                    <div class="form-group">
                        <label>Receiver IP</label>
                        <input type="text" id="gnmi_receiver_ip" placeholder="10.0.0.100">
                    </div>
                    <div class="form-group">
                        <label>Receiver Port</label>
                        <input type="number" id="gnmi_receiver_port" placeholder="57500">
                    </div>
                    <div class="form-group">
                        <label>Encoding</label>
                        <select id="gnmi_encoding">
                            <option value="encode-kvgpb">Key-Value GPB</option>
                            <option value="encode-proto3">Protobuf 3</option>
                            <option value="encode-json">JSON</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Update Interval (ms)</label>
                        <input type="number" id="gnmi_interval" placeholder="30000">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveGnmiData()" style="width: 100%;">
                    💾 Save gNMI Configuration
                </button>
            `;
            break;

        case 'netconf':
            html += `
                <h4>NETCONF / RESTCONF Configuration</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="netconf_enabled"> Enable NETCONF</label>
                </div>
                <div class="form-group">
                    <label>NETCONF SSH Port</label>
                    <input type="number" id="netconf_port" placeholder="830">
                </div>
                <div class="form-group">
                    <label>NETCONF ACL</label>
                    <input type="text" id="netconf_acl" placeholder="NETCONF-ACL">
                </div>
                <details class="advanced-section">
                    <summary>RESTCONF Configuration</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="restconf_enabled"> Enable RESTCONF</label>
                    </div>
                    <div class="form-group">
                        <label>RESTCONF Port</label>
                        <input type="number" id="restconf_port" placeholder="443">
                    </div>
                    <div class="form-group">
                        <label>RESTCONF ACL</label>
                        <input type="text" id="restconf_acl" placeholder="RESTCONF-ACL">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveNetconfData()" style="width: 100%;">
                    💾 Save NETCONF/RESTCONF Configuration
                </button>
            `;
            break;

        case 'ip_sla':
            html += `
                <h4>IP SLA Configuration</h4>
                <div class="form-group">
                    <label>SLA Operation ID</label>
                    <input type="number" id="ipsla_id" min="1" max="2147483647" placeholder="1" required>
                </div>
                <div class="form-group">
                    <label>SLA Type</label>
                    <select id="ipsla_type" required>
                        <option value="">Select Type...</option>
                        <option value="icmp-echo">ICMP Echo</option>
                        <option value="udp-jitter">UDP Jitter (VoIP)</option>
                        <option value="http">HTTP</option>
                        <option value="tcp-connect">TCP Connect</option>
                        <option value="dns">DNS</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Target IP/URL</label>
                    <input type="text" id="ipsla_target" placeholder="8.8.8.8 or http://example.com" required>
                </div>
                <div class="form-group">
                    <label>Source IP/Interface</label>
                    <input type="text" id="ipsla_source" placeholder="192.168.1.1 or GigabitEthernet0/0">
                </div>
                <details class="advanced-section">
                    <summary>SLA Parameters</summary>
                    <div class="form-group">
                        <label>Frequency (seconds)</label>
                        <input type="number" id="ipsla_frequency" placeholder="60">
                    </div>
                    <div class="form-group">
                        <label>Timeout (ms)</label>
                        <input type="number" id="ipsla_timeout" placeholder="5000">
                    </div>
                    <div class="form-group">
                        <label>Threshold (ms)</label>
                        <input type="number" id="ipsla_threshold" placeholder="100">
                    </div>
                    <div class="form-group">
                        <label>VRF</label>
                        <input type="text" id="ipsla_vrf" placeholder="management">
                    </div>
                    <div class="form-group">
                        <label>ToS/DSCP</label>
                        <input type="number" id="ipsla_tos" placeholder="0" min="0" max="255">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Scheduling</summary>
                    <div class="form-group">
                        <label>Start Time</label>
                        <select id="ipsla_start">
                            <option value="now">Now</option>
                            <option value="hh:mm:ss">Specific Time</option>
                            <option value="after">After delay</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Life</label>
                        <select id="ipsla_life">
                            <option value="forever">Forever</option>
                            <option value="seconds">Specific duration</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="ipsla_recurring"> Recurring</label>
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveIpSlaData()" style="width: 100%;">
                    💾 Save IP SLA Configuration
                </button>
            `;
            break;

        case 'erspan':
            html += `
                <h4>ERSPAN Configuration</h4>
                <div class="form-group">
                    <label>ERSPAN Session ID</label>
                    <input type="number" id="erspan_session_id" min="1" max="1023" placeholder="1" required>
                </div>
                <div class="form-group">
                    <label>ERSPAN ID</label>
                    <input type="number" id="erspan_id" min="1" max="1023" placeholder="101" required>
                </div>
                <div class="form-group">
                    <label>Destination IP</label>
                    <input type="text" id="erspan_dest_ip" placeholder="10.0.0.100" required>
                </div>
                <div class="form-group">
                    <label>Origin IP</label>
                    <input type="text" id="erspan_origin_ip" placeholder="10.0.0.1">
                </div>
                <details class="advanced-section">
                    <summary>Source Configuration</summary>
                    <div class="form-group">
                        <label>Source Type</label>
                        <select id="erspan_source_type">
                            <option value="interface">Interface</option>
                            <option value="vlan">VLAN</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Source Interface/VLAN</label>
                        <input type="text" id="erspan_source" placeholder="GigabitEthernet0/1 or 100">
                    </div>
                    <div class="form-group">
                        <label>Traffic Direction</label>
                        <select id="erspan_direction">
                            <option value="both">Both</option>
                            <option value="rx">RX (Ingress)</option>
                            <option value="tx">TX (Egress)</option>
                        </select>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Advanced Settings</summary>
                    <div class="form-group">
                        <label>VRF</label>
                        <input type="text" id="erspan_vrf" placeholder="default">
                    </div>
                    <div class="form-group">
                        <label>IP TTL</label>
                        <input type="number" id="erspan_ttl" placeholder="255" min="1" max="255">
                    </div>
                    <div class="form-group">
                        <label>IP DSCP</label>
                        <input type="number" id="erspan_dscp" placeholder="0" min="0" max="63">
                    </div>
                    <div class="form-group">
                        <label>MTU</label>
                        <input type="number" id="erspan_mtu" placeholder="1500">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveErspanData()" style="width: 100%;">
                    💾 Save ERSPAN Configuration
                </button>
            `;
            break;

        case 'lisp':
            html += `
                <h4>LISP Mobility Configuration</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="lisp_enabled"> Enable LISP</label>
                </div>
                <div class="form-group">
                    <label>LISP Instance ID</label>
                    <input type="number" id="lisp_instance_id" placeholder="0">
                </div>
                <div class="form-group">
                    <label>LISP Role</label>
                    <select id="lisp_role">
                        <option value="xtr">xTR (Both ITR and ETR)</option>
                        <option value="itr">ITR (Ingress Tunnel Router)</option>
                        <option value="etr">ETR (Egress Tunnel Router)</option>
                        <option value="ms">Map Server</option>
                        <option value="mr">Map Resolver</option>
                    </select>
                </div>
                <details class="advanced-section">
                    <summary>EID Configuration</summary>
                    <div class="form-group">
                        <label>EID Prefix</label>
                        <input type="text" id="lisp_eid_prefix" placeholder="10.0.0.0/24">
                    </div>
                    <div class="form-group">
                        <label>RLOC Address</label>
                        <input type="text" id="lisp_rloc" placeholder="203.0.113.1">
                    </div>
                    <div class="form-group">
                        <label>RLOC Priority</label>
                        <input type="number" id="lisp_rloc_priority" placeholder="1" min="0" max="255">
                    </div>
                    <div class="form-group">
                        <label>RLOC Weight</label>
                        <input type="number" id="lisp_rloc_weight" placeholder="100" min="0" max="100">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Map Server/Resolver</summary>
                    <div class="form-group">
                        <label>Map Server IP</label>
                        <input type="text" id="lisp_map_server" placeholder="10.0.0.100">
                    </div>
                    <div class="form-group">
                        <label>Map Resolver IP</label>
                        <input type="text" id="lisp_map_resolver" placeholder="10.0.0.100">
                    </div>
                    <div class="form-group">
                        <label>Authentication Key</label>
                        <input type="password" id="lisp_auth_key" placeholder="lisp-key">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveLispData()" style="width: 100%;">
                    💾 Save LISP Configuration
                </button>
            `;
            break;

        case 'nat':
            html += `
                <h4>NAT Configuration</h4>
                <div class="form-group">
                    <label>NAT Type</label>
                    <select id="nat_type" required>
                        <option value="">Select NAT Type...</option>
                        <option value="static">Static NAT</option>
                        <option value="dynamic">Dynamic NAT (Pool)</option>
                        <option value="pat">PAT (Port Address Translation)</option>
                        <option value="cgnat">CGNAT (Carrier Grade NAT)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Inside Interface</label>
                    <input type="text" id="nat_inside_if" placeholder="GigabitEthernet0/0">
                </div>
                <div class="form-group">
                    <label>Outside Interface</label>
                    <input type="text" id="nat_outside_if" placeholder="GigabitEthernet0/1">
                </div>
                <details class="advanced-section">
                    <summary>NAT Pool Configuration</summary>
                    <div class="form-group">
                        <label>Pool Name</label>
                        <input type="text" id="nat_pool_name" placeholder="NAT-POOL-1">
                    </div>
                    <div class="form-group">
                        <label>Pool Start IP</label>
                        <input type="text" id="nat_pool_start" placeholder="203.0.113.10">
                    </div>
                    <div class="form-group">
                        <label>Pool End IP</label>
                        <input type="text" id="nat_pool_end" placeholder="203.0.113.20">
                    </div>
                    <div class="form-group">
                        <label>Netmask</label>
                        <input type="text" id="nat_pool_netmask" placeholder="255.255.255.0">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Static NAT Mappings</summary>
                    <div class="form-group">
                        <label>Inside Local IP</label>
                        <input type="text" id="nat_inside_local" placeholder="192.168.1.10">
                    </div>
                    <div class="form-group">
                        <label>Inside Global IP</label>
                        <input type="text" id="nat_inside_global" placeholder="203.0.113.10">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveNatData()" style="width: 100%;">
                    💾 Save NAT Configuration
                </button>
            `;
            break;

        case 'mpls':
            html += `
                <h4>MPLS Configuration</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="mpls_enabled"> Enable MPLS</label>
                </div>
                <div class="form-group">
                    <label>LDP Router ID</label>
                    <input type="text" id="mpls_ldp_router_id" placeholder="1.1.1.1">
                </div>
                <details class="advanced-section">
                    <summary>MPLS L3VPN Configuration</summary>
                    <div class="form-group">
                        <label>VRF Name</label>
                        <input type="text" id="mpls_vrf_name" placeholder="CUSTOMER-A">
                    </div>
                    <div class="form-group">
                        <label>Route Distinguisher (RD)</label>
                        <input type="text" id="mpls_rd" placeholder="65000:100">
                    </div>
                    <div class="form-group">
                        <label>Route Target Export</label>
                        <input type="text" id="mpls_rt_export" placeholder="65000:100">
                    </div>
                    <div class="form-group">
                        <label>Route Target Import</label>
                        <input type="text" id="mpls_rt_import" placeholder="65000:100">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>MPLS TE (Traffic Engineering)</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="mpls_te_enabled"> Enable MPLS TE</label>
                    </div>
                    <div class="form-group">
                        <label>TE Tunnel Interface</label>
                        <input type="text" id="mpls_te_tunnel" placeholder="Tunnel100">
                    </div>
                    <div class="form-group">
                        <label>TE Bandwidth (kbps)</label>
                        <input type="number" id="mpls_te_bandwidth" placeholder="1000000">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveMplsData()" style="width: 100%;">
                    💾 Save MPLS Configuration
                </button>
            `;
            break;

        case 'sr':
            html += `
                <h4>Segment Routing Configuration</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="sr_enabled"> Enable Segment Routing</label>
                </div>
                <div class="form-group">
                    <label>SR Type</label>
                    <select id="sr_type">
                        <option value="sr-mpls">SR-MPLS</option>
                        <option value="srv6">SRv6</option>
                    </select>
                </div>
                <details class="advanced-section">
                    <summary>SR-MPLS Configuration</summary>
                    <div class="form-group">
                        <label>SRGB Start Label</label>
                        <input type="number" id="sr_srgb_start" placeholder="16000">
                    </div>
                    <div class="form-group">
                        <label>SRGB End Label</label>
                        <input type="number" id="sr_srgb_end" placeholder="23999">
                    </div>
                    <div class="form-group">
                        <label>Node SID (Prefix-SID)</label>
                        <input type="number" id="sr_node_sid" placeholder="100">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>SRv6 Configuration</summary>
                    <div class="form-group">
                        <label>Locator Name</label>
                        <input type="text" id="srv6_locator_name" placeholder="LOC1">
                    </div>
                    <div class="form-group">
                        <label>Locator Prefix</label>
                        <input type="text" id="srv6_locator_prefix" placeholder="2001:db8:1::/48">
                    </div>
                    <div class="form-group">
                        <label>SRv6 Behavior</label>
                        <select id="srv6_behavior">
                            <option value="end">End</option>
                            <option value="end.x">End.X</option>
                            <option value="end.dt4">End.DT4</option>
                            <option value="end.dt6">End.DT6</option>
                        </select>
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveSrData()" style="width: 100%;">
                    💾 Save Segment Routing Configuration
                </button>
            `;
            break;

        case 'qos':
            html += `
                <h4>QoS Configuration</h4>
                <div class="form-group">
                    <label>Policy Name</label>
                    <input type="text" id="qos_policy_name" placeholder="QOS-POLICY-1" required>
                </div>
                <details class="advanced-section" open>
                    <summary>Class Configuration</summary>
                    <div class="form-group">
                        <label>Class Name</label>
                        <input type="text" id="qos_class_name" placeholder="VOICE">
                    </div>
                    <div class="form-group">
                        <label>Match DSCP</label>
                        <input type="text" id="qos_match_dscp" placeholder="ef,af41">
                    </div>
                    <div class="form-group">
                        <label>Priority Bandwidth (kbps)</label>
                        <input type="number" id="qos_priority_bw" placeholder="1000">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Policing & Shaping</summary>
                    <div class="form-group">
                        <label>Police Rate (bps)</label>
                        <input type="number" id="qos_police_rate" placeholder="10000000">
                    </div>
                    <div class="form-group">
                        <label>Police Burst (bytes)</label>
                        <input type="number" id="qos_police_burst" placeholder="1500000">
                    </div>
                    <div class="form-group">
                        <label>Shape Rate (bps)</label>
                        <input type="number" id="qos_shape_rate" placeholder="100000000">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Queueing</summary>
                    <div class="form-group">
                        <label>Queue Limit (packets)</label>
                        <input type="number" id="qos_queue_limit" placeholder="64">
                    </div>
                    <div class="form-group">
                        <label>Random Detect</label>
                        <select id="qos_random_detect">
                            <option value="">None</option>
                            <option value="dscp-based">DSCP-Based WRED</option>
                            <option value="precedence-based">Precedence-Based WRED</option>
                        </select>
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveQosData()" style="width: 100%;">
                    💾 Save QoS Configuration
                </button>
            `;
            break;

        case 'bfd':
            html += `
                <h4>BFD (Bidirectional Forwarding Detection)</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="bfd_enabled"> Enable BFD</label>
                </div>
                <div class="form-group">
                    <label>BFD Interval (ms)</label>
                    <input type="number" id="bfd_interval" placeholder="50" min="50" max="999">
                </div>
                <div class="form-group">
                    <label>BFD Multiplier</label>
                    <input type="number" id="bfd_multiplier" placeholder="3" min="3" max="50">
                </div>
                <details class="advanced-section">
                    <summary>BFD Templates</summary>
                    <div class="form-group">
                        <label>Template Name</label>
                        <input type="text" id="bfd_template_name" placeholder="BFD-TEMPLATE-1">
                    </div>
                    <div class="form-group">
                        <label>Echo Mode</label>
                        <select id="bfd_echo_mode">
                            <option value="disabled">Disabled</option>
                            <option value="enabled">Enabled</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="bfd_authentication"> BFD Authentication</label>
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveBfdData()" style="width: 100%;">
                    💾 Save BFD Configuration
                </button>
            `;
            break;

        case 'security':
            html += `
                <h4>L2 Security Configuration</h4>
                <details class="advanced-section" open>
                    <summary>Port Security</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_port_security"> Enable Port Security</label>
                    </div>
                    <div class="form-group">
                        <label>Default Maximum MACs</label>
                        <input type="number" id="security_max_macs" placeholder="2" min="1" max="8192">
                    </div>
                    <div class="form-group">
                        <label>Violation Action</label>
                        <select id="security_violation">
                            <option value="protect">Protect</option>
                            <option value="restrict">Restrict</option>
                            <option value="shutdown">Shutdown</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_port_sticky"> Enable Sticky MAC Learning</label>
                    </div>
                    <div class="form-group">
                        <label>Aging Time (minutes)</label>
                        <input type="number" id="security_port_aging_time" placeholder="0" min="0" max="1440">
                    </div>
                    <div class="form-group">
                        <label>Aging Type</label>
                        <select id="security_port_aging_type">
                            <option value="">None</option>
                            <option value="absolute">Absolute</option>
                            <option value="inactivity">Inactivity</option>
                        </select>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>DHCP Snooping</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dhcp_snooping"> Enable DHCP Snooping</label>
                    </div>
                    <div class="form-group">
                        <label>DHCP Snooping VLANs</label>
                        <input type="text" id="security_dhcp_vlans" placeholder="10,20,30-40">
                    </div>
                    <div class="form-group">
                        <label>Trusted Interfaces (comma-separated)</label>
                        <input type="text" id="security_dhcp_trusted" placeholder="GigabitEthernet0/1,GigabitEthernet0/24">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dhcp_verify_mac"> Verify MAC Address</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dhcp_option82"> Insert Option 82</label>
                    </div>
                    <div class="form-group">
                        <label>Rate Limit (pps)</label>
                        <input type="number" id="security_dhcp_rate_limit" placeholder="100" min="1" max="2048">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dhcp_database"> Enable Database Persistence</label>
                    </div>
                    <div class="form-group">
                        <label>Database File</label>
                        <input type="text" id="security_dhcp_database_file" placeholder="flash:dhcp_snooping.db">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Dynamic ARP Inspection (DAI)</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dai"> Enable DAI</label>
                    </div>
                    <div class="form-group">
                        <label>DAI VLANs</label>
                        <input type="text" id="security_dai_vlans" placeholder="10,20,30-40">
                    </div>
                    <div class="form-group">
                        <label>Trusted Interfaces (comma-separated)</label>
                        <input type="text" id="security_dai_trusted" placeholder="GigabitEthernet0/1,GigabitEthernet0/24">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dai_validate_src_mac"> Validate Source MAC</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dai_validate_dst_mac"> Validate Destination MAC</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dai_validate_ip"> Validate IP</label>
                    </div>
                    <div class="form-group">
                        <label>ARP ACL Name</label>
                        <input type="text" id="security_dai_arp_acl" placeholder="DAI_ACL">
                    </div>
                    <div class="form-group">
                        <label>Rate Limit (pps)</label>
                        <input type="number" id="security_dai_rate_limit" placeholder="15" min="1" max="2048">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>802.1X Authentication</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dot1x"> Enable 802.1X</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dot1x_system_auth"> Enable System Auth Control</label>
                    </div>
                    <div class="form-group">
                        <label>Re-authentication Interval (seconds)</label>
                        <input type="number" id="security_dot1x_reauth" placeholder="3600" min="60" max="65535">
                    </div>
                    <div class="form-group">
                        <label>Quiet Period (seconds)</label>
                        <input type="number" id="security_dot1x_quiet" placeholder="60" min="1" max="65535">
                    </div>
                    <div class="form-group">
                        <label>TX Period (seconds)</label>
                        <input type="number" id="security_dot1x_tx_period" placeholder="30" min="1" max="65535">
                    </div>
                    <div class="form-group">
                        <label>Max Re-authentication Requests</label>
                        <input type="number" id="security_dot1x_max_reauth" placeholder="2" min="1" max="10">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_dot1x_mab"> Enable MAC Authentication Bypass (MAB)</label>
                    </div>
                    <div class="form-group">
                        <label>Guest VLAN</label>
                        <input type="number" id="security_dot1x_guest_vlan" placeholder="100" min="1" max="4094">
                    </div>
                    <div class="form-group">
                        <label>Critical VLAN (Server Dead)</label>
                        <input type="number" id="security_dot1x_critical_vlan" placeholder="999" min="1" max="4094">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>IP Source Guard (IPSG)</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_ipsg"> Enable IP Source Guard</label>
                    </div>
                    <div class="form-group">
                        <label>Interfaces (comma-separated)</label>
                        <input type="text" id="security_ipsg_interfaces" placeholder="GigabitEthernet0/1,GigabitEthernet0/2">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>MACsec (802.1AE)</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="security_macsec"> Enable MACsec</label>
                    </div>
                    <div class="form-group">
                        <label>Policy Name</label>
                        <input type="text" id="security_macsec_policy" placeholder="MACSEC_POLICY">
                    </div>
                    <div class="form-group">
                        <label>Cipher Suite</label>
                        <select id="security_macsec_cipher">
                            <option value="gcm-aes-128">GCM-AES-128</option>
                            <option value="gcm-aes-256">GCM-AES-256</option>
                            <option value="gcm-aes-xpn-128">GCM-AES-XPN-128</option>
                            <option value="gcm-aes-xpn-256">GCM-AES-XPN-256</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>Interfaces (comma-separated)</label>
                        <input type="text" id="security_macsec_interfaces" placeholder="TenGigabitEthernet0/1">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveSecurityData()" style="width: 100%;">
                    💾 Save Security Configuration
                </button>
            `;
            break;

        case 'dcb':
            html += `
                <h4>Data Center Bridging (DCB)</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="dcb_enabled"> Enable DCB</label>
                </div>
                <details class="advanced-section" open>
                    <summary>Priority Flow Control (PFC)</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="dcb_pfc_enabled"> Enable PFC</label>
                    </div>
                    <div class="form-group">
                        <label>PFC Priority Classes</label>
                        <input type="text" id="dcb_pfc_priorities" placeholder="3,4" title="Comma-separated CoS values">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Enhanced Transmission Selection (ETS)</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="dcb_ets_enabled"> Enable ETS</label>
                    </div>
                    <div class="form-group">
                        <label>Traffic Class 0 Bandwidth %</label>
                        <input type="number" id="dcb_ets_tc0" placeholder="25" min="0" max="100">
                    </div>
                    <div class="form-group">
                        <label>Traffic Class 1 Bandwidth %</label>
                        <input type="number" id="dcb_ets_tc1" placeholder="25" min="0" max="100">
                    </div>
                    <div class="form-group">
                        <label>Traffic Class 2 Bandwidth %</label>
                        <input type="number" id="dcb_ets_tc2" placeholder="25" min="0" max="100">
                    </div>
                    <div class="form-group">
                        <label>Traffic Class 3 Bandwidth %</label>
                        <input type="number" id="dcb_ets_tc3" placeholder="25" min="0" max="100">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>DCBX (DCB Exchange)</summary>
                    <div class="form-group">
                        <label>DCBX Version</label>
                        <select id="dcb_dcbx_version">
                            <option value="ieee">IEEE 802.1Qaz</option>
                            <option value="cee">CEE</option>
                        </select>
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveDcbData()" style="width: 100%;">
                    💾 Save DCB Configuration
                </button>
            `;
            break;

        case 'erps':
            html += `
                <h4>Ethernet Ring Protection Switching (ERPS G.8032)</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="erps_enabled"> Enable ERPS</label>
                </div>
                <div class="form-group">
                    <label>Ring ID</label>
                    <input type="number" id="erps_ring_id" placeholder="1" min="1" max="255">
                </div>
                <div class="form-group">
                    <label>Control VLAN</label>
                    <input type="number" id="erps_control_vlan" placeholder="4094" min="1" max="4094">
                </div>
                <details class="advanced-section">
                    <summary>Ring Ports Configuration</summary>
                    <div class="form-group">
                        <label>Port 0 Interface</label>
                        <input type="text" id="erps_port0" placeholder="GigabitEthernet0/1">
                    </div>
                    <div class="form-group">
                        <label>Port 1 Interface</label>
                        <input type="text" id="erps_port1" placeholder="GigabitEthernet0/2">
                    </div>
                    <div class="form-group">
                        <label>RPL (Ring Protection Link) Role</label>
                        <select id="erps_rpl_role">
                            <option value="none">None</option>
                            <option value="owner">RPL Owner</option>
                            <option value="neighbor">RPL Neighbor</option>
                        </select>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Timing Parameters</summary>
                    <div class="form-group">
                        <label>Guard Timer (ms)</label>
                        <input type="number" id="erps_guard_timer" placeholder="500">
                    </div>
                    <div class="form-group">
                        <label>Hold-off Timer (ms)</label>
                        <input type="number" id="erps_holdoff_timer" placeholder="0">
                    </div>
                    <div class="form-group">
                        <label>WTR Timer (seconds)</label>
                        <input type="number" id="erps_wtr_timer" placeholder="300">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveErpsData()" style="width: 100%;">
                    💾 Save ERPS Configuration
                </button>
            `;
            break;

        case 'discovery':
            html += `
                <h4>Discovery Protocols (LLDP / CDP)</h4>
                <details class="advanced-section" open>
                    <summary>LLDP Configuration</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="lldp_enabled" checked> Enable LLDP</label>
                    </div>
                    <div class="form-group">
                        <label>LLDP Timer (seconds)</label>
                        <input type="number" id="lldp_timer" placeholder="30">
                    </div>
                    <div class="form-group">
                        <label>LLDP Hold Time (seconds)</label>
                        <input type="number" id="lldp_holdtime" placeholder="120">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="lldp_med"> Enable LLDP-MED</label>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>CDP Configuration</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="cdp_enabled"> Enable CDP (Cisco Only)</label>
                    </div>
                    <div class="form-group">
                        <label>CDP Timer (seconds)</label>
                        <input type="number" id="cdp_timer" placeholder="60">
                    </div>
                    <div class="form-group">
                        <label>CDP Holdtime (seconds)</label>
                        <input type="number" id="cdp_holdtime" placeholder="180">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveDiscoveryData()" style="width: 100%;">
                    💾 Save Discovery Configuration
                </button>
            `;
            break;

        case 'mlag':
            html += `
                <h4>Multi-Chassis LAG (MLAG/vPC)</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="mlag_enabled"> Enable MLAG/vPC</label>
                </div>
                <div class="form-group">
                    <label>Domain ID</label>
                    <input type="number" id="mlag_domain_id" placeholder="1" min="1" max="1000">
                </div>
                <details class="advanced-section">
                    <summary>Peer Configuration</summary>
                    <div class="form-group">
                        <label>Peer Keepalive IP</label>
                        <input type="text" id="mlag_keepalive_ip" placeholder="10.0.0.2">
                    </div>
                    <div class="form-group">
                        <label>Peer Keepalive Source IP</label>
                        <input type="text" id="mlag_keepalive_src" placeholder="10.0.0.1">
                    </div>
                    <div class="form-group">
                        <label>Peer Keepalive VRF</label>
                        <input type="text" id="mlag_keepalive_vrf" placeholder="management">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Peer Link Configuration</summary>
                    <div class="form-group">
                        <label>Peer Link Interface</label>
                        <input type="text" id="mlag_peer_link" placeholder="port-channel10">
                    </div>
                    <div class="form-group">
                        <label>Role</label>
                        <select id="mlag_role">
                            <option value="primary">Primary</option>
                            <option value="secondary">Secondary</option>
                        </select>
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Advanced Features</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="mlag_peer_gateway"> Peer Gateway</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="mlag_peer_switch"> Peer Switch</label>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="mlag_anycast_vtep"> Anycast VTEP</label>
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveMlagData()" style="width: 100%;">
                    💾 Save MLAG Configuration
                </button>
            `;
            break;

        case 'multicast':
            html += `
                <h4>Multicast Configuration</h4>
                <details class="advanced-section" open>
                    <summary>PIM (Protocol Independent Multicast)</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="multicast_pim_enabled"> Enable PIM</label>
                    </div>
                    <div class="form-group">
                        <label>PIM Mode</label>
                        <select id="multicast_pim_mode">
                            <option value="sparse-mode">Sparse Mode</option>
                            <option value="dense-mode">Dense Mode</option>
                            <option value="sparse-dense-mode">Sparse-Dense Mode</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label>RP Address (for Sparse Mode)</label>
                        <input type="text" id="multicast_rp_address" placeholder="10.0.0.100">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>IGMP Configuration</summary>
                    <div class="form-group">
                        <label>IGMP Version</label>
                        <select id="multicast_igmp_version">
                            <option value="3">Version 3</option>
                            <option value="2">Version 2</option>
                            <option value="1">Version 1</option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="multicast_igmp_snooping"> IGMP Snooping</label>
                    </div>
                    <div class="form-group">
                        <label>Snooping VLANs</label>
                        <input type="text" id="multicast_igmp_vlans" placeholder="10,20,30-40">
                    </div>
                </details>
                <details class="advanced-section">
                    <summary>Advanced Multicast</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="multicast_msdp"> Enable MSDP</label>
                    </div>
                    <div class="form-group">
                        <label>MSDP Peer IP</label>
                        <input type="text" id="multicast_msdp_peer" placeholder="10.0.0.101">
                    </div>
                    <div class="form-group">
                        <label><input type="checkbox" id="multicast_ssm"> SSM (Source-Specific Multicast)</label>
                    </div>
                    <div class="form-group">
                        <label>SSM Range</label>
                        <input type="text" id="multicast_ssm_range" placeholder="232.0.0.0/8">
                    </div>
                </details>
                <button class="btn btn-primary" onclick="saveMulticastData()" style="width: 100%;">
                    💾 Save Multicast Configuration
                </button>
            `;
            break;

        // ===== LAYER 2 ADVANCED =====

        case 'lacp_advanced':
            html += `
                <h4>LACP Advanced Configuration</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="lacp_adv_enabled" checked> Enable LACP Advanced Features</label>
                </div>

                <div class="form-group">
                    <label>LACP System Priority</label>
                    <input type="number" id="lacp_system_priority" value="32768" min="1" max="65535" placeholder="32768">
                    <small class="help-text">Lower value = higher priority (default: 32768)</small>
                </div>

                <div class="form-group">
                    <label>Global Load Balance Algorithm</label>
                    <select id="lacp_load_balance">
                        <option value="src-dst-ip">Source-Destination IP</option>
                        <option value="src-dst-mac">Source-Destination MAC</option>
                        <option value="src-ip">Source IP</option>
                        <option value="dst-ip">Destination IP</option>
                        <option value="src-mac">Source MAC</option>
                        <option value="dst-mac">Destination MAC</option>
                        <option value="src-dst-port">Source-Destination Port</option>
                    </select>
                </div>

                <h5>Port-Channel Configuration</h5>
                <div class="form-group">
                    <label>Port-Channel ID</label>
                    <input type="number" id="lacp_po_id" min="1" max="4096" placeholder="1">
                </div>

                <div class="form-group">
                    <label>Description</label>
                    <input type="text" id="lacp_po_desc" placeholder="Uplink to Core">
                </div>

                <div class="form-group">
                    <label>Minimum Links</label>
                    <input type="number" id="lacp_min_links" min="1" max="16" value="1" placeholder="1">
                    <small class="help-text">Minimum active members required</small>
                </div>

                <div class="form-group">
                    <label>Maximum Bundle</label>
                    <input type="number" id="lacp_max_bundle" min="1" max="16" value="8" placeholder="8">
                </div>

                <div class="form-group">
                    <label>LACP Mode</label>
                    <select id="lacp_mode">
                        <option value="active">Active</option>
                        <option value="passive">Passive</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>LACP Rate</label>
                    <select id="lacp_rate">
                        <option value="normal">Normal (30s)</option>
                        <option value="fast">Fast (1s)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Member Interfaces (comma-separated)</label>
                    <input type="text" id="lacp_members" placeholder="Gi0/1,Gi0/2,Gi0/3,Gi0/4">
                </div>

                <div class="form-group">
                    <label>Member Port Priority</label>
                    <input type="number" id="lacp_port_priority" min="1" max="65535" value="32768" placeholder="32768">
                </div>

                <button class="btn btn-primary" onclick="saveLacpAdvancedData()" style="width: 100%;">
                    💾 Save LACP Advanced Configuration
                </button>
            `;
            break;

        case 'mst':
            html += `
                <h4>Multiple Spanning Tree (MST) Configuration</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="mst_enabled" checked> Enable MST</label>
                </div>

                <h5>MST Region Configuration</h5>
                <div class="form-group">
                    <label>Region Name</label>
                    <input type="text" id="mst_region_name" placeholder="REGION1" required>
                </div>

                <div class="form-group">
                    <label>Revision Number</label>
                    <input type="number" id="mst_revision" min="0" max="65535" value="1" placeholder="1">
                </div>

                <h5>MST Instance Configuration</h5>
                <div class="form-group">
                    <label>Instance ID</label>
                    <input type="number" id="mst_instance_id" min="1" max="4094" placeholder="1">
                </div>

                <div class="form-group">
                    <label>VLANs (comma-separated or range)</label>
                    <input type="text" id="mst_instance_vlans" placeholder="10,20,30-40">
                </div>

                <div class="form-group">
                    <label>Instance Priority</label>
                    <input type="number" id="mst_instance_priority" min="0" max="61440" step="4096" value="32768">
                </div>

                <details class="advanced-section">
                    <summary>Advanced MST Timers</summary>
                    <div class="form-group">
                        <label>Hello Time (seconds)</label>
                        <input type="number" id="mst_hello_time" min="1" max="10" value="2">
                    </div>
                    <div class="form-group">
                        <label>Forward Time (seconds)</label>
                        <input type="number" id="mst_forward_time" min="4" max="30" value="15">
                    </div>
                    <div class="form-group">
                        <label>Max Age (seconds)</label>
                        <input type="number" id="mst_max_age" min="6" max="40" value="20">
                    </div>
                    <div class="form-group">
                        <label>Max Hops</label>
                        <input type="number" id="mst_max_hops" min="1" max="255" value="20">
                    </div>
                </details>

                <button class="btn btn-primary" onclick="saveMstData()" style="width: 100%;">
                    💾 Save MST Configuration
                </button>
            `;
            break;

        case 'udld':
            html += `
                <h4>UniDirectional Link Detection (UDLD)</h4>
                <div class="form-group">
                    <label><input type="checkbox" id="udld_enabled" checked> Enable UDLD</label>
                </div>

                <div class="form-group">
                    <label>UDLD Mode</label>
                    <select id="udld_mode">
                        <option value="normal">Normal</option>
                        <option value="aggressive">Aggressive</option>
                    </select>
                    <small class="help-text">Aggressive mode brings down the port on failure</small>
                </div>

                <div class="form-group">
                    <label>Message Time (seconds)</label>
                    <input type="number" id="udld_message_time" min="7" max="90" value="15">
                    <small class="help-text">Interval between UDLD probe messages</small>
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="udld_recovery" checked> Enable Error Disable Recovery</label>
                </div>

                <div class="form-group">
                    <label>Recovery Interval (seconds)</label>
                    <input type="number" id="udld_recovery_interval" min="30" max="86400" value="300">
                </div>

                <h5>Per-Interface UDLD</h5>
                <div class="form-group">
                    <label>Interface</label>
                    <input type="text" id="udld_interface" placeholder="GigabitEthernet0/1">
                </div>

                <div class="form-group">
                    <label>Interface UDLD Mode</label>
                    <select id="udld_interface_mode">
                        <option value="enable">Enable</option>
                        <option value="aggressive">Aggressive</option>
                        <option value="disable">Disable</option>
                    </select>
                </div>

                <button class="btn btn-primary" onclick="saveUdldData()" style="width: 100%;">
                    💾 Save UDLD Configuration
                </button>
            `;
            break;

        case 'storm_control':
            html += `
                <h4>Storm Control Configuration</h4>
                <p class="help-text">Prevent broadcast/multicast/unicast storms</p>

                <div class="form-group">
                    <label>Interface</label>
                    <input type="text" id="storm_interface" placeholder="GigabitEthernet0/1" required>
                </div>

                <h5>Traffic Thresholds (%)</h5>
                <div class="form-group">
                    <label>Broadcast Level</label>
                    <input type="number" id="storm_broadcast_level" min="0" max="100" step="0.01" placeholder="1.00">
                    <small class="help-text">Percentage of bandwidth (e.g., 1.00 = 1%)</small>
                </div>

                <div class="form-group">
                    <label>Multicast Level</label>
                    <input type="number" id="storm_multicast_level" min="0" max="100" step="0.01" placeholder="1.00">
                </div>

                <div class="form-group">
                    <label>Unicast Level</label>
                    <input type="number" id="storm_unicast_level" min="0" max="100" step="0.01" placeholder="1.00">
                </div>

                <div class="form-group">
                    <label>Action on Violation</label>
                    <select id="storm_action">
                        <option value="shutdown">Shutdown Port</option>
                        <option value="trap">Send SNMP Trap</option>
                        <option value="shutdown trap">Shutdown + Trap</option>
                    </select>
                </div>

                <button class="btn btn-primary" onclick="saveStormControlData()" style="width: 100%;">
                    💾 Save Storm Control Configuration
                </button>
            `;
            break;

        case 'flexlinks':
            html += `
                <h4>FlexLinks (Layer 2 Backup Links)</h4>
                <p class="help-text">Configure backup interfaces for link redundancy</p>

                <div class="form-group">
                    <label>Primary Interface</label>
                    <input type="text" id="flexlink_primary" placeholder="GigabitEthernet0/1" required>
                </div>

                <div class="form-group">
                    <label>Backup Interface</label>
                    <input type="text" id="flexlink_backup" placeholder="GigabitEthernet0/2" required>
                </div>

                <div class="form-group">
                    <label>Preemption Mode</label>
                    <select id="flexlink_preemption_mode">
                        <option value="forced">Forced</option>
                        <option value="bandwidth">Bandwidth</option>
                        <option value="off">Off (No Preemption)</option>
                    </select>
                    <small class="help-text">When primary comes back, should it take over?</small>
                </div>

                <div class="form-group">
                    <label>Preemption Delay (seconds)</label>
                    <input type="number" id="flexlink_preemption_delay" min="1" max="300" value="35">
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="flexlink_multicast_fast" checked> Multicast Fast Convergence</label>
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="flexlink_mac_move" checked> MAC Address Move Update</label>
                </div>

                <button class="btn btn-primary" onclick="saveFlexLinksData()" style="width: 100%;">
                    💾 Save FlexLinks Configuration
                </button>
            `;
            break;

        case 'stp_protection':
            html += `
                <h4>STP Protection Mechanisms</h4>
                <p class="help-text">PortFast, BPDU Guard, Root Guard, Loop Guard</p>

                <h5>Global STP Protection</h5>
                <div class="form-group">
                    <label><input type="checkbox" id="stp_prot_portfast_default" checked> PortFast Default</label>
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="stp_prot_bpduguard_default" checked> BPDU Guard Default</label>
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="stp_prot_bpdufilter_default"> BPDU Filter Default</label>
                    <small class="help-text">⚠️ Use with caution - disables STP on edge ports</small>
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="stp_prot_loopguard_default"> Loop Guard Default</label>
                </div>

                <h5>Per-Interface STP Protection</h5>
                <div class="form-group">
                    <label>Interface</label>
                    <input type="text" id="stp_prot_interface" placeholder="GigabitEthernet0/1">
                </div>

                <div class="form-group">
                    <label>PortFast Type</label>
                    <select id="stp_prot_portfast_type">
                        <option value="">None</option>
                        <option value="edge">Edge (Access Port)</option>
                        <option value="trunk">Trunk</option>
                        <option value="network">Network (Point-to-Point)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="stp_prot_bpduguard"> BPDU Guard</label>
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="stp_prot_bpdufilter"> BPDU Filter</label>
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="stp_prot_rootguard"> Root Guard</label>
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="stp_prot_loopguard"> Loop Guard</label>
                </div>

                <div class="form-group">
                    <label>STP Cost</label>
                    <input type="number" id="stp_prot_cost" min="1" max="200000000" placeholder="Auto">
                </div>

                <div class="form-group">
                    <label>Port Priority</label>
                    <input type="number" id="stp_prot_port_priority" min="0" max="240" step="16" value="128">
                </div>

                <details class="advanced-section">
                    <summary>Error Disable Recovery</summary>
                    <div class="form-group">
                        <label>BPDU Guard Timeout (seconds)</label>
                        <input type="number" id="stp_prot_bpduguard_timeout" min="30" max="86400" value="300">
                    </div>
                </details>

                <button class="btn btn-primary" onclick="saveStpProtectionData()" style="width: 100%;">
                    💾 Save STP Protection Configuration
                </button>
            `;
            break;

        // ===== LAYER 3 ADVANCED =====

        case 'route_maps':
            html += `
                <h4>Route Maps Configuration</h4>
                <p class="help-text">Define routing policies with match/set conditions</p>

                <div class="form-group">
                    <label>Route-Map Name</label>
                    <input type="text" id="rm_name" placeholder="RM-REDISTRIBUTE" required>
                </div>

                <div class="form-group">
                    <label>Action</label>
                    <select id="rm_action">
                        <option value="permit">Permit</option>
                        <option value="deny">Deny</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Sequence Number</label>
                    <input type="number" id="rm_sequence" min="1" max="65535" value="10" placeholder="10">
                </div>

                <div class="form-group">
                    <label>Description</label>
                    <input type="text" id="rm_description" placeholder="Redistribute OSPF to BGP">
                </div>

                <details class="advanced-section" open>
                    <summary>Match Conditions</summary>

                    <div class="form-group">
                        <label>Match IP Address (ACL)</label>
                        <input type="text" id="rm_match_acl" placeholder="100">
                    </div>

                    <div class="form-group">
                        <label>Match IP Address (Prefix-list)</label>
                        <input type="text" id="rm_match_prefix_list" placeholder="PREFIX-LIST-1">
                    </div>

                    <div class="form-group">
                        <label>Match Interface</label>
                        <input type="text" id="rm_match_interface" placeholder="GigabitEthernet0/0">
                    </div>

                    <div class="form-group">
                        <label>Match Metric</label>
                        <input type="number" id="rm_match_metric" placeholder="100">
                    </div>

                    <div class="form-group">
                        <label>Match Route Type</label>
                        <select id="rm_match_route_type">
                            <option value="">None</option>
                            <option value="external">External</option>
                            <option value="internal">Internal</option>
                            <option value="level-1">Level-1</option>
                            <option value="level-2">Level-2</option>
                            <option value="local">Local</option>
                            <option value="nssa-external">NSSA External</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Match Tag</label>
                        <input type="number" id="rm_match_tag" placeholder="100">
                    </div>

                    <div class="form-group">
                        <label>Match AS-Path</label>
                        <input type="text" id="rm_match_as_path" placeholder="AS-PATH-LIST">
                    </div>

                    <div class="form-group">
                        <label>Match Community</label>
                        <input type="text" id="rm_match_community" placeholder="COMMUNITY-LIST">
                    </div>
                </details>

                <details class="advanced-section">
                    <summary>Set Actions</summary>

                    <div class="form-group">
                        <label>Set Next-Hop</label>
                        <input type="text" id="rm_set_next_hop" placeholder="10.0.0.1">
                    </div>

                    <div class="form-group">
                        <label>Set Default Next-Hop</label>
                        <input type="text" id="rm_set_default_next_hop" placeholder="10.0.0.254">
                    </div>

                    <div class="form-group">
                        <label>Set Interface</label>
                        <input type="text" id="rm_set_interface" placeholder="Null0">
                    </div>

                    <div class="form-group">
                        <label>Set Metric</label>
                        <input type="number" id="rm_set_metric" placeholder="100">
                    </div>

                    <div class="form-group">
                        <label>Set Metric Type</label>
                        <select id="rm_set_metric_type">
                            <option value="">None</option>
                            <option value="type-1">Type-1</option>
                            <option value="type-2">Type-2</option>
                            <option value="internal">Internal</option>
                            <option value="external">External</option>
                        </select>
                    </div>

                    <div class="form-group">
                        <label>Set Tag</label>
                        <input type="number" id="rm_set_tag" placeholder="100">
                    </div>

                    <div class="form-group">
                        <label>Set Local-Preference</label>
                        <input type="number" id="rm_set_local_pref" placeholder="200">
                    </div>

                    <div class="form-group">
                        <label>Set Weight</label>
                        <input type="number" id="rm_set_weight" placeholder="100">
                    </div>

                    <div class="form-group">
                        <label>Set AS-Path Prepend</label>
                        <input type="text" id="rm_set_as_path_prepend" placeholder="65000 65000">
                    </div>

                    <div class="form-group">
                        <label>Set Community</label>
                        <input type="text" id="rm_set_community" placeholder="65000:100">
                    </div>
                </details>

                <button class="btn btn-primary" onclick="saveRouteMapData()" style="width: 100%;">
                    💾 Save Route-Map Configuration
                </button>
            `;
            break;

        case 'prefix_lists':
            html += `
                <h4>Prefix Lists Configuration</h4>
                <p class="help-text">Filter prefixes based on length and value</p>

                <div class="form-group">
                    <label>Prefix-List Name</label>
                    <input type="text" id="pl_name" placeholder="PREFIX-FILTER" required>
                </div>

                <div class="form-group">
                    <label>Description</label>
                    <input type="text" id="pl_description" placeholder="Filter internal routes">
                </div>

                <h5>Prefix Entry</h5>
                <div class="form-group">
                    <label>Sequence Number</label>
                    <input type="number" id="pl_sequence" min="1" max="4294967295" value="10" placeholder="10">
                </div>

                <div class="form-group">
                    <label>Action</label>
                    <select id="pl_action">
                        <option value="permit">Permit</option>
                        <option value="deny">Deny</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Network Prefix (CIDR)</label>
                    <input type="text" id="pl_prefix" placeholder="10.0.0.0/8" required>
                </div>

                <details class="advanced-section">
                    <summary>Advanced Matching (ge/le)</summary>
                    <div class="form-group">
                        <label>Greater or Equal (ge)</label>
                        <input type="number" id="pl_ge" min="0" max="32" placeholder="Optional">
                        <small class="help-text">Match prefixes with length >= this value</small>
                    </div>

                    <div class="form-group">
                        <label>Less or Equal (le)</label>
                        <input type="number" id="pl_le" min="0" max="32" placeholder="Optional">
                        <small class="help-text">Match prefixes with length <= this value</small>
                    </div>

                    <p class="help-text">Example: 10.0.0.0/8 ge 24 le 32 = Match 10.x.x.x/24 to /32</p>
                </details>

                <button class="btn btn-primary" onclick="savePrefixListData()" style="width: 100%;">
                    💾 Save Prefix-List Configuration
                </button>
            `;
            break;

        case 'vrf_lite':
            html += `
                <h4>VRF-Lite Configuration</h4>
                <p class="help-text">Virtual Routing and Forwarding without MPLS</p>

                <div class="form-group">
                    <label>VRF Name</label>
                    <input type="text" id="vrf_name" placeholder="CUSTOMER-A" required>
                </div>

                <div class="form-group">
                    <label>Description</label>
                    <input type="text" id="vrf_description" placeholder="Customer A Network">
                </div>

                <div class="form-group">
                    <label>Use VRF Definition (IOS-XE Modern)</label>
                    <select id="vrf_use_definition">
                        <option value="true">vrf definition (IOS-XE)</option>
                        <option value="false">ip vrf (Legacy)</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Route Distinguisher (RD)</label>
                    <input type="text" id="vrf_rd" placeholder="65000:100">
                    <small class="help-text">Format: ASN:nn or IP:nn</small>
                </div>

                <details class="advanced-section">
                    <summary>Route Targets</summary>
                    <div class="form-group">
                        <label>RT Export</label>
                        <input type="text" id="vrf_rt_export" placeholder="65000:100">
                    </div>

                    <div class="form-group">
                        <label>RT Import</label>
                        <input type="text" id="vrf_rt_import" placeholder="65000:100">
                    </div>
                </details>

                <details class="advanced-section">
                    <summary>VRF Interfaces</summary>
                    <div class="form-group">
                        <label>Interface</label>
                        <input type="text" id="vrf_interface" placeholder="GigabitEthernet0/1">
                    </div>

                    <div class="form-group">
                        <label>IP Address (CIDR)</label>
                        <input type="text" id="vrf_ip_address" placeholder="192.168.1.1/24">
                    </div>
                </details>

                <details class="advanced-section">
                    <summary>Route Leaking</summary>
                    <div class="form-group">
                        <label><input type="checkbox" id="vrf_route_leak_enabled"> Enable Route Leaking</label>
                    </div>

                    <div class="form-group">
                        <label>Import from VRF</label>
                        <input type="text" id="vrf_import_from_vrf" placeholder="GLOBAL">
                    </div>

                    <div class="form-group">
                        <label>Import Route-Map</label>
                        <input type="text" id="vrf_import_map" placeholder="IMPORT-FILTER">
                    </div>
                </details>

                <button class="btn btn-primary" onclick="saveVrfLiteData()" style="width: 100%;">
                    💾 Save VRF-Lite Configuration
                </button>
            `;
            break;

        case 'ipv6_advanced':
            html += `
                <h4>IPv6 Advanced Configuration</h4>
                <p class="help-text">DHCPv6, SLAAC, ND, First-Hop Security</p>

                <div class="form-group">
                    <label><input type="checkbox" id="ipv6_enabled" checked> Enable IPv6</label>
                </div>

                <div class="form-group">
                    <label><input type="checkbox" id="ipv6_unicast_routing" checked> IPv6 Unicast Routing</label>
                </div>

                <h5>DHCPv6 Server</h5>
                <div class="form-group">
                    <label><input type="checkbox" id="ipv6_dhcpv6_server_enabled"> Enable DHCPv6 Server</label>
                </div>

                <div class="form-group">
                    <label>Pool Name</label>
                    <input type="text" id="ipv6_dhcpv6_pool_name" placeholder="DHCPV6-POOL1">
                </div>

                <div class="form-group">
                    <label>Address Prefix</label>
                    <input type="text" id="ipv6_dhcpv6_prefix" placeholder="2001:db8::/64">
                </div>

                <div class="form-group">
                    <label>DNS Server</label>
                    <input type="text" id="ipv6_dhcpv6_dns" placeholder="2001:4860:4860::8888">
                </div>

                <div class="form-group">
                    <label>Domain Name</label>
                    <input type="text" id="ipv6_dhcpv6_domain" placeholder="example.com">
                </div>

                <h5>SLAAC (Stateless Address Autoconfiguration)</h5>
                <div class="form-group">
                    <label><input type="checkbox" id="ipv6_slaac_enabled"> Enable SLAAC</label>
                </div>

                <div class="form-group">
                    <label>Interface for SLAAC</label>
                    <input type="text" id="ipv6_slaac_interface" placeholder="GigabitEthernet0/0">
                </div>

                <div class="form-group">
                    <label>ND Prefix</label>
                    <input type="text" id="ipv6_nd_prefix" placeholder="2001:db8::/64">
                </div>

                <details class="advanced-section">
                    <summary>First-Hop Security</summary>

                    <h6>RA Guard</h6>
                    <div class="form-group">
                        <label><input type="checkbox" id="ipv6_ra_guard_enabled"> Enable RA Guard</label>
                    </div>

                    <div class="form-group">
                        <label>Policy Name</label>
                        <input type="text" id="ipv6_ra_guard_policy" placeholder="RA-GUARD-POLICY">
                    </div>

                    <div class="form-group">
                        <label>Device Role</label>
                        <select id="ipv6_ra_guard_role">
                            <option value="host">Host</option>
                            <option value="router">Router</option>
                        </select>
                    </div>

                    <h6>ND Inspection</h6>
                    <div class="form-group">
                        <label><input type="checkbox" id="ipv6_nd_inspection_enabled"> Enable ND Inspection</label>
                    </div>

                    <div class="form-group">
                        <label>Policy Name</label>
                        <input type="text" id="ipv6_nd_inspection_policy" placeholder="ND-INSPECTION">
                    </div>

                    <h6>Source Guard</h6>
                    <div class="form-group">
                        <label><input type="checkbox" id="ipv6_source_guard_enabled"> Enable IPv6 Source Guard</label>
                    </div>

                    <div class="form-group">
                        <label>Policy Name</label>
                        <input type="text" id="ipv6_source_guard_policy" placeholder="SOURCE-GUARD">
                    </div>
                </details>

                <button class="btn btn-primary" onclick="saveIpv6AdvancedData()" style="width: 100%;">
                    💾 Save IPv6 Advanced Configuration
                </button>
            `;
            break;

        case 'route_filtering':
            html += `
                <h4>Route Filtering Configuration</h4>
                <p class="help-text">Distribute-lists for OSPF/EIGRP/BGP</p>

                <div class="form-group">
                    <label>Routing Protocol</label>
                    <select id="rf_protocol">
                        <option value="ospf">OSPF</option>
                        <option value="eigrp">EIGRP</option>
                        <option value="bgp">BGP</option>
                    </select>
                </div>

                <div class="form-group" id="rf_ospf_process_group">
                    <label>OSPF Process ID</label>
                    <input type="number" id="rf_ospf_process" min="1" max="65535" placeholder="1">
                </div>

                <div class="form-group" id="rf_eigrp_asn_group" style="display:none;">
                    <label>EIGRP AS Number</label>
                    <input type="number" id="rf_eigrp_asn" min="1" max="65535" placeholder="100">
                </div>

                <div class="form-group" id="rf_bgp_asn_group" style="display:none;">
                    <label>BGP AS Number</label>
                    <input type="number" id="rf_bgp_asn" min="1" max="4294967295" placeholder="65000">
                </div>

                <h5>Distribute-List Configuration</h5>
                <div class="form-group">
                    <label>Direction</label>
                    <select id="rf_direction">
                        <option value="in">Inbound</option>
                        <option value="out">Outbound</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>Filter Type</label>
                    <select id="rf_filter_type">
                        <option value="acl">Access List</option>
                        <option value="prefix-list">Prefix List</option>
                        <option value="route-map">Route Map</option>
                    </select>
                </div>

                <div class="form-group">
                    <label>ACL/Prefix-List/Route-Map Name</label>
                    <input type="text" id="rf_filter_name" placeholder="FILTER-LIST" required>
                </div>

                <details class="advanced-section">
                    <summary>Per-Interface Filtering</summary>
                    <div class="form-group">
                        <label>Interface (optional)</label>
                        <input type="text" id="rf_interface" placeholder="GigabitEthernet0/0">
                        <small class="help-text">Leave empty for global filtering</small>
                    </div>
                </details>

                <button class="btn btn-primary" onclick="saveRouteFilteringData()" style="width: 100%;">
                    💾 Save Route Filtering Configuration
                </button>

                <script>
                    document.getElementById('rf_protocol')?.addEventListener('change', function() {
                        document.getElementById('rf_ospf_process_group').style.display = this.value === 'ospf' ? 'block' : 'none';
                        document.getElementById('rf_eigrp_asn_group').style.display = this.value === 'eigrp' ? 'block' : 'none';
                        document.getElementById('rf_bgp_asn_group').style.display = this.value === 'bgp' ? 'block' : 'none';
                    });
                </script>
            `;
            break;

        default:
            html += `
                <p>📝 Configuration form for ${protocolData.name}</p>
                <p class="help-text">This protocol form is being implemented.</p>
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
            // Show error message
            statusDiv.innerHTML = `<div class="error">❌ Error: ${result.error || 'Unknown error'}</div>`;

            // Make preview panel visible to show error details
            document.getElementById('preview-panel').style.display = 'block';

            // Check if it's a validation error or rendering error
            if (result.validation) {
                showValidationErrors(result.validation);
            }

            // Show error details in config output
            const configOutput = document.getElementById('config-output');
            if (configOutput) {
                let errorMessage = '# Configuration generation failed\n\n';

                // Check if validation errors exist
                if (result.validation && result.validation.errors && result.validation.errors.length > 0) {
                    errorMessage += '# VALIDATION ERRORS:\n';
                    result.validation.errors.forEach(err => {
                        errorMessage += `# - ${err}\n`;
                    });
                    errorMessage += '\n# Please fix the validation errors above and try again';
                } else {
                    // It's a rendering/template error
                    errorMessage += '# RENDERING ERROR:\n';
                    errorMessage += `# ${result.error || 'Unknown error'}\n\n`;
                    errorMessage += '# This is likely a template error. Check:\n';
                    errorMessage += '# - Protocol configuration data structure\n';
                    errorMessage += '# - Template syntax in config_templates/\n';
                    errorMessage += '# - Missing required fields in protocol forms';
                }

                configOutput.textContent = errorMessage;
            }
        }
    } catch (error) {
        statusDiv.innerHTML = `<div class="error">❌ Network error: ${error.message}</div>`;
    }
}

// Show validation errors
function showValidationErrors(validation) {
    const validationDiv = document.getElementById('validation-results');
    if (!validationDiv) return;

    let html = '';

    if (validation.errors && validation.errors.length > 0) {
        html += `<h4 style="color: #e74c3c; margin-top: 0;">❌ Validation Errors (${validation.errors.length})</h4>`;
        html += '<ul style="color: #e74c3c; margin-bottom: 20px;">' +
                validation.errors.map(e => `<li><strong>${e}</strong></li>`).join('') +
                '</ul>';
    }

    if (validation.warnings && validation.warnings.length > 0) {
        html += `<h4 style="color: #f39c12;">⚠️ Warnings (${validation.warnings.length})</h4>`;
        html += '<ul style="color: #f39c12;">' +
                validation.warnings.map(w => `<li>${w}</li>`).join('') +
                '</ul>';
    }

    if (!validation.errors || validation.errors.length === 0) {
        if (!validation.warnings || validation.warnings.length === 0) {
            html = '<p style="color: #27ae60;">✅ Configuration validation passed</p>';
        }
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
