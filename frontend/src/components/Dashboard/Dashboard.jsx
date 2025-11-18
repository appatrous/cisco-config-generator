import React, { useState } from 'react'
import { Row, Col, Card, Statistic, Space, Button } from 'antd'
import {
  DatabaseOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  PlusOutlined,
  UploadOutlined,
} from '@ant-design/icons'
import { useQuery } from 'react-query'
import InventoryTable from './InventoryTable'
import BulkImport from './BulkImport'
import AddDeviceModal from './AddDeviceModal'
import { deviceAPI } from '../../services/api'

export default function Dashboard() {
  const [bulkImportOpen, setBulkImportOpen] = useState(false)
  const [addDeviceOpen, setAddDeviceOpen] = useState(false)

  // Fetch devices
  const { data: devices, isLoading, refetch } = useQuery(
    'devices',
    () => deviceAPI.getAll().then(res => res.data),
    {
      refetchInterval: 30000, // Auto-refresh every 30s
    }
  )

  // Calculate statistics
  const stats = React.useMemo(() => {
    if (!devices) return { total: 0, reachable: 0, unreachable: 0, unknown: 0 }

    return {
      total: devices.length,
      reachable: devices.filter(d => d.status === 'reachable').length,
      unreachable: devices.filter(d => d.status === 'unreachable').length,
      unknown: devices.filter(d => d.status === 'unknown').length,
    }
  }, [devices])

  return (
    <div>
      <div style={{ marginBottom: 24, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1 style={{ margin: 0 }}>Device Inventory Dashboard</h1>
        <Space>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setAddDeviceOpen(true)}
          >
            Add Device
          </Button>
          <Button
            icon={<UploadOutlined />}
            onClick={() => setBulkImportOpen(true)}
          >
            Import CSV
          </Button>
          <Button
            icon={<SyncOutlined />}
            onClick={() => refetch()}
            loading={isLoading}
          >
            Refresh
          </Button>
        </Space>
      </div>

      {/* Statistics Cards */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Devices"
              value={stats.total}
              prefix={<DatabaseOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Reachable"
              value={stats.reachable}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Unreachable"
              value={stats.unreachable}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Unknown"
              value={stats.unknown}
              prefix={<SyncOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Device Table */}
      <InventoryTable devices={devices || []} isLoading={isLoading} refetch={refetch} />

      {/* Modals */}
      <BulkImport
        open={bulkImportOpen}
        onClose={() => setBulkImportOpen(false)}
        onSuccess={() => {
          setBulkImportOpen(false)
          refetch()
        }}
      />

      <AddDeviceModal
        open={addDeviceOpen}
        onClose={() => setAddDeviceOpen(false)}
        onSuccess={() => {
          setAddDeviceOpen(false)
          refetch()
        }}
      />
    </div>
  )
}
