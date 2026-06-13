import React, { useState } from 'react';
import ServiceShell from '../components/ServiceShell';

function AutomationPage() {
  const [frequency, setFrequency] = useState('weekly');
  const [enabled, setEnabled] = useState(true);
  return (
    <ServiceShell title="자동 스캔 설정" description="정해진 일정마다 도메인의 보안 변화를 자동으로 확인합니다." mascot="/ppt-mascot-search.png">
      <section className="settings-layout">
        <div className="settings-card schedule-card"><div className="setting-head"><div><span>자동 스캔</span><h2>정기 스캔 일정</h2><p>새로운 취약점과 보안 점수 변화를 놓치지 않도록 자동 점검합니다.</p></div><button type="button" aria-label="자동 스캔 사용 여부" aria-pressed={enabled} className={`toggle ${enabled ? 'on' : ''}`} onClick={() => setEnabled(!enabled)}><i /></button></div>
          <div className="frequency-picker"><button className={frequency === 'daily' ? 'active' : ''} onClick={() => setFrequency('daily')}><img src="/ppt-icon-scan.png" alt="" /><strong>매일 검사</strong><span>매일 같은 시간에 자동 실행</span></button><button className={frequency === 'weekly' ? 'active' : ''} onClick={() => setFrequency('weekly')}><img src="/ppt-icon-balance.png" alt="" /><strong>매주 검사</strong><span>선택한 요일에 자동 실행</span></button></div>
          <div className="schedule-form"><label><span>실행 요일</span><select defaultValue="monday"><option value="monday">월요일</option><option value="friday">금요일</option></select></label><label><span>실행 시간</span><input type="time" defaultValue="09:00" /></label><label><span>시간대</span><select defaultValue="seoul"><option value="seoul">Asia/Seoul</option></select></label></div>
          <button className="save-setting">일정 저장하기</button>
        </div>
        <aside className="settings-side"><div className="next-run"><span>NEXT RUN</span><strong>6월 15일 월요일</strong><b>오전 9:00</b><small>다음 스캔까지 1일 22시간</small></div><div className="scan-history-mini"><h3>최근 자동 스캔</h3>{['6월 8일 · 점수 86','6월 1일 · 점수 84','5월 25일 · 점수 81'].map((x,i)=><article key={x}><i className={i===0?'down':'up'} /><span>{x}</span><b>완료</b></article>)}</div><img className="settings-mascot" src="/ppt-mascot-clipboard.png" alt="" /></aside>
      </section>
    </ServiceShell>
  );
}
export default AutomationPage;
