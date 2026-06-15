// Safe Set: quiet, non-dismissable disclaimer present on every screen.
export function DisclaimerBanner() {
  return (
    <div
      style={{
        background: "var(--surface)",
        color: "var(--ink-muted-80)",
        borderTop: "1px solid var(--hairline)",
      }}
      className="fixed bottom-0 inset-x-0 z-40 px-5 py-2 text-center"
    >
      <p style={{ fontSize: 12, lineHeight: 1.4, margin: 0 }}>
        Stillframe supports reflection. It is not therapy, diagnosis, or crisis care.
        If you are in danger, contact a crisis line.
      </p>
    </div>
  );
}
