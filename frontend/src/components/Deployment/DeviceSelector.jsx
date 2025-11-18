import React from 'react'
import { Card, Table, Tag, Alert } from 'antd'
import { CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons'
import { useQuery } from 'react-query'
import { deviceAPI } from '../../services/api'

export default function DeviceSelector({ selectedDevices, onSelectionChange }) {
  const { data: devices, isLoading } = useQuery('devices', () =>
    deviceAPI.getAll().then((res) => res.data)
  )

  const rowSelection = {
    selectedRowKeys: selectedDevices,
    onChange: (selectedRowKeys) => {
      onSelectionChange(selectedRowKeys)
    },
    getCheckboxProps: (record) => ({
      disabled: record.status === 'unreachable',
    }),
  }

  const columns = [
    {
      title: 'Hostname',
      dataIndex: 'hostname',
      key: 'hostname',
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'IP Address',
      dataIndex: 'ip_address',
      key: 'ip_address',
    },
    {
      title: 'Platform',
      dataIndex: 'platform',
      key: 'platform',
      render: (platform) => (
        <Tag color={platform === 'ios' ? 'blue' : platform === 'nxos' ? 'green' : 'orange'}>
          {platform?.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const isReachable = status === 'reachable'
        return (
          <Tag
            icon={isReachable ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
            color={isReachable ? 'success' : 'error'}
          >
            {status}
          </Tag>
        )
      },
    },
  ]

  return (
    <Card title="Select Target Devices">
      <Alert
        message="Select devices for configuration deployment"
        description="Only reachable devices can be selected. Unreachable devices are disabled."
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Table
        rowSelection={rowSelection}
        columns={columns}
        dataSource={devices || []}
        loading={isLoading}
        rowKey="id"
        pagination={{ pageSize: 10 }}
      />

      <div style={{ marginTop: 16 }}>
        <strong>Selected devices: {selectedDevices.length}</strong>
      </div>
    </Card>
  )
}
