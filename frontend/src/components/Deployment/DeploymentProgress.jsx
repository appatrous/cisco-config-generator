import React, { useState, useEffect } from 'react'
import { Card, Progress, Table, Button, Tag, Modal, Space, Alert } from 'antd'
import {
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import { deploymentAPI } from '../../services/api'
import { message } from 'antd'

export default function DeploymentProgress({
  selectedDevices,
  configText,
  dryRun,
  onDeployStart,
  deploymentData,
}) {
  const [deploying, setDeploying] = useState(false)
  const [deployments, setDeployments] = useState([])
  const [progress, setProgress] = useState(0)
  const [taskId, setTaskId] = useState(null)
  const [logsModalOpen, setLogsModalOpen] = useState(false)
  const [selectedLogs, setSelectedLogs] = useState('')

  const startDeployment = async () => {
    setDeploying(true)
    try {
      const response = await deploymentAPI.deploy(selectedDevices, null, dryRun)
      setTaskId(response.data.task_id)
      onDeployStart(response.data)
      message.info('Deployment started')

      // Simulate deployment progress
      simulateDeployment()
    } catch (error) {
      message.error('Failed to start deployment')
      console.error(error)
      setDeploying(false)
    }
  }

  const simulateDeployment = () => {
    // Simulate deployment for demo purposes
    // In production, use WebSocket or polling for real-time updates
    const mockDeployments = selectedDevices.map((deviceId, index) => ({
      id: index + 1,
      device_id: deviceId,
      device_name: `Device ${deviceId}`,
      status: 'pending',
      progress: 0,
      logs: '',
    }))

    setDeployments(mockDeployments)

    let completed = 0
    const interval = setInterval(() => {
      setDeployments((prev) =>
        prev.map((d) => {
          if (d.status === 'pending') {
            const random = Math.random()
            if (random > 0.7) {
              completed++
              return {
                ...d,
                status: random > 0.85 ? 'failed' : 'success',
                progress: 100,
                logs: random > 0.85
                  ? 'Error: Connection timeout\nFailed to connect to device'
                  : 'Connecting to device...\nBackup current config...\nApplying configuration...\nSaving config...\nSuccess!',
              }
            }
            return {
              ...d,
              status: 'in_progress',
              progress: Math.min(d.progress + 20, 90),
              logs: d.logs + `\nStep ${Math.floor(d.progress / 20) + 1}...`,
            }
          }
          return d
        })
      )

      setProgress(Math.floor((completed / selectedDevices.length) * 100))

      if (completed === selectedDevices.length) {
        clearInterval(interval)
        setDeploying(false)
        message.success('Deployment completed')
      }
    }, 1500)
  }

  const columns = [
    {
      title: 'Device',
      dataIndex: 'device_name',
      key: 'device_name',
      render: (text) => <strong>{text}</strong>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => {
        const statusConfig = {
          pending: { icon: <SyncOutlined />, color: 'default', text: 'Pending' },
          in_progress: { icon: <SyncOutlined spin />, color: 'processing', text: 'In Progress' },
          success: { icon: <CheckCircleOutlined />, color: 'success', text: 'Success' },
          failed: { icon: <CloseCircleOutlined />, color: 'error', text: 'Failed' },
        }
        const { icon, color, text } = statusConfig[status]
        return <Tag icon={icon} color={color}>{text}</Tag>
      },
    },
    {
      title: 'Progress',
      dataIndex: 'progress',
      key: 'progress',
      render: (progress, record) => (
        <Progress
          percent={progress}
          size="small"
          status={record.status === 'failed' ? 'exception' : record.status === 'success' ? 'success' : 'active'}
        />
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Button
          size="small"
          icon={<EyeOutlined />}
          onClick={() => {
            setSelectedLogs(record.logs || 'No logs available')
            setLogsModalOpen(true)
          }}
          disabled={!record.logs}
        >
          View Logs
        </Button>
      ),
    },
  ]

  return (
    <div>
      <Card title="Deployment Progress" style={{ marginBottom: 16 }}>
        {!deploymentData ? (
          <div style={{ textAlign: 'center', padding: '40px 0' }}>
            <Alert
              message={dryRun ? 'Ready for Dry Run' : 'Ready for Deployment'}
              description={
                dryRun
                  ? 'Click the button below to test the configuration without applying changes'
                  : `Configuration will be deployed to ${selectedDevices.length} device(s)`
              }
              type="info"
              showIcon
              style={{ marginBottom: 24 }}
            />
            <Button
              type="primary"
              size="large"
              onClick={startDeployment}
              loading={deploying}
            >
              {dryRun ? '🧪 Start Dry Run' : '🚀 Start Deployment'}
            </Button>
          </div>
        ) : (
          <div>
            <div style={{ marginBottom: 24 }}>
              <h3>Overall Progress</h3>
              <Progress percent={progress} status={deploying ? 'active' : 'success'} />
            </div>

            <Table
              columns={columns}
              dataSource={deployments}
              rowKey="id"
              pagination={false}
            />
          </div>
        )}
      </Card>

      <Modal
        title="Deployment Logs"
        open={logsModalOpen}
        onCancel={() => setLogsModalOpen(false)}
        footer={[
          <Button key="close" onClick={() => setLogsModalOpen(false)}>
            Close
          </Button>,
        ]}
        width={800}
      >
        <pre
          style={{
            background: '#1e1e1e',
            color: '#d4d4d4',
            padding: 16,
            borderRadius: 4,
            maxHeight: 500,
            overflow: 'auto',
            fontFamily: 'monospace',
          }}
        >
          {selectedLogs}
        </pre>
      </Modal>
    </div>
  )
}
