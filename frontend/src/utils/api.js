import axios from 'axios';

// 백엔드 URL 설정 (환경변수 권장: process.env.REACT_APP_API_URL)
const API_BASE_URL = 'http://localhost:8000';

// Axios 인스턴스 생성
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 10000, // 10초 타임아웃
});

// --- [레이스 컨디션 방지용 상태 변수] ---
let isRefreshing = false; // 현재 토큰 갱신 중인지 여부 (Lock 역할)
let refreshSubscribers = []; // 토큰 갱신을 기다리는 요청들의 큐(Queue)

// 대기 중인 요청들을 큐에 등록하는 함수
const addRefreshSubscriber = (callback) => {
  refreshSubscribers.push(callback);
};

// 토큰 갱신 완료 시, 대기 중이던 요청들을 새로운 토큰과 함께 순차적으로 재실행
const onRefreshed = (newAccessToken) => {
  refreshSubscribers.forEach((callback) => callback(newAccessToken));
  refreshSubscribers = []; // 큐 초기화
};

// --- [Request Interceptor] ---
api.interceptors.request.use(
  (config) => {
    // 모든 API 요청이 나가기 직전에 localStorage에서 토큰을 꺼내어 헤더에 주입
    const accessToken = localStorage.getItem('accessToken');
    if (accessToken) {
      config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// --- [Response Interceptor] ---
api.interceptors.response.use(
  (response) => response, // 성공한 응답은 그대로 통과
  async (error) => {
    const { config, response } = error;
    const originalRequest = config;

    // 401 Unauthorized 에러 발생 시 처리 로직
    if (response && response.status === 401) {
      // originalRequest._retry 속성으로 무한 루프 방지 (한 번만 재시도)
      if (!originalRequest._retry) {
        
        // 1. 이미 다른 요청이 토큰을 갱신 중인 경우 (Lock이 걸려있을 때)
        if (isRefreshing) {
          // Promise를 반환하여 큐에 대기시킴 (갱신이 완료되면 resolve 됨)
          return new Promise((resolve) => {
            addRefreshSubscriber((newAccessToken) => {
              originalRequest.headers.Authorization = `Bearer ${newAccessToken}`;
              resolve(api(originalRequest)); // 원래 요청 재실행
            });
          });
        }

        // 2. 내가 처음으로 401 에러를 맞은 요청인 경우 (Lock 걸기)
        originalRequest._retry = true;
        isRefreshing = true;

        try {
          const refreshToken = localStorage.getItem('refreshToken');
          if (!refreshToken) {
            throw new Error('Refresh token not found in localStorage');
          }

          // 백엔드에 Refresh Token을 보내서 새로운 Access Token 발급 요청
          // (주의: 여기서는 인터셉터가 없는 순수 axios를 사용해야 무한 루프에 안 빠짐)
          const { data } = await axios.post(`${API_BASE_URL}/auth/refresh`, {
            refresh_token: refreshToken, // 백엔드 Pydantic 필드명에 맞춤
          });

          // 새로운 토큰 저장
          localStorage.setItem('accessToken', data.accessToken);
          if (data.refreshToken) {
             // 갱신 API가 새로운 Refresh Token도 내려주면 같이 업데이트
             localStorage.setItem('refreshToken', data.refreshToken);
          }

          // 현재 요청의 헤더에 새 토큰 세팅
          originalRequest.headers.Authorization = `Bearer ${data.accessToken}`;

          // Lock 해제 및 대기 중이던 큐의 요청들 모두 실행
          isRefreshing = false;
          onRefreshed(data.accessToken);

          // 실패했던 원래 요청 재실행
          return api(originalRequest);

        } catch (refreshError) {
          // Refresh Token 자체가 만료되었거나 변조된 경우 (완전 로그아웃 처리)
          isRefreshing = false;
          refreshSubscribers = [];
          
          localStorage.removeItem('accessToken');
          localStorage.removeItem('refreshToken');
          
          alert('로그인 세션이 만료되었습니다. 다시 로그인해 주세요.');
          window.location.href = '/login'; // 프론트 라우터 방식에 맞춰 수정 가능 (ex: navigate('/login'))
          
          return Promise.reject(refreshError);
        }
      }
    }

    // 429 에러 (스캔 한도 초과) 공통 처리
    if (response && response.status === 429) {
       // 프론트엔드 공통 Toast UI 등을 호출하는 것이 좋습니다.
       alert(error.response?.data?.detail || '일일 사용 한도를 초과했습니다.');
    }

    // 401, 429 외의 에러는 그대로 던짐
    return Promise.reject(error);
  }
);

export default api;
