import React, { useState } from 'react'
import { Card, Button, Checkbox, Tabs, Alert, Spin } from 'antd'
import { CheckCircleOutlined, WarningOutlined } from '@ant-design/icons'
import CodeMirror from '@uiw/react-codemirror'
import { StreamLanguage } from '@codemirror/language'
import { validationAPI } from '../../services/api'

export default function ConfigPreview({ selectedDevices, onConfigReady, dryRun, setDryRun }) {
  const [configText, setConfigText] = useState(`! Sample configuration
hostname router1
!
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
!
router ospf 1
 router-id 1.1.1.1
 network 192.168.1.0 0.0.0.255 area 0
!
end`)
  const [validationResult, setValidationResult] = useState(null)
  const [validating, setValidating] = useState(false)

  const handleValidate = async () => {
    setValidating(true)
    try {
      const response = await validationAPI.validate(configText)
      setValidationResult(response.data)
      if (response.data.valid) {
        onConfigReady(configText)
      }
    } catch (error) {
      console.error('Validation failed:', error)
    } finally {
      setValidating(false)
    }
  }

  const tabItems = [
    {
      key: 'editor',
      label: 'Configuration Editor',
      children: (
        <div>
          <Alert
            message="Edit Configuration"
            description="Paste or type your configuration below. The config will be applied to all selected devices."
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
          />
          <CodeMirror
            value={configText}
            height="400px"
            onChange={(value) => {
              setConfigText(value)
              setValidationResult(null)
            }}
            theme="light"
          />
        </div>
      ),
    },
    {
      key: 'validation',
      label: validationResult ? (
        validationResult.valid ? (
          <span>
            <CheckCircleOutlined style={{ color: '#52c41a', marginRight: 4 }} />
            Validation Results
          </span>
        ) : (
          <span>
            <WarningOutlined style={{ color: '#faad14', marginRight: 4 }} />
            Validation Results
          </span>
        )
      ) : (
        'Validation Results'
      ),
      children: (
        <div>
          {!validationResult ? (
            <Alert
              message="No validation performed yet"
              description="Click the 'Validate Configuration' button to check for errors and best practices"
              type="info"
              showIcon
            />
          ) : (
            <div>
              <Alert
                message={validationResult.valid ? 'Configuration Valid' : 'Validation Issues Found'}
                description={
                  validationResult.valid
                    ? `Quality Score: ${validationResult.score}/100 | Risk Level: ${validationResult.risk_level}`
                    : 'Please review the issues below'
                }
                type={validationResult.valid ? 'success' : 'warning'}
                showIcon
                style={{ marginBottom: 16 }}
              />

              {validationResult.conflicts?.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <h4>❌ Conflicts</h4>
                  {validationResult.conflicts.map((conflict, i) => (
                    <Alert
                      key={i}
                      message={conflict.message}
                      type="error"
                      showIcon
                      style={{ marginBottom: 8 }}
                    />
                  ))}
                </div>
              )}

              {validationResult.security_issues?.length > 0 && (
                <div style={{ marginBottom: 16 }}>
                  <h4>🔒 Security Issues</h4>
                  {validationResult.security_issues.map((issue, i) => (
                    <Alert
                      key={i}
                      message={`[${issue.severity}] ${issue.message}`}
                      description={issue.recommendation}
                      type="warning"
                      showIcon
                      style={{ marginBottom: 8 }}
                    />
                  ))}
                </div>
              )}

              {validationResult.best_practices?.length > 0 && (
                <div>
                  <h4>💡 Best Practices</h4>
                  {validationResult.best_practices.map((bp, i) => (
                    <Alert
                      key={i}
                      message={bp.message}
                      type="info"
                      showIcon
                      style={{ marginBottom: 8 }}
                    />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      ),
    },
  ]

  return (
    <Card
      title={`Configuration Preview (${selectedDevices.length} devices selected)`}
      extra={
        <div>
          <Checkbox checked={dryRun} onChange={(e) => setDryRun(e.target.checked)}>
            Dry Run (Test Only)
          </Checkbox>
          <Button
            type="primary"
            onClick={handleValidate}
            loading={validating}
            style={{ marginLeft: 16 }}
          >
            Validate Configuration
          </Button>
        </div>
      }
    >
      <Tabs items={tabItems} />
    </Card>
  )
}
