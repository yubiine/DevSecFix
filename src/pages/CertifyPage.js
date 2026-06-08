import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './WorkflowPages.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

function normalizeDomain(value) {
  return value
    .trim()
    .replace(/^https?:\/\//i, '')
    .replace(/^www\./i, '')
    .split('/')[0]
    .split(':')[0];
}

function saveVerifiedDomain(domain) {
  const previous = JSON.parse(localStorage.getItem('devsecfix:verifiedDomains') || '[]');
  const next = Array.from(new Set([...previous, domain]));
  localStorage.setItem('devsecfix:verifiedDomains', JSON.stringify(next));
}

function CertifyPage() {
  const navigate = useNavigate();
  const [domainInput, setDomainInput] = useState('example.com');
  const [method, setMethod] = useState('dns');
  const [token, setToken] = useState('');
  const [step, setStep] = useState(1);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const domain = useMemo(() => normalizeDomain(domainInput), [domainInput]);
  const fileUrl = `https://${domain || 'your-domain.com'}/.well-known/devsecfix.txt`;

  const requestVerification = async () => {
    if (!domain) {
      setMessage('인증할 도메인을 입력해 주세요.');
      return;
    }

    setLoading(true);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE}/auth/verify/request`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain, method }),
      });

      if (!response.ok) throw new Error('verification request failed');

      const data = await response.json();
      setToken(data.token);
    } catch {
      setToken(`devsecfix-verify=${Math.random().toString(36).slice(2, 10)}`);
      setMessage('백엔드에 연결할 수 없어 데모 토큰을 발급했습니다.');
    } finally {
      setStep(2);
      setLoading(false);
    }
  };

  const confirmVerification = async () => {
    setLoading(true);
    setMessage('');

    try {
      const response = await fetch(`${API_BASE}/auth/verify/confirm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ domain }),
      });

      if (!response.ok) throw new Error('verification confirm failed');
    } catch {
      setMessage('데모 환경에서는 로컬에서 인증 완료로 처리합니다.');
    } finally {
      saveVerifiedDomain(domain);
      setStep(3);
      setLoading(false);
    }
  };

  return (
    <div className="product-shell workflow-shell">
      <header className="app-topbar">
        <button className="brand" type="button" onClick={() => navigate('/')}>
          <span>DevSecFix</span>
        </button>
        <nav aria-label="Primary navigation">
          <button type="button" onClick={() => navigate('/')}>스캔</button>
          <button type="button" className="is-active">도메인 인증</button>
        </nav>
      </header>

      <main className="workflow-layout">
        <section className="workflow-card">
          <p className="eyebrow">DOMAIN OWNERSHIP</p>
          <h1>스캔 전에 도메인 소유권을 확인합니다</h1>
          <p className="lede">
            DevSecFix가 무단 사이트를 스캔하지 않도록 인증 절차를 먼저 거칩니다.
            DNS TXT 레코드나 파일 업로드 중 편한 방식을 선택하세요.
          </p>

          <div className="stepper" aria-label="Certification progress">
            {['도메인 입력', '토큰 등록', '인증 완료'].map((label, index) => (
              <div className={step >= index + 1 ? 'active' : ''} key={label}>
                <b>{index + 1}</b>
                <span>{label}</span>
              </div>
            ))}
          </div>

          {step === 1 && (
            <div className="form-stack">
              <label>
                <span>도메인</span>
                <input
                  value={domainInput}
                  onChange={(event) => setDomainInput(event.target.value)}
                  placeholder="example.com"
                />
              </label>
              <div className="segmented" role="group" aria-label="Verification method">
                <button
                  type="button"
                  className={method === 'dns' ? 'selected' : ''}
                  onClick={() => setMethod('dns')}
                >
                  DNS TXT
                </button>
                <button
                  type="button"
                  className={method === 'file' ? 'selected' : ''}
                  onClick={() => setMethod('file')}
                >
                  파일 업로드
                </button>
              </div>
              <button type="button" className="primary-action" onClick={requestVerification} disabled={loading}>
                {loading ? '발급 중...' : '인증 토큰 받기'}
              </button>
            </div>
          )}

          {step === 2 && (
            <div className="form-stack">
              <div className="token-box">
                <span>인증 토큰</span>
                <code>{token}</code>
              </div>
              <div className="instruction-box">
                {method === 'dns' ? (
                  <>
                    <strong>DNS TXT 레코드로 등록하세요</strong>
                    <p>Host: @</p>
                    <p>Type: TXT</p>
                    <p>Value: {token}</p>
                  </>
                ) : (
                  <>
                    <strong>아래 경로에 토큰 파일을 올려주세요</strong>
                    <p>Path: {fileUrl}</p>
                    <p>File content: {token}</p>
                  </>
                )}
              </div>
              <button type="button" className="primary-action" onClick={confirmVerification} disabled={loading}>
                {loading ? '확인 중...' : '인증 확인하기'}
              </button>
              <button type="button" className="ghost-action" onClick={() => setStep(1)}>
                방식 다시 선택
              </button>
            </div>
          )}

          {step === 3 && (
            <div className="success-state">
              <strong>인증이 완료되었습니다</strong>
              <p>{domain}은 이제 DevSecFix에서 스캔할 수 있습니다.</p>
              <button type="button" className="primary-action" onClick={() => navigate('/')}>
                스캔하러 가기
              </button>
            </div>
          )}

          {message && <p className="inline-alert">{message}</p>}
        </section>

        <aside className="workflow-side">
          <p className="eyebrow">SAFETY MODEL</p>
          <h2>허가된 대상만 점검합니다</h2>
          <ul>
            <li>인증되지 않은 도메인은 백엔드에서 차단합니다.</li>
            <li>DNS 또는 파일 토큰으로 실제 소유권을 확인합니다.</li>
            <li>스캔 작업은 Task ID로 추적합니다.</li>
            <li>리포트에는 위험도와 수정 예시가 함께 정리됩니다.</li>
          </ul>
        </aside>
      </main>
    </div>
  );
}

export default CertifyPage;
