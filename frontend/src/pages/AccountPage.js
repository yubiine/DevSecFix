import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ServiceShell from '../components/ServiceShell';

function AccountPage() {
  const navigate = useNavigate();
  const [saved, setSaved] = useState(false);
  const [passwordMessage, setPasswordMessage] = useState('');

  return (
    <ServiceShell title="내 계정" description="프로필과 서비스 정보를 관리해요." mascot="/ppt-mascot-clipboard.png">
      <section className="account-layout">
        <div className="account-main">
          <article className="profile-overview">
            <div className="profile-avatar">EB</div>
            <div><span>PROFILE</span><h2>이은빈</h2><p>team@devsecfix.com</p></div>
            <b>사용자</b>
          </article>
          <article className="settings-card account-form">
            <div className="setting-head"><div><span>기본 정보</span><h2>프로필 설정</h2><p>서비스에서 사용할 이름과 연락처를 관리합니다.</p></div></div>
            <div className="account-fields">
              <label><span>이름</span><input defaultValue="이은빈" /></label>
              <label><span>이메일</span><input defaultValue="team@devsecfix.com" type="email" /></label>
              <label><span>전화번호</span><input defaultValue="010-0000-0000" /></label>
              <label><span>시간대</span><select defaultValue="seoul"><option value="seoul">Asia/Seoul</option></select></label>
            </div>
            <button className="save-setting" type="button" onClick={() => setSaved(true)}>{saved ? '변경사항이 저장됐어요' : '변경사항 저장'}</button>
          </article>
          <article className="settings-card account-form">
            <div className="setting-head"><div><span>보안</span><h2>비밀번호 관리</h2><p>계정을 안전하게 보호하기 위해 주기적으로 변경해 주세요.</p></div></div>
            <div className="account-fields password-fields">
              <label><span>현재 비밀번호</span><input type="password" placeholder="현재 비밀번호" /></label>
              <label><span>새 비밀번호</span><input type="password" placeholder="새 비밀번호" /></label>
            </div>
            <button className="ghost-account-action" type="button" onClick={() => setPasswordMessage('실제 비밀번호 변경은 로그인 API 연결 후 사용할 수 있어요.')}>비밀번호 변경</button>
            {passwordMessage && <p className="inline-alert">{passwordMessage}</p>}
          </article>
        </div>
        <aside className="account-side">
          <article className="workspace-summary">
            <span>서비스 요약</span><strong>DevSecFix</strong><small>발표용 데모 계정</small>
            <div><b>1</b><p>인증 도메인</p></div><div><b>3</b><p>알림 채널</p></div>
          </article>
          <article className="quick-account-menu">
            <h3>빠른 설정</h3>
            <button type="button" onClick={() => navigate('/notifications')}><img src="/ppt-icon-alert.png" alt="" /><span><strong>알림 수신 설정</strong><small>이메일 · Slack · 카카오워크</small></span><b>›</b></button>
            <button type="button" onClick={() => navigate('/automation')}><img src="/ppt-icon-scan.png" alt="" /><span><strong>자동 스캔 일정</strong><small>매주 월요일 오전 9:00</small></span><b>›</b></button>
            <button type="button" onClick={() => navigate('/certify')}><img src="/ppt-icon-lock.png" alt="" /><span><strong>도메인 관리</strong><small>example.com 인증됨</small></span><b>›</b></button>
          </article>
          <button className="logout-action" type="button" onClick={() => navigate('/login')}>로그아웃</button>
        </aside>
      </section>
    </ServiceShell>
  );
}

export default AccountPage;
