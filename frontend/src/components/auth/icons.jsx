// Icon SVG dùng ở các trang tài khoản — lấy từ màn demo (FĐ3). Không dùng thư viện icon.
const base = {
  'aria-hidden': true,
  width: 18,
  height: 18,
  viewBox: '0 0 24 24',
  fill: 'none',
  stroke: 'currentColor',
  strokeWidth: 1.8,
  strokeLinecap: 'round',
  strokeLinejoin: 'round',
};

export function MailIcon() {
  return (
    <svg {...base}>
      <rect x="3" y="5" width="18" height="14" rx="2" />
      <path d="m3 7 9 6 9-6" />
    </svg>
  );
}

export function LockIcon() {
  return (
    <svg {...base}>
      <rect x="5" y="11" width="14" height="10" rx="2" />
      <path d="M8 11V7a4 4 0 0 1 8 0v4" />
    </svg>
  );
}

export function UserIcon() {
  return (
    <svg {...base}>
      <circle cx="12" cy="8" r="4" />
      <path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" />
    </svg>
  );
}

export function EyeOpenIcon() {
  return (
    <svg {...base}>
      <path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12z" />
      <circle cx="12" cy="12" r="3" />
    </svg>
  );
}

export function EyeClosedIcon() {
  return (
    <svg {...base}>
      <path d="M3 3l18 18M10.6 6.1A10 10 0 0 1 12 6c6.5 0 10 6 10 6a17 17 0 0 1-3.2 3.9M6.6 6.6C3.8 8.4 2 12 2 12s3.5 7 10 7a9.6 9.6 0 0 0 5.4-1.6" />
      <path d="M9.9 9.9a3 3 0 0 0 4.2 4.2" />
    </svg>
  );
}

export function ArrowIcon() {
  return (
    <svg {...base} strokeWidth={2} className="arrow">
      <path d="M5 12h14M13 6l6 6-6 6" />
    </svg>
  );
}

export function BackArrowIcon() {
  return (
    <svg {...base} width={16} height={16}>
      <path d="M19 12H5M11 6l-6 6 6 6" />
    </svg>
  );
}

export function SendIcon({ size = 26 }) {
  return (
    <svg {...base} width={size} height={size}>
      <path d="M22 2 11 13M22 2l-7 20-4-9-9-4z" />
    </svg>
  );
}

export function ClockIcon({ size = 26 }) {
  return (
    <svg {...base} width={size} height={size}>
      <circle cx="12" cy="13" r="8" />
      <path d="M12 9v4l2 2M9 2h6" />
    </svg>
  );
}

export function EmptyCircleIcon() {
  return (
    <svg aria-hidden="true" width="16" height="16" viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" fill="none" stroke="#5a5650" strokeWidth="1.5" />
    </svg>
  );
}

export function CheckCircleIcon({ size = 18 }) {
  return (
    <svg aria-hidden="true" width={size} height={size} viewBox="0 0 24 24">
      <circle cx="12" cy="12" r="10" fill="#f5a524" />
      <path
        d="m7.5 12.5 3 3 6-6.5"
        fill="none"
        stroke="#1a1206"
        strokeWidth="2.4"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function BrandLogo() {
  return (
    <svg aria-hidden="true" width="36" height="36" viewBox="0 0 32 32">
      <path d="M16 3 29 10.5v11L16 29 3 21.5v-11z" fill="none" stroke="var(--accent)" strokeWidth="2.4" />
      <path d="M8 14l8-4 8 4-8 4z" fill="var(--accent)" />
      <path
        d="M11 16v4c0 1.5 2.2 3 5 3s5-1.5 5-3v-4"
        fill="none"
        stroke="var(--accent)"
        strokeWidth="2"
      />
    </svg>
  );
}
