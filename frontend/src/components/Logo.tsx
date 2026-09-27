interface Props {
  size?: number
  className?: string
}

/** Lumi's mark — a soft glowing orb with an inner ring. Kept as one reusable SVG. */
export function Logo({ size = 40, className }: Props) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 40 40"
      fill="none"
      className={className}
      aria-hidden="true"
    >
      <defs>
        <radialGradient id="lumi-glow" cx="35%" cy="30%" r="75%">
          <stop offset="0%" stopColor="#EFF6E9" />
          <stop offset="45%" stopColor="#7FAF98" />
          <stop offset="100%" stopColor="#6E7FC9" />
        </radialGradient>
      </defs>
      <circle cx="20" cy="20" r="18" fill="url(#lumi-glow)" />
      <circle cx="20" cy="20" r="18" fill="none" stroke="#FFFFFF" strokeOpacity="0.35" strokeWidth="1" />
      <circle cx="14" cy="14" r="4" fill="#FFFFFF" fillOpacity="0.55" />
    </svg>
  )
}
