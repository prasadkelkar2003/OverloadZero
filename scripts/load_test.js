import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '15s', target: 50 },   // Warm-up ramp
    { duration: '30s', target: 300 },  // Flash crowd spike
    { duration: '15s', target: 0 },    // Cool-down
  ],
  thresholds: {
    http_req_duration: ['p(95)<100'],  // 95% of requests must complete under 100ms
  },
};

export default function () {
  const randomRoll = '21BCE' + Math.floor(1001 + Math.random() * 50);
  const res = http.get(`http://localhost:8000/api/result?roll_no=${randomRoll}`);
  check(res, {
    'status is 200 or 429': (r) => r.status === 200 || r.status === 429,
  });
  sleep(0.05);
}
