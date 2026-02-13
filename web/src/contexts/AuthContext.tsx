import { createContext, useState, useEffect, useCallback, type ReactNode } from "react"
import { getAuthStatus, verifyToken } from "@/api"

interface AuthState {
  required: boolean | null
  authenticated: boolean
  loading: boolean
}

interface AuthContextValue extends AuthState {
  login: (token: string) => Promise<void>
  logout: () => void
}

export const AuthContext = createContext<AuthContextValue>({
  required: null,
  authenticated: false,
  loading: true,
  login: async () => {},
  logout: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    required: null,
    authenticated: false,
    loading: true,
  })

  useEffect(() => {
    let cancelled = false
    async function check() {
      try {
        const { required } = await getAuthStatus()
        if (cancelled) return
        if (!required) {
          setState({ required: false, authenticated: true, loading: false })
          return
        }
        const stored = localStorage.getItem("auth_token")
        if (!stored) {
          setState({ required: true, authenticated: false, loading: false })
          return
        }
        const { valid } = await verifyToken(stored)
        if (cancelled) return
        setState({ required: true, authenticated: valid, loading: false })
        if (!valid) localStorage.removeItem("auth_token")
      } catch {
        if (!cancelled) setState({ required: null, authenticated: false, loading: false })
      }
    }
    check()
    return () => { cancelled = true }
  }, [])

  const login = useCallback(async (token: string) => {
    const { valid } = await verifyToken(token)
    if (valid) {
      localStorage.setItem("auth_token", token)
      setState(s => ({ ...s, authenticated: true }))
    } else {
      throw new Error("Invalid token")
    }
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem("auth_token")
    setState(s => ({ ...s, authenticated: false }))
  }, [])

  return (
    <AuthContext value={{ ...state, login, logout }}>
      {children}
    </AuthContext>
  )
}
