import React from 'react'
import { Card, Tag, Alert, Tabs, Statistic, Row, Col } from 'antd'
import {
  PlusOutlined,
  MinusOutlined,
  WarningOutlined,
  InfoCircleOutlined,
} from '@ant-design/icons'
import ReactDiffViewer from 'react-diff-viewer'

export default function DiffViewer({ diffResult }) {
  const {
    changes,
    sections_changed,
    risk_assessment,
    affected_resources,
    summary,
  } = diffResult

  const getRiskColor = (risk) => {
    const colors = {
      CRITICAL: '#f5222d',
      HIGH: '#fa8c16',
      MEDIUM: '#faad14',
      LOW: '#52c41a',
    }
    return colors[risk] || '#d9d9d9'
  }

  const tabItems = [
    {
      key: 'visual',
      label: '📊 Visual Diff',
      children: (
        <div>
          {changes?.additions && changes?.deletions && (
            <ReactDiffViewer
              oldValue={changes.deletions.join('\n')}
              newValue={changes.additions.join('\n')}
              splitView={true}
              showDiffOnly={false}
              useDarkTheme={false}
              leftTitle="Previous Configuration"
              rightTitle="New Configuration"
              styles={{
                variables: {
                  dark: {
                    diffViewerBackground: '#2b2b2b',
                    addedBackground: '#044B53',
                    addedColor: '#8ed99b',
                    removedBackground: '#632F34',
                    removedColor: '#f08d8d',
                  },
                },
              }}
            />
          )}
        </div>
      ),
    },
    {
      key: 'summary',
      label: '📋 Summary',
      children: (
        <div>
          <Alert
            message={`Risk Assessment: ${risk_assessment}`}
            description={summary}
            type={risk_assessment === 'LOW' ? 'success' : risk_assessment === 'CRITICAL' ? 'error' : 'warning'}
            showIcon
            style={{ marginBottom: 16 }}
          />

          <Row gutter={16} style={{ marginBottom: 24 }}>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Additions"
                  value={changes?.additions?.length || 0}
                  prefix={<PlusOutlined style={{ color: '#52c41a' }} />}
                  valueStyle={{ color: '#52c41a' }}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Deletions"
                  value={changes?.deletions?.length || 0}
                  prefix={<MinusOutlined style={{ color: '#f5222d' }} />}
                  valueStyle={{ color: '#f5222d' }}
                />
              </Card>
            </Col>
            <Col span={8}>
              <Card>
                <Statistic
                  title="Sections Changed"
                  value={sections_changed?.length || 0}
                  prefix={<InfoCircleOutlined style={{ color: '#1890ff' }} />}
                  valueStyle={{ color: '#1890ff' }}
                />
              </Card>
            </Col>
          </Row>

          {sections_changed && sections_changed.length > 0 && (
            <div style={{ marginBottom: 16 }}>
              <h4>Affected Sections:</h4>
              <div>
                {sections_changed.map((section, i) => (
                  <Tag key={i} color="blue" style={{ marginBottom: 8 }}>
                    {section}
                  </Tag>
                ))}
              </div>
            </div>
          )}

          {affected_resources && (
            <div>
              <h4>Affected Resources:</h4>
              {affected_resources.interfaces && affected_resources.interfaces.length > 0 && (
                <div style={{ marginBottom: 8 }}>
                  <strong>Interfaces:</strong>{' '}
                  {affected_resources.interfaces.map((iface, i) => (
                    <Tag key={i} color="purple">{iface}</Tag>
                  ))}
                </div>
              )}
              {affected_resources.vlans && affected_resources.vlans.length > 0 && (
                <div style={{ marginBottom: 8 }}>
                  <strong>VLANs:</strong>{' '}
                  {affected_resources.vlans.map((vlan, i) => (
                    <Tag key={i} color="green">{vlan}</Tag>
                  ))}
                </div>
              )}
              {affected_resources.routing_protocols && affected_resources.routing_protocols.length > 0 && (
                <div>
                  <strong>Routing Protocols:</strong>{' '}
                  {affected_resources.routing_protocols.map((proto, i) => (
                    <Tag key={i} color="orange">{proto}</Tag>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      ),
    },
    {
      key: 'changes',
      label: '🔄 Change List',
      children: (
        <div>
          {changes?.additions && changes.additions.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <h4 style={{ color: '#52c41a' }}>
                <PlusOutlined /> Additions ({changes.additions.length})
              </h4>
              <pre style={{ background: '#f6ffed', padding: 16, borderRadius: 4, border: '1px solid #b7eb8f' }}>
                {changes.additions.join('\n')}
              </pre>
            </div>
          )}

          {changes?.deletions && changes.deletions.length > 0 && (
            <div style={{ marginBottom: 24 }}>
              <h4 style={{ color: '#f5222d' }}>
                <MinusOutlined /> Deletions ({changes.deletions.length})
              </h4>
              <pre style={{ background: '#fff2e8', padding: 16, borderRadius: 4, border: '1px solid #ffbb96' }}>
                {changes.deletions.join('\n')}
              </pre>
            </div>
          )}

          {(!changes?.additions || changes.additions.length === 0) &&
           (!changes?.deletions || changes.deletions.length === 0) && (
            <Alert
              message="No changes detected"
              description="The configurations are identical"
              type="info"
              showIcon
            />
          )}
        </div>
      ),
    },
  ]

  return (
    <Card
      title={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span>Configuration Diff Results</span>
          <Tag
            color={getRiskColor(risk_assessment)}
            style={{ marginLeft: 8 }}
            icon={<WarningOutlined />}
          >
            Risk: {risk_assessment}
          </Tag>
        </div>
      }
    >
      <Tabs items={tabItems} />
    </Card>
  )
}
