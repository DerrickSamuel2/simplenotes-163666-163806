import React, { createContext, useContext, useEffect, useState } from "react";
import { Api } from "./apiClient";

const AuthCtx = createContext(null);

// PUBLIC_INTERFACE
export function AuthProvider({ children }) {
  /** Provide authentication state (token, user) to the app. */
  const [token, setToken] = useState(localStorage.getItem("token") || "");
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!token);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      if (!token) return;
      try {
        const me = await Api.me(token);
        if (!cancelled) setUser(me);
      } catch (e) {
        console.warn("Auth load error", e);
        if (!cancelled) {
          setToken("");
          localStorage.removeItem("token");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    load();
    return () => { cancelled = true; };
  }, [token]);

  const login = async (email, password) => {
    const res = await Api.login({ email, password });
    setToken(res.access_token);
    localStorage.setItem("token", res.access_token);
    const me = await Api.me(res.access_token);
    setUser(me);
  };

  const logout = () => {
    setToken("");
    setUser(null);
    localStorage.removeItem("token");
  };

  const value = { token, user, loading, login, logout, setUser };
  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}

// PUBLIC_INTERFACE
export function useAuth() {
  /** Hook to access auth state. */
  return useContext(AuthCtx);
}
