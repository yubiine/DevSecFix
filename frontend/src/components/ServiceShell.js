import React, { useState, useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import '../pages/SubscriptionPages.css';

const items = [
  { path: '/dashboard', label: '대시보드', icon: '/ppt-icon-balance.png' },
  { path: '/automation', label: '자동 스캔', icon: '/ppt-icon-scan.png' },
  { path: '/notifications', label: '알림 설정', icon: '/ppt-icon-alert.png' },
  { path: '/certify', label: '도메인 인증', icon: '/ppt-icon-lock.png' },
  { path: '/result/demo', label: '최근 리포트', icon: '/ppt-icon-balance.png' },
];

function ServiceShell({ children, title, description, mascot = '/ppt-mascot-point.png', action }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [user, setUser] = useState(null);
  const [latestScanId, setLatestScanId] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      const token = localStorage.getItem('accessToken');
      if (!token) {
        navigate('/login');
        return;
      }
      try {
        const userResponse = await api.get('/auth/me');
        setUser(userResponse.data);
      } catch (err) {
        console.error('세션 검증 실패:', err);
        // api.js 인터셉터가 토큰 갱신 실패 시 이미 로그인창으로 보내주지만 안전장치로 추가
        localStorage.removeItem('accessToken');
        localStorage.removeItem('refreshToken');
        navigate('/login');
        return;
      }

      try {
        // 대시보드 API를 통해 가장 최근의 완료된 스캔 ID를 획득
        const summaryResponse = await api.get('/dashboard/summary');
        const doneScans = summaryResponse.data.recentScans?.filter(s => s.grade !== null) || [];
        if (doneScans.length > 0) {
          setLatestScanId(doneScans[0].scanId);
        }
      } catch (err) {
        console.error('사이드바 최신 스캔 조회 실패:', err);
      }
    };
    fetchData();
  }, [navigate]);

  // 이름 첫 글자 따기 (예: "이은빈" -> "이", "Test User" -> "T")
  const getUserInitial = () => {
    if (!user || !user.name) return 'EB';
    return user.name.charAt(0).toUpperCase();
  };

  const getUserDisplayName = () => {
    if (!user || !user.name) return '은빈 님';
    return `${user.name} 님`;
  };

  return (
    <div className="product-shell service-page">
      <header className="app-topbar service-topbar">
        <button className="brand" type="button" onClick={() => navigate('/')}><span>DevSecFix</span></button>
        <div className="service-account">
          <button type="button" onClick={() => navigate('/')}>수동 스캔</button>
          <button type="button" className={`account-chip ${location.pathname === '/account' ? 'active' : ''}`} onClick={() => navigate('/account')} title="내 계정">
            <span>{getUserInitial()}</span><strong>{getUserDisplayName()}</strong>
          </button>
        </div>
      </header>
      <div className="service-frame">
        <aside className="service-sidebar">
          <div className="workspace-label"><span>내 서비스</span><strong>DevSecFix</strong></div>
          <nav aria-label="서비스 메뉴">
            {items.map((item) => {
              const isActive = location.pathname === item.path || 
                (item.path === '/result/demo' && location.pathname.startsWith('/result/'));
              
              const handleClick = () => {
                if (item.path === '/result/demo') {
                  if (latestScanId) {
                    navigate(`/result/${latestScanId}`);
                  } else {
                    navigate('/result/demo');
                  }
                } else {
                  navigate(item.path);
                }
              };

              return (
                <button type="button" key={item.path} className={isActive ? 'active' : ''} onClick={handleClick}>
                  <img src={item.icon} alt="" /><span>{item.label}</span>
                </button>
              );
            })}
          </nav>
          <div className="sidebar-plan"><img src="/ppt-mascot-shield.png" alt="" /><span>현재 플랜</span><strong>Starter</strong><small>도메인 1개 · 주간 스캔</small></div>
        </aside>
        <main className="service-main">
          <section className="service-heading">
            <div><p className="eyebrow">지속적인 보안 관리</p><h1>{title}</h1><p>{description}</p>{action}</div>
            <img src={mascot} alt="" />
          </section>
          {children}
        </main>
      </div>
    </div>
  );
}

export default ServiceShell;

