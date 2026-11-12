// Bộ icon nhỏ cho trang chủ (nét mảnh, cùng kiểu icon trong app).
const PATHS = {
  route: (
    <>
      <circle cx="6" cy="18" r="2" />
      <circle cx="18" cy="6" r="2" />
      <path d="M8 18h6a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h6" />
    </>
  ),
  bulb: (
    <>
      <path d="M9 18h6M10 21h4" />
      <path d="M12 3a6 6 0 0 0-3.5 10.9c.6.4 1 1.1 1 1.8V16h5v-.3c0-.7.4-1.4 1-1.8A6 6 0 0 0 12 3z" />
    </>
  ),
  check: (
    <>
      <rect x="5" y="4" width="14" height="17" rx="2" />
      <path d="M9 4V3h6v1M9 13l2 2 4-4" />
    </>
  ),
  chart: <path d="M4 20V4M4 20h16M8 16l4-5 3 3 5-6" />,
  badge: (
    <>
      <circle cx="12" cy="9" r="5" />
      <path d="m9 13.5-1.5 7L12 18l4.5 2.5-1.5-7" />
    </>
  ),
  bot: (
    <>
      <rect x="4" y="8" width="16" height="11" rx="3" />
      <path d="M12 4v4M9 13h.01M15 13h.01M10 16h4" />
    </>
  ),
  arrow: <path d="M5 12h14M13 6l6 6-6 6" />,
  play: <path d="M8 5v14l11-7z" />,
  book: (
    <>
      <path d="M12 6c-2-1.3-5-2-8-1.5v14c3-.5 6 .2 8 1.5 2-1.3 5-2 8-1.5v-14c-3-.5-6 .2-8 1.5z" />
      <path d="M12 6v14" />
    </>
  ),
  news: (
    <>
      <rect x="3" y="5" width="18" height="15" rx="2" />
      <path d="M7 9h10M7 13h6M7 16h4" />
    </>
  ),
};

export default function HomeIcon({ name, size = 18 }) {
  return (
    <svg
      aria-hidden="true"
      width={size}
      height={size}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      {PATHS[name]}
    </svg>
  );
}
