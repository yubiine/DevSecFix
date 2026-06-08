import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './MainPage.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

const steps = [
  { no: '1', title: 'CERTIFICATION', label: '도메인 인증', icon: '/icon-certify.svg' },
  { no: '2', title: 'SCANNING', label: 'URL 스캔', icon: '/icon-url.svg' },
  { no: '3', title: 'RESULTS', label: '리포트 확인', icon: '/icon-result.svg' },
];

const scanModules = [
  { key: 'AUTH', title: '소유권 확인', detail: 'DNS TXT / file token' },
  { key: 'PORT', title: 'Port 노출', detail: 'SSH, DB, Admin' },
  { key: 'TLS', title: 'TLS 설정', detail: 'Protocol / certificate' },
  { key: 'HDR', title: '보안 헤더', detail: 'HSTS, CSP, X-Frame' },
];

function normalizeDomain(value) {
  return value
    .trim()
    .replace(/^https?:\/\//i, '')
    .replace(/^www\./i, '')
    .split('/')[0]
    .split(':')[0];
}

function IconTile({ type }) {
  const iconSrc = type === 'search' ? '/icon-scan.svg' : '/icon-certify.svg';
  return (
    <span className="cute-icon" aria-hidden="true">
      <img src={iconSrc} alt="" />
    </span>
  );
}

function MainPage() {
  const navigate = useNavigate();
  const [targetUrl, setTargetUrl] = useState('https://example.com');
  const [error, setError] = useState('');
  const [isScanning, setIsScanning] = useState(false);
  const [scanCount, setScanCount] = useState(1284);

  useEffect(() => {
    const interval = setInterval(() => {
      setScanCount((value) => value + 1);
    }, 3200);
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

    if (!isLocallyVerified && !canDemoScan) {
      setError('실제 도메인은 인증 후 스캔할 수 있어요. 데모는 example.com으로 바로 확인할 수 있습니다.');
      return;
    }

    setIsScanning(true);
    setError('');

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
        <button className="brand" type="button" onClick={() => navigate('/')}>
          <span>DevSecFix</span>
        </button>
        <nav aria-label="Primary navigation">
          <button type="button" className="is-active" onClick={() => navigate('/')}>스캔</button>
          <button type="button" onClick={() => navigate('/certify')}>도메인 인증</button>
          <button type="button" onClick={() => navigate('/result/demo')}>샘플 리포트</button>
        </nav>
      </header>

      <main className="artboard-shell">
        <aside className="step-rail" aria-label="Scan flow">
          {steps.map((step, index) => (
            <React.Fragment key={step.title}>
              <article className={index === 0 ? 'active' : ''}>
                <div className="step-icon-box">
                  <img src={step.icon} alt="" />
                </div>
                <span>{step.no}. {step.title}</span>
                <strong>{step.label}</strong>
              </article>
              {index < steps.length - 1 && <b className="rail-arrow">→</b>}
            </React.Fragment>
          ))}
          <div className="rail-log">
            <span />
            <b>LOGGING ACTIVE</b>
          </div>
        </aside>

        <section className="scan-stage" aria-labelledby="main-title">
          <div className="stage-line">
            <span>FREQ. ANALYZING</span>
            <i />
            <span>DATA STREAM</span>
          </div>

          <div className="stage-orbit" aria-hidden="true">
            <span />
            <span />
            <span />
          </div>

          <p className="eyebrow">DEVSECFIX SECURITY CONSOLE</p>
          <h1 id="main-title">도메인 보안 상태를 빠르게 점검하세요</h1>
          <p className="stage-copy">
            인증된 도메인만 스캔하고, Port / TLS / Header 결과를 리포트로 정리합니다.
          </p>

          <div className="mini-flow" aria-label="Current scan workflow">
            <article className="ready">
              <IconTile type="check" />
              <div>
                <strong>STEP 1: CERTIFY</strong>
                <span>STATUS: READY</span>
              </div>
            </article>
            <b>→</b>
            <article>
              <IconTile type="search" />
              <div>
                <strong>STEP 2: SCAN</strong>
                <span>WAITING TARGET</span>
              </div>
            </article>
          </div>

          <div className="scan-bar">
            <input
              aria-label="스캔 대상 URL"
              value={targetUrl}
              onChange={(event) => {
                setTargetUrl(event.target.value);
                setError('');
              }}
              onKeyDown={(event) => event.key === 'Enter' && startScan()}
              placeholder="https://your-domain.com"
            />
            <button type="button" onClick={startScan} disabled={isScanning}>
              {isScanning ? '준비 중...' : 'SCAN →'}
            </button>
          </div>

          <div className="notice-strip">
            <span>{error || (isLocallyVerified || canDemoScan
              ? `${domain || '대상 도메인'}을 스캔할 수 있습니다.`
              : '실제 도메인은 인증 후 스캔할 수 있습니다.')}</span>
            <button type="button" onClick={() => navigate('/certify')}>CERTIFY NOW →</button>
          </div>

          <div className="module-dock">
            {scanModules.map((module) => (
              <article key={module.key}>
                <span>{module.key}</span>
                <strong>{module.title}</strong>
                <small>{module.detail}</small>
              </article>
            ))}
          </div>
        </section>

        <aside className="grade-panel" aria-label="Security grade preview">
          <div className="grade-box">
            <span>SECURITY GRADE</span>
            <strong>A</strong>
            <small>NEON SEC</small>
          </div>
          <div className="grade-bars">
            {['A', 'B', 'C', 'D', 'F'].map((grade, index) => (
              <div className={index < 2 ? 'on' : ''} key={grade}>
                <span>{grade}</span>
                <i />
                <b>{grade}</b>
              </div>
            ))}
          </div>
          <div className="counter-card">
            <span>RECENTLY SCANNED</span>
            <strong>[{scanCount.toLocaleString()}]</strong>
          </div>
          <div className="rail-log right">
            <span />
            <b>REPORT READY</b>
          </div>
        </aside>
      </main>

      <footer className="project-meta">
        <div>
          <strong>DevSecFix</strong>
          <span>웹 보안 자동 점검 도구</span>
        </div>
        <p>학생 2인 프로젝트 · Frontend / Backend · Authorized Web Security Checkup</p>
      </footer>
    </div>
  );
}

export default MainPage;
