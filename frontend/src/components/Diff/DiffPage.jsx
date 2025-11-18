import React, { useState } from 'react'
import { Card, Select, Button, Alert, Space, Spin } from 'antd'
import { SwapOutlined } from '@ant-design/icons'
import { useQuery } from 'react-query'
import DiffViewer from './DiffViewer'
import { deviceAPI, configAPI } from '../../services/api'

export default function DiffPage() {
  const [selectedDevice, setSelectedDevice] = useState(null)
  const [config1Id, setConfig1Id] = useState(null)
  const [config2Id, setConfig2Id] = useState(null)
  const [diffResult, setDiffResult] = useState(null)
  const [comparing, setComparing] = useState(false)

  // Fetch devices
  const { data: devices, isLoading: loadingDevices } = useQuery('devices', () =>
    deviceAPI.getAll().then((res) => res.data)
  )

  // Fetch config history for selected device
  const { data: configs, isLoading: loadingConfigs } = useQuery(
    ['configs', selectedDevice],
    () => configAPI.getHistory(selectedDevice).then((res) => res.data),
    {
      enabled: !!selectedDevice,
    }
  )

  const handleCompare = async () => {
    if (!config1Id || !config2Id) return

    setComparing(true)
    try {
      const response = await configAPI.compare(config1Id, config2Id)
      setDiffResult(response.data)
    } catch (error) {
      console.error('Comparison failed:', error)
    } finally {
      setComparing(false)
    }
  }

  const handleSwap = () => {
    const temp = config1Id
    setConfig1Id(config2Id)
    setConfig2Id(temp)
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Configuration Comparison</h1>

      <Card title="Select Configurations to Compare" style={{ marginBottom: 24 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
              1. Select Device
            </label>
            <Select
              placeholder="Choose a device"
              style={{ width: '100%' }}
              loading={loadingDevices}
              value={selectedDevice}
              onChange={(value) => {
                setSelectedDevice(value)
                setConfig1Id(null)
                setConfig2Id(null)
                setDiffResult(null)
              }}
            >
              {devices?.map((device) => (
                <Select.Option key={device.id} value={device.id}>
                  {device.hostname} ({device.ip_address})
                </Select.Option>
              ))}
            </Select>
          </div>

          {selectedDevice && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: 16, alignItems: 'end' }}>
              <div>
                <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                  2. Select First Configuration
                </label>
                <Select
                  placeholder="Choose config version"
                  style={{ width: '100%' }}
                  loading={loadingConfigs}
                  value={config1Id}
                  onChange={setConfig1Id}
                >
                  {configs?.map((config) => (
                    <Select.Option key={config.id} value={config.id}>
                      v{config.version} - {new Date(config.created_at).toLocaleString()}
                      {config.is_active && <span style={{ color: '#52c41a' }}> (Active)</span>}
                    </Select.Option>
                  ))}
                </Select>
              </div>

              <Button
                icon={<SwapOutlined />}
                onClick={handleSwap}
                disabled={!config1Id || !config2Id}
                style={{ marginBottom: 0 }}
              >
                Swap
              </Button>

              <div>
                <label style={{ display: 'block', marginBottom: 8, fontWeight: 500 }}>
                  3. Select Second Configuration
                </label>
                <Select
                  placeholder="Choose config version"
                  style={{ width: '100%' }}
                  loading={loadingConfigs}
                  value={config2Id}
                  onChange={setConfig2Id}
                >
                  {configs?.map((config) => (
                    <Select.Option key={config.id} value={config.id}>
                      v{config.version} - {new Date(config.created_at).toLocaleString()}
                      {config.is_active && <span style={{ color: '#52c41a' }}> (Active)</span>}
                    </Select.Option>
                  ))}
                </Select>
              </div>
            </div>
          )}

          <div>
            <Button
              type="primary"
              size="large"
              onClick={handleCompare}
              disabled={!config1Id || !config2Id}
              loading={comparing}
            >
              Compare Configurations
            </Button>
          </div>
        </Space>
      </Card>

      {comparing && (
        <Card>
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>Analyzing differences...</p>
          </div>
        </Card>
      )}

      {diffResult && !comparing && (
        <DiffViewer diffResult={diffResult} />
      )}
    </div>
  )
}
