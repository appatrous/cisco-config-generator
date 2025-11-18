import React from 'react'
import { Routes, Route } from 'react-router-dom'
import { Layout } from 'antd'
import AppHeader from './components/Layout/Header'
import AppSidebar from './components/Layout/Sidebar'
import AppFooter from './components/Layout/Footer'
import Dashboard from './components/Dashboard/Dashboard'
import DeploymentPage from './components/Deployment/DeploymentPage'
import DiffPage from './components/Diff/DiffPage'
import TimelinePage from './components/Timeline/TimelinePage'
import ConfigGeneratorPage from './components/ConfigGenerator/ConfigGeneratorPage'

const { Content } = Layout

function App() {
  const [collapsed, setCollapsed] = React.useState(false)

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <AppSidebar collapsed={collapsed} />
      <Layout>
        <AppHeader collapsed={collapsed} setCollapsed={setCollapsed} />
        <Content style={{ margin: '24px 16px', padding: 24, background: '#fff' }}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/inventory" element={<Dashboard />} />
            <Route path="/deployment" element={<DeploymentPage />} />
            <Route path="/diff" element={<DiffPage />} />
            <Route path="/history" element={<TimelinePage />} />
            <Route path="/generator" element={<ConfigGeneratorPage />} />
          </Routes>
        </Content>
        <AppFooter />
      </Layout>
    </Layout>
  )
}

export default App
