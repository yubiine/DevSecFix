import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ServiceShell from '../components/ServiceShell';
import api from '../utils/api';

function NotificationPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  
  // 알림 조건 상태
  const [notifyNewVulnerability, setNotifyNewVulnerability] = useState(true);
  const [notifyCertificateExpiry, setNotifyCertificateExpiry] = useState(true);
  const [notifyScoreDrop, setNotifyScoreDrop] = useState(true);

  // 알림 채널 상태
  const [emailEnabled, setEmailEnabled] = useState(true);
  const [emailAddress, setEmailAddress] = useState('');
  const [slackEnabled, setSlackEnabled] = useState(false);
  const [slackWebhookUrl, setSlackWebhookUrl] = useState('');
  const [kakaoworkEnabled, setKakaoworkEnabled] = useState(false);
  const [kakaoworkWebhookUrl, setKakaoworkWebhookUrl] = useState('');

  const [logs, setLogs] = useState([]);
  const [message, setMessage] = useState('');
  const [saving, setSaving] = useState(false);

  // 세션 가드
  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
      navigate('/login');
    }
  }, [navigate]);

  // 설정 및 로그 로드
  const loadData = async () => {
    setLoading(true);
    try {
      const [settingsRes, logsRes] = await Promise.all([
        api.get('/notifications/settings'),
        api.get('/notifications/logs')
      ]);

      const s = settingsRes.data;
      setNotifyNewVulnerability(s.notifyNewVulnerability);
      setNotifyCertificateExpiry(s.notifyCertificateExpiry);
      setNotifyScoreDrop(s.notifyScoreDrop);

      setEmailEnabled(s.emailEnabled);
      setEmailAddress(s.emailAddress || '');
      setSlackEnabled(s.slackEnabled);
      setSlackWebhookUrl(s.slackWebhookUrl || '');
      setKakaoworkEnabled(s.kakaoworkEnabled);
      setKakaoworkWebhookUrl(s.kakaoworkWebhookUrl || '');

      setLogs(logsRes.data);
    } catch (err) {
      console.error('알림 데이터 로드 실패:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleSaveSettings = async () => {
    setSaving(true);
    setMessage('');
    try {
      await api.put('/notifications/settings', {
        emailEnabled,
        emailAddress: emailAddress || null,
        slackEnabled,
        slackWebhookUrl: slackWebhookUrl || null,
        kakaoworkEnabled,
        kakaoworkWebhookUrl: kakaoworkWebhookUrl || null,
        notifyNewVulnerability,
        notifyScoreDrop,
        notifyCertificateExpiry
      });
      setMessage('알림 설정이 성공적으로 저장되었습니다.');
      setTimeout(() => setMessage(''), 3000);
    } catch (err) {
      console.error('알림 설정 저장 실패:', err);
      setMessage(err.response?.data?.detail || '알림 설정 저장에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <ServiceShell title="알림 설정" description="중요한 보안 변화만 원하는 채널로 받아보세요." mascot="/ppt-mascot-point.png">
      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px', fontSize: '18px', color: '#666' }}>데이터를 불러오는 중입니다...</div>
      ) : (
        <section className="notification-layout">
          <div className="settings-card" style={{ gridColumn: 'span 2' }}>
            <div className="setting-head">
              <div>
                <span>알림 조건</span>
                <h2>어떤 변화를 알려드릴까요?</h2>
                <p>반복되는 결과는 제외하고 확인이 필요한 변화만 전달합니다.</p>
              </div>
            </div>
            
            <div className="condition-list">
              <label>
                <input
                  type="checkbox"
                  checked={notifyNewVulnerability}
                  onChange={(e) => setNotifyNewVulnerability(e.target.checked)}
                />
                <div>
                  <strong>새로운 취약점 발견</strong>
                  <span>이전 점검에는 없던 취약점이 탐지되면 알려드려요.</span>
                </div>
              </label>

              <label>
                <input
                  type="checkbox"
                  checked={notifyCertificateExpiry}
                  onChange={(e) => setNotifyCertificateExpiry(e.target.checked)}
                />
                <div>
                  <strong>서버 인증서 만료 예정</strong>
                  <span>도메인 SSL 인증서 만료 30일, 14일, 7일 전에 사전 안내해 드려요.</span>
                </div>
              </label>

              <label>
                <input
                  type="checkbox"
                  checked={notifyScoreDrop}
                  onChange={(e) => setNotifyScoreDrop(e.target.checked)}
                />
                <div>
                  <strong>보안 점수 하락</strong>
                  <span>이전 점검 점수와 비교하여 총 점수가 하락했을 때 알려드려요.</span>
                </div>
              </label>
            </div>
          </div>

          <div className="settings-card" style={{ gridColumn: 'span 2', marginTop: '20px' }}>
            <div className="setting-head">
              <div>
                <span>수신 채널 설정</span>
                <h2>알림 채널 구성</h2>
                <p>알림을 연동할 이메일 및 메신저 웹훅 정보를 입력하세요.</p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '20px', padding: '20px 0' }}>
              {/* 이메일 */}
              <div style={{ border: '1px solid #eee', padding: '20px', borderRadius: '12px', background: emailEnabled ? '#f9fcfb' : '#fff' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <strong style={{ fontSize: '18px', color: '#333' }}>✉️ 이메일</strong>
                  <input
                    type="checkbox"
                    checked={emailEnabled}
                    onChange={(e) => setEmailEnabled(e.target.checked)}
                    style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                  />
                </div>
                <label style={{ display: 'block', fontSize: '12px', color: '#666', marginBottom: '5px' }}>이메일 주소</label>
                <input
                  type="email"
                  value={emailAddress}
                  onChange={(e) => setEmailAddress(e.target.value)}
                  placeholder="name@domain.com"
                  disabled={!emailEnabled}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #ddd', fontSize: '14px' }}
                />
              </div>

              {/* Slack */}
              <div style={{ border: '1px solid #eee', padding: '20px', borderRadius: '12px', background: slackEnabled ? '#fcf9fb' : '#fff' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <strong style={{ fontSize: '18px', color: '#333' }}>💬 Slack</strong>
                  <input
                    type="checkbox"
                    checked={slackEnabled}
                    onChange={(e) => setSlackEnabled(e.target.checked)}
                    style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                  />
                </div>
                <label style={{ display: 'block', fontSize: '12px', color: '#666', marginBottom: '5px' }}>Slack Webhook URL</label>
                <input
                  type="text"
                  value={slackWebhookUrl}
                  onChange={(e) => setSlackWebhookUrl(e.target.value)}
                  placeholder="https://hooks.slack.com/services/..."
                  disabled={!slackEnabled}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #ddd', fontSize: '14px' }}
                />
              </div>

              {/* KakaoWork */}
              <div style={{ border: '1px solid #eee', padding: '20px', borderRadius: '12px', background: kakaoworkEnabled ? '#f9fafc' : '#fff' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
                  <strong style={{ fontSize: '18px', color: '#333' }}>📱 카카오워크</strong>
                  <input
                    type="checkbox"
                    checked={kakaoworkEnabled}
                    onChange={(e) => setKakaoworkEnabled(e.target.checked)}
                    style={{ width: '18px', height: '18px', cursor: 'pointer' }}
                  />
                </div>
                <label style={{ display: 'block', fontSize: '12px', color: '#666', marginBottom: '5px' }}>카카오워크 Webhook URL</label>
                <input
                  type="text"
                  value={kakaoworkWebhookUrl}
                  onChange={(e) => setKakaoworkWebhookUrl(e.target.value)}
                  placeholder="https://open.work.kakao.com/api/..."
                  disabled={!kakaoworkEnabled}
                  style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #ddd', fontSize: '14px' }}
                />
              </div>
            </div>

            {message && (
              <p style={{
                color: message.includes('실패') ? 'red' : 'green',
                fontSize: '14px',
                marginBottom: '15px'
              }}>
                {message}
              </p>
            )}

            <button
              type="button"
              className="primary-action"
              onClick={handleSaveSettings}
              disabled={saving}
              style={{ width: '200px', margin: '10px 0 0 0' }}
            >
              {saving ? '저장 중...' : '알림 설정 저장하기'}
            </button>
          </div>

          <div className="settings-card" style={{ gridColumn: 'span 2', marginTop: '20px' }}>
            <div className="setting-head">
              <div>
                <span>RECENT LOGS</span>
                <h2>최근 발송된 알림 내역</h2>
                <p>시스템에서 전송한 최근 알림 발송 기록입니다.</p>
              </div>
            </div>

            <div style={{ marginTop: '20px' }}>
              {logs.length === 0 ? (
                <div style={{ padding: '35px', textAlign: 'center', color: '#999', border: '1px dashed #eee', borderRadius: '12px' }}>
                  최근 전송된 알림이 없습니다.
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {logs.map((log) => (
                    <div
                      key={log.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        padding: '15px 20px',
                        border: '1px solid #f2f2f2',
                        borderRadius: '12px',
                        background: '#fcfcfc'
                      }}
                    >
                      <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                        <span style={{
                          padding: '6px 12px',
                          borderRadius: '20px',
                          fontSize: '11px',
                          fontWeight: 'bold',
                          background: log.channel === 'email' ? '#eefbf7' : (log.channel === 'slack' ? '#fcf0f7' : '#f0f5fc'),
                          color: log.channel === 'email' ? '#20c997' : (log.channel === 'slack' ? '#d63384' : '#0d6efd')
                        }}>
                          {log.channel.toUpperCase()}
                        </span>
                        <div>
                          <strong style={{ display: 'block', fontSize: '15px', color: '#333', marginBottom: '3px' }}>
                            {log.message}
                          </strong>
                          <span style={{ fontSize: '12px', color: '#999' }}>
                            수신처: {log.recipient} · {new Date(log.createdAt).toLocaleString()}
                          </span>
                        </div>
                      </div>
                      <span style={{
                        fontSize: '13px',
                        fontWeight: 'bold',
                        color: log.status === 'sent' || log.status === 'success' ? '#2b8a3e' : '#c92a2a'
                      }}>
                        {log.status === 'sent' || log.status === 'success' ? '발송성공' : '발송실패'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </section>
      )}
    </ServiceShell>
  );
}

export default NotificationPage;

