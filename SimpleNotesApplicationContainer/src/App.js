import React, { useEffect, useState } from "react";
import { BrowserRouter, Link, Navigate, Route, Routes } from "react-router-dom";
import "./App.css";
import { AuthProvider, useAuth } from "./authContext";
import { Api } from "./apiClient";

function Layout({ children }) {
  const { user, logout } = useAuth();
  return (
    <div className="App">
      <header className="App-header" style={{ alignItems: "stretch" }}>
        <nav className="navbar" style={{ display: "flex", gap: 16, padding: 12 }}>
          <Link to="/" className="App-link">SimpleNotes</Link>
          <Link to="/notes" className="App-link">Notes</Link>
          <Link to="/search" className="App-link">Search</Link>
          <div style={{ marginLeft: "auto" }}>
            {user ? (
              <>
                <Link to="/profile" className="App-link">{user.email}</Link>
                <button className="theme-toggle" onClick={logout} aria-label="Logout">Logout</button>
              </>
            ) : (
              <>
                <Link to="/login" className="App-link">Login</Link>
                <Link to="/register" className="App-link" style={{ marginLeft: 12 }}>Register</Link>
              </>
            )}
          </div>
        </nav>
        <div style={{ padding: 24, textAlign: "left", maxWidth: 1000, margin: "0 auto", width: "100%" }}>
          {children}
        </div>
      </header>
    </div>
  );
}

function RequireAuth({ children }) {
  const { user, loading } = useAuth();
  if (loading) return <p>Loading...</p>;
  if (!user) return <Navigate to="/login" replace />;
  return children;
}

function LoginPage() {
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [err, setErr] = useState("");
  const onSubmit = async (e) => {
    e.preventDefault();
    setErr("");
    try {
      await login(email, password);
    } catch (e) {
      setErr(e.message);
    }
  };
  return (
    <form onSubmit={onSubmit}>
      <h2>Login</h2>
      {err && <p style={{ color: "salmon" }}>{err}</p>}
      <div><label>Email</label><br /><input value={email} onChange={e => setEmail(e.target.value)} /></div>
      <div><label>Password</label><br /><input type="password" value={password} onChange={e => setPassword(e.target.value)} /></div>
      <button className="theme-toggle" type="submit">Login</button>
      <div style={{ marginTop: 8 }}>
        <Link to="/request-reset" className="App-link">Forgot password?</Link>
      </div>
    </form>
  );
}

function RegisterPage() {
  const [email, setEmail] = useState("");
  const [fullName, setFullName] = useState("");
  const [password, setPassword] = useState("");
  const [ok, setOk] = useState("");
  const [err, setErr] = useState("");
  const onSubmit = async (e) => {
    e.preventDefault();
    setErr(""); setOk("");
    try {
      await Api.register({ email, password, full_name: fullName || null });
      setOk("Registered! Check your email for verification link (stubbed in backend logs).");
    } catch (e) {
      setErr(e.message);
    }
  };
  return (
    <form onSubmit={onSubmit}>
      <h2>Register</h2>
      {err && <p style={{ color: "salmon" }}>{err}</p>}
      {ok && <p style={{ color: "lightgreen" }}>{ok}</p>}
      <div><label>Email</label><br /><input value={email} onChange={e => setEmail(e.target.value)} /></div>
      <div><label>Full name</label><br /><input value={fullName} onChange={e => setFullName(e.target.value)} /></div>
      <div><label>Password</label><br /><input type="password" value={password} onChange={e => setPassword(e.target.value)} /></div>
      <button className="theme-toggle" type="submit">Create account</button>
    </form>
  );
}

function VerifyPage() {
  const [msg, setMsg] = useState("Verifying...");
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    if (!token) { setMsg("Missing token"); return; }
    const fd = new FormData();
    fd.append("token", token);
    Api.verifyEmail(fd).then(() => setMsg("Email verified! You may login now.")).catch((e) => setMsg(e.message));
  }, []);
  return <p>{msg}</p>;
}

function RequestResetPage() {
  const [email, setEmail] = useState("");
  const [msg, setMsg] = useState("");
  const onSubmit = async (e) => {
    e.preventDefault();
    const fd = new FormData();
    fd.append("email", email);
    await Api.requestReset(fd);
    setMsg("If the email exists, a reset link has been sent.");
  };
  return (
    <form onSubmit={onSubmit}>
      <h2>Reset password</h2>
      {msg && <p>{msg}</p>}
      <div><label>Email</label><br /><input value={email} onChange={e => setEmail(e.target.value)} /></div>
      <button className="theme-toggle" type="submit">Send reset link</button>
    </form>
  );
}

function ResetPasswordPage() {
  const [msg, setMsg] = useState("");
  const [password, setPassword] = useState("");
  const onSubmit = async (e) => {
    e.preventDefault();
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    const fd = new FormData();
    fd.append("token", token || "");
    fd.append("new_password", password);
    try{
      await Api.resetPassword(fd);
      setMsg("Password updated!");
    }catch(e){ setMsg(e.message); }
  };
  return (
    <form onSubmit={onSubmit}>
      <h2>Set new password</h2>
      {msg && <p>{msg}</p>}
      <div><label>New password</label><br /><input type="password" value={password} onChange={e => setPassword(e.target.value)} /></div>
      <button className="theme-toggle" type="submit">Update password</button>
    </form>
  );
}

function NotesPage() {
  const { token } = useAuth();
  const [notes, setNotes] = useState([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [tags, setTags] = useState("");
  const [error, setError] = useState("");

  const load = async () => {
    try {
      const list = await Api.listNotes(token);
      setNotes(list);
    } catch (e) {
      setError(e.message);
    }
  };
  useEffect(() => { load(); }, []);

  const create = async (e) => {
    e.preventDefault();
    try {
      await Api.createNote(token, { title, content, tags: tags.split(",").map(s=>s.trim()).filter(Boolean) });
      setTitle(""); setContent(""); setTags("");
      await load();
    } catch (e) { setError(e.message); }
  };

  const del = async (id) => {
    await Api.deleteNote(token, id);
    await load();
  };

  const upload = async (noteId, file) => {
    if (!file) return;
    await Api.uploadAttachment(token, noteId, file);
    await load();
  };

  return (
    <>
      <h2>My Notes</h2>
      {error && <p style={{ color: "salmon" }}>{error}</p>}
      <form onSubmit={create} style={{ marginBottom: 16 }}>
        <div><label>Title</label><br /><input value={title} onChange={e => setTitle(e.target.value)} required /></div>
        <div><label>Content (rich: accepts HTML/Markdown)</label><br /><textarea value={content} onChange={e => setContent(e.target.value)} rows={5} /></div>
        <div><label>Tags (comma separated)</label><br /><input value={tags} onChange={e => setTags(e.target.value)} /></div>
        <button className="theme-toggle" type="submit">Add</button>
      </form>
      <ul>
        {notes.map(n => (
          <li key={n.id} style={{ marginBottom: 12 }}>
            <strong>{n.title}</strong> {n.is_archived ? "(archived)" : ""}<br />
            <div dangerouslySetInnerHTML={{ __html: n.content }} />
            <div>Tags: {(n.tags || []).map(t => t.name).join(", ")}</div>
            <div>Attachments: {(n.attachments || []).map(a => (<a key={a.id} href={a.url} target="_blank" rel="noreferrer">{a.filename}</a>))}</div>
            <div style={{ marginTop: 6 }}>
              <button className="theme-toggle" onClick={() => del(n.id)}>Delete</button>
              <label style={{ marginLeft: 8 }}>
                <input type="file" onChange={e => upload(n.id, e.target.files?.[0])} />
              </label>
            </div>
          </li>
        ))}
      </ul>
    </>
  );
}

function SearchPage() {
  const { token } = useAuth();
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const find = async (e) => {
    e?.preventDefault();
    const found = await Api.searchNotes(token, { query });
    setResults(found);
  };
  return (
    <>
      <h2>Search</h2>
      <form onSubmit={find}>
        <input placeholder="Search notes" value={query} onChange={e => setQuery(e.target.value)} />
        <button className="theme-toggle" type="submit">Search</button>
      </form>
      <ul>
        {results.map(n => (<li key={n.id}><strong>{n.title}</strong></li>))}
      </ul>
    </>
  );
}

function ProfilePage() {
  const { user, token, setUser } = useAuth();
  const [fullName, setFullName] = useState(user?.full_name || "");
  const [allowAnalytics, setAllowAnalytics] = useState(!!user?.allow_analytics);
  const [privateAccount, setPrivateAccount] = useState(!!user?.private_account);
  const [msg, setMsg] = useState("");

  const save = async (e) => {
    e.preventDefault();
    const updated = await Api.updateMe(token, { full_name: fullName, allow_analytics: allowAnalytics, private_account: privateAccount });
    setUser(updated);
    setMsg("Profile updated");
  };
  return (
    <form onSubmit={save}>
      <h2>Profile</h2>
      {msg && <p>{msg}</p>}
      <div><label>Full name</label><br /><input value={fullName} onChange={e => setFullName(e.target.value)} /></div>
      <div><label><input type="checkbox" checked={allowAnalytics} onChange={e => setAllowAnalytics(e.target.checked)} /> Allow analytics</label></div>
      <div><label><input type="checkbox" checked={privateAccount} onChange={e => setPrivateAccount(e.target.checked)} /> Private account</label></div>
      <button className="theme-toggle" type="submit">Save</button>
    </form>
  );
}

function Home() {
  return (
    <>
      <h2>Welcome to SimpleNotes</h2>
      <p>Create, organize, and search your notes.</p>
    </>
  );
}

// PUBLIC_INTERFACE
function App() {
  const [theme, setTheme] = useState("light");
  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
  }, [theme]);
  return (
    <AuthProvider>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/verified" element={<VerifyPage />} />
            <Route path="/request-reset" element={<RequestResetPage />} />
            <Route path="/reset-success" element={<p>Password updated. You can login.</p>} />
            <Route path="/reset-password" element={<ResetPasswordPage />} />
            <Route path="/notes" element={<RequireAuth><NotesPage /></RequireAuth>} />
            <Route path="/search" element={<RequireAuth><SearchPage /></RequireAuth>} />
            <Route path="/profile" element={<RequireAuth><ProfilePage /></RequireAuth>} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
