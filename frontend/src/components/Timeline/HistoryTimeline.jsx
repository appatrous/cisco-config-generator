import React from 'react'
import { Card, Timeline, Tag, Button, Empty, Spin, Space, Typography, Badge } from 'antd'
import {
  ClockCircleOutlined,
  UserOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  RollbackOutlined,
  PlusOutlined,
  EditOutlined,
  DeleteOutlined,
  RocketOutlined,
  EyeOutlined,
} from '@ant-design/icons'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'

dayjs.extend(relativeTime)

const { Text, Paragraph } = Typography

export default function HistoryTimeline({ history, isLoading }) {
  if (isLoading) {
    return (
      <Card>
        <div style={{ textAlign: 'center', padding: 40 }}>
          <Spin size="large" />
        </div>
      </Card>
    )
  }

  if (!history || history.length === 0) {
    return (
      <Card>
        <Empty description="No change history found" />
      </Card>
    )
  }

  const getActionIcon = (action) => {
    const icons = {
      deploy_config: <RocketOutlined />,
      rollback: <RollbackOutlined />,
      create_device: <PlusOutlined />,
      update_device: <EditOutlined />,
      delete_device: <DeleteOutlined />,
    }
    return icons[action] || <ClockCircleOutlined />
  }

  const getActionColor = (action) => {
    const colors = {
      deploy_config: 'blue',
      rollback: 'orange',
      create_device: 'green',
      update_device: 'cyan',
      delete_device: 'red',
    }
    return colors[action] || 'default'
  }

  const getActionLabel = (action) => {
    const labels = {
      deploy_config: 'Deploy Config',
      rollback: 'Rollback',
      create_device: 'Create Device',
      update_device: 'Update Device',
      delete_device: 'Delete Device',
    }
    return labels[action] || action
  }

  const getStatusColor = (status) => {
    const colors = {
      success: 'success',
      failed: 'error',
      in_progress: 'processing',
      pending: 'default',
    }
    return colors[status] || 'default'
  }

  // Group by date
  const groupedHistory = React.useMemo(() => {
    const groups = {}
    history.forEach((item) => {
      const date = dayjs(item.created_at).format('YYYY-MM-DD')
      if (!groups[date]) {
        groups[date] = []
      }
      groups[date].push(item)
    })
    return groups
  }, [history])

  return (
    <Card title="Change Timeline">
      {Object.entries(groupedHistory).map(([date, items]) => (
        <div key={date} style={{ marginBottom: 32 }}>
          <div
            style={{
              background: '#f0f2f5',
              padding: '8px 16px',
              marginBottom: 16,
              borderRadius: 4,
              fontWeight: 500,
            }}
          >
            {dayjs(date).format('MMMM D, YYYY')} ({dayjs(date).fromNow()})
          </div>

          <Timeline>
            {items.map((item, index) => (
              <Timeline.Item
                key={item.id || index}
                dot={getActionIcon(item.action)}
                color={getStatusColor(item.status)}
              >
                <Card
                  size="small"
                  hoverable
                  style={{ marginBottom: 8 }}
                  bodyStyle={{ padding: 16 }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div style={{ flex: 1 }}>
                      <Space size="small" wrap>
                        <Tag color={getActionColor(item.action)} icon={getActionIcon(item.action)}>
                          {getActionLabel(item.action)}
                        </Tag>
                        {item.status && (
                          <Tag
                            color={getStatusColor(item.status)}
                            icon={
                              item.status === 'success' ? (
                                <CheckCircleOutlined />
                              ) : item.status === 'failed' ? (
                                <CloseCircleOutlined />
                              ) : null
                            }
                          >
                            {item.status}
                          </Tag>
                        )}
                        {item.device_name && (
                          <Tag color="purple">
                            <strong>{item.device_name}</strong>
                          </Tag>
                        )}
                      </Space>

                      <Paragraph style={{ marginTop: 8, marginBottom: 8 }}>
                        {item.description || item.details?.description || 'No description available'}
                      </Paragraph>

                      <Space size="middle" style={{ marginTop: 8 }}>
                        <Text type="secondary">
                          <ClockCircleOutlined /> {dayjs(item.created_at).format('HH:mm:ss')}
                        </Text>
                        {item.user_name && (
                          <Text type="secondary">
                            <UserOutlined /> {item.user_name}
                          </Text>
                        )}
                        {item.ip_address && (
                          <Text type="secondary" code>
                            {item.ip_address}
                          </Text>
                        )}
                      </Space>

                      {item.details && Object.keys(item.details).length > 0 && (
                        <div style={{ marginTop: 12, background: '#fafafa', padding: 8, borderRadius: 4 }}>
                          <Text type="secondary" style={{ fontSize: '12px' }}>
                            <pre style={{ margin: 0 }}>
                              {JSON.stringify(item.details, null, 2)}
                            </pre>
                          </Text>
                        </div>
                      )}
                    </div>

                    <div>
                      <Button
                        type="link"
                        size="small"
                        icon={<EyeOutlined />}
                        onClick={() => {
                          // TODO: Open detail modal
                          console.log('View details:', item)
                        }}
                      >
                        Details
                      </Button>
                    </div>
                  </div>
                </Card>
              </Timeline.Item>
            ))}
          </Timeline>
        </div>
      ))}
    </Card>
  )
}
