import Link from "next/link";
import { ArrowRight, Banknote, Users, ReceiptText, Fingerprint } from "lucide-react";

const journey = [
  { title: "Release funds", copy: "Record the relief budget.", icon: Banknote },
  { title: "Review households", copy: "Check possible duplicates.", icon: Users },
  { title: "Record a payout", copy: "Keep a household receipt.", icon: ReceiptText },
  { title: "Check the record", copy: "Compare it with its saved proof.", icon: Fingerprint },
];

export default function LandingPage() {
  return (
    <div className="landing">
      <a className="landing-skip" href="#main-content">Skip to content</a>
      <header className="landing-header landing-width">
        <Link href="/" className="landing-brand" aria-label="AyudaChain home">
          <img src="/logo-emblem-transparent.png" alt="" width={44} height={44} />
          <span>AyudaChain<span className="landing-brand-caption">Relief with a record</span></span>
        </Link>
        <nav aria-label="Page navigation">
          <a href="#how-it-works">How it works <ArrowRight size={16} aria-hidden="true" /></a>
        </nav>
      </header>

      <main id="main-content" tabIndex={-1}>
        <section className="landing-hero landing-width" aria-labelledby="landing-heading">
          <div className="landing-intro">
            <span className="landing-eyebrow"><span aria-hidden="true" /> Fictional relief demo</span>
            <h1 id="landing-heading">Follow the aid.<br /><span>Keep the trust.</span></h1>
            <p className="landing-lead">Relief records can be lost, duplicated, or changed. AyudaChain helps citizens, field workers, and auditors follow the trail from funds to household receipts.</p>
            <Link href="/dashboard" className="landing-primary">Explore demo <ArrowRight size={20} aria-hidden="true" /></Link>
            <p className="landing-demo-note">Sample households. Simulated payouts. No real money.</p>
          </div>

          <figure className="landing-example" aria-labelledby="example-caption">
            <div className="landing-example-heading"><span>A household, a clear record</span><span className="landing-example-tag">Illustration</span></div>
            <div className="landing-receipt">
              <div className="landing-receipt-top"><ReceiptText size={25} aria-hidden="true" /><span>Household receipt<br /><small>Fictional example</small></span><span className="landing-receipt-number">01</span></div>
              <div className="landing-receipt-amount"><span>Recorded aid</span><strong>₱5,000<span>.00</span></strong></div>
              <dl><div><dt>Household</dt><dd>Soriano family</dd></div><div><dt>Relief batch</dt><dd>Typhoon Salinlahi</dd></div><div><dt>Payment</dt><dd>Simulated</dd></div></dl>
              <div className="landing-receipt-foot"><Fingerprint size={22} aria-hidden="true" /><p>A saved proof gives this receipt<br />a record to compare against.</p></div>
            </div>
            <figcaption id="example-caption">If the amount later changes to ₱2,000, comparing the receipt with its original proof can reveal the change.</figcaption>
          </figure>
        </section>

        <section id="how-it-works" className="landing-journey landing-width" aria-labelledby="journey-heading">
          <div className="landing-section-heading"><span className="landing-overline">The relief trail</span><h2 id="journey-heading">From a fund release to a family receipt.</h2></div>
          <ol>
            {journey.map(({ title, copy, icon: Icon }, index) => (
              <li key={title}><div className="landing-step-top"><span className="landing-step-number">0{index + 1}</span><Icon size={22} aria-hidden="true" /></div><h3>{title}</h3><p>{copy}</p></li>
            ))}
          </ol>
          <details className="landing-proof-details">
            <summary>What does a receipt check prove?</summary>
            <p>A receipt check compares the current record with a proof saved on a local or test blockchain. A match can show that the covered record is unchanged. It cannot prove that a household physically received cash. This demo uses fictional records and simulated payments; some workflows are still being developed.</p>
          </details>
        </section>
      </main>

      <footer className="landing-footer landing-width"><span>AyudaChain</span><p>Built for clearer disaster relief records in the Philippines.</p><span className="landing-footer-demo">Synthetic demo only</span></footer>
    </div>
  );
}
