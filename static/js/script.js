/*
 * Client-side interactivity for Cisco Configuration Generator.
 *
 * Handles dynamic addition/removal of form entries, toggles the
 * visibility of optional sections (OSPF and AAA), collects form
 * data and submits to the back end for processing.  The result
 * pages handle tab switching inline.
 */

(() => {
  const dynamicSections = [
    ['addStaticRoute', 'staticRoutesContainer', 'route-entry'],
    ['addOspfNetwork', 'ospfNetworksContainer', 'network-entry'],
    ['addVlan', 'vlanContainer', 'vlan-entry'],
    ['addNtpServer', 'ntpContainer', 'ntp-entry'],
    ['addTacacsServer', 'tacacsContainer', 'tacacs-entry'],
    ['addRadiusServer', 'radiusContainer', 'radius-entry'],
    ['addLocalUser', 'localUsersContainer', 'user-entry'],
    ['addEigrpNetwork', 'eigrpNetworksContainer', 'eigrp-network-entry'],
    ['addVrrpGroup', 'vrrpContainer', 'vrrp-entry'],
    ['addHsrpGroup', 'hsrpContainer', 'hsrp-entry'],
    ['addGlbpGroup', 'glbpContainer', 'glbp-entry'],
    ['addRipNetwork', 'ripNetworksContainer', 'rip-network-entry'],
    ['addVrf', 'vrfContainer', 'vrf-entry'],
    ['addGreTunnel', 'greContainer', 'gre-entry'],
    ['addDhcpPool', 'dhcpPoolsContainer', 'dhcp-pool-entry'],
    ['addDhcpRelay', 'dhcpRelaysContainer', 'dhcp-relay-entry'],
    ['addEtherChannel', 'etherChannelContainer', 'etherchannel-entry'],
    ['addSpanSession', 'spanContainer', 'span-entry'],
    ['addAclEntry', 'aclContainer', 'acl-entry'],
    ['addObjectGroup', 'objectGroupContainer', 'object-group-entry'],
    ['addUrpf', 'urpfContainer', 'urpf-entry'],
    ['addIgmp', 'igmpContainer', 'igmp-entry'],
    ['addPimInterface', 'pimInterfacesContainer', 'pim-interface-entry'],
    ['addQosClass', 'qosContainer', 'qos-entry'],
    ['addPvlan', 'pvlanContainer', 'pvlan-entry'],
    ['addVoiceVlan', 'voiceVlanContainer', 'voice-entry'],
    ['addStackMember', 'stackwiseContainer', 'stack-entry'],
    ['addIpSourceGuard', 'ipsgContainer', 'ipsg-entry'],
    ['addZone', 'zoneContainer', 'zone-entry'],
    ['addZonePair', 'zonePairContainer', 'zonepair-entry'],
    ['addNetflowCollector', 'netflowCollectorsContainer', 'netflow-collector-entry'],
    ['addEemPolicy', 'eemContainer', 'eem-entry'],
    ['addSnmpCommunity', 'snmpCommunitiesContainer', 'snmp-community-entry'],
    ['addSnmpV3User', 'snmpV3UsersContainer', 'snmp-v3-user-entry'],
    ['addSnmpTrap', 'snmpTrapContainer', 'snmp-trap-entry'],
    ['addSyslogServer', 'syslogServersContainer', 'syslog-server-entry'],
  ];

  function clearInputs(element) {
    element.querySelectorAll('input').forEach((input) => {
      input.value = '';
      input.classList.remove('is-valid', 'is-invalid');
      input.removeAttribute('aria-invalid');
    });
    element.querySelectorAll('select').forEach((select) => {
      select.selectedIndex = 0;
      select.classList.remove('is-valid', 'is-invalid');
      select.removeAttribute('aria-invalid');
    });
  }

  function registerRemoveButtons(scope, form) {
    scope.querySelectorAll('.remove-btn').forEach((btn) => {
      if (btn.dataset.handlerAttached === 'true') {
        return;
      }
      btn.dataset.handlerAttached = 'true';
      btn.addEventListener('click', () => {
        const row = btn.closest('.row');
        const container = btn.closest('.dynamic-container');
        if (!row || !container) {
          return;
        }
        if (container.children.length > 1) {
          row.remove();
        } else {
          clearInputs(row);
        }
        if (form) {
          form.classList.remove('was-validated');
        }
      });
    });
  }

  function registerDynamicSection([buttonId, containerId, entryClass], form) {
    const button = document.getElementById(buttonId);
    const container = document.getElementById(containerId);
    if (!button || !container) {
      return;
    }
    const firstEntry = container.querySelector(`.${entryClass}`);
    if (!firstEntry) {
      return;
    }
    button.addEventListener('click', () => {
      const clone = firstEntry.cloneNode(true);
      clearInputs(clone);
      container.appendChild(clone);
      registerRemoveButtons(clone, form);
      if (form) {
        form.classList.remove('was-validated');
      }
    });
  }

  function initToggle(checkboxId, targetId, form, hiddenClass = 'hidden') {
    const checkbox = document.getElementById(checkboxId);
    const target = document.getElementById(targetId);
    if (!checkbox || !target) {
      return;
    }
    const update = () => {
      const hidden = !checkbox.checked;
      target.classList.toggle(hiddenClass, hidden);
      target.querySelectorAll('input, select, textarea').forEach((input) => {
        input.disabled = hidden;
        if (hidden) {
          input.classList.remove('is-invalid', 'is-valid');
          input.removeAttribute('aria-invalid');
        }
      });
      if (hidden && form) {
        form.classList.remove('was-validated');
      }
    };
    update();
    checkbox.addEventListener('change', update);
  }

  function initFormValidation(form) {
    if (!form) {
      return;
    }
    form.addEventListener('submit', (event) => {
      if (!form.checkValidity()) {
        event.preventDefault();
        event.stopPropagation();
      }
      form.classList.add('was-validated');
    });

    form.addEventListener(
      'input',
      (event) => {
        const target = event.target;
        if (!(target instanceof HTMLInputElement || target instanceof HTMLSelectElement)) {
          return;
        }
        if (!form.classList.contains('was-validated')) {
          return;
        }
        if (target.checkValidity()) {
          target.classList.remove('is-invalid');
        }
      },
      true,
    );
  }

  document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('configForm');
    if (!form) {
      return;
    }

    document.querySelectorAll('.dynamic-container').forEach((container) => {
      registerRemoveButtons(container, form);
    });

    dynamicSections.forEach((section) => registerDynamicSection(section, form));

    initToggle('ospf_enable', 'ospfFields', form);
    initToggle('aaa_enable', 'aaaFields', form);
    initFormValidation(form);
  });
})();
