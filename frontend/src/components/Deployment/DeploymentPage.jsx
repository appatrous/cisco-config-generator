import React, { useState } from 'react'
import { Steps, Card, Button, Space, Alert } from 'antd'
import { useSearchParams } from 'react-router-dom'
import DeviceSelector from './DeviceSelector'
import ConfigPreview from './ConfigPreview'
import DeploymentProgress from './DeploymentProgress'

const { Step } = Steps

export default function DeploymentPage() {
  const [searchParams] = useSearchParams()
  const preselectedDevice = searchParams.get('device')

  const [currentStep, setCurrentStep] = useState(0)
  const [selectedDevices, setSelectedDevices] = useState(
    preselectedDevice ? [parseInt(preselectedDevice)] : []
  )
  const [configText, setConfigText] = useState('')
  const [deploymentData, setDeploymentData] = useState(null)
  const [dryRun, setDryRun] = useState(false)

  const steps = [
    {
      title: 'Select Devices',
      description: 'Choose devices for deployment',
    },
    {
      title: 'Review Configuration',
      description: 'Preview and validate config',
    },
    {
      title: 'Deploy',
      description: 'Push config to devices',
    },
  ]

  const next = () => setCurrentStep(currentStep + 1)
  const prev = () => setCurrentStep(currentStep - 1)

  const handleDeviceSelection = (devices) => {
    setSelectedDevices(devices)
  }

  const handleConfigReady = (config) => {
    setConfigText(config)
  }

  const handleDeployStart = (data) => {
    setDeploymentData(data)
  }

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Configuration Deployment</h1>

      <Card style={{ marginBottom: 24 }}>
        <Steps current={currentStep}>
          {steps.map((item) => (
            <Step key={item.title} title={item.title} description={item.description} />
          ))}
        </Steps>
      </Card>

      {currentStep === 0 && (
        <DeviceSelector
          selectedDevices={selectedDevices}
          onSelectionChange={handleDeviceSelection}
        />
      )}

      {currentStep === 1 && (
        <ConfigPreview
          selectedDevices={selectedDevices}
          onConfigReady={handleConfigReady}
          dryRun={dryRun}
          setDryRun={setDryRun}
        />
      )}

      {currentStep === 2 && (
        <DeploymentProgress
          selectedDevices={selectedDevices}
          configText={configText}
          dryRun={dryRun}
          onDeployStart={handleDeployStart}
          deploymentData={deploymentData}
        />
      )}

      <Card style={{ marginTop: 16 }}>
        <Space>
          {currentStep > 0 && (
            <Button onClick={prev}>Previous</Button>
          )}
          {currentStep < steps.length - 1 && (
            <Button
              type="primary"
              onClick={next}
              disabled={
                (currentStep === 0 && selectedDevices.length === 0) ||
                (currentStep === 1 && !configText)
              }
            >
              Next
            </Button>
          )}
          {currentStep === steps.length - 1 && deploymentData && (
            <Alert
              message="Deployment in progress"
              description="Monitor the progress below"
              type="info"
              showIcon
            />
          )}
        </Space>
      </Card>
    </div>
  )
}
