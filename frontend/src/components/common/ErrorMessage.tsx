export function ErrorMessage({ message }: { message: string }) {
  return (
    <div className="rounded-lg border border-corner-b/40 bg-corner-b-dim/20 px-4 py-3 text-sm text-corner-b">
      {message}
    </div>
  )
}
