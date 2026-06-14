import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './WorkflowPages.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';
const stages = ['작업 등록', 'Port 점검', 'TLS 분석', 'Header 확인', 'CVSS 계산', '수정 예시 매칭'];

function ScanningPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('running');
  const [stageIndex, setStageIndex] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    const clock = setInterval(() => setElapsed((value) => value + 1), 1000);
    const stageTimer = setInterval(() => setStageIndex((value) => Math.min(value + 1, stages.length - 1)), 1100);
    if (taskId?.startsWith('demo-')) {
      const done = setTimeout(() => navigate(`/result/${taskId}`), 7200);
      return () => { clearInterval(clock); clearInterval(stageTimer); clearTimeout(done); };
    }
    const poll = setInterval(async () => {
      try {
        const response = await fetch(`${API_BASE}/scan/${taskId}`);
        if (!response.ok) throw new Error('poll failed');
        const data = await response.json();
        setStatus(data.status || 'running');
        if (data.status === 'done') navigate(`/result/${taskId}`);
      } catch {
        setStatus('running');
      }
    }, 2000);
    return () => { clearInterval(clock); clearInterval(stageTimer); clearInterval(poll); };
  }, [taskId, navigate]);

  const progress = useMemo(() => status === 'failed' ? 100 : Math.min(96, 16 + stageIndex * 14 + elapsed * 2), [elapsed, stageIndex, status]);

  return (
    <div className="product-shell workflow-shell">
      <header className="app-topbar"><button className="brand" type="button" onClick={() => navigate('/')}><span>DevSecFix</span></button><nav aria-label="주요 메뉴"><button type="button" onClick={() => navigate('/')}>스캔</button><button type="button" className="is-active">분석 중</button></nav></header>
      <main className="scan-layout">
        <section className="workflow-card scan-card">
          <p className="eyebrow">LIVE SCAN</p><h1>{status === 'failed' ? '스캔을 완료하지 못했습니다' : '보안 설정을 점검하고 있습니다'}</h1><p className="lede">Task ID: {taskId}</p>
          <div className="scan-radar" aria-hidden="true"><span /></div>
          <div className="progress-track"><i style={{ width: `${progress}%` }} /></div>
          <div className="stage-grid">{stages.map((stage, index) => <article className={index <= stageIndex ? 'active' : ''} key={stage}><b>{String(index + 1).padStart(2, '0')}</b><span>{stage}</span></article>)}</div>
          {status === 'failed' ? <div className="inline-alert">대상 URL과 백엔드 로그를 확인한 뒤 다시 시도해 주세요.</div> : <p className="scan-note">분석이 끝나면 리포트 화면으로 자동 이동합니다.</p>}
        </section>
      </main>
    </div>
  );
}

export default ScanningPage;
