"use client";
import { useEffect, useState } from "react";

/**
 * useState that survives closing the page. Data stays in this browser's localStorage only.
 * `ready` is false until saved data has been loaded, so callers can avoid flashing the first screen.
 */
export function usePersistentState<T>(key: string, initial: T) {
  const [state, setState] = useState<T>(initial);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    try {
      const raw = localStorage.getItem(key);
      if (raw) setState(JSON.parse(raw) as T);
    } catch {
      /* corrupted or blocked storage: start fresh */
    }
    setReady(true);
  }, [key]);

  useEffect(() => {
    if (!ready) return;
    try {
      localStorage.setItem(key, JSON.stringify(state));
    } catch {
      /* storage full or blocked: keep working in memory */
    }
  }, [key, state, ready]);

  return [state, setState, ready] as const;
}
