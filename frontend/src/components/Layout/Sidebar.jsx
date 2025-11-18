import React from 'react'
import { Layout, Menu } from 'antd'
import { useNavigate, useLocation } from 'react-router-dom'
import {
  DashboardOutlined,
  DatabaseOutlined,
  RocketOutlined,
  DiffOutlined,
  HistoryOutlined,
  ToolOutlined,
  SettingOutlined,
} from '@ant-design/icons'

const { Sider } = Layout

export default function AppSidebar({ collapsed }) {
  const navigate = useNavigate()
  const location = useLocation()

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: 'Dashboard',
    },
    {
      key: '/inventory',
      icon: <DatabaseOutlined />,
      label: 'Device Inventory',
    },
    {
      key: '/deployment',
      icon: <RocketOutlined />,
      label: 'Deployment',
    },
    {
      key: '/diff',
      icon: <DiffOutlined />,
      label: 'Config Compare',
    },
    {
      key: '/history',
      icon: <HistoryOutlined />,
      label: 'Change History',
    },
    {
      type: 'divider',
    },
    {
      key: '/generator',
      icon: <ToolOutlined />,
      label: 'Config Generator',
    },
    {
      key: '/settings',
      icon: <SettingOutlined />,
      label: 'Settings',
    },
  ]

  const handleMenuClick = ({ key }) => {
    navigate(key)
  }

  return (
    <Sider
      collapsible
      collapsed={collapsed}
      trigger={null}
      width={250}
      style={{
        overflow: 'auto',
        height: '100vh',
        position: 'sticky',
        left: 0,
        top: 0,
        bottom: 0,
      }}
    >
      <div
        style={{
          height: 64,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: '20px',
          fontWeight: 'bold',
          borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
        }}
      >
        {!collapsed ? '🌐 NetConfig' : '🌐'}
      </div>

      <Menu
        theme="dark"
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        onClick={handleMenuClick}
        style={{ borderRight: 0 }}
      />
    </Sider>
  )
}
