import React, { useEffect } from 'react'
import { Card, Button, Alert } from 'antd'
import { LinkOutlined } from '@ant-design/icons'

export default function ConfigGeneratorPage() {
  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>Configuration Generator</h1>

      <Card>
        <Alert
          message="Legacy Configuration Generator"
          description={
            <div>
              <p>
                The original configuration generator interface is still available at the root URL.
                This new interface focuses on device management, deployment, and monitoring.
              </p>
              <p>
                Click the button below to open the configuration generator in a new tab.
              </p>
            </div>
          }
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Button
          type="primary"
          size="large"
          icon={<LinkOutlined />}
          onClick={() => window.open('/modern', '_blank')}
        >
          Open Configuration Generator
        </Button>
      </Card>
    </div>
  )
}
