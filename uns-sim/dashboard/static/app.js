const points = {};
let connected = false;
let wing = "Wing01";
let hall = "Hall01";
let enterprise = "";
let siteName = "";
let section = "Site KPIs";
let dirty = false;

function key(cell, name) {
  return `${wing}/${hall}/${cell}/${name}`;
}

function point(cell, name) {
  return points[key(cell, name)];
}

function num(cell, name) {
  const item = point(cell, name);
  if (!item || item.value == null || item.value === "" || typeof item.value === "boolean") return null;
  const value = Number(item.value);
  return Number.isFinite(value) ? value : null;
}

function flag(cell, name) {
  const item = point(cell, name);
  return item ? item.value === true : false;
}

function sitePoint(cell, name) {
  return points[`Campus/${cell}/${name}`];
}

function numSite(cell, name) {
  const item = sitePoint(cell, name);
  if (!item || item.value == null || item.value === "" || typeof item.value === "boolean") return null;
  const value = Number(item.value);
  return Number.isFinite(value) ? value : null;
}

function fmt(value, digits, unit) {
  if (value == null || Number.isNaN(value)) return "—";
  const text = Number(value).toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  return unit ? `${text} ${unit}` : text;
}

function mark(id, state) {
  const el = document.getElementById(id);
  const card = el && el.closest(".card");
  if (!card) return;
  card.classList.toggle("bad", state === "bad");
  card.classList.toggle("warn", state === "warn");
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el && el.textContent !== text) el.textContent = text;
}

function setHtml(id, html) {
  const el = document.getElementById(id);
  if (el && el.innerHTML !== html) el.innerHTML = html;
}

function chip(id, on, badText, okText) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = on ? badText : okText;
  el.className = on ? "chip bad" : "chip";
}

function big(value, digits, unit) {
  if (value == null) return "—";
  const text = Number(value).toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  return `${text}<small>${unit}</small>`;
}

function updateCrumb() {
  const base = enterprise && siteName ? `${enterprise} / ${siteName} / Hall overview` : "Hall overview";
  setText("crumb", section ? `${base} / ${section}` : base);
}

function renderAlarms() {
  chip("alm-cdu", flag("CDU01", "Level1CommonAlm"), "CDU", "CDU");
  chip("alm-fire", flag("FirePanel", "Alarm") || flag("FirePanel", "Trouble"), "FIRE", "FIRE");
  chip("alm-gen", flag("TurboCell01", "Alarm"), "GEN", "GEN");
  const broker = document.getElementById("alm-broker");
  broker.textContent = connected ? "BROKER OK" : "BROKER";
  broker.className = connected ? "chip" : "chip bad";
  document.getElementById("banner").className = connected ? "banner" : "banner show";
  if (!connected) document.getElementById("banner").textContent = "Broker disconnected. Values shown are the last update.";
}

function renderSite() {
  setText("kpi-pue", fmt(numSite("KPI", "PUE"), 3));
  setText("kpi-cue", fmt(numSite("KPI", "CUE"), 3));
  setText("kpi-wue", fmt(numSite("KPI", "WUE"), 2));
  setText("kpi-unavail", fmt(numSite("KPI", "EquipUnavailable"), 0));
  mark("kpi-unavail", (numSite("KPI", "EquipUnavailable") || 0) > 0 ? "bad" : "ok");
  setHtml("kpi-demand", big(numSite("ElecPlant", "DemandKW"), 0, "kW"));
  setText("kpi-peak", `Peak ${fmt(numSite("ElecPlant", "PeakDemandKW"), 0, "kW")}`);
  setHtml("kpi-month", big(numSite("ElecPlant", "MonthEnergyKWh"), 0, "kWh"));
  setText("kpi-month-cost", `Cost ${fmt(numSite("ElecPlant", "MonthCost"), 0, "USD")}`);
  setHtml("kpi-ytd", big(numSite("ElecPlant", "YTDEnergyKWh"), 0, "kWh"));
  setText("kpi-ytd-cost", `Cost ${fmt(numSite("ElecPlant", "YTDCost"), 0, "USD")}`);
  setHtml("kpi-gen", big(numSite("Gen", "SiteProducedKW"), 0, "kW"));
  setText("kpi-gen-kwh", `Energy ${fmt(numSite("Gen", "SiteProducedKWh"), 0, "kWh")}`);
  setText("kpi-green", fmt(numSite("Gen", "GreenEnergyKWh"), 0, "kWh"));
  setText("kpi-co2", fmt(numSite("KPI", "CO2e"), 0, "kg"));
  setText("kpi-saved", fmt(numSite("KPI", "CO2Saved"), 0, "kg"));
  setText("kpi-tenant", fmt(numSite("KPI", "TenantMonthKWh"), 0, "kWh"));
  setText("kpi-response", fmt(numSite("KPI", "AlarmResponseMin"), 0, "min"));
  setText("sys-cdu", `${fmt(num("CDU01", "ServerGlySupTemp"), 1, "°F")} · ${fmt(num("CDU01", "TotSecCoolingLoadLead"), 0, "kW")}`);
  setText("sys-chiller", `${fmt(num("ChillerMCP", "MasterCHWSupTemp"), 1, "°F")} · ${fmt(num("Chiller01", "ActivePowerTot"), 0, "kW")}`);
  setText("sys-air", `${fmt(num("AireBlockMCP", "ColdAisleAvgTemp"), 1, "°F")} · ${fmt(num("MiniAireBlock01", "RoomTemp"), 1, "°F")}`);
  setText("sys-power", `${fmt(num("HallPower", "TotalKW"), 0, "kW")} · PF ${fmt(num("HallPower", "PowerFactor"), 3)}`);
  setText("sys-ups", `${fmt(num("UPS01", "LoadPct"), 0, "%")} · battery ${fmt(num("UPS01", "BatteryPct"), 0, "%")}`);
  setText("sys-gen", `${fmt(num("TurboCell01", "RealPowerKW"), 0, "kW")} · ${flag("TurboCell01", "RunSts") ? "running" : "stopped"}`);
  const fireOn = flag("FirePanel", "Alarm") || flag("FirePanel", "Trouble");
  setText("sys-fire", fireOn ? "Off normal" : "Normal");
  document.getElementById("sys-fire").className = fireOn ? "ink-bad" : "ink-eff";
  setText("sys-plant", `${fmt(numSite("GasPlant", "SupplyPressure"), 0, "psi")} · ${fmt(numSite("Water", "WaterGPM"), 1, "gpm")}`);
}

function renderCdu() {
  const supply = num("CDU01", "ServerGlySupTemp");
  const returned = num("CDU01", "ServerGlyRetTemp");
  const alarm = flag("CDU01", "Level1CommonAlm");
  setHtml("cdu-supply", big(supply, 1, "°F"));
  setText("cdu-dt", `Return ${fmt(returned, 1, "°F")}${supply != null && returned != null ? ` · ΔT ${fmt(returned - supply, 1, "°F")}` : ""}`);
  setHtml("cdu-flow", big(num("CDU01", "ServerGlySupFlow"), 0, "gpm"));
  setHtml("cdu-dp", big(num("CDU01", "LowestCHWHeaderDPLead"), 1, "psi"));
  setText("cdu-dp-sub", `Setpoint ${fmt(num("CDU01", "CHWHeaderDPSPLead"), 1, "psi")}`);
  setHtml("cdu-load", big(num("CDU01", "TotSecCoolingLoadLead"), 0, "kW"));
  setText("cdu-valve", `Valve ${fmt(num("CDU01", "PriGlyValvePosFb"), 0, "%")}`);
  chip("cdu-run", alarm, "ALARM", "NORMAL");
  mark("cdu-supply", alarm ? "bad" : "ok");
  for (let i = 1; i <= 3; i += 1) {
    const on = flag("CDU01", `Pump${i}VFDRunSts`);
    const pill = document.getElementById(`pump-pill-${i}`);
    if (pill) {
      pill.textContent = on ? "RUNNING" : "STANDBY";
      pill.className = on ? "chip" : "chip idle";
    }
    setText(`pump-spd-${i}`, fmt(num("CDU01", `Pump${i}SpdCmd`), 0, "%"));
  }
  fillInput("sp-supply", num("CDU01", "ServerGlySupTempSP"), 1);
  fillInput("sp-dp", num("CDU01", "CHWHeaderDPSPLead"), 1);
}

function renderChiller() {
  const power = num("Chiller01", "ActivePowerTot");
  setHtml("ch-sup", big(num("ChillerMCP", "MasterCHWSupTemp"), 1, "°F"));
  setText("ch-ret", `Return ${fmt(num("ChillerMCP", "MasterCHWRetTemp"), 1, "°F")}`);
  setHtml("ch-flow", big(num("ChillerMCP", "MasterGlyFlowSensor"), 0, "gpm"));
  setHtml("ch-out", big(num("Chiller01", "ChillerGlyOutletTemp"), 1, "°F"));
  setHtml("ch-kw", big(power, 0, "kW"));
  let fansOn = 0;
  for (let i = 1; i <= 12; i += 1) {
    const speed = num("Chiller01", `CondFan${i}VFDSpdCmd`);
    const on = speed != null && speed > 5;
    if (on) fansOn += 1;
    const fan = document.getElementById(`fan-${i}`);
    if (!fan) continue;
    fan.className = on ? "fan" : "fan off";
    fan.textContent = `${String(i).padStart(2, "0")}\n${speed == null ? "—" : Math.round(speed) + "%"}`;
  }
  setText("ch-fans", `${fansOn} of 12 fans running`);
  chip("ch-run", power != null && power < 20, "STOPPED", "RUNNING");
  fillInput("sp-gly", num("ChillerMCP", "GlySupWaterTempSP"), 1);
}

function renderAir() {
  setHtml("air-cold", big(num("AireBlockMCP", "ColdAisleAvgTemp"), 1, "°F"));
  setHtml("air-sup", big(num("AireBlockMCP", "CCUSupTempAvg"), 1, "°F"));
  setText("air-kw", `Power ${fmt(num("AireBlockMCP", "CCUTotKW"), 0, "kW")}`);
  setHtml("air-dp", big(num("AireBlockMCP", "DPAAvg"), 3, "in/WC"));
  setHtml("air-room", big(num("MiniAireBlock01", "RoomTemp"), 1, "°F"));
  setText("air-dis", `Humidity ${fmt(num("MiniAireBlock01", "RoomHum"), 0, "%rh")} · discharge ${fmt(num("MiniAireBlock01", "DischargeAirTemp"), 1, "°F")}`);
  setText("air-hum", fmt(num("MiniAireBlock01", "RoomHum"), 0, "%rh"));
  setText("air-discharge", fmt(num("MiniAireBlock01", "DischargeAirTemp"), 1, "°F"));
  setText("air-power", fmt(num("AireBlockMCP", "CCUTotKW"), 0, "kW"));
  fillInput("sp-air", num("AireBlockMCP", "CCUSupAirTempSP"), 1);
  fillInput("sp-room", num("MiniAireBlock01", "RoomTempSP"), 1);
}

function renderPower() {
  const onBattery = flag("UPS01", "OnBattery");
  setHtml("pwr-hall", big(num("HallPower", "TotalKW"), 0, "kW"));
  setText("pwr-it", `IT ${fmt(num("HallPower", "ITKW"), 0, "kW")}`);
  setText("pwr-pf", fmt(num("HallPower", "PowerFactor"), 3));
  setText("pwr-v", `Voltage ${fmt(num("HallPower", "VoltageLL"), 0, "V")}`);
  setHtml("pwr-ups", big(num("UPS01", "LoadPct"), 0, "%"));
  setHtml("pwr-batt", big(num("UPS01", "BatteryPct"), 0, "%"));
  chip("ups-state", onBattery, "ON BATTERY", "NORMAL");
  mark("pwr-batt", onBattery ? "warn" : "ok");
}

function renderGen() {
  const alarm = flag("TurboCell01", "Alarm");
  const running = flag("TurboCell01", "RunSts");
  setHtml("gen-unit", big(num("TurboCell01", "RealPowerKW"), 0, "kW"));
  setText("gen-alm", alarm ? "Alarm" : "No alarm");
  setHtml("gen-line", big(num("Lineup01", "TotalKW"), 0, "kW"));
  setText("gen-online", `${fmt(num("Lineup01", "OnlineCount"), 0)} online`);
  setHtml("gen-site", big(numSite("Gen", "SiteProducedKW"), 0, "kW"));
  setText("gen-kwh", `Energy ${fmt(numSite("Gen", "SiteProducedKWh"), 0, "kWh")}`);
  setHtml("gen-green", big(numSite("Gen", "GreenEnergyKWh"), 0, "kWh"));
  chip("gen-run", alarm || !running, alarm ? "ALARM" : "STOPPED", "RUNNING");
  mark("gen-unit", alarm ? "bad" : "ok");
  fillInput("sp-power", num("TurboCell01", "PowerSP"), 0);
}

function renderUtil() {
  setHtml("util-gp", big(numSite("GasPlant", "SupplyPressure"), 1, "psi"));
  setHtml("util-gf", big(numSite("GasPlant", "FlowSCFM"), 0, "scfm"));
  setHtml("util-wf", big(numSite("Water", "WaterGPM"), 1, "gpm"));
  setHtml("util-wp", big(numSite("Water", "SupplyPressure"), 1, "psi"));
}

function renderFire() {
  const alarm = flag("FirePanel", "Alarm");
  const trouble = flag("FirePanel", "Trouble");
  const supervisory = flag("FirePanel", "Supervisory");
  setText("fire-alm", alarm ? "ALARM" : "Normal");
  setText("fire-trb", trouble ? "TROUBLE" : "Normal");
  setText("fire-sup", supervisory ? "SUPERVISORY" : "Normal");
  setText("fire-out", fmt(numSite("KPI", "EquipUnavailable"), 0));
  mark("fire-alm", alarm ? "bad" : "ok");
  mark("fire-trb", trouble ? "warn" : "ok");
  mark("fire-sup", supervisory ? "warn" : "ok");
  mark("fire-out", (numSite("KPI", "EquipUnavailable") || 0) > 0 ? "bad" : "ok");
  chip("fire-state", alarm || trouble || supervisory, alarm ? "ALARM" : trouble ? "TROUBLE" : "SUPERVISORY", "NORMAL");
}

function render() {
  const number = hall.replace("Hall", "");
  setText("hall-title", `Data Hall ${number}`);
  updateCrumb();
  renderAlarms();
  renderSite();
  renderCdu();
  renderChiller();
  renderAir();
  renderPower();
  renderGen();
  renderUtil();
  renderFire();
}

function discoverHall() {
  const keys = Object.keys(points);
  if (!keys.length) return;
  if (points[key("CDU01", "ServerGlySupTemp")]) return;
  const hallKey = keys.find((item) => item.startsWith("Wing"));
  if (!hallKey) return;
  const [foundWing, foundHall] = hallKey.split("/");
  wing = foundWing;
  hall = foundHall;
}

function bindTabs() {
  document.querySelectorAll(".tabs button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tabs button").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".tab").forEach((item) => item.classList.remove("show"));
      button.classList.add("active");
      document.getElementById(`tab-${button.dataset.tab}`).classList.add("show");
      const names = {
        site: "Site KPIs",
        cdu: "CDU",
        chiller: "Chillers",
        air: "Air",
        power: "Power",
        gen: "Generation",
        util: "Utilities",
        fire: "Fire",
      };
      section = names[button.dataset.tab];
      updateCrumb();
      redraw();
    });
  });
}

const trends = {};
const TRENDS = [
  ["cv-pue", () => numSite("KPI", "PUE")],
  ["cv-cue", () => numSite("KPI", "CUE")],
  ["cv-wue", () => numSite("KPI", "WUE")],
  ["cv-unavail", () => numSite("KPI", "EquipUnavailable")],
  ["cv-demand", () => numSite("ElecPlant", "DemandKW")],
  ["cv-month", () => numSite("ElecPlant", "MonthEnergyKWh")],
  ["cv-ytd", () => numSite("ElecPlant", "YTDEnergyKWh")],
  ["cv-produced", () => numSite("Gen", "SiteProducedKW")],
  ["cv-cdu-t", () => num("CDU01", "ServerGlySupTemp")],
  ["cv-cdu-f", () => num("CDU01", "ServerGlySupFlow")],
  ["cv-cdu-d", () => num("CDU01", "LowestCHWHeaderDPLead")],
  ["cv-cdu-k", () => num("CDU01", "TotSecCoolingLoadLead")],
  ["cv-ch-s", () => num("ChillerMCP", "MasterCHWSupTemp")],
  ["cv-ch-f", () => num("ChillerMCP", "MasterGlyFlowSensor")],
  ["cv-ch-o", () => num("Chiller01", "ChillerGlyOutletTemp")],
  ["cv-ch-k", () => num("Chiller01", "ActivePowerTot")],
  ["cv-air-c", () => num("AireBlockMCP", "ColdAisleAvgTemp")],
  ["cv-air-s", () => num("AireBlockMCP", "CCUSupTempAvg")],
  ["cv-air-d", () => num("AireBlockMCP", "DPAAvg")],
  ["cv-air-r", () => num("MiniAireBlock01", "RoomTemp")],
  ["cv-pwr-h", () => num("HallPower", "TotalKW")],
  ["cv-pwr-p", () => num("HallPower", "PowerFactor")],
  ["cv-pwr-u", () => num("UPS01", "LoadPct")],
  ["cv-pwr-b", () => num("UPS01", "BatteryPct")],
  ["cv-gen-u", () => num("TurboCell01", "RealPowerKW")],
  ["cv-gen-l", () => num("Lineup01", "TotalKW")],
  ["cv-gen-s", () => numSite("Gen", "SiteProducedKW")],
  ["cv-gen-g", () => numSite("Gen", "GreenEnergyKWh")],
  ["cv-gas-p", () => numSite("GasPlant", "SupplyPressure")],
  ["cv-gas-f", () => numSite("GasPlant", "FlowSCFM")],
  ["cv-h2o-f", () => numSite("Water", "WaterGPM")],
  ["cv-h2o-p", () => numSite("Water", "SupplyPressure")],
  ["cv-fire-a", () => (flag("FirePanel", "Alarm") ? 1 : 0)],
  ["cv-fire-t", () => (flag("FirePanel", "Trouble") ? 1 : 0)],
  ["cv-fire-s", () => (flag("FirePanel", "Supervisory") ? 1 : 0)],
  ["cv-fire-o", () => numSite("KPI", "EquipUnavailable")],
];

function sampleTrends() {
  TRENDS.forEach(([canvasId, read]) => {
    const value = read();
    if (value == null) return;
    const series = trends[canvasId] || (trends[canvasId] = []);
    series.push(value);
    if (series.length > 40) series.shift();
    draw(canvasId, series);
  });
}

function redraw() {
  Object.entries(trends).forEach(([id, series]) => draw(id, series));
}

function draw(id, series) {
  const canvas = document.getElementById(id);
  if (!canvas || canvas.clientWidth < 2) return;
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth * ratio;
  const height = 36 * ratio;
  if (canvas.width !== width) canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, width, height);
  if (series.length < 2) return;
  const min = Math.min(...series);
  const max = Math.max(...series);
  const span = max - min || 1;
  const tone = getComputedStyle(canvas.parentElement).getPropertyValue("--tone").trim() || "#8fd4ff";
  ctx.lineWidth = 1.6 * ratio;
  ctx.beginPath();
  const points = series.map((value, index) => {
    const x = (index / (series.length - 1)) * (width - 6) + 3;
    const y = height - ((value - min) / span) * (height - 8) - 4;
    return [x, y];
  });
  points.forEach(([x, y], index) => {
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.strokeStyle = tone;
  ctx.stroke();
  ctx.lineTo(points[points.length - 1][0], height);
  ctx.lineTo(points[0][0], height);
  ctx.closePath();
  ctx.globalAlpha = 0.16;
  ctx.fillStyle = tone;
  ctx.fill();
  ctx.globalAlpha = 1;
}

function fillInput(id, value, digits) {
  const el = document.getElementById(id);
  if (!el || document.activeElement === el || value == null) return;
  const text = Number(value).toFixed(digits);
  if (el.value !== text) el.value = text;
}

async function writePoint(cell, name, value) {
  await fetch("/api/write", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ wing, hall, cell, name, value }),
  });
}

function bindWrite(id, cell, name) {
  document.getElementById(id).addEventListener("change", (event) => {
    const value = Number(event.target.value);
    if (!Number.isFinite(value)) return;
    writePoint(cell, name, value);
  });
}

function buildFans() {
  const grid = document.getElementById("fan-grid");
  for (let i = 1; i <= 12; i += 1) {
    const fan = document.createElement("div");
    fan.className = "fan off";
    fan.id = `fan-${i}`;
    fan.textContent = String(i).padStart(2, "0");
    grid.appendChild(fan);
  }
}

function apply(batch) {
  if (!batch) return;
  if (typeof batch.connected === "boolean") connected = batch.connected;
  if (batch.enterprise) enterprise = batch.enterprise;
  if (batch.site) siteName = batch.site;
  if (batch.points) Object.assign(points, batch.points);
  discoverHall();
  dirty = true;
}

async function boot() {
  buildFans();
  bindTabs();
  bindWrite("sp-supply", "CDU01", "ServerGlySupTempSP");
  bindWrite("sp-dp", "CDU01", "CHWHeaderDPSPLead");
  bindWrite("sp-gly", "ChillerMCP", "GlySupWaterTempSP");
  bindWrite("sp-air", "AireBlockMCP", "CCUSupAirTempSP");
  bindWrite("sp-room", "MiniAireBlock01", "RoomTempSP");
  bindWrite("sp-power", "TurboCell01", "PowerSP");
  const snapshot = await fetch("/api/state").then((response) => response.json());
  apply(snapshot);
  render();
  const stream = new EventSource("/events");
  stream.onmessage = (event) => apply(JSON.parse(event.data));
  stream.onerror = () => { connected = false; dirty = true; };
  setInterval(() => { if (dirty) { dirty = false; render(); } }, 250);
  setInterval(sampleTrends, 2000);
  sampleTrends();
}

boot();
