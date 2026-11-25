const form = document.querySelector("#loan-form");
const result = document.querySelector("#result");
const placeholder = document.querySelector(".result-placeholder");
const errorBox = document.querySelector("#error");
const submitButton = document.querySelector("#submit-btn");
const money = value => new Intl.NumberFormat("en-IN", {style:"currency",currency:"INR",maximumFractionDigits:0}).format(value);

form.addEventListener("submit", async event => {
  event.preventDefault();
  errorBox.textContent = "";
  submitButton.disabled = true;
  submitButton.textContent = "Assessing…";
  const data = Object.fromEntries(new FormData(form).entries());
  for (const key of ["applicant_income","coapplicant_income","monthly_debt","loan_amount","loan_term","credit_history"]) data[key] = Number(data[key]);
  try {
    const response = await fetch("/api/predict", {method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(data)});
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || "Unable to process application.");
    placeholder.hidden = true;
    result.hidden = false;
    const eligible = payload.prediction === "Eligible";
    result.innerHTML = `<div class="prediction ${eligible ? "" : "no"}"><small>MODEL PREDICTION</small><h2>${eligible ? "Eligible" : "Not eligible"}</h2><div>${eligible ? "The model classified this sample as eligible." : "The model classified this sample as not eligible."}</div></div>
      <div class="metric"><b>Model score:</b> ${(payload.model_score*100).toFixed(1)}%<br><b>Loan requested:</b> ${money(payload.loan_amount)}<br><b>Application ID:</b> ${payload.application_id}<br><br>This score is the model's class probability estimate, not the probability of loan approval. This prediction is not a credit decision.</div>`;
    await loadHistory();
  } catch (error) { errorBox.textContent = error.message; }
  finally { submitButton.disabled = false; submitButton.innerHTML = 'Assess eligibility <span>→</span>'; }
});
async function loadHistory() {
  const body = document.querySelector("#history-body");
  try {
    const response = await fetch("/api/applications");
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Could not load history");
    body.innerHTML = data.applications.length ? data.applications.map(item => `<tr><td>${escapeHtml(item.applicant_name)}</td><td>${money(item.loan_amount)}</td><td><span class="tag ${item.prediction === "Eligible" ? "" : "no"}">${item.prediction}</span></td><td>${new Date(item.created_at).toLocaleString()}</td></tr>`).join("") : '<tr><td colspan="4">No applications yet. Submit a sample application to begin.</td></tr>';
  } catch { body.innerHTML = '<tr><td colspan="4">History is temporarily unavailable. Check the backend and database.</td></tr>'; }
}
function escapeHtml(value) { return String(value).replace(/[&<>"']/g, char => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"}[char])); }
document.querySelector("#refresh-history").addEventListener("click", loadHistory);
loadHistory();