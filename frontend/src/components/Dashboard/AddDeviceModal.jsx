import React from 'react'
import { Modal, Form, Input, Select, message } from 'antd'
import { deviceAPI } from '../../services/api'

export default function AddDeviceModal({ open, onClose, onSuccess }) {
  const [form] = Form.useForm()
  const [loading, setLoading] = React.useState(false)

  const handleSubmit = async (values) => {
    setLoading(true)
    try {
      await deviceAPI.create(values)
      message.success('Device added successfully')
      form.resetFields()
      onSuccess()
    } catch (error) {
      message.error('Failed to add device')
      console.error(error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      title="Add New Device"
      open={open}
      onOk={() => form.submit()}
      onCancel={() => {
        form.resetFields()
        onClose()
      }}
      confirmLoading={loading}
      okText="Add Device"
    >
      <Form
        form={form}
        layout="vertical"
        onFinish={handleSubmit}
      >
        <Form.Item
          name="hostname"
          label="Hostname"
          rules={[
            { required: true, message: 'Please enter hostname' },
            { pattern: /^[a-zA-Z0-9-]+$/, message: 'Only alphanumeric and hyphens allowed' },
          ]}
        >
          <Input placeholder="router1" />
        </Form.Item>

        <Form.Item
          name="ip_address"
          label="IP Address"
          rules={[
            { required: true, message: 'Please enter IP address' },
            {
              pattern: /^(\d{1,3}\.){3}\d{1,3}$/,
              message: 'Please enter a valid IP address',
            },
          ]}
        >
          <Input placeholder="192.168.1.1" />
        </Form.Item>

        <Form.Item
          name="platform"
          label="Platform"
          rules={[{ required: true, message: 'Please select platform' }]}
          initialValue="ios"
        >
          <Select>
            <Select.Option value="ios">Cisco IOS</Select.Option>
            <Select.Option value="nxos">Cisco NX-OS</Select.Option>
            <Select.Option value="asa">Cisco ASA</Select.Option>
            <Select.Option value="eos">Arista EOS</Select.Option>
            <Select.Option value="junos">Juniper Junos</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="device_type"
          label="Device Type"
          initialValue="router"
        >
          <Select>
            <Select.Option value="router">Router</Select.Option>
            <Select.Option value="switch">Switch</Select.Option>
            <Select.Option value="firewall">Firewall</Select.Option>
          </Select>
        </Form.Item>

        <Form.Item
          name="location"
          label="Location"
        >
          <Input placeholder="Data Center 1 / Rack 5" />
        </Form.Item>
      </Form>
    </Modal>
  )
}
