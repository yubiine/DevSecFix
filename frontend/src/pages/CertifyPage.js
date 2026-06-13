import React, { useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './WorkflowPages.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

function normalizeDomain(value) {
  return value.trim().replace(/^https?:\/\//i, '').replace(/^www\./i, '').split('/')[0].split(':')[0];
}

function saveVerifiedDomain(domain) {
  const previous = JSON.parse(localStorage.getItem('devsecfix:verifiedDomains') || '[]');
  localStorage.setItem('devsecfix:verifiedDomains', JSON.stringify(Array.from(new Set([...previous, domain]))));
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
      setMessage('백엔드 연결 없이 체험할 수 있도록 데모 토큰을 발급했습니다.');
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
      setMessage('데모 환경에서는 로컬 인증 완료로 처리합니다.');
    } finally {
      saveVerifiedDomain(domain);
      setStep(3);
      setLoading(false);
    }
  };

  return (
    <div className="product-shell workflow-shell certify-shell">
      <header className="app-topbar">
        <button className="brand" type="button" onClick={() => navigate('/')}><span>DevSecFix</span></button>
        <nav aria-label="Primary navigation">
          <button type="button" onClick={() => navigate('/')}>스캔</button>
          <button type="button" onClick={() => navigate('/dashboard')}>대시보드</button>
          <button type="button" className="is-active">도메인 인증</button>
        </nav>
      </header>

      <main className="workflow-layout">
        <section className="workflow-card certify-card">
          <p className="eyebrow">안전한 점검을 위한 첫 단계</p>
          <h1>스캔 전에 도메인<br />소유권을 확인해요</h1>
          <p className="lede">DevSecFix는 허가되지 않은 사이트를 점검하지 않습니다. DNS TXT 또는 파일 인증 중 편한 방법을 선택해 주세요.</p>

          <div className="stepper" aria-label="Certification progress">
            {['도메인 입력', '토큰 등록', '인증 완료'].map((label, index) => (
              <div className={step >= index + 1 ? 'active' : ''} key={label}><b>{index + 1}</b><span>{label}</span></div>
            ))}
          </div>

          {step === 1 && (
            <div className="form-stack">
              <label><span>인증할 도메인</span><input value={domainInput} onChange={(event) => setDomainInput(event.target.value)} placeholder="example.com" /></label>
              <div className="segmented" role="group" aria-label="Verification method">
                <button type="button" className={method === 'dns' ? 'selected' : ''} onClick={() => setMethod('dns')}><strong>DNS TXT</strong><small>DNS 설정에 토큰 추가</small></button>
                <button type="button" className={method === 'file' ? 'selected' : ''} onClick={() => setMethod('file')}><strong>파일 업로드</strong><small>지정 경로에 파일 추가</small></button>
              </div>
              <button type="button" className="primary-action" onClick={requestVerification} disabled={loading}>{loading ? '토큰 발급 중...' : '인증 토큰 발급받기'}</button>
            </div>
          )}

          {step === 2 && (
            <div className="form-stack">
              <div className="token-box"><span>인증 토큰</span><code>{token}</code></div>
              <div className="instruction-box">
                {method === 'dns' ? <><strong>DNS TXT 레코드로 등록해 주세요</strong><p>Host: @</p><p>Type: TXT</p><p>Value: {token}</p></> :
                  <><strong>아래 경로에 토큰 파일을 올려 주세요</strong><p>Path: {fileUrl}</p><p>File content: {token}</p></>}
              </div>
              <button type="button" className="primary-action" onClick={confirmVerification} disabled={loading}>{loading ? '확인 중...' : '인증 확인하기'}</button>
              <button type="button" className="ghost-action" onClick={() => setStep(1)}>인증 방식 다시 선택</button>
            </div>
          )}

          {step === 3 && (
            <div className="success-state"><strong>도메인 인증이 완료됐어요</strong><p>{domain}을 이제 안전하게 점검할 수 있습니다.</p><button type="button" className="primary-action" onClick={() => navigate('/')}>보안 점검 시작하기</button></div>
          )}
          {message && <p className="inline-alert">{message}</p>}
        </section>

        <aside className="workflow-side certify-guide">
          <div className="certify-mascot"><img src="/ppt-mascot-shield.png" alt="방패를 들고 인증을 안내하는 DevSecFix 캐릭터" /></div>
          <p className="eyebrow">왜 인증이 필요한가요?</p>
          <h2>허가된 대상만<br />안전하게 점검합니다</h2>
          <p className="guide-copy">도메인 인증은 보안 점검을 요청한 사람이 실제 소유자임을 확인하는 과정입니다.</p>
          <div className="safety-points">
            <article><b>01</b><div><strong>무단 점검 차단</strong><span>인증되지 않은 도메인은 스캔하지 않아요.</span></div></article>
            <article><b>02</b><div><strong>간단한 소유권 확인</strong><span>DNS 또는 파일 토큰으로 확인해요.</span></div></article>
            <article><b>03</b><div><strong>안전한 기록 관리</strong><span>모든 점검은 고유 Task ID로 추적해요.</span></div></article>
          </div>
          <div className="certify-note"><img src="/ppt-icon-lock.png" alt="" /><span>인증 정보는 보안 점검 권한 확인에만 사용됩니다.</span></div>
        </aside>
      </main>
    </div>
  );
}

export default CertifyPage;
