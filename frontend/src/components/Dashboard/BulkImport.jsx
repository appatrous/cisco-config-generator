import React, { useState } from 'react'
import { Modal, Upload, Alert, List, Typography, message } from 'antd'
import { InboxOutlined } from '@ant-design/icons'
import { deviceAPI } from '../../services/api'

const { Dragger } = Upload
const { Text } = Typography

export default function BulkImport({ open, onClose, onSuccess }) {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)

  const handleUpload = async () => {
    if (!file) {
      message.warning('Please select a file first')
      return
    }

    setUploading(true)
    try {
      const response = await deviceAPI.bulkImport(file)
      setResult(response.data)
      message.success(`Successfully imported ${response.data.created} devices`)
      if (response.data.errors.length === 0) {
        setTimeout(() => {
          onSuccess()
        }, 1500)
      }
    } catch (error) {
      message.error('Failed to import devices')
      console.error(error)
    } finally {
      setUploading(false)
    }
  }

  const uploadProps = {
    name: 'file',
    multiple: false,
    accept: '.csv',
    beforeUpload: (file) => {
      setFile(file)
      setResult(null)
      return false // Prevent auto-upload
    },
    onRemove: () => {
      setFile(null)
      setResult(null)
    },
  }

  return (
    <Modal
      title="Bulk Import Devices from CSV"
      open={open}
      onOk={handleUpload}
      onCancel={onClose}
      confirmLoading={uploading}
      okText="Import"
      width={700}
      okButtonProps={{ disabled: !file }}
    >
      <Alert
        message="CSV Format Requirements"
        description={
          <div>
            <p>Your CSV file should contain the following columns (with header row):</p>
            <ul>
              <li><strong>hostname</strong> (required)</li>
              <li><strong>ip_address</strong> (required)</li>
              <li><strong>platform</strong> (optional: ios, nxos, asa, eos, junos)</li>
              <li><strong>device_type</strong> (optional: router, switch, firewall)</li>
              <li><strong>location</strong> (optional)</li>
            </ul>
            <p><Text code>Example: hostname,ip_address,platform,device_type,location</Text></p>
          </div>
        }
        type="info"
        showIcon
        style={{ marginBottom: 16 }}
      />

      <Dragger {...uploadProps}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined />
        </p>
        <p className="ant-upload-text">Click or drag CSV file to this area to upload</p>
        <p className="ant-upload-hint">
          Upload a CSV file containing device information. Maximum file size: 5MB
        </p>
      </Dragger>

      {result && (
        <div style={{ marginTop: 16 }}>
          <Alert
            message={`Import completed: ${result.created} devices created`}
            type={result.errors.length === 0 ? 'success' : 'warning'}
            showIcon
            style={{ marginBottom: 8 }}
          />

          {result.errors.length > 0 && (
            <div>
              <Text strong style={{ color: '#ff4d4f' }}>Errors ({result.errors.length}):</Text>
              <List
                size="small"
                bordered
                dataSource={result.errors}
                renderItem={(error) => (
                  <List.Item>
                    <Text type="danger">{error.hostname}: {error.error}</Text>
                  </List.Item>
                )}
                style={{ maxHeight: 200, overflow: 'auto', marginTop: 8 }}
              />
            </div>
          )}

          {result.devices && result.devices.length > 0 && (
            <div style={{ marginTop: 8 }}>
              <Text strong style={{ color: '#52c41a' }}>Successfully imported devices:</Text>
              <Text code style={{ display: 'block', marginTop: 4 }}>
                {result.devices.join(', ')}
              </Text>
            </div>
          )}
        </div>
      )}
    </Modal>
  )
}
