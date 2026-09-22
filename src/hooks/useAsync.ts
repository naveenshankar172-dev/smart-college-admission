import { useEffect, useState } from 'react'

export function useAsync<T>(loader: () => Promise<T>, initial: T) {
  const [data, setData] = useState<T>(initial)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { let active = true; loader().then(value => { if (active) setData(value) }).catch(() => { if (active) setError('Unable to load this information right now.') }).finally(() => { if (active) setLoading(false) }); return () => { active = false } }, [loader])
  return { data, loading, error }
}
