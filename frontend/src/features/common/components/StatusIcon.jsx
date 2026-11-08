// Icon 3 trạng thái (07/11): 'ok' = tích xanh · 'error' = dấu ✗ đỏ · 'neutral' = vòng tròn xám.
// Luôn đi kèm CHỮ (không chỉ dựa vào màu) — người mù màu vẫn phân biệt được.
export default function StatusIcon({ state, size = 16 }) {
  if (state === 'ok') {
    return (
      <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="var(--ok-fg)" />
        <path
          d="m7.5 12.5 3 3 6-6.5"
          fill="none"
          stroke="var(--card)"
          strokeWidth="2.4"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    );
  }
  if (state === 'error') {
    return (
      <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" fill="var(--danger-icon)" />
        <path
          d="M8.5 8.5l7 7M15.5 8.5l-7 7"
          fill="none"
          stroke="var(--card)"
          strokeWidth="2.4"
          strokeLinecap="round"
        />
      </svg>
    );
  }
  return (
    <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" fill="none" stroke="var(--text-dim)" strokeWidth="1.5" />
    </svg>
  );
}
