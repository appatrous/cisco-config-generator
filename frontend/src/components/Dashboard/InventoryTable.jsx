import React, { useState } from 'react'
import { Table, Tag, Space, Button, Input, Select, message, Popconfirm, Tooltip } from 'antd'
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  SearchOutlined,
  RocketOutlined,
  DeleteOutlined,
  EditOutlined,
  HistoryOutlined,
  ApiOutlined,
} from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import { deviceAPI } from '../../services/api'

dayjs.extend(relativeTime)

export default function InventoryTable({ devices, isLoading, refetch }) {
  const navigate = useNavigate()
  const [filters, setFilters] = useState({
    search: '',
    platform: null,
    status: null,
  })
  const [pinging, setPinging] = useState({})

  // Filter devices
  const filteredDevices = React.useMemo(() => {
    let result = devices

    if (filters.search) {
      const search = filters.search.toLowerCase()
      result = result.filter(d =>
        d.hostname?.toLowerCase().includes(search) ||
        d.ip_address?.toLowerCase().includes(search) ||
        d.location?.toLowerCase().includes(search)
      )
    }

    if (filters.platform) {
      result = result.filter(d => d.platform === filters.platform)
    }

    if (filters.status) {
      result = result.filter(d => d.status === filters.status)
    }

    return result
  }, [devices, filters])

  const handlePing = async (device) => {
    setPinging({ ...pinging, [device.id]: true })
    try {
      const response = await deviceAPI.ping(device.id)
      if (response.data.alive) {
        message.success(`${device.hostname} is reachable`)
      } else {
        message.error(`${device.hostname} is unreachable`)
      }
      refetch()
    } catch (error) {
      message.error('Failed to ping device')
    } finally {
      setPinging({ ...pinging, [device.id]: false })
    }
  }

  const handleDelete = async (id) => {
    try {
      await deviceAPI.delete(id)
      message.success('Device deleted successfully')
      refetch()
    } catch (error) {
      message.error('Failed to delete device')
    }
  }

  const columns = [
    {
      title: 'Hostname',
      dataIndex: 'hostname',
      key: 'hostname',
      sorter: (a, b) => (a.hostname || '').localeCompare(b.hostname || ''),
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'IP Address',
      dataIndex: 'ip_address',
      key: 'ip_address',
      render: (text) => <code style={{ background: '#f5f5f5', padding: '2px 6px', borderRadius: '4px' }}>{text}</code>,
    },
    {
      title: 'Platform',
      dataIndex: 'platform',
      key: 'platform',
      filters: [
        { text: 'IOS', value: 'ios' },
        { text: 'NX-OS', value: 'nxos' },
        { text: 'ASA', value: 'asa' },
        { text: 'EOS', value: 'eos' },
        { text: 'Junos', value: 'junos' },
      ],
      onFilter: (value, record) => record.platform === value,
      render: (platform) => {
        const colors = {
          ios: 'blue',
          nxos: 'green',
          asa: 'orange',
          eos: 'purple',
          junos: 'cyan',
        }
        return (
          <Tag color={colors[platform] || 'default'}>
            {platform?.toUpperCase() || 'UNKNOWN'}
          </Tag>
        )
      },
    },
    {
      title: 'Type',
      dataIndex: 'device_type',
      key: 'device_type',
      render: (type) => type || 'N/A',
    },
    {
      title: 'Location',
      dataIndex: 'location',
      key: 'location',
      render: (text) => text || '-',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      filters: [
        { text: 'Reachable', value: 'reachable' },
        { text: 'Unreachable', value: 'unreachable' },
        { text: 'Unknown', value: 'unknown' },
      ],
      onFilter: (value, record) => record.status === value,
      render: (status) => {
        const config = {
          reachable: { icon: <CheckCircleOutlined />, color: 'success', text: 'Reachable' },
          unreachable: { icon: <CloseCircleOutlined />, color: 'error', text: 'Unreachable' },
          unknown: { icon: <SyncOutlined />, color: 'warning', text: 'Unknown' },
        }
        const { icon, color, text } = config[status] || config.unknown
        return <Tag icon={icon} color={color}>{text}</Tag>
      },
    },
    {
      title: 'Last Seen',
      dataIndex: 'last_seen',
      key: 'last_seen',
      sorter: (a, b) => {
        if (!a.last_seen) return 1
        if (!b.last_seen) return -1
        return new Date(a.last_seen) - new Date(b.last_seen)
      },
      render: (date) => date ? (
        <Tooltip title={dayjs(date).format('YYYY-MM-DD HH:mm:ss')}>
          {dayjs(date).fromNow()}
        </Tooltip>
      ) : 'Never',
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="small">
          <Tooltip title="Test Connectivity">
            <Button
              size="small"
              icon={<ApiOutlined />}
              loading={pinging[record.id]}
              onClick={() => handlePing(record)}
            />
          </Tooltip>
          <Tooltip title="Deploy Config">
            <Button
              size="small"
              type="primary"
              icon={<RocketOutlined />}
              onClick={() => navigate(`/deployment?device=${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="View History">
            <Button
              size="small"
              icon={<HistoryOutlined />}
              onClick={() => navigate(`/history?device=${record.id}`)}
            />
          </Tooltip>
          <Tooltip title="Edit">
            <Button
              size="small"
              icon={<EditOutlined />}
              onClick={() => {/* TODO: Open edit modal */}}
            />
          </Tooltip>
          <Popconfirm
            title="Delete device?"
            description="This action cannot be undone."
            onConfirm={() => handleDelete(record.id)}
            okText="Yes"
            cancelText="No"
          >
            <Tooltip title="Delete">
              <Button
                size="small"
                danger
                icon={<DeleteOutlined />}
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ]

  return (
    <div>
      {/* Filters */}
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="Search hostname, IP or location"
          prefix={<SearchOutlined />}
          value={filters.search}
          onChange={(e) => setFilters({ ...filters, search: e.target.value })}
          style={{ width: 300 }}
          allowClear
        />
        <Select
          placeholder="Platform"
          value={filters.platform}
          onChange={(value) => setFilters({ ...filters, platform: value })}
          style={{ width: 120 }}
          allowClear
        >
          <Select.Option value="ios">IOS</Select.Option>
          <Select.Option value="nxos">NX-OS</Select.Option>
          <Select.Option value="asa">ASA</Select.Option>
          <Select.Option value="eos">EOS</Select.Option>
          <Select.Option value="junos">Junos</Select.Option>
        </Select>
        <Select
          placeholder="Status"
          value={filters.status}
          onChange={(value) => setFilters({ ...filters, status: value })}
          style={{ width: 140 }}
          allowClear
        >
          <Select.Option value="reachable">Reachable</Select.Option>
          <Select.Option value="unreachable">Unreachable</Select.Option>
          <Select.Option value="unknown">Unknown</Select.Option>
        </Select>
      </Space>

      {/* Table */}
      <Table
        columns={columns}
        dataSource={filteredDevices}
        loading={isLoading}
        rowKey="id"
        pagination={{
          pageSize: 20,
          showSizeChanger: true,
          showTotal: (total) => `Total ${total} devices`,
        }}
        scroll={{ x: 1200 }}
      />
    </div>
  )
}
