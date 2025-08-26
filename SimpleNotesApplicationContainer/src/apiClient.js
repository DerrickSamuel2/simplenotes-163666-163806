const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000/api/v1";

async function request(path, { method = "GET", body, token, headers = {} } = {}) {
  const init = {
    method,
    headers: {
      "Content-Type": body instanceof FormData ? undefined : "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...headers,
    },
    body: body instanceof FormData ? body : body ? JSON.stringify(body) : undefined,
  };
  const res = await fetch(`${API_BASE}${path}`, init);
  const ct = res.headers.get("content-type") || "";
  const data = ct.includes("application/json") ? await res.json() : await res.text();
  if (!res.ok) {
    throw new Error(data?.detail || data?.message || res.statusText);
  }
  return data;
}

// PUBLIC_INTERFACE
export const Api = {
  /** Register a user */
  register: (payload) => request("/auth/register", { method: "POST", body: payload }),
  /** Login and get access token */
  login: (payload) => request("/auth/login", { method: "POST", body: payload }),
  /** Verify email */
  verifyEmail: (formData) => request("/auth/verify", { method: "POST", body: formData }),
  /** Request password reset */
  requestReset: (formData) => request("/auth/request-password-reset", { method: "POST", body: formData }),
  /** Reset password */
  resetPassword: (formData) => request("/auth/reset-password", { method: "POST", body: formData }),

  me: (token) => request("/users/me", { token }),
  updateMe: (token, payload) => request("/users/me", { method: "PATCH", token, body: payload }),

  listNotes: (token) => request("/notes", { token }),
  getNote: (token, id) => request(`/notes/${id}`, { token }),
  createNote: (token, payload) => request("/notes", { method: "POST", token, body: payload }),
  updateNote: (token, id, payload) => request(`/notes/${id}`, { method: "PATCH", token, body: payload }),
  deleteNote: (token, id) => request(`/notes/${id}`, { method: "DELETE", token }),

  uploadAttachment: async (token, noteId, file) => {
    const fd = new FormData();
    fd.append("file", file);
    return request(`/notes/${noteId}/attachments`, { method: "POST", token, body: fd, headers: {} });
  },

  searchNotes: (token, payload) => request("/notes/search", { method: "POST", token, body: payload }),
  bulk: (token, payload) => request("/notes/bulk", { method: "POST", token, body: payload }),

  listTags: (token) => request("/taxonomy/tags", { token }),
  createTag: (token, payload) => request("/taxonomy/tags", { method: "POST", token, body: payload }),
  listCategories: (token) => request("/taxonomy/categories", { token }),
  createCategory: (token, payload) => request("/taxonomy/categories", { method: "POST", token, body: payload }),
};
