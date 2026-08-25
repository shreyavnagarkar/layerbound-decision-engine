// Renders Yes / No / Not specified radios for an Optional[bool] field.
// "Not specified" maps to null, which the backend's hard-rule checks treat
// the same as "No" when the requirement is mandatory - see README.
function TriStateField({ label, name, value, onChange }) {
  const options = [
    { label: 'Yes', value: 'true' },
    { label: 'No', value: 'false' },
    { label: 'Not specified', value: 'null' },
  ]

  return (
    <fieldset className="tri-state-field">
      <legend>{label}</legend>
      <div className="tri-state-options">
        {options.map((opt) => (
          <label key={opt.value} className="tri-state-option">
            <input
              type="radio"
              name={name}
              value={opt.value}
              checked={String(value) === opt.value}
              onChange={() =>
                onChange(opt.value === 'null' ? null : opt.value === 'true')
              }
            />
            {opt.label}
          </label>
        ))}
      </div>
    </fieldset>
  )
}

export default TriStateField
