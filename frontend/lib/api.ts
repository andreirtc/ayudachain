export function getApiBase(): string {
  if (typeof window !== "undefined" && window.location && window.location.hostname) {
    return process.env.NEXT_PUBLIC_API_URL || `http://${window.location.hostname}:8000`;
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
}

export interface DashboardStats {
  batch_id: string;
  calamity_name: string;
  total_released: number;
  total_allocated: number;
  total_distributed: number;
  unallocated_funds: number;
  total_beneficiaries: number;
  historical_beneficiaries: number;
  verified_beneficiaries: number;
  flagged_records: number;
  confirmed_distributions: number;
  blockchain_status: string;
  active_network: string;
  contract_address: string;
  recent_transactions: Array<{
    event_type: string;
    description: string;
    amount?: number;
    tx_hash?: string;
    timestamp: string;
  }>;
}

export interface ReliefBatch {
  id: number;
  batch_id: string;
  calamity_name: string;
  calamity_type: string;
  source_agency: string;
  recipient_lgu: string;
  purpose: string;
  amount: number;
  standard_grant: number;
  max_grant: number;
  status: string;
  blockchain_tx_hash?: string;
  created_at: string;
}

export interface Allocation {
  id: number;
  allocation_id: string;
  batch_id: string;
  barangay_id: string;
  barangay_name: string;
  amount: number;
  beneficiary_count: number;
  status: string;
  blockchain_tx_hash?: string;
  created_at: string;
}

export interface Beneficiary {
  id: number;
  beneficiary_id: string;
  dafac_id?: string;
  record_status: "ACTIVE" | "DUPLICATE";
  canonical_beneficiary_id?: string;
  household_name: string;
  barangay_id: string;
  barangay_name: string;
  batch_id: string;
  contact_number?: string;
  verification_status: string;
  duplicate_flag: boolean;
  duplicate_confidence: number;
  duplicate_matched_id?: string;
  anomaly_flag: boolean;
  review_status: string;
  review_notes?: string;
  created_at: string;
}

export interface Distribution {
  id: number;
  distribution_id: string;
  beneficiary_id: string;
  batch_id: string;
  allocation_id?: string;
  amount: number;
  amount_centavos?: number;
  verification_method: string;
  receipt_hash: string;
  receipt_file_path?: string;
  ocr_text?: string;
  status: string;
  blockchain_tx_hash?: string;
  distributed_at: string;
}

export interface VerifyResponse {
  record_id: string;
  beneficiary_id?: string;
  receipt_hash_local: string;
  receipt_hash_onchain: string;
  is_verified: boolean;
  blockchain_tx_hash?: string;
  timestamp?: number;
  network: string;
  contract_address: string;
  explorer_url?: string;
  status_message: string;
}

export interface AuditEvent {
  id: number;
  batch_id: string;
  event_type: string;
  description: string;
  amount?: number;
  entity_id?: string;
  blockchain_tx_hash?: string;
  timestamp: string;
}

export async function fetchDashboard(): Promise<DashboardStats> {
  const res = await fetch(`${getApiBase()}/api/dashboard`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch dashboard");
  return res.json();
}

export function formatPeso(amount: number): string {
  return `₱${amount.toLocaleString("en-PH", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

async function errorFrom(res: Response, fallback: string): Promise<Error> {
  try {
    const body = await res.json();
    if (typeof body.detail === "string") return new Error(body.detail);
  } catch {
    // Response had no JSON body
  }
  return new Error(fallback);
}

export async function fetchBatches(): Promise<ReliefBatch[]> {
  const res = await fetch(`${getApiBase()}/api/batches`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch batches");
  return res.json();
}

export async function fetchBatchDetail(batchId: string): Promise<{
  batch: ReliefBatch;
  allocations: Allocation[];
  total_distributions: number;
  distributed_amount: number;
  timeline: AuditEvent[];
}> {
  const res = await fetch(`${getApiBase()}/api/batches/${batchId}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch batch detail");
  return res.json();
}

export async function fetchBeneficiaries(params?: { batch_id?: string; flagged_only?: boolean; include_historical?: boolean }): Promise<Beneficiary[]> {
  const query = new URLSearchParams();
  if (params?.batch_id) query.set("batch_id", params.batch_id);
  if (params?.flagged_only) query.set("flagged_only", "true");
  if (params?.include_historical) query.set("include_historical", "true");
  const res = await fetch(`${getApiBase()}/api/beneficiaries?${query.toString()}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch beneficiaries");
  return res.json();
}

export async function registerBeneficiary(payload: {
  beneficiary_id: string;
  household_name: string;
  barangay_id: string;
  barangay_name: string;
  batch_id: string;
}): Promise<Beneficiary> {
  const res = await fetch(`${getApiBase()}/api/beneficiaries`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error("Failed to register beneficiary");
  return res.json();
}

export type ReviewDecision = "VERIFIED" | "REJECTED" | "FLAGGED_FOR_REVIEW";
export type DemoReviewer = "demo-officer-01" | "demo-auditor-01";

export interface BeneficiaryReview {
  review_id: string;
  beneficiary_id: string;
  batch_id: string;
  decision: ReviewDecision | "DUPLICATE";
  reason: string;
  reviewed_by: DemoReviewer;
  reviewed_at: string;
  previous_verification_status: string;
  previous_review_status: string;
  previous_review_notes?: string;
  duplicate_flag_before: boolean;
  anomaly_flag_before: boolean;
  duplicate_flag_after: boolean;
  anomaly_flag_after: boolean;
  linked_beneficiary_id?: string;
  matched_beneficiary_id?: string;
  duplicate_confidence: number;
}

export async function verifyBeneficiary(beneficiaryId: string, status: ReviewDecision, notes: string, reviewedBy: DemoReviewer): Promise<Beneficiary> {
  const res = await fetch(getApiBase() + "/api/beneficiaries/" + beneficiaryId + "/verify", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status, review_notes: notes, reviewed_by: reviewedBy })
  });
  if (!res.ok) throw await errorFrom(res, "Failed to save review");
  return res.json();
}

export async function fetchBeneficiaryReviews(beneficiaryId: string): Promise<BeneficiaryReview[]> {
  const res = await fetch(getApiBase() + "/api/beneficiaries/" + beneficiaryId + "/reviews", { cache: "no-store" });
  if (!res.ok) throw await errorFrom(res, "Failed to load review history");
  return res.json();
}

export async function fetchDistributions(batchId?: string): Promise<Distribution[]> {
  const url = batchId ? `${getApiBase()}/api/distributions?batch_id=${batchId}` : `${getApiBase()}/api/distributions`;
  const res = await fetch(url, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch distributions");
  return res.json();
}

export interface DistributionConfirmPayload {
  distribution_id?: string;
  beneficiary_id: string;
  batch_id: string;
  amount: number;
  receipt_filename?: string;
  ocr_raw_text?: string;
}

export async function confirmDistribution(payload: DistributionConfirmPayload, idempotencyKey: string): Promise<Distribution> {
  const res = await fetch(`${getApiBase()}/api/distributions/confirm`, {
    method: "POST",
    headers: { "Content-Type": "application/json", "Idempotency-Key": idempotencyKey },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw await errorFrom(res, "Failed to confirm distribution");
  return res.json();
}

export async function verifyBlockchain(distributionId?: string, receiptHash?: string): Promise<VerifyResponse> {
  const res = await fetch(`${getApiBase()}/api/blockchain/verify`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ distribution_id: distributionId, receipt_hash: receiptHash })
  });
  if (!res.ok) throw new Error("Failed to verify record on blockchain");
  return res.json();
}

export async function fetchAuditTrail(batchId: string): Promise<AuditEvent[]> {
  const res = await fetch(`${getApiBase()}/api/audit-trail/${batchId}`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch audit trail");
  return res.json();
}

export async function resetDemoData(): Promise<{ success: boolean; message: string }> {
  const res = await fetch(`${getApiBase()}/api/demo/reset`, {
    method: "POST"
  });
  if (!res.ok) throw new Error("Failed to reset demo data");
  return res.json();
}

export interface CsvBatchResult {
  status: string;
  total_records_processed: number;
  flagged_duplicates_count: number;
  flagged_records: Array<{
    record_a: {
      id: string;
      name: string;
      address: string;
      barangay: string;
      dafac_id: string;
    };
    record_b: {
      id: string;
      name: string;
      address: string;
      barangay: string;
      dafac_id: string;
    };
    anomaly_type: string;
    match_metrics: {
      overall_score: number;
      name_score: number;
      address_score: number;
      dafac_match: boolean;
    };
    requires_human_review: boolean;
  }>;
}

export async function uploadBeneficiaryCsv(csvContent?: string): Promise<CsvBatchResult> {
  const res = await fetch(`${getApiBase()}/api/beneficiaries/upload-csv`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ csv_content: csvContent || "" })
  });
  if (!res.ok) throw new Error("Failed to upload and analyze CSV");
  return res.json();
}

export async function resolveBeneficiaryDuplicate(beneficiaryId: string, canonicalId: string, notes: string, reviewedBy: DemoReviewer): Promise<Beneficiary> {
  const res = await fetch(getApiBase() + "/api/beneficiaries/" + beneficiaryId + "/resolve-duplicate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ canonical_beneficiary_id: canonicalId, review_notes: notes, reviewed_by: reviewedBy })
  });
  if (!res.ok) throw await errorFrom(res, "Failed to retain duplicate record");
  return res.json();
}

export function apiUrl(path: string): string {
  return path.startsWith("http") ? path : `${getApiBase()}${path}`;
}

export interface ChainStatus {
  success: boolean;
  network: string;
  chainId?: number;
  contractAddress?: string;
  error?: string;
}

export async function fetchChainStatus(): Promise<ChainStatus> {
  const res = await fetch(`${getApiBase()}/api/health`, { cache: 'no-store' });
  if (!res.ok) throw new Error("Failed to fetch backend health");
  const data = await res.json();
  return data.blockchain;
}
