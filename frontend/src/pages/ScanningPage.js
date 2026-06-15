import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../utils/api';
import './WorkflowPages.css';

const stages = ['작업 등록', 'Port 점검', 'TLS 분석', 'Header 확인', 'CVSS 계산', '수정 예시 매칭'];

function ScanningPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState('running');
  const [stageIndex, setStageIndex] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  useEffect(() => {
    let isMounted = true;
    let timerId = null;
    let currentDelay = 2000; // 초기 딜레이 2초

    // 데모 모드 지원 (MainPage에서 demo- 로 시작하는 경우)
    if (taskId?.startsWith('demo-')) {
      const clock = setInterval(() => {
        if (isMounted) setElapsed((value) => value + 1);
      }, 1000);
      const stageTimer = setInterval(() => {
        if (isMounted) setStageIndex((value) => Math.min(value + 1, stages.length - 1));
      }, 1100);
      const done = setTimeout(() => {
        if (isMounted) navigate(`/result/${taskId}`);
      }, 7200);

      return () => {
        isMounted = false;
        clearInterval(clock);
        clearInterval(stageTimer);
        clearTimeout(done);
      };
    }

    const poll = async () => {
      try {
        // 백엔드 /scans/{taskId} API 호출
        const response = await api.get(`/scans/${taskId}`);
        if (!isMounted) return;

        const data = response.data;
        const scanStatus = data.status || 'running';
        setStatus(scanStatus);

        if (scanStatus === 'done' || scanStatus === 'success') {
          navigate(`/result/${taskId}`);
          return;
        } else if (scanStatus === 'failed') {
          return;
        }

        // 지수 백오프 적용: 딜레이 1.5배 증가 (최대 10초)
        currentDelay = Math.min(currentDelay * 1.5, 10000);
        timerId = setTimeout(poll, currentDelay);
      } catch (err) {
        console.error('스캔 상태 조회 에러:', err);
        if (!isMounted) return;
        currentDelay = Math.min(currentDelay * 1.5, 10000);
        timerId = setTimeout(poll, currentDelay);
      }
    };

    // 최초 폴링 시작
    timerId = setTimeout(poll, currentDelay);

    const clock = setInterval(() => {
      if (isMounted) setElapsed((value) => value + 1);
    }, 1000);

    const stageTimer = setInterval(() => {
      if (isMounted) setStageIndex((value) => Math.min(value + 1, stages.length - 1));
    }, 1100);

    return () => {
      isMounted = false;
      if (timerId) clearTimeout(timerId);
      clearInterval(clock);
      clearInterval(stageTimer);
    };
  }, [taskId, navigate]);

  const progress = useMemo(() => status === 'failed' ? 100 : Math.min(96, 16 + stageIndex * 14 + elapsed * 2), [elapsed, stageIndex, status]);

  return (
    <div className="product-shell workflow-shell">
      <header className="app-topbar">
        <button className="brand" type="button" onClick={() => navigate('/')}><span>DevSecFix</span></button>
        <nav aria-label="주요 메뉴">
          <button type="button" onClick={() => navigate('/')}>스캔</button>
          <button type="button" className="is-active">분석 중</button>
        </nav>
      </header>
      <main className="scan-layout">
        <section className="workflow-card scan-card">
          <p className="eyebrow">LIVE SCAN</p>
          <h1>{status === 'failed' ? '스캔을 완료하지 못했습니다' : '보안 설정을 점검하고 있습니다'}</h1>
          <p className="lede">Task ID: {taskId}</p>
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

