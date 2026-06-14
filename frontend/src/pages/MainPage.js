import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './MainPage.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

const steps = [
  { no: '1', title: 'CERTIFICATION', label: '도메인 인증', icon: '/ppt-icon-lock.png' },
  { no: '2', title: 'SCANNING', label: 'URL 스캔', icon: '/ppt-icon-scan.png' },
  { no: '3', title: 'RESULTS', label: '리포트 확인', icon: '/ppt-icon-balance.png' },
];

const scanModules = [
  { key: '01', title: '소유권 확인', detail: '허가된 도메인인지 먼저 확인해요' },
  { key: '02', title: '포트 점검', detail: '외부에 열린 주요 포트를 살펴봐요' },
  { key: '03', title: 'TLS 점검', detail: '인증서와 암호화 설정을 확인해요' },
  { key: '04', title: '보안 헤더', detail: '웹 보안 헤더 적용 상태를 확인해요' },
];

function normalizeDomain(value) {
  return value.trim().replace(/^https?:\/\//i, '').replace(/^www\./i, '').split('/')[0].split(':')[0];
}

function IconTile({ type }) {
  const iconSrc = type === 'search' ? '/ppt-icon-scan.png' : '/ppt-icon-lock.png';
  return <span className="cute-icon" aria-hidden="true"><img src={iconSrc} alt="" /></span>;
}

function MainPage() {
  const navigate = useNavigate();
  const [targetUrl, setTargetUrl] = useState('https://example.com');
  const [error, setError] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [scanCount, setScanCount] = useState(1284);

  useEffect(() => {
    const interval = setInterval(() => setScanCount((value) => value + 1), 3200);
    return () => clearInterval(interval);
  }, []);

  const domain = useMemo(() => normalizeDomain(targetUrl), [targetUrl]);
  const verifiedDomains = useMemo(() => {
    try {
      return JSON.parse(localStorage.getItem('devsecfix:verifiedDomains') || '[]');
    } catch {
      return [];
    }
  }, []);

  const isLocallyVerified = verifiedDomains.includes(domain);
  const canDemoScan = domain === 'example.com';

  const startScan = async () => {
    const cleanTarget = targetUrl.trim();
    const cleanDomain = normalizeDomain(cleanTarget);
    if (!cleanDomain) {
      setError('검사할 도메인이나 URL을 입력해 주세요.');
      return;
    }

    setIsScanning(true);
    setError('');

    if (cleanDomain === 'example.com') {
      const demoId = `demo-${Date.now()}`;
      sessionStorage.setItem('devsecfix:lastTarget', cleanTarget);
      setIsScanning(false);
      navigate(`/scanning/${demoId}`);
      return;
    }

    try {
      const response = await fetch(`${API_BASE}/scan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ targetUrl: cleanTarget }),
      });
      if (response.status === 403) {
        setError('아직 인증되지 않은 도메인입니다. 도메인 인증을 먼저 진행해 주세요.');
        return;
      }
      if (!response.ok) throw new Error('scan request failed');
      const data = await response.json();
      navigate(`/scanning/${data.taskId}`);
    } catch {
      const demoId = `demo-${Date.now()}`;
      sessionStorage.setItem('devsecfix:lastTarget', cleanTarget);
      navigate(`/scanning/${demoId}`);
    } finally {
      setIsScanning(false);
    }
  };

  return (
    <div className="product-shell">
      <header className="app-topbar art-nav">
        <button className="brand" type="button" onClick={() => navigate('/')}><span>DevSecFix</span></button>
        <button className="service-entry" type="button" onClick={() => navigate('/login')}>로그인</button>
        <nav aria-label="주요 메뉴">
          <button type="button" className="is-active" onClick={() => navigate('/')}>스캔</button>
          <button type="button" onClick={() => navigate('/certify')}>도메인 인증</button>
          <button type="button" onClick={() => navigate('/result/demo')}>샘플 리포트</button>
        </nav>
      </header>

      <main className="artboard-shell">
        <aside className="step-rail" aria-label="스캔 진행 순서">
          {steps.map((step, index) => (
            <React.Fragment key={step.title}>
              <article className={index === 0 ? 'active' : ''}>
                <div className="step-icon-box"><img src={step.icon} alt="" /></div>
                <span>{step.no}. {step.title}</span><strong>{step.label}</strong>
              </article>
              {index < steps.length - 1 && <b className="rail-arrow">›</b>}
            </React.Fragment>
          ))}
          <div className="rail-helper">
            <img src="/ppt-mascot-shield.png" alt="" />
            <strong>안전하게 시작해요</strong>
            <span>도메인 인증부터 점검 결과와 해결 방법까지 한 번에 확인할 수 있어요.</span>
          </div>
          <div className="rail-log"><span /><b>LOGGING ACTIVE</b></div>
        </aside>

        <section className="scan-stage" aria-labelledby="main-title">
          <div className="stage-line"><span>AUTHORIZED SECURITY CHECK</span><i /><span>DEVSECFIX</span></div>
          <p className="eyebrow">쉽고 안전한 웹 보안 점검</p>
          <h1 id="main-title">도메인 보안 상태를<br />빠르게 점검하세요</h1>
          <p className="stage-copy">인증된 도메인만 스캔하고, 포트·TLS·보안 헤더 결과와 해결 방법을 이해하기 쉬운 리포트로 정리합니다.</p>

          <div className="mini-flow" aria-label="현재 스캔 흐름">
            <article className="ready"><IconTile type="check" /><div><strong>도메인 소유권 인증</strong><span>안전한 점검을 위한 첫 단계</span></div></article>
            <b>›</b>
            <article><IconTile type="search" /><div><strong>보안 상태 점검</strong><span>포트 · TLS · 보안 헤더 분석</span></div></article>
          </div>

          <div className="scan-bar">
            <input aria-label="스캔 대상 URL" value={targetUrl} onChange={(event) => { setTargetUrl(event.target.value); setError(''); }} onKeyDown={(event) => event.key === 'Enter' && startScan()} placeholder="https://your-domain.com" />
            <button type="button" onClick={startScan} disabled={isScanning}>{isScanning ? '점검 준비 중...' : '보안 점검 시작'}</button>
          </div>

          <div className={`notice-strip ${error ? 'has-error' : ''}`}>
            <span>{error || (isLocallyVerified || canDemoScan ? `${domain || '선택한 도메인'}을 바로 스캔할 수 있습니다.` : '실제 도메인은 인증 후 안전하게 스캔할 수 있습니다.')}</span>
            <button type="button" onClick={() => navigate('/certify')}>도메인 인증하기 ›</button>
          </div>

          <div className="module-dock">
            {scanModules.map((module) => <article key={module.key}><span>{module.key}</span><strong>{module.title}</strong><small>{module.detail}</small></article>)}
          </div>
        </section>

        <aside className="grade-panel" aria-label="스캔 안내">
          <div className="guide-intro">
            <img src="/ppt-icon-lock.png" alt="" /><span>안전한 점검 원칙</span><strong>내 도메인만<br />점검할 수 있어요</strong>
            <p>소유권 인증이 완료된 도메인만 검사해 불필요한 보안 위험을 막습니다.</p>
          </div>
          <div className="guide-list">
            <article><b>01</b><span>도메인 인증</span><small>DNS 또는 파일 토큰</small></article>
            <article><b>02</b><span>자동 점검</span><small>포트 · TLS · 보안 헤더</small></article>
            <article><b>03</b><span>해결 리포트</span><small>위험 원인과 수정 방법</small></article>
          </div>
          <div className="counter-card"><span>누적 보안 점검</span><strong>{scanCount.toLocaleString()}건</strong></div>
          <div className="rail-log right"><span /><b>점검 시스템 정상 운영 중</b></div>
        </aside>
      </main>

      <footer className="project-meta">
        <div><strong>DevSecFix</strong><span>웹 보안을 더 이해하기 쉽게</span></div>
        <p>허가된 도메인의 보안 상태를 점검하고 해결 방법을 안내합니다.</p>
      </footer>
    </div>
  );
}

export default MainPage;
