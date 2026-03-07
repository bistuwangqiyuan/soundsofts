import { useState } from 'react';
import { Card, Upload, message, Alert, Table } from 'antd';
import type { UploadProps } from 'antd';
import { InboxOutlined } from '@ant-design/icons';
import { dataImportApi } from '@/services/api';
import type { DataImportResult } from '@/types/api';

const { Dragger } = Upload;

const ACCEPT_TYPES = '.csv,.hdf5,.mat';
const MAX_SIZE = 100 * 1024 * 1024; // 100MB

function DataImporter() {
  const [importing, setImporting] = useState(false);
  const [results, setResults] = useState<DataImportResult[]>([]);

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: true,
    accept: ACCEPT_TYPES,
    maxCount: 5,
    showUploadList: true,
    beforeUpload: (file) => {
      if (file.size > MAX_SIZE) {
        message.error(`文件 ${file.name} 超过 100MB 限制`);
        return Upload.LIST_IGNORE;
      }
      return true;
    },
    customRequest: async ({ file, onSuccess, onError }) => {
      setImporting(true);
      try {
        const res = await dataImportApi.uploadFile(file as File);
        const data = res.data.data;
        if (data) {
          setResults((prev: DataImportResult[]) => [data, ...prev]);
          message.success(`文件 ${(file as File).name} 导入成功，${data.recordCount} 条记录`);
        }
        onSuccess?.(data);
      } catch (err) {
        message.error(`导入失败: ${(err as Error).message}`);
        onError?.(err as Error);
      } finally {
        setImporting(false);
      }
    },
  };

  const columns = [
    { title: '文件ID', dataIndex: 'fileId', key: 'fileId', width: 200 },
    { title: '格式', dataIndex: 'format', key: 'format', width: 80 },
    { title: '记录数', dataIndex: 'recordCount', key: 'recordCount', width: 100 },
    { title: '状态', key: 'success', render: (_: unknown, r: DataImportResult) => (r.success ? '成功' : '失败') },
  ];

  return (
    <Card title="数据导入">
      <Alert
        message="支持 CSV、HDF5、MAT 格式"
        description="单文件最大 100MB，支持批量上传。上传后将由后端解析并写入数据库。"
        type="info"
        showIcon
        style={{ marginBottom: 24 }}
      />
      <Dragger {...uploadProps} disabled={importing}>
        <p className="ant-upload-drag-icon">
          <InboxOutlined style={{ fontSize: 48, color: '#1677ff' }} />
        </p>
        <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p className="ant-upload-hint">支持 .csv / .hdf5 / .mat，单文件最大 100MB</p>
      </Dragger>
      {results.length > 0 && (
        <Table
          columns={columns}
          dataSource={results}
          rowKey="fileId"
          pagination={false}
          style={{ marginTop: 24 }}
          size="small"
        />
      )}
    </Card>
  );
}

export default DataImporter;
