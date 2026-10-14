"use client";
import { FormEvent, useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useRole } from "@/lib/roleContext";
import { useBrowserOnline } from "@/lib/useBrowserOnline";
import { DAMAGE_CATEGORIES, PayoutSession, SessionAction, SessionDetails, SessionState, ValidatedListVersion, createPayoutSession, fetchPayoutSessions, fetchSessionStaff, fetchValidatedLists, formatPeso, revisePayoutSession } from "@/lib/api";
import { formatRecordedDate } from "@/lib/recordedDate";
import { receiptVerificationHref } from "@/lib/receiptNavigation";

const STATE: Record<SessionState, string> = { SCHEDULED: "Scheduled", OPEN: "Open now", CLOSED: "Closed", CANCELLED: "Cancelled" };
const ACTION: Record<SessionAction | "SCHEDULE", string> = { SCHEDULE: "Scheduled", OPEN: "Opened", CLOSE: "Closed", REOPEN: "Reopened", EDIT: "Edited", CANCEL: "Cancelled" };
const badge = (state: SessionState) => "registry-badge " + (state === "OPEN" ? "registry-approved" : state === "CANCELLED" ? "registry-rejected" : "registry-pending");
const day = (value: string) => new Date(value + "T00:00:00").toLocaleDateString("en-PH", { weekday: "long", year: "numeric", month: "long", day: "numeric" });
const blank: SessionDetails = { session_date: "", site: "", assigned: [] };

function DetailsFields({ value, staff, onChange, disabled }: { value: SessionDetails; staff: { id: string; name: string }[]; onChange: (v: SessionDetails) => void; disabled: boolean }) {
  return <>
    <label>Session date<input type="date" required disabled={disabled} value={value.session_date} onChange={e => onChange({ ...value, session_date: e.target.value })} /></label>
    <label>Payout site<input required maxLength={200} disabled={disabled} value={value.site} onChange={e => onChange({ ...value, site: e.target.value })} /></label>
    <fieldset className="space-y-2"><legend>Assigned disbursing staff</legend>
      {!staff.length ? <p className="registry-muted">No enabled disbursing accounts for this barangay.</p> : staff.map(s => <label key={s.id} className="registry-checkbox"><input type="checkbox" disabled={disabled} checked={value.assigned.includes(s.id)} onChange={e => onChange({ ...value, assigned: e.target.checked ? [...value.assigned, s.id] : value.assigned.filter(id => id !== s.id) })} />{s.name}</label>)}
    </fieldset>
  </>;
}

export default function SessionsPage() {
  const { account } = useRole(), online = useBrowserOnline(), params = useSearchParams(), router = useRouter();
  const role = account?.role;
  const [sessions, setSessions] = useState<PayoutSession[]>([]), [lists, setLists] = useState<ValidatedListVersion[]>([]), [staff, setStaff] = useState<{ id: string; name: string }[]>([]);
  const [loading, setLoading] = useState(true), [readError, setReadError] = useState(""), [busy, setBusy] = useState(false), [error, setError] = useState(""), [notice, setNotice] = useState("");
  const [listId, setListId] = useState(""), [draft, setDraft] = useState<SessionDetails>(blank), [change, setChange] = useState<SessionAction | null>(null), [edit, setEdit] = useState<SessionDetails>(blank), [reason, setReason] = useState("");
  const generation = useRef(0), retry = useRef<string | null>(null);
  const requested = params.get("session_id");
  const selected = sessions.find(s => s.session_id === requested) || (requested === null ? sessions[0] : undefined);
  const active = (s: PayoutSession) => s.current.state !== "CANCELLED";
  const open = lists.filter(l => l.state === "FINALIZED" && !l.stale && !sessions.some(s => s.list_id === l.list_id && active(s)));
  const scheduleBarangay = lists.find(l => l.list_id === listId)?.snapshot.barangay_id;
  const assignedToMe = !!selected && selected.current.assigned.some(a => a.id === account?.id);

  async function load() {
    const current = ++generation.current; setLoading(true); setReadError("");
    try {
      const [s, l] = await Promise.all([fetchPayoutSessions(), role === "DSWD" ? fetchValidatedLists() : Promise.resolve([])]);
      if (current !== generation.current) return;
      setSessions(s); setLists(l);
    } catch (e) { if (current === generation.current) setReadError(e instanceof Error ? e.message : "Payout sessions unavailable."); }
    finally { if (current === generation.current) setLoading(false); }
  }
  useEffect(() => { if (account && role !== "BENEFICIARY") void load(); return () => { generation.current++; }; }, [account?.id]);
  useEffect(() => { if (!listId && open[0]) setListId(open[0].list_id); }, [lists, sessions]);
  useEffect(() => {
    const barangay = change === "EDIT" ? selected?.barangay_id : scheduleBarangay;
    if (role !== "DSWD" || !barangay) return;
    let live = true;
    fetchSessionStaff(barangay).then(rows => { if (live) setStaff(rows); }).catch(() => { if (live) setStaff([]); });
    return () => { live = false; };
  }, [role, scheduleBarangay, change, selected?.barangay_id]);
  useEffect(() => { setChange(null); setReason(""); setError(""); retry.current = null; }, [selected?.session_id, selected?.current.revision]);
  function changed() { retry.current = null; setError(""); setNotice(""); }

  async function run(work: () => Promise<PayoutSession>, message: string) {
    if (busy || !online) return false;
    setBusy(true); setError(""); retry.current ||= crypto.randomUUID();
    try {
      const result = await work();
      setSessions(prev => [result, ...prev.filter(s => s.session_id !== result.session_id)]);
      retry.current = null; setNotice(message); setChange(null); setReason("");
      router.replace("/sessions?" + new URLSearchParams({ session_id: result.session_id }), { scroll: false });
      return true;
    } catch (e) { setError(e instanceof Error ? e.message : "Session change was not saved."); return false; }
    finally { setBusy(false); }
  }
  async function schedule(event: FormEvent) {
    event.preventDefault();
    if (await run(() => createPayoutSession({ ...draft, list_id: listId, request_id: retry.current! }), "Session scheduled. Assigned staff see it in their sessions.")) setDraft(blank);
  }
  function act(action: SessionAction, event?: FormEvent) {
    event?.preventDefault();
    if (!selected) return;
    void run(() => revisePayoutSession(selected.session_id, { request_id: retry.current!, expected_revision: selected.current.revision, action, ...(reason.trim() ? { reason } : {}), ...(action === "EDIT" ? { details: edit } : {}) }), ACTION[action] + ".");
  }

  if (role === "BENEFICIARY") return <section className="registry space-y-3"><h1>Payout sessions are a staff task</h1><p>Your collection date and site appear on your household home.</p><Link href="/household" className="registry-button">My household</Link></section>;
  const state = selected?.current.state;
  const quick: SessionAction[] = !selected || selected.superseded ? [] : [
    ...(state === "SCHEDULED" && (role === "DSWD" || assignedToMe) ? ["OPEN" as const] : []),
    ...(state === "OPEN" && (role === "DSWD" || assignedToMe) ? ["CLOSE" as const] : []),
  ];
  const withReason: SessionAction[] = !selected || role !== "DSWD" || selected.superseded ? [] : [
    ...(state === "SCHEDULED" || state === "OPEN" ? ["EDIT" as const] : []),
    ...(state === "CLOSED" ? ["REOPEN" as const] : []),
    ...(state === "SCHEDULED" ? ["CANCEL" as const] : []),
  ];
  const label: Record<SessionAction, string> = { OPEN: "Open session", CLOSE: "Close session", REOPEN: "Reopen session", EDIT: "Edit session", CANCEL: "Cancel session" };
  const percent = selected && selected.progress.included ? Math.round(100 * selected.progress.recorded / selected.progress.included) : 0;

  return <div className="registry workflow sessions-page space-y-6">
    <header className="registry-header"><div><p className="registry-eyebrow">Payout day</p><h1>{role === "DISBURSING" ? "My payout sessions" : "Payout sessions"}</h1><p className="registry-description">{role === "DISBURSING" ? "Open your assigned session, pay each listed household at the desk, then close it." : "Assign disbursing staff to a finalized list for a set day. Once a session exists, only its assigned staff can record that list's payouts, and only while it is open."}</p></div>
      <div className="flex flex-wrap gap-2">{role === "DSWD" && <Link href="/lists" className="registry-button">Validated lists</Link>}<button className="registry-button registry-text-button" disabled={loading || !online} onClick={() => void load()}>Refresh sessions</button></div></header>
    {!online && <p role="alert" className="registry-notice">Offline. These are the last loaded sessions. Reconnect before changing a session; nothing is queued.</p>}
    {loading && <p role="status">Loading payout sessions...</p>}
    {readError && <div role="alert" className="registry-error"><p>{readError}</p><button className="registry-button" disabled={loading || !online} onClick={() => void load()}>Retry sessions</button></div>}
    {notice && <p role="status" className="registry-success">{notice}</p>}
    {!loading && !readError && <div className="workflow-columns list-workspace">
      <div className="space-y-6">
        {role === "DSWD" && <form className="workflow-panel space-y-4" onSubmit={schedule} aria-label="Schedule a session"><h2>Schedule a session</h2>
          {!open.length ? <p>No finalized, unchanged list is waiting for a session. <Link className="underline" href="/lists">Finalize a list first.</Link></p> : <>
            <label htmlFor="session-list">Finalized list version</label><select id="session-list" disabled={busy} value={listId} onChange={e => { setListId(e.target.value); setDraft({ ...draft, assigned: [] }); changed(); }}>{open.map(l => <option key={l.list_id} value={l.list_id}>{l.snapshot.barangay_name} · version {l.version} · {l.snapshot.rows.filter(r => r.included).length} included</option>)}</select>
            <DetailsFields value={draft} staff={staff} disabled={busy} onChange={v => { setDraft(v); changed(); }} />
            <button className="registry-button registry-primary" disabled={busy || !online || !listId || !draft.assigned.length}>{busy ? "Saving..." : "Schedule session"}</button></>}
        </form>}
        <section className="workflow-panel space-y-3" aria-label="Sessions"><h2>{role === "DISBURSING" ? "Assigned to you" : "Sessions"}</h2>
          {!sessions.length ? <div className="registry-empty"><h3>No sessions yet</h3><p className="registry-muted">{role === "DISBURSING" ? "DSWD has not assigned you to a payout session. Households without a session can still be paid at the desk." : "Schedule a session for a finalized list."}</p></div>
            : <ul>{sessions.map(s => <li key={s.session_id} className="workflow-record"><Link className="version-row" aria-current={s.session_id === selected?.session_id ? "page" : undefined} href={"/sessions?" + new URLSearchParams({ session_id: s.session_id })} scroll={false}>{s.barangay_name} · {day(s.current.session_date)}</Link><p><span className={badge(s.current.state)}>{STATE[s.current.state]}</span> {s.progress.recorded} of {s.progress.included} paid{s.superseded ? " · superseded list" : ""}</p></li>)}</ul>}
        </section>
      </div>
      <section className="workflow-panel space-y-4" aria-label="Selected session">
        {!selected ? <><h2>{requested ? "Session unavailable" : "Select a session"}</h2><p>{requested ? "This session is missing or not assigned to your account." : "Choose a session to see its households and progress."}</p></> : <>
          <div className="workflow-section-heading"><h2>{selected.barangay_name} · {day(selected.current.session_date)}</h2><span className={badge(selected.current.state)}>{STATE[selected.current.state]}</span></div>
          <p className="registry-muted">{selected.current.site} · list version {selected.list_version} · {selected.batch_name}</p>
          <dl className="receipt-references"><dt>Assigned staff</dt><dd>{selected.current.assigned.map(a => a.name).join(", ")}</dd><dt>Progress</dt><dd>{selected.progress.recorded} of {selected.progress.included} households paid</dd></dl>
          <div className="session-progress" role="progressbar" aria-label="Households paid" aria-valuemin={0} aria-valuemax={100} aria-valuenow={percent}><span style={{ width: percent + "%" }} /></div>
          {selected.superseded && <p role="alert" className="registry-notice">A newer finalized list exists for this barangay. Schedule a session for that version.</p>}
          {error && <p role="alert" className="registry-error">{error}</p>}
          {change ? <form className="registry-decision space-y-3" onSubmit={e => act(change, e)}><h3>{label[change]}</h3>
            {change === "EDIT" && <DetailsFields value={edit} staff={staff} disabled={busy} onChange={v => { setEdit(v); changed(); }} />}
            <label>Reason (staff only)<textarea required maxLength={512} disabled={busy} value={reason} onChange={e => { setReason(e.target.value); changed(); }} /></label>
            <div className="flex flex-wrap gap-3"><button className="registry-button registry-primary" disabled={busy || !online || !reason.trim() || (change === "EDIT" && !edit.assigned.length)}>{busy ? "Saving..." : "Confirm: " + label[change].toLowerCase()}</button><button type="button" className="registry-button" disabled={busy} onClick={() => { setChange(null); setReason(""); changed(); }}>Back</button></div>
          </form> : (quick.length > 0 || withReason.length > 0) && <div className="flex flex-wrap gap-3">
            {quick.map(a => <button key={a} className="registry-button registry-primary" disabled={busy || !online} onClick={() => act(a)}>{busy ? "Saving..." : label[a]}</button>)}
            {withReason.map(a => <button key={a} className="registry-button" disabled={busy} onClick={() => { setChange(a); changed(); if (a === "EDIT") setEdit({ session_date: selected.current.session_date, site: selected.current.site, assigned: selected.current.assigned.map(s => s.id) }); }}>{label[a]}</button>)}
          </div>}
          {selected.roster && <div className="material-table-wrap"><table className="material-table"><caption className="sr-only">Households in this session</caption><thead><tr><th>Household</th><th>Amount</th><th>Payout</th></tr></thead><tbody>{selected.roster.map(r => <tr key={r.beneficiary_id}><td><strong>{r.household_name}</strong><small>{r.beneficiary_id}</small></td><td data-label="Amount">{formatPeso(r.amount_centavos / 100)}<small>{r.category ? DAMAGE_CATEGORIES[r.category] : "Standard grant"}</small></td><td data-label="Payout">{r.distribution_id ? <Link className="registry-button registry-text-button" href={receiptVerificationHref(r.distribution_id)}>Paid · check receipt</Link> : role === "DISBURSING" && assignedToMe && state === "OPEN" ? <Link className="registry-button" href={"/distributions?" + new URLSearchParams({ beneficiary_id: r.beneficiary_id })}>Record payout</Link> : <span className="registry-muted">Not paid</span>}</td></tr>)}</tbody></table></div>}
          {!selected.roster && <p className="registry-muted">Household names and payouts are visible to DSWD, auditors and assigned staff.</p>}
          <details><summary>Session history ({selected.history.length})</summary><ul>{selected.history.map(h => <li key={h.revision} className="workflow-record"><p><strong>{ACTION[h.action]}</strong> · {h.revised_name} · {formatRecordedDate(h.revised_at)}</p><p>{day(h.session_date)} · {h.site}</p>{h.reason && <p className="registry-muted">{h.reason}</p>}</li>)}</ul></details>
        </>}
      </section>
    </div>}
  </div>;
}
