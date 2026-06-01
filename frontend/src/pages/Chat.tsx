import React from 'react';
import {
  Card,
  Input,
  Button,
  List,
  Spin,
  Alert,
  Empty,
  Space,
  Tag,
  Divider,
} from 'antd';
import {
  SendOutlined,
  DeleteOutlined,
  DownloadOutlined,
  ClearOutlined,
} from '@ant-design/icons';
import apiService from '../services/api';
import { ChatMessage } from '../types';
import { formatDate } from '../utils/helpers';
import Markdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const markdownComponents = {
  table: ({ children }: any) => (
    <table style={{ borderCollapse: 'collapse', width: '100%', marginTop: '8px', marginBottom: '8px' }}>
      {children}
    </table>
  ),
  thead: ({ children }: any) => (
    <thead style={{ backgroundColor: '#fafafa', borderBottom: '2px solid #d9d9d9' }}>
      {children}
    </thead>
  ),
  tbody: ({ children }: any) => (
    <tbody>
      {children}
    </tbody>
  ),
  tr: ({ children }: any) => (
    <tr style={{ borderBottom: '1px solid #d9d9d9' }}>
      {children}
    </tr>
  ),
  th: ({ children }: any) => (
    <th style={{ padding: '8px 12px', textAlign: 'left', fontWeight: 'bold', borderRight: '1px solid #d9d9d9' }}>
      {children}
    </th>
  ),
  td: ({ children }: any) => (
    <td style={{ padding: '8px 12px', borderRight: '1px solid #d9d9d9' }}>
      {children}
    </td>
  ),
  code: ({ inline, children }: any) => (
    inline ? (
      <code style={{ backgroundColor: '#f5f5f5', padding: '2px 6px', borderRadius: '2px', fontFamily: 'monospace' }}>
        {children}
      </code>
    ) : (
      <code style={{ display: 'block', backgroundColor: '#f5f5f5', padding: '12px', borderRadius: '4px', overflow: 'auto', fontFamily: 'monospace', margin: '8px 0' }}>
        {children}
      </code>
    )
  ),
};

const ChatPage: React.FC = () => {
  const [messages, setMessages] = React.useState<ChatMessage[]>([]);
  const [input, setInput] = React.useState('');
  const [loading, setLoading] = React.useState(false);
  const [sessionId, setSessionId] = React.useState<string>(
    `session_${Date.now()}`
  );
  const [error, setError] = React.useState<string | null>(null);

  const messagesEndRef = React.useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: ChatMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages([...messages, userMessage]);
    setInput('');
    setLoading(true);
    setError(null);

    try {
      let assistantResponse = '';

      // 使用串流 API
      for await (const chunk of apiService.chatStream(
        input,
        sessionId
      )) {
        if (chunk.error) {
          setError(chunk.error);
          break;
        }

        if (chunk.content) {
          assistantResponse += chunk.content;
          setMessages((prev) => {
            const lastMsg = prev[prev.length - 1];
            if (lastMsg?.role === 'assistant') {
              return [
                ...prev.slice(0, -1),
                {
                  ...lastMsg,
                  content: assistantResponse,
                },
              ];
            } else {
              return [
                ...prev,
                {
                  role: 'assistant',
                  content: assistantResponse,
                  timestamp: new Date().toISOString(),
                },
              ];
            }
          });
        }
      }
    } catch (err: any) {
      setError('無法獲取回應，請檢查後端服務');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([]);
    setSessionId(`session_${Date.now()}`);
  };

  return (
    <Card
      title="LLM 智能對話"
      extra={
        <Space>
          <Button
            icon={<ClearOutlined />}
            onClick={handleClearChat}
            disabled={messages.length === 0}
          >
            清空對話
          </Button>
        </Space>
      }
    >
      {error && (
        <Alert
          message={error}
          type="error"
          showIcon
          closable
          style={{ marginBottom: '16px' }}
          onClose={() => setError(null)}
        />
      )}

      <div
        style={{
          height: '500px',
          overflowY: 'auto',
          marginBottom: '16px',
          padding: '16px',
          backgroundColor: '#fafafa',
          borderRadius: '4px',
          border: '1px solid #ddd',
        }}
      >
        {messages.length === 0 ? (
          <Empty description="開始對話">
            <p style={{ fontSize: '12px', color: '#999' }}>
              輸入您的問題，AI 將為您提供安全分析建議
            </p>
          </Empty>
        ) : (
          <List
            dataSource={messages}
            renderItem={(msg) => (
              <div
                style={{
                  marginBottom: '12px',
                  textAlign: msg.role === 'user' ? 'right' : 'left',
                }}
              >
                <div
                  style={{
                    display: 'inline-block',
                    maxWidth: '70%',
                    padding: '8px 12px',
                    borderRadius: '4px',
                    backgroundColor:
                      msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                    color: msg.role === 'user' ? '#fff' : '#000',
                    wordWrap: 'break-word',
                    whiteSpace: 'pre-wrap',
                  }}
                >
                  {msg.role === 'assistant' ? (
                    <Markdown remarkPlugins={[remarkGfm]} components={markdownComponents}>{msg.content}</Markdown>
                  ) : (
                    msg.content
                  )}
                </div>
                <div
                  style={{
                    fontSize: '12px',
                    color: '#999',
                    marginTop: '4px',
                  }}
                >
                  {formatDate(msg.timestamp)}
                </div>
              </div>
            )}
          />
        )}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex', gap: '8px' }}>
        <Input
          placeholder="輸入您的問題或安全相關的查詢..."
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onPressEnter={handleSendMessage}
          disabled={loading}
          allowClear
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={handleSendMessage}
          loading={loading}
          disabled={!input.trim() || loading}
        >
          發送
        </Button>
      </div>
    </Card>
  );
};

export default ChatPage;
