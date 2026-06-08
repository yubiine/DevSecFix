import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './WorkflowPages.css';

const API_BASE = process.env.REACT_APP_API_BASE || 'http://localhost:8000';

const sampleReport = {
  target: 'https://example.com',
  securityGrade: 'B',
  totalScore: 82,
  scanDurationSec: 74,
  falsePositiveRisk: 'LOW',
  vulnerabilities: [
    {
      title: 'Strict-Transport-Security 헤더 없음',
      severity: 'high',
      cvssScore: 7.5,
      detail: 'HTTPS가 적용되어 있지만 브라우저가 HTTPS 접속을 계속 사용하도록 강제하는 설정이 없습니다.',
      snippets: [
        {
          serverType: 'nginx',
          title: 'HSTS 적용',
          code: 'add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;',
        },
        {
          serverType: 'apache',
          title: 'HSTS 적용',
          code: 'Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"',
        },
      ],
    },
    {
      title: 'Content-Security-Policy 미설정',
      severity: 'medium',
      cvssScore: 6.1,
      detail: 'CSP가 없으면 XSS에 의한 콘텐츠 로딩 우회가 발생했을 때 피해 범위가 커질 수 있습니다.',
      snippets: [
        {
          serverType: 'nginx',
          title: '기본 CSP 적용',
          code: "add_header Content-Security-Policy \"default-src 'self'; object-src 'none'; frame-ancestors 'self'\" always;",
        },
      ],
    },
    {
      title: 'X-Frame-Options 헤더 없음',
      severity: 'low',
      cvssScore: 3.1,
      detail: '다른 사이트에서 페이지를 iframe으로 불러올 수 있어 clickjacking 위험이 생길 수 있습니다.',
      snippets: [
        {
          serverType: 'nginx',
          title: '프레임 제한',
          code: 'add_header X-Frame-Options "SAMEORIGIN" always;',
        },
      ],
    },
  ],
};

const severityOrder = { critical: 4, high: 3, medium: 2, low: 1, info: 0 };

function ResultPage() {
  const { taskId } = useParams();
  const navigate = useNavigate();
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(true);
  const [demoMode, setDemoMode] = useState(false);

  useEffect(() => {
    const loadReport = async () => {
      if (taskId === 'demo' || taskId?.startsWith('demo-')) {
        const target = sessionStorage.getItem('devsecfix:lastTarget') || sampleReport.target;
        setReport({ ...sampleReport, target, taskId });
        setDemoMode(true);
        setLoading(false);
        return;
      }

      try {
        const response = await fetch(`${API_BASE}/scan/${taskId}`);
        if (!response.ok) throw new Error('result request failed');
        const data = await response.json();
        setReport(data);
      } catch {
        setReport({ ...sampleReport, taskId });
        setDemoMode(true);
      } finally {
        setLoading(false);
      }
    };

    loadReport();
  }, [taskId]);

  const vulnerabilities = useMemo(() => {
    return [...(report?.vulnerabilities || [])].sort(
      (a, b) => (severityOrder[b.severity] || 0) - (severityOrder[a.severity] || 0)
    );
  }, [report]);

  const highRiskCount = vulnerabilities.filter((item) => ['critical', 'high'].includes(item.severity)).length;

  if (loading) {
    return (
      <div className="product-shell workflow-shell">
        <main className="scan-layout">
          <section className="workflow-card scan-card">
            <p className="eyebrow">REPORT</p>
            <h1>리포트를 불러오고 있습니다</h1>
          </section>
        </main>
      </div>
    );
  }

  return (
    <div className="product-shell workflow-shell result-shell">
      <header className="app-topbar">
        <button className="brand" type="button" onClick={() => navigate('/')}>
          <span>DevSecFix</span>
        </button>
        <nav aria-label="Primary navigation">
          <button type="button" onClick={() => navigate('/')}>스캔</button>
          <button type="button" className="is-active">리포트</button>
        </nav>
      </header>

      <main className="result-layout">
        <section className="report-summary">
          <div>
            <p className="eyebrow">SECURITY REPORT</p>
            <h1>{report.target || report.taskId || taskId}</h1>
            {demoMode && <p className="inline-alert">현재는 샘플 리포트를 보여주고 있습니다.</p>}
          </div>
          <div className="score-orb">
            <strong>{report.securityGrade || '?'}</strong>
            <span>{report.totalScore || 0}/100</span>
          </div>
        </section>

        <section className="report-metrics">
          <article>
            <b>{vulnerabilities.length}</b>
            <span>발견 항목</span>
          </article>
          <article>
            <b>{highRiskCount}</b>
            <span>고위험</span>
          </article>
          <article>
            <b>{report.scanDurationSec || '-'}s</b>
            <span>소요 시간</span>
          </article>
          <article>
            <b>{report.falsePositiveRisk || 'LOW'}</b>
            <span>오탐 가능성</span>
          </article>
          <button type="button" onClick={() => window.print()}>PDF 저장</button>
        </section>

        <section className="finding-list">
          <h2>확인된 보안 이슈</h2>
          {vulnerabilities.map((vulnerability, index) => (
            <article className="finding-card" key={`${vulnerability.title}-${index}`}>
              <div className="finding-head">
                <span>{String(index + 1).padStart(2, '0')}</span>
                <div>
                  <h3>{vulnerability.title}</h3>
                  <p>{vulnerability.detail}</p>
                </div>
                <b className={`severity ${vulnerability.severity || 'info'}`}>
                  {(vulnerability.severity || 'info').toUpperCase()} / CVSS {vulnerability.cvssScore || '-'}
                </b>
              </div>

              {vulnerability.snippets?.length > 0 && (
                <div className="snippet-grid">
                  {vulnerability.snippets.map((snippet, snippetIndex) => (
                    <div className="snippet-card" key={`${snippet.title}-${snippetIndex}`}>
                      <span>{snippet.serverType?.toUpperCase() || 'CONFIG'}</span>
                      <strong>{snippet.title}</strong>
                      <pre>{snippet.code}</pre>
                    </div>
                  ))}
                </div>
              )}
            </article>
          ))}
        </section>
      </main>
    </div>
  );
}

export default ResultPage;
