import React from 'react'
import { Layout } from 'antd'

const { Footer } = Layout

export default function AppFooter() {
  return (
    <Footer style={{ textAlign: 'center', background: '#f0f2f5' }}>
      <div>
        Network Configuration Generator v2.0 | Multi-Vendor NetDevOps Tool
      </div>
      <div style={{ fontSize: '12px', color: '#8c8c8c', marginTop: '4px' }}>
        Supports: Cisco IOS/IOS-XE/NX-OS • Arista EOS • Juniper Junos • FRRouting
      </div>
    </Footer>
  )
}
