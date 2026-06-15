import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import ServiceShell from '../components/ServiceShell';
import api from '../utils/api';

function AccountPage() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [saved, setSaved] = useState(false);
  
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [passwordError, setPasswordError] = useState('');
  const [passwordSuccess, setPasswordSuccess] = useState('');

  const handleChangePassword = async (e) => {
    e.preventDefault();
    setPasswordError('');
    setPasswordSuccess('');

    if (!currentPassword || !newPassword) {
      setPasswordError('현재 비밀번호와 새 비밀번호를 모두 입력해 주세요.');
      return;
    }
    if (newPassword.length < 6) {
      setPasswordError('새 비밀번호는 최소 6자 이상이어야 합니다.');
      return;
    }

    try {
      await api.put('/auth/change-password', {
        currentPassword,
        newPassword,
      });
      setPasswordSuccess('비밀번호가 성공적으로 변경되었습니다.');
      setCurrentPassword('');
      setNewPassword('');
    } catch (err) {
      const errMsg = err.response?.data?.detail || '비밀번호 변경에 실패했습니다.';
      setPasswordError(errMsg);
    }
  };

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await api.get('/auth/me');
        setUser(response.data);
      } catch (err) {
        console.error('계정 정보 로드 실패:', err);
      }
    };
    fetchUserData();
  }, []);

  const handleLogout = async () => {
    try {
      const refreshToken = localStorage.getItem('refreshToken');
      if (refreshToken) {
        await api.post('/auth/logout', { refreshToken });
      }
    } catch (err) {
      console.error('서버 로그아웃 실패:', err);
    } finally {
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
      navigate('/login');
    }
  };

  const getUserInitial = () => {
    if (!user || !user.name) return 'EB';
    return user.name.charAt(0).toUpperCase();
  };

  const getUserName = () => {
    if (!user || !user.name) return '이은빈';
    return user.name;
  };

  const getUserEmail = () => {
    if (!user || !user.email) return 'team@devsecfix.com';
    return user.email;
  };

  return (
    <ServiceShell title="내 계정" description="프로필과 서비스 정보를 관리해요." mascot="/ppt-mascot-clipboard.png">
      <section className="account-layout">
        <div className="account-main">
          <article className="profile-overview">
            <div className="profile-avatar">{getUserInitial()}</div>
            <div><span>PROFILE</span><h2>{getUserName()}</h2><p>{getUserEmail()}</p></div>
            <b>사용자</b>
          </article>
          <article className="settings-card account-form">
            <div className="setting-head"><div><span>기본 정보</span><h2>프로필 설정</h2><p>서비스에서 사용할 이름과 연락처를 관리합니다.</p></div></div>
            <div className="account-fields">
              <label><span>이름</span><input value={getUserName()} disabled /></label>
              <label><span>이메일</span><input value={getUserEmail()} disabled type="email" /></label>
              <label><span>시간대</span><select defaultValue="seoul"><option value="seoul">Asia/Seoul</option></select></label>
            </div>
            <button className="save-setting" type="button" onClick={() => setSaved(true)}>{saved ? '변경사항이 저장됐어요' : '변경사항 저장'}</button>
          </article>
          <article className="settings-card account-form">
            <div className="setting-head"><div><span>보안</span><h2>비밀번호 관리</h2><p>계정을 안전하게 보호하기 위해 주기적으로 변경해 주세요.</p></div></div>
            <form onSubmit={handleChangePassword} style={{ width: '100%' }}>
              <div className="account-fields password-fields">
                <label><span>현재 비밀번호</span><input type="password" placeholder="현재 비밀번호" value={currentPassword} onChange={(e) => setCurrentPassword(e.target.value)} /></label>
                <label><span>새 비밀번호</span><input type="password" placeholder="새 비밀번호" value={newPassword} onChange={(e) => setNewPassword(e.target.value)} /></label>
              </div>
              <button className="ghost-account-action" type="submit" style={{ marginTop: '15px' }}>비밀번호 변경</button>
              {passwordError && <p className="inline-alert" style={{ color: '#ff4d4f', marginTop: '10px' }}>{passwordError}</p>}
              {passwordSuccess && <p className="inline-alert" style={{ color: '#2b8a3e', marginTop: '10px' }}>{passwordSuccess}</p>}
            </form>
          </article>
        </div>
        <aside className="account-side">
          <article className="workspace-summary">
            <span>서비스 요약</span><strong>DevSecFix</strong><small>활성 계정 정보</small>
            <div><b>1</b><p>인증 도메인</p></div><div><b>3</b><p>알림 채널</p></div>
          </article>
          <article className="quick-account-menu">
            <h3>빠른 설정</h3>
            <button type="button" onClick={() => navigate('/notifications')}><img src="/ppt-icon-alert.png" alt="" /><span><strong>알림 수신 설정</strong><small>이메일 · Slack · 카카오워크</small></span><b>›</b></button>
            <button type="button" onClick={() => navigate('/automation')}><img src="/ppt-icon-scan.png" alt="" /><span><strong>자동 스캔 일정</strong><small>주간 자동 스캔 설정</small></span><b>›</b></button>
            <button type="button" onClick={() => navigate('/certify')}><img src="/ppt-icon-lock.png" alt="" /><span><strong>도메인 관리</strong><small>도메인 인증하기</small></span><b>›</b></button>
          </article>
          <button className="logout-action" type="button" onClick={handleLogout}>로그아웃</button>
        </aside>
      </section>
    </ServiceShell>
  );
}

export default AccountPage;

