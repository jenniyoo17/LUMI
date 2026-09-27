interface Props {
  enabled: boolean
  onChange: (next: boolean) => void
  label: string
}

/** An accessible on/off switch that also spells out ON / OFF in text, per spec. */
export function DataSourceToggle({ enabled, onChange, label }: Props) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
      <span className="toggle-status" data-on={enabled}>
        {enabled ? 'ON' : 'OFF'}
      </span>
      <button
        type="button"
        className="toggle"
        data-on={enabled}
        role="switch"
        aria-checked={enabled}
        aria-label={`Turn ${label} ${enabled ? 'off' : 'on'}`}
        onClick={() => onChange(!enabled)}
      >
        <span className="toggle-knob" />
      </button>
    </div>
  )
}
