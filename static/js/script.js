/*
 * Client-side interactivity for Cisco Configuration Generator.
 *
 * Handles dynamic addition/removal of form entries, toggles the
 * visibility of optional sections (OSPF and AAA), collects form
 * data and submits to the back end for processing.  The result
 * pages handle tab switching inline.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Utility to add an entry clone within a container
  function addEntry(containerId, entryClass) {
    const container = document.getElementById(containerId);
    const first = container.querySelector('.' + entryClass);
    const clone = first.cloneNode(true);
    // Clear input values in clone
    clone.querySelectorAll('input').forEach(input => input.value = '');
    container.appendChild(clone);
    attachRemoveHandlers(clone);
  }
  // Attach remove handlers to remove buttons in a given element
  function attachRemoveHandlers(element) {
    const buttons = element.querySelectorAll('.remove-btn');
    buttons.forEach(btn => {
      btn.onclick = () => {
        const row = btn.closest('.row');
        const container = btn.closest('.dynamic-container');
        if (container.children.length > 1) {
          row.remove();
        } else {
          // clear the only entry
          row.querySelectorAll('input').forEach(input => input.value = '');
        }
      };
    });
  }
  // Initialise remove handlers for all existing entries
  document.querySelectorAll('.dynamic-container').forEach(container => {
    attachRemoveHandlers(container);
  });
  // Add buttons
  const addRouteBtn = document.getElementById('addStaticRoute');
  if (addRouteBtn) addRouteBtn.addEventListener('click', () => addEntry('staticRoutesContainer', 'route-entry'));
  const addNetBtn = document.getElementById('addOspfNetwork');
  if (addNetBtn) addNetBtn.addEventListener('click', () => addEntry('ospfNetworksContainer', 'network-entry'));
  const addVlanBtn = document.getElementById('addVlan');
  if (addVlanBtn) addVlanBtn.addEventListener('click', () => addEntry('vlanContainer', 'vlan-entry'));
  const addNtpBtn = document.getElementById('addNtpServer');
  if (addNtpBtn) addNtpBtn.addEventListener('click', () => addEntry('ntpContainer', 'ntp-entry'));
  const addTacBtn = document.getElementById('addTacacsServer');
  if (addTacBtn) addTacBtn.addEventListener('click', () => addEntry('tacacsContainer', 'tacacs-entry'));
  const addRadBtn = document.getElementById('addRadiusServer');
  if (addRadBtn) addRadBtn.addEventListener('click', () => addEntry('radiusContainer', 'radius-entry'));
  const addUserBtn = document.getElementById('addLocalUser');
  if (addUserBtn) addUserBtn.addEventListener('click', () => addEntry('localUsersContainer', 'user-entry'));

  // Additional dynamic add handlers for new protocol forms
  // EIGRP networks
  const addEigrpNetworkBtn = document.getElementById('addEigrpNetwork');
  if (addEigrpNetworkBtn) addEigrpNetworkBtn.addEventListener('click', () => addEntry('eigrpNetworksContainer', 'eigrp-network-entry'));
  // VRRP groups
  const addVrrpGroupBtn = document.getElementById('addVrrpGroup');
  if (addVrrpGroupBtn) addVrrpGroupBtn.addEventListener('click', () => addEntry('vrrpContainer', 'vrrp-entry'));
  // HSRP groups
  const addHsrpGroupBtn = document.getElementById('addHsrpGroup');
  if (addHsrpGroupBtn) addHsrpGroupBtn.addEventListener('click', () => addEntry('hsrpContainer', 'hsrp-entry'));
  // GLBP groups
  const addGlbpGroupBtn = document.getElementById('addGlbpGroup');
  if (addGlbpGroupBtn) addGlbpGroupBtn.addEventListener('click', () => addEntry('glbpContainer', 'glbp-entry'));

  // New dynamic add handlers for additional protocol pages
  const addRipNetworkBtn = document.getElementById('addRipNetwork');
  if (addRipNetworkBtn) addRipNetworkBtn.addEventListener('click', () => addEntry('ripNetworksContainer', 'rip-network-entry'));
  const addVrfBtn = document.getElementById('addVrf');
  if (addVrfBtn) addVrfBtn.addEventListener('click', () => addEntry('vrfContainer', 'vrf-entry'));
  const addGreTunnelBtn = document.getElementById('addGreTunnel');
  if (addGreTunnelBtn) addGreTunnelBtn.addEventListener('click', () => addEntry('greContainer', 'gre-entry'));
  const addDhcpPoolBtn = document.getElementById('addDhcpPool');
  if (addDhcpPoolBtn) addDhcpPoolBtn.addEventListener('click', () => addEntry('dhcpPoolsContainer', 'dhcp-pool-entry'));
  const addDhcpRelayBtn = document.getElementById('addDhcpRelay');
  if (addDhcpRelayBtn) addDhcpRelayBtn.addEventListener('click', () => addEntry('dhcpRelaysContainer', 'dhcp-relay-entry'));
  const addEtherChannelBtn = document.getElementById('addEtherChannel');
  if (addEtherChannelBtn) addEtherChannelBtn.addEventListener('click', () => addEntry('etherChannelContainer', 'etherchannel-entry'));
  const addSpanSessionBtn = document.getElementById('addSpanSession');
  if (addSpanSessionBtn) addSpanSessionBtn.addEventListener('click', () => addEntry('spanContainer', 'span-entry'));
  const addAclEntryBtn = document.getElementById('addAclEntry');
  if (addAclEntryBtn) addAclEntryBtn.addEventListener('click', () => addEntry('aclContainer', 'acl-entry'));
  const addObjectGroupBtn = document.getElementById('addObjectGroup');
  if (addObjectGroupBtn) addObjectGroupBtn.addEventListener('click', () => addEntry('objectGroupContainer', 'object-group-entry'));
  const addUrpfBtn = document.getElementById('addUrpf');
  if (addUrpfBtn) addUrpfBtn.addEventListener('click', () => addEntry('urpfContainer', 'urpf-entry'));

  // New dynamic add handlers for remaining protocol pages
  const addIgmpBtn = document.getElementById('addIgmp');
  if (addIgmpBtn) addIgmpBtn.addEventListener('click', () => addEntry('igmpContainer', 'igmp-entry'));
  const addPimInterfaceBtn = document.getElementById('addPimInterface');
  if (addPimInterfaceBtn) addPimInterfaceBtn.addEventListener('click', () => addEntry('pimInterfacesContainer', 'pim-interface-entry'));
  const addQosClassBtn = document.getElementById('addQosClass');
  if (addQosClassBtn) addQosClassBtn.addEventListener('click', () => addEntry('qosContainer', 'qos-entry'));
  const addPvlanBtn = document.getElementById('addPvlan');
  if (addPvlanBtn) addPvlanBtn.addEventListener('click', () => addEntry('pvlanContainer', 'pvlan-entry'));
  const addVoiceVlanBtn = document.getElementById('addVoiceVlan');
  if (addVoiceVlanBtn) addVoiceVlanBtn.addEventListener('click', () => addEntry('voiceVlanContainer', 'voice-entry'));
  const addStackMemberBtn = document.getElementById('addStackMember');
  if (addStackMemberBtn) addStackMemberBtn.addEventListener('click', () => addEntry('stackwiseContainer', 'stack-entry'));
  const addIpSourceGuardBtn = document.getElementById('addIpSourceGuard');
  if (addIpSourceGuardBtn) addIpSourceGuardBtn.addEventListener('click', () => addEntry('ipsgContainer', 'ipsg-entry'));
  const addZoneBtn = document.getElementById('addZone');
  if (addZoneBtn) addZoneBtn.addEventListener('click', () => addEntry('zoneContainer', 'zone-entry'));
  const addZonePairBtn = document.getElementById('addZonePair');
  if (addZonePairBtn) addZonePairBtn.addEventListener('click', () => addEntry('zonePairContainer', 'zonepair-entry'));
  const addNetflowCollectorBtn = document.getElementById('addNetflowCollector');
  if (addNetflowCollectorBtn) addNetflowCollectorBtn.addEventListener('click', () => addEntry('netflowCollectorsContainer', 'netflow-collector-entry'));
  const addEemPolicyBtn = document.getElementById('addEemPolicy');
  if (addEemPolicyBtn) addEemPolicyBtn.addEventListener('click', () => addEntry('eemContainer', 'eem-entry'));

  // AAA, SNMP and Syslog dynamic handlers
  const addSnmpCommunityBtn = document.getElementById('addSnmpCommunity');
  if (addSnmpCommunityBtn) addSnmpCommunityBtn.addEventListener('click', () => addEntry('snmpCommunitiesContainer', 'snmp-community-entry'));
  const addSnmpV3UserBtn = document.getElementById('addSnmpV3User');
  if (addSnmpV3UserBtn) addSnmpV3UserBtn.addEventListener('click', () => addEntry('snmpV3UsersContainer', 'snmp-v3-user-entry'));
  const addSnmpTrapBtn = document.getElementById('addSnmpTrap');
  if (addSnmpTrapBtn) addSnmpTrapBtn.addEventListener('click', () => addEntry('snmpTrapContainer', 'snmp-trap-entry'));
  const addSyslogServerBtn = document.getElementById('addSyslogServer');
  if (addSyslogServerBtn) addSyslogServerBtn.addEventListener('click', () => addEntry('syslogServersContainer', 'syslog-server-entry'));
  // Toggle OSPF fields
  const ospfCheckbox = document.getElementById('ospf_enable');
  if (ospfCheckbox) ospfCheckbox.addEventListener('change', () => {
    document.getElementById('ospfFields').classList.toggle('hidden', !ospfCheckbox.checked);
  });
  // Toggle AAA fields
  const aaaCheckbox = document.getElementById('aaa_enable');
  if (aaaCheckbox) aaaCheckbox.addEventListener('change', () => {
    document.getElementById('aaaFields').classList.toggle('hidden', !aaaCheckbox.checked);
  });
});