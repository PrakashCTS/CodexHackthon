const ticket = {
  id: "DEMO-101", title: "Add configurable account lockout threshold",
  description: "Authentication must lock an account after a configurable number of failed sign-in attempts. Reset behavior requires product confirmation.",
  acceptance_criteria: ["Lock at the configured threshold", "Default to five attempts", "Reset after successful sign-in"],
  non_functional_requirements: ["Never log credentials or personal data"], labels: ["authentication", "configuration", "security"], repository: "."
};
let selected;
const $ = (id) => document.getElementById(id);
async function request(path, options) { const response = await fetch(path, options); const data = await response.json(); if (!response.ok) throw new Error(data.error || "Request failed"); return data; }
function render(run) {
  selected = run; $("empty").hidden = true; $("run").hidden = false;
  $("run-id").textContent = run.run_id; $("risk").textContent = run.risk; $("status").textContent = run.status.replaceAll("_", " ");
  const gate = run.status === "waiting_for_approval"; $("gate").hidden = !gate;
  $("approve").dataset.gate = run.current_stage === "security" ? "security" : "plan";
  $("timeline").replaceChildren(...run.artifacts.map((artifact, index) => {
    const item = document.createElement("li");
    const number = document.createElement("span"); number.textContent = String(index + 1).padStart(2, "0");
    const copy = document.createElement("div"); const title = document.createElement("b"); title.textContent = artifact.kind.replaceAll("_", " ");
    const detail = document.createElement("p"); detail.textContent = `${artifact.stage} · ${new Date(artifact.created_at).toLocaleTimeString()}`;
    copy.append(title, detail); item.append(number, copy); return item;
  }));
}
async function refresh() { const data = await request("/api/runs"); $("run-count").textContent = data.runs.length; if (selected) render(await request(`/api/runs/${selected.run_id}`)); }
$("launch").addEventListener("click", async () => { $("launch").disabled = true; try { render(await request("/api/runs", {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify(ticket)})); await refresh(); } catch (error) { alert(error.message); } finally { $("launch").disabled = false; } });
$("approve").addEventListener("click", async () => { render(await request(`/api/runs/${selected.run_id}/approve`, {method: "POST", headers: {"Content-Type": "application/json"}, body: JSON.stringify({gate: $("approve").dataset.gate, approver: "local-demo-user"})})); });
$("refresh").addEventListener("click", refresh); refresh().catch(console.error);
