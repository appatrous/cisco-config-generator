import React, { useState } from 'react'
import { Card, Select, DatePicker, Space, Button, Row, Col, Statistic } from 'antd'
import { useQuery } from 'react-query'
import { useSearchParams } from 'react-router-dom'
import {
  HistoryOutlined,
  UserOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import HistoryTimeline from './HistoryTimeline'
import { deviceAPI, auditAPI } from '../../services/api'

const { RangePicker } = DatePicker

export default function TimelinePage() {
  const [searchParams] = useSearchParams()
  const preselectedDevice = searchParams.get('device')

  const [filters, setFilters] = useState({
    device_id: preselectedDevice ? parseInt(preselectedDevice) : null,
    user_id: null,
    action: null,
    dateRange: [dayjs().subtract(30, 'days'), dayjs()],
  })

  // Fetch devices for filter
  const { data: devices } = useQuery('devices', () =>
    deviceAPI.getAll().then((res) => res.data)
  )

  // Fetch history
  const { data: history, isLoading, refetch } = useQuery(
    ['history', filters],
    () => {
      const params = {
        device_id: filters.device_id,
        user_id: filters.user_id,
        action: filters.action,
        start_date: filters.dateRange?.[0]?.format('YYYY-MM-DD'),
        end_date: filters.dateRange?.[1]?.format('YYYY-MM-DD'),
      }
      return filters.device_id
        ? auditAPI.getDeviceHistory(filters.device_id, params).then((res) => res.data)
        : auditAPI.getHistory(params).then((res) => res.data)
    },
    {
      enabled: true,
    }
  )

  // Calculate statistics
  const stats = React.useMemo(() => {
    if (!history) return { total: 0, deployments: 0, success: 0, failed: 0 }

    return {
      total: history.length,
      deployments: history.filter((h) => h.action === 'deploy_config').length,
      success: history.filter((h) => h.status === 'success').length,
      failed: history.filter((h) => h.status === 'failed').length,
    }
  }, [history])

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Change History & Timeline</h1>

      {/* Statistics */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Total Changes"
              value={stats.total}
              prefix={<HistoryOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Deployments"
              value={stats.deployments}
              prefix={<SyncOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Successful"
              value={stats.success}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} md={6}>
          <Card>
            <Statistic
              title="Failed"
              value={stats.failed}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#f5222d' }}
            />
          </Card>
        </Col>
      </Row>

      {/* Filters */}
      <Card title="Filters" style={{ marginBottom: 24 }}>
        <Space wrap size="middle">
          <div>
            <label style={{ display: 'block', marginBottom: 4, fontSize: '12px' }}>
              Device
            </label>
            <Select
              placeholder="All devices"
              style={{ width: 200 }}
              value={filters.device_id}
              onChange={(value) => setFilters({ ...filters, device_id: value })}
              allowClear
            >
              {devices?.map((device) => (
                <Select.Option key={device.id} value={device.id}>
                  {device.hostname}
                </Select.Option>
              ))}
            </Select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: 4, fontSize: '12px' }}>
              Action
            </label>
            <Select
              placeholder="All actions"
              style={{ width: 180 }}
              value={filters.action}
              onChange={(value) => setFilters({ ...filters, action: value })}
              allowClear
            >
              <Select.Option value="deploy_config">Deploy Config</Select.Option>
              <Select.Option value="rollback">Rollback</Select.Option>
              <Select.Option value="create_device">Create Device</Select.Option>
              <Select.Option value="update_device">Update Device</Select.Option>
              <Select.Option value="delete_device">Delete Device</Select.Option>
            </Select>
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: 4, fontSize: '12px' }}>
              Date Range
            </label>
            <RangePicker
              value={filters.dateRange}
              onChange={(dates) => setFilters({ ...filters, dateRange: dates })}
              presets={[
                { label: 'Last 7 Days', value: [dayjs().subtract(7, 'days'), dayjs()] },
                { label: 'Last 30 Days', value: [dayjs().subtract(30, 'days'), dayjs()] },
                { label: 'Last 90 Days', value: [dayjs().subtract(90, 'days'), dayjs()] },
              ]}
            />
          </div>

          <Button
            type="primary"
            onClick={() => refetch()}
            style={{ marginTop: 20 }}
          >
            Apply Filters
          </Button>
        </Space>
      </Card>

      {/* Timeline */}
      <HistoryTimeline history={history || []} isLoading={isLoading} />
    </div>
  )
}
