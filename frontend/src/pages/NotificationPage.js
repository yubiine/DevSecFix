import React, { useState } from 'react';
import ServiceShell from '../components/ServiceShell';

const conditions = [
  ['새로운 취약점 발견', '이전 점검에는 없던 취약점만 알려드려요.'],
  ['서버 인증서 만료 예정', '만료 30일, 14일, 7일 전에 알려드려요.'],
  ['보안 점수 하락', '이전 점검보다 점수가 낮아지면 알려드려요.'],
  ['자동 스캔 실패', '점검이 완료되지 못했을 때 알려드려요.'],
];

function NotificationPage() {
  const [checks, setChecks] = useState([true, true, true, true]);
  const [message, setMessage] = useState('');
  const notify = (text) => {
    setMessage(text);
    window.setTimeout(() => setMessage(''), 2200);
  };

  return (
    <ServiceShell title="알림 설정" description="중요한 보안 변화만 원하는 채널로 받아보세요." mascot="/ppt-mascot-point.png">
      <section className="notification-layout">
        <div className="settings-card">
          <div className="setting-head"><div><span>알림 조건</span><h2>어떤 변화를 알려드릴까요?</h2><p>반복되는 결과는 제외하고 확인이 필요한 변화만 전달합니다.</p></div></div>
          <div className="condition-list">{conditions.map((condition, index) => <label key={condition[0]}><input type="checkbox" checked={checks[index]} onChange={() => setChecks(checks.map((value, itemIndex) => itemIndex === index ? !value : value))} /><div><strong>{condition[0]}</strong><span>{condition[1]}</span></div><i /></label>)}</div>
        </div>
        <div className="channel-grid">
          <article className="channel-card connected email"><div className="channel-icon">@</div><span>EMAIL</span><strong>이메일</strong><p>team@devsecfix.com</p><b>연결됨</b><button type="button" onClick={() => notify('이메일 수신자 설정을 확인했어요.')}>수신자 관리</button></article>
          <article className="channel-card connected slack"><div className="channel-icon">S</div><span>SLACK</span><strong>Slack</strong><p>#security-alerts</p><b>연결됨</b><button type="button" onClick={() => notify('Slack 채널 설정을 확인했어요.')}>채널 변경</button></article>
          <article className="channel-card kakao"><div className="channel-icon">K</div><span>KAKAOWORK</span><strong>카카오워크</strong><p>팀 워크스페이스와 연결하세요.</p><button type="button" onClick={() => notify('카카오워크 연결은 백엔드 웹훅 연결 후 사용할 수 있어요.')}>연결하기</button></article>
        </div>
        {message && <p className="inline-alert">{message}</p>}
        <div className="notification-preview"><img src="/ppt-icon-alert.png" alt="" /><div><span>알림 미리보기</span><strong>example.com의 보안 점수가 86점에서 82점으로 낮아졌어요.</strong><small>새로운 고위험 취약점 1개를 확인해 주세요.</small></div><b>방금 전</b></div>
      </section>
    </ServiceShell>
  );
}

export default NotificationPage;
