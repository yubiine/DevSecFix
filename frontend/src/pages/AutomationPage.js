import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import ServiceShell from '../components/ServiceShell';
import api from '../utils/api';

function AutomationPage() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [assets, setAssets] = useState([]);
  const [schedules, setSchedules] = useState([]);
  
  const [selectedDomain, setSelectedDomain] = useState('');
  const [frequency, setFrequency] = useState('weekly');
  const [enabled, setEnabled] = useState(false);
  const [saved, setSaved] = useState(false);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  // 1. 세션 가드
  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
      navigate('/login');
    }
  }, [navigate]);

  // 2. 자산 및 스케줄 목록 로드
  const loadData = async () => {
    setLoading(true);
    try {
      const [assetsRes, schedulesRes] = await Promise.all([
        api.get('/assets'),
        api.get('/schedules')
      ]);
      setAssets(assetsRes.data);
      setSchedules(schedulesRes.data);

      if (assetsRes.data.length > 0) {
        // 첫 번째 자산 기본 선택
        const defaultDomain = assetsRes.data[0].domain;
        setSelectedDomain(defaultDomain);
        
        // 해당 자산의 활성화된 스케줄이 있는지 확인
        const existingSched = schedulesRes.data.find(s => s.domain === defaultDomain);
        if (existingSched) {
          setEnabled(existingSched.isEnabled);
          setFrequency(existingSched.interval);
        } else {
          setEnabled(false);
          setFrequency('weekly');
        }
      }
    } catch (err) {
      console.error('자동 스캔 설정 데이터 로드 실패:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // 3. 선택 도메인이 바뀔 때 설정값 동기화
  const handleDomainChange = (e) => {
    const domain = e.target.value;
    setSelectedDomain(domain);
    setSaved(false);
    setMessage('');
    
    const existingSched = schedules.find(s => s.domain === domain);
    if (existingSched) {
      setEnabled(existingSched.isEnabled);
      setFrequency(existingSched.interval);
    } else {
      setEnabled(false);
      setFrequency('weekly');
    }
  };

  // 4. 스케줄 활성화 토글
  const handleToggleEnabled = () => {
    setEnabled(!enabled);
    setSaved(false);
    setMessage('');
  };

  // 5. 스케줄 저장하기 (POST로 생성/수정 또는 DELETE로 비활성화)
  const handleSave = async () => {
    if (!selectedDomain) {
      setMessage('인증된 도메인이 없습니다. 먼저 도메인을 인증해주세요.');
      return;
    }
    setSaving(true);
    setMessage('');
    try {
      if (enabled) {
        // 활성화: POST /schedules
        await api.post('/schedules', {
          domain: selectedDomain,
          interval: frequency
        });
        setSaved(true);
        setMessage('스케줄이 성공적으로 저장되었습니다.');
      } else {
        // 비활성화: 해당 도메인의 기존 스케줄 찾아서 DELETE
        const existingSched = schedules.find(s => s.domain === selectedDomain);
        if (existingSched) {
          await api.delete(`/schedules/${existingSched.id}`);
          setSaved(true);
          setMessage('스케줄이 비활성화되었습니다.');
        } else {
          setSaved(true);
          setMessage('저장되었습니다.');
        }
      }
      // 데이터 재로드하여 최신 상태 동기화
      const schedulesRes = await api.get('/schedules');
      setSchedules(schedulesRes.data);
    } catch (err) {
      console.error('스케줄 저장 실패:', err);
      setMessage(err.response?.data?.detail || '스케줄 저장에 실패했습니다.');
    } finally {
      setSaving(false);
    }
  };

  // 선택된 도메인의 활성 스케줄 상세 정보 계산
  const currentSchedule = useMemo(() => {
    return schedules.find(s => s.domain === selectedDomain);
  }, [schedules, selectedDomain]);

  // 다음 스캔 예정 시간 텍스트 구성
  const nextRunText = useMemo(() => {
    if (!enabled || !currentSchedule || !currentSchedule.nextRunAt) {
      return { date: '스케줄 없음', time: '자동 스캔이 비활성화 상태입니다.' };
    }
    try {
      const dateObj = new Date(currentSchedule.nextRunAt);
      const options = { month: 'long', day: 'numeric', weekday: 'long' };
      const dateStr = dateObj.toLocaleDateString('ko-KR', options);
      const timeStr = dateObj.toLocaleTimeString('ko-KR', { hour: '2-digit', minute: '2-digit' });
      return { date: dateStr, time: timeStr };
    } catch (e) {
      return { date: '예정된 시간 없음', time: '-' };
    }
  }, [enabled, currentSchedule]);

  return (
    <ServiceShell title="자동 스캔 설정" description="정해진 일정마다 도메인의 보안 변화를 자동으로 확인합니다." mascot="/ppt-mascot-search.png">
      {loading ? (
        <div style={{ textAlign: 'center', padding: '50px', fontSize: '18px', color: '#666' }}>데이터를 불러오는 중입니다...</div>
      ) : (
        <section className="settings-layout">
          <div className="settings-card schedule-card">
            <div className="setting-head">
              <div>
                <span>자동 스캔</span>
                <h2>정기 스캔 일정</h2>
                <p>새로운 취약점과 보안 점수 변화를 놓치지 않도록 자동 점검합니다.</p>
              </div>
              {assets.length > 0 && (
                <button
                  type="button"
                  aria-label="자동 스캔 사용 여부"
                  aria-pressed={enabled}
                  className={`toggle ${enabled ? 'on' : ''}`}
                  onClick={handleToggleEnabled}
                >
                  <i />
                </button>
              )}
            </div>

            {assets.length === 0 ? (
              <div style={{ padding: '30px 0', textAlign: 'center' }}>
                <p style={{ color: '#888', marginBottom: '20px' }}>아직 인증된 자산 도메인이 없습니다.</p>
                <button
                  type="button"
                  className="primary-action"
                  style={{ width: 'auto', display: 'inline-block', padding: '10px 20px' }}
                  onClick={() => navigate('/certify')}
                >
                  도메인 인증하러 가기
                </button>
              </div>
            ) : (
              <>
                <div className="schedule-form" style={{ marginBottom: '20px' }}>
                  <label>
                    <span>설정 대상 도메인</span>
                    <select value={selectedDomain} onChange={handleDomainChange} style={{ width: '100%', padding: '10px', borderRadius: '8px', border: '1px solid #ddd' }}>
                      {assets.map((a) => (
                        <option key={a.domain} value={a.domain}>{a.domain}</option>
                      ))}
                    </select>
                  </label>
                </div>

                <div className="frequency-picker">
                  <button
                    type="button"
                    className={frequency === 'daily' ? 'active' : ''}
                    onClick={() => { setFrequency('daily'); setSaved(false); }}
                    disabled={!enabled}
                  >
                    <img src="/ppt-icon-scan.png" alt="" />
                    <strong>매일 검사</strong>
                    <span>매일 자정에 자동 실행</span>
                  </button>
                  <button
                    type="button"
                    className={frequency === 'weekly' ? 'active' : ''}
                    onClick={() => { setFrequency('weekly'); setSaved(false); }}
                    disabled={!enabled}
                  >
                    <img src="/ppt-icon-balance.png" alt="" />
                    <strong>매주 검사</strong>
                    <span>매주 월요일 자정에 자동 실행</span>
                  </button>
                </div>

                <div className="schedule-form" style={{ marginTop: '20px', opacity: enabled ? 1 : 0.5 }}>
                  <label>
                    <span>실행 시간</span>
                    <input type="time" value="00:00" disabled />
                  </label>
                  <label>
                    <span>시간대</span>
                    <select value="seoul" disabled>
                      <option value="seoul">Asia/Seoul</option>
                    </select>
                  </label>
                </div>

                {message && (
                  <p style={{
                    color: message.includes('실패') ? 'red' : 'green',
                    fontSize: '14px',
                    marginTop: '15px'
                  }}>
                    {message}
                  </p>
                )}

                <button
                  type="button"
                  className="save-setting"
                  onClick={handleSave}
                  disabled={saving}
                  style={{ marginTop: '20px' }}
                >
                  {saving ? '저장 중...' : (saved ? '일정이 저장됐어요' : '일정 저장하기')}
                </button>
              </>
            )}
          </div>
          <aside className="settings-side">
            <div className="next-run">
              <span>NEXT RUN</span>
              <strong>{nextRunText.date}</strong>
              <b>{nextRunText.time}</b>
              <small>{enabled ? '자동 스캔이 활성화되어 있어요' : '자동 스캔이 일시 중지됐어요'}</small>
            </div>
            <div className="scan-history-mini">
              <h3>자동 스캔 안내</h3>
              <p style={{ fontSize: '13px', color: '#666', lineHeight: '1.6' }}>
                스케줄 스캔이 완료되면 즉시 알림 설정 채널을 통해 보고서가 발송됩니다. 상세 이력은 대시보드 리포트에서 확인하실 수 있습니다.
              </p>
            </div>
            <img className="settings-mascot" src="/ppt-mascot-clipboard.png" alt="" />
          </aside>
        </section>
      )}
    </ServiceShell>
  );
}

export default AutomationPage;

