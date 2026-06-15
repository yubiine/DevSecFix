import React, { useMemo, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import './WorkflowPages.css';

function normalizeDomain(value) {
  return value.trim().replace(/^https?:\/\//i, '').replace(/^www\./i, '').split('/')[0].split(':')[0];
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

  // 세션 가드
  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken');
    if (!accessToken) {
      navigate('/login');
    }
  }, [navigate]);

  const requestVerification = async () => {
    if (!domain) {
      setMessage('인증할 도메인을 입력해 주세요.');
      return;
    }
    setLoading(true);
    setMessage('');
    try {
      const response = await api.post('/auth/verify/request', {
        domain,
        method
      });
      setToken(response.data.token);
      setStep(2);
    } catch (err) {
      console.error(err);
      setMessage(err.response?.data?.detail || '인증 토큰 발급에 실패했습니다.');
    } finally {
      setLoading(false);
    }
  };

  const confirmVerification = async () => {
    setLoading(true);
    setMessage('');
    try {
      // 1. 소유권 확인 API 호출
      await api.post('/auth/verify/confirm', {
        domain,
        method
      });

      // 2. 자산 등록 API 호출
      await api.post('/assets', {
        domain
      });

      setStep(3);
    } catch (err) {
      console.error(err);
      setMessage(err.response?.data?.detail || '소유권 인증 및 자산 등록에 실패했습니다. DNS TXT 설정을 확인하세요.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="product-shell workflow-shell certify-shell">
      <header className="app-topbar">
        <button className="brand" type="button" onClick={() => navigate('/')}><span>DevSecFix</span></button>
        <nav aria-label="주요 메뉴">
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
          <div className="stepper" aria-label="도메인 인증 진행 단계">{['도메인 입력', '토큰 등록', '인증 완료'].map((label, index) => <div className={step >= index + 1 ? 'active' : ''} key={label}><b>{index + 1}</b><span>{label}</span></div>)}</div>

          {step === 1 && <div className="form-stack">
            <label><span>인증할 도메인</span><input value={domainInput} onChange={(event) => setDomainInput(event.target.value)} placeholder="example.com" /></label>
            <div className="segmented" role="group" aria-label="인증 방식">
              <button type="button" className={method === 'dns' ? 'selected' : ''} onClick={() => setMethod('dns')}><strong>DNS TXT</strong><small>DNS 설정에 토큰 추가</small></button>
              <button type="button" className={method === 'file' ? 'selected' : ''} onClick={() => setMethod('file')}><strong>파일 업로드</strong><small>지정 경로에 토큰 파일 추가</small></button>
            </div>
            <button type="button" className="primary-action" onClick={requestVerification} disabled={loading}>{loading ? '토큰 발급 중...' : '인증 토큰 발급받기'}</button>
          </div>}

          {step === 2 && <div className="form-stack">
            <div className="token-box"><span>인증 토큰</span><code>{token}</code></div>
            <div className="instruction-box">{method === 'dns' ? <><strong>DNS TXT 레코드로 등록해 주세요.</strong><p>Host: @</p><p>Type: TXT</p><p>Value: {token}</p></> : <><strong>아래 경로에 토큰 파일을 올려 주세요.</strong><p>Path: {fileUrl}</p><p>File content: {token}</p></>}</div>
            <button type="button" className="primary-action" onClick={confirmVerification} disabled={loading}>{loading ? '확인 중...' : '인증 확인하기'}</button>
            <button type="button" className="ghost-action" onClick={() => setStep(1)}>인증 방식 다시 선택</button>
          </div>}

          {step === 3 && <div className="success-state"><strong>도메인 인증이 완료됐어요</strong><p>{domain}을 이제 안전하게 점검할 수 있습니다.</p><button type="button" className="primary-action" onClick={() => navigate('/')}>보안 점검 시작하기</button></div>}
          {message && <p className="inline-alert">{message}</p>}
        </section>
        <aside className="workflow-side certify-guide">
          <div className="certify-mascot"><img src="/ppt-mascot-shield.png" alt="방패를 들고 인증을 안내하는 DevSecFix 캐릭터" /></div>
          <p className="eyebrow">왜 인증이 필요한가요?</p><h2>허가된 대상만<br />안전하게 점검합니다</h2>
          <p className="guide-copy">도메인 인증은 보안 점검을 요청한 사람이 실제 소유자인지 확인하는 과정입니다.</p>
          <div className="safety-points">
            <article><b>01</b><div><strong>무단 점검 차단</strong><span>인증되지 않은 도메인은 스캔하지 않아요.</span></div></article>
            <article><b>02</b><div><strong>간단한 소유권 확인</strong><span>DNS 또는 파일 토큰으로 확인해요.</span></div></article>
            <article><b>03</b><div><strong>안전한 기록 관리</strong><span>모든 점검은 고유 Task ID로 추적해요.</span></div></article>
          </div>
          <div className="certify-note"><img src="/ppt-icon-lock.png" alt="" /><span>인증 정보는 보안 점검 권한 확인에만 사용합니다.</span></div>
        </aside>
      </main>
    </div>
  );
}

export default CertifyPage;
