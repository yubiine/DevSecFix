import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import './SubscriptionPages.css';

function LoginPage() {
  const navigate = useNavigate();
  const [mode, setMode] = useState('login');
  const [name, setName] = useState('이은빈');
  const [email, setEmail] = useState('team@devsecfix.com');
  const [password, setPassword] = useState('devsecfix');
  const [errorMsg, setErrorMsg] = useState('');

  // 세션 가드: 이미 토큰이 존재하면 대시보드로 자동 이동
  useEffect(() => {
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      navigate('/dashboard');
    }
  }, [navigate]);

  const handleSubmit = async () => {
    setErrorMsg('');
    try {
      if (mode === 'login') {
        const response = await api.post('/auth/login', {
          email,
          password
        });
        const { accessToken, refreshToken } = response.data;
        localStorage.setItem('accessToken', accessToken);
        localStorage.setItem('refreshToken', refreshToken);
        navigate('/dashboard');
      } else {
        await api.post('/auth/register', {
          email,
          password,
          name
        });
        alert('회원가입이 완료되었습니다. 로그인해 주세요.');
        setMode('login');
      }
    } catch (err) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || '요청 처리 중 오류가 발생했습니다.');
    }
  };

  return (
    <div className="product-shell login-page">
      <header className="app-topbar">
        <button className="brand" type="button" onClick={() => navigate('/')}><span>DevSecFix</span></button>
        <button className="back-home" type="button" onClick={() => navigate('/')}>서비스 소개로 돌아가기</button>
      </header>
      <main className="login-layout">
        <section className="login-story">
          <p className="eyebrow">매일 달라지는 보안 상태를 놓치지 마세요</p>
          <h1>한 번의 점검을<br />지속적인 안심으로</h1>
          <p>정기 자동 스캔과 필요한 알림만으로 도메인의 변화를 꾸준히 확인하세요.</p>
          <div className="login-benefits">
            <article><img src="/ppt-icon-scan.png" alt="" /><strong>매일·매주 자동 검사</strong><span>설정한 일정에 맞춰 자동 실행</span></article>
            <article><img src="/ppt-icon-alert.png" alt="" /><strong>새로운 변화만 알림</strong><span>이메일 · Slack · 카카오워크</span></article>
            <article><img src="/ppt-icon-lock.png" alt="" /><strong>인증서 만료 사전 안내</strong><span>서비스 중단 전에 미리 확인</span></article>
          </div>
          <img className="login-mascot" src="/ppt-mascot-point.png" alt="" />
        </section>
        <section className="login-card">
          <span className="soft-label">{mode === 'login' ? '계정 로그인' : '무료 계정 만들기'}</span>
          <h2>{mode === 'login' ? '다시 만나서 반가워요' : '지속적인 보안 관리를 시작해요'}</h2>
          <p>{mode === 'login' ? '내 도메인의 최신 보안 상태를 확인해 보세요.' : '계정을 만든 뒤 도메인을 인증하고 자동 스캔을 설정할 수 있습니다.'}</p>
          
          {errorMsg && <p style={{ color: 'red', fontSize: '14px', marginBottom: '10px' }}>{errorMsg}</p>}

          {mode === 'signup' && (
            <label>
              <span>이름</span>
              <input value={name} onChange={(event) => setName(event.target.value)} />
            </label>
          )}
          <label><span>이메일</span><input value={email} onChange={(event) => setEmail(event.target.value)} type="email" /></label>
          <label><span>비밀번호</span><input value={password} onChange={(event) => setPassword(event.target.value)} type="password" /></label>
          {mode === 'signup' && <label><span>비밀번호 확인</span><input defaultValue={password} type="password" /></label>}
          {mode === 'login' && (
            <div className="login-options">
              <label><input type="checkbox" defaultChecked /> 로그인 유지</label>
              <button type="button">비밀번호 찾기</button>
            </div>
          )}
          <button className="login-submit" type="button" onClick={handleSubmit}>
            {mode === 'login' ? '로그인' : '무료 계정 만들기'}
          </button>
          <div className="login-divider"><span>또는</span></div>
          <button className="signup-button" type="button" onClick={() => setMode(mode === 'login' ? 'signup' : 'login')}>
            {mode === 'login' ? '처음이라면 무료로 시작하기' : '이미 계정이 있다면 로그인'}
          </button>
          <div style={{ marginTop: '10px', fontSize: '12px', color: '#666' }}>
            <span>데모 계정: team@devsecfix.com / devsecfix</span>
          </div>
        </section>
      </main>
    </div>
  );
}

export default LoginPage;

