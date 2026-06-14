import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
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

  return (
    <div className="product-shell service-page">
      <header className="app-topbar service-topbar">
        <button className="brand" type="button" onClick={() => navigate('/')}><span>DevSecFix</span></button>
        <div className="service-account">
          <button type="button" onClick={() => navigate('/')}>수동 스캔</button>
          <button type="button" className={`account-chip ${location.pathname === '/account' ? 'active' : ''}`} onClick={() => navigate('/account')} title="내 계정">
            <span>EB</span><strong>은빈 님</strong>
          </button>
        </div>
      </header>
      <div className="service-frame">
        <aside className="service-sidebar">
          <div className="workspace-label"><span>내 서비스</span><strong>DevSecFix</strong></div>
          <nav aria-label="서비스 메뉴">
            {items.map((item) => (
              <button type="button" key={item.path} className={location.pathname === item.path ? 'active' : ''} onClick={() => navigate(item.path)}>
                <img src={item.icon} alt="" /><span>{item.label}</span>
              </button>
            ))}
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
