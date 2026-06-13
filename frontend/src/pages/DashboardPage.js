import React from 'react';
import { useNavigate } from 'react-router-dom';
import ServiceShell from '../components/ServiceShell';

function DashboardPage() {
  const navigate = useNavigate();
  return (
    <ServiceShell title="보안 모니터링 대시보드" description="새로 생긴 위험과 다음 점검 일정을 한눈에 확인하세요." mascot="/ppt-mascot-clipboard.png" action={<button className="heading-action" onClick={() => navigate('/automation')}>자동 스캔 설정</button>}>
      <section className="dashboard-grid">
        <article className="security-score-card"><div><span>현재 보안 점수</span><strong>82</strong><small>지난 점검보다 <b>-4점</b></small></div><div className="score-ring"><strong>B</strong><span>양호</span></div></article>
        <article className="next-scan-card"><img src="/ppt-icon-scan.png" alt="" /><span>다음 자동 스캔</span><strong>월요일 오전 9:00</strong><small>매주 자동 실행 · Asia/Seoul</small><button onClick={() => navigate('/automation')}>일정 변경</button></article>
        <article className="certificate-card"><img src="/ppt-icon-lock.png" alt="" /><span>인증서 만료까지</span><strong>24일</strong><small>7일 전에 알림을 보내드려요.</small></article>
      </section>
      <section className="dashboard-columns">
        <div className="dashboard-panel"><div className="panel-title"><div><span>NEW FINDINGS</span><h2>새로운 취약점</h2></div><b>2</b></div>
          <div className="change-list"><article className="danger"><i /><div><strong>Strict-Transport-Security 헤더 없음</strong><span>오늘 오전 9:03 · 새로 발견됨</span></div><b>높음</b></article><article className="medium"><i /><div><strong>오래된 TLS 프로토콜 허용</strong><span>오늘 오전 9:03 · 새로 발견됨</span></div><b>보통</b></article><article className="fixed"><i /><div><strong>X-Frame-Options 헤더 적용</strong><span>지난 점검 이후 해결됨</span></div><b>해결</b></article></div>
          <button className="panel-link" onClick={() => navigate('/result/demo')}>전체 리포트 확인 →</button>
        </div>
        <div className="dashboard-panel"><div className="panel-title"><div><span>RECENT ALERTS</span><h2>최근 알림</h2></div></div>
          <div className="alert-timeline"><article><img src="/ppt-icon-alert.png" alt="" /><div><strong>보안 점수가 4점 낮아졌어요</strong><span>Slack · 8분 전</span></div></article><article><img src="/ppt-icon-lock.png" alt="" /><div><strong>인증서 만료가 30일 남았어요</strong><span>이메일 · 6일 전</span></div></article><article><img src="/ppt-icon-scan.png" alt="" /><div><strong>주간 자동 스캔이 완료됐어요</strong><span>카카오워크 · 7일 전</span></div></article></div>
          <button className="panel-link" onClick={() => navigate('/notifications')}>알림 설정 관리 →</button>
        </div>
      </section>
    </ServiceShell>
  );
}
export default DashboardPage;
