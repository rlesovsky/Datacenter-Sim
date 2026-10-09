const points = {};
let connected = false;
let wing = "Wing01";
let hall = "Hall01";
let chiller = 1;
let dirty = false;

const trends = {};
const TRENDS = [
  ["cv-cdu-t", "tr-cdu-t", () => num("CDU01", "ServerGlySupTemp"), 1, "°F"],
  ["cv-cdu-d", "tr-cdu-d", () => num("CDU01", "LowestCHWHeaderDPLead"), 1, "psi"],
  ["cv-cdu-f", "tr-cdu-f", () => num("CDU01", "ServerGlySupFlow"), 0, "gpm"],
  ["cv-cdu-k", "tr-cdu-k", () => num("CDU01", "TotSecCoolingLoadLead"), 0, "kW"],
  ["cv-air-t", "tr-air-t", () => num("AireBlockMCP", "ColdAisleAvgTemp"), 1, "°F"],
  ["cv-air-s", "tr-air-s", () => num("AireBlockMCP", "CCUSupTempAvg"), 1, "°F"],
  ["cv-air-d", "tr-air-d", () => num("AireBlockMCP", "DPAAvg"), 4, "in/WC"],
  ["cv-air-k", "tr-air-k", () => num("AireBlockMCP", "CCUTotKW"), 0, "kW"],
  ["cv-ch-t", "tr-ch-t", () => num(chCell(), "ChillerGlyOutletTemp"), 1, "°F"],
  ["cv-ch-c", "tr-ch-c", () => num(chCell(), "TotCoolingCapacity"), 0, "kW"],
  ["cv-ch-k", "tr-ch-k", () => num(chCell(), "ActivePowerTot"), 0, "kW"],
  ["cv-ch-m", "tr-ch-m", () => num(chCell(), "MPUE"), 2, ""],
  ["cv-mini-t", "tr-mini-t", () => num("MiniAireBlock01", "RoomTemp"), 1, "°F"],
  ["cv-mini-d", "tr-mini-d", () => num("MiniAireBlock01", "DischargeAirTemp"), 1, "°F"],
  ["cv-mini-v", "tr-mini-v", () => num("MiniAireBlock01", "ControlValveCmdSignalOut"), 0, "%"],
  ["cv-mini-f", "tr-mini-f", () => num("MiniAireBlock01", "Fan1ActualSpd"), 0, "rpm"],
];

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

function fmt(value, digits, unit) {
  if (value == null || Number.isNaN(value)) return "—";
  const text = Number(value).toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  return unit ? `${text} ${unit}` : text;
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

function fillInput(id, value, digits) {
  const el = document.getElementById(id);
  if (!el || document.activeElement === el || value == null) return;
  const text = Number(value).toFixed(digits);
  if (el.value !== text) el.value = text;
}

function bar(id, value, span) {
  const el = document.getElementById(id);
  if (!el || value == null) return;
  el.style.width = `${Math.max(4, Math.min(100, (value / span) * 100))}%`;
}

function chCell() {
  return `Chiller${String(chiller).padStart(2, "0")}`;
}

function pad(n) {
  return String(n).padStart(2, "0");
}

function big(value, digits, unit) {
  if (value == null) return "—";
  const text = Number(value).toLocaleString("en-US", {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits,
  });
  return `${text}<small>${unit}</small>`;
}

function renderAlarms() {
  ["Level1CommonAlm", "Level2CommonAlm", "Level3CommonAlm", "Level4CommonAlm"].forEach((name, index) => {
    const on = flag("CDU01", name);
    chip(`alm-l${index + 1}`, on, `L${index + 1}`, `L${index + 1}`);
    chip(`side-l${index + 1}`, on, `L${index + 1}`, `L${index + 1}`);
  });
  const broker = document.getElementById("alm-broker");
  broker.textContent = connected ? "BROKER OK" : "BROKER";
  broker.className = connected ? "chip" : "chip bad";
  document.getElementById("banner").className = connected ? "banner" : "banner show";
  if (!connected) document.getElementById("banner").textContent = "Broker disconnected. Values shown are the last update.";
}

function renderCdu() {
  const supply = num("CDU01", "ServerGlySupTemp");
  const supplySp = num("CDU01", "ServerGlySupTempSP");
  const dp = num("CDU01", "LowestCHWHeaderDPLead");
  const dpSp = num("CDU01", "CHWHeaderDPSPLead");
  const flow = num("CDU01", "ServerGlySupFlow");
  const load = num("CDU01", "TotSecCoolingLoadLead");
  const primaryLoad = num("CDU01", "TotPriCoolingLoadLead");
  setHtml("cdu-supply", big(supply, 1, "°F"));
  setText("cdu-supply-sub", `SP ${fmt(supplySp, 1, "°F")}`);
  setHtml("cdu-dp", big(dp, 1, "psi"));
  setText("cdu-dp-sub", `SP ${fmt(dpSp, 1, "psi")}`);
  document.getElementById("cdu-dp-card").className = dp != null && dpSp != null && dp < dpSp - 1 ? "card warn" : "card";
  setHtml("cdu-flow", big(flow, 0, "gpm"));
  const headerA = num("CDU01", "HeaderAFlowMeter");
  const headerB = num("CDU01", "HeaderBFlowMeter");
  setText("cdu-flow-sub", `Header A ${fmt(headerA, 0)} · Header B ${fmt(headerB, 0)}`);
  setHtml("cdu-load", big(load, 0, "kW"));
  setText("cdu-load-sub", `Primary ${fmt(primaryLoad, 0, "kW")}`);

  setText("pri-s", fmt(num("CDU01", "PriGlySupTemp"), 1, "°F"));
  setText("pri-r", fmt(num("CDU01", "PriGlyRetTemp"), 1, "°F"));
  setText("pri-f", fmt(num("CDU01", "PriGlyFlowMeter"), 0, "gpm"));
  setText("valve-fb", fmt(num("CDU01", "PriGlyValvePosFb"), 0, "%"));
  setText("valve-cmd", fmt(num("CDU01", "PriGlyRetValveCmd"), 0, "%"));
  setText("strainer", fmt(num("CDU01", "HXStrainerDP"), 1, "psi"));

  let running = 0;
  for (let i = 1; i <= 3; i += 1) {
    const on = flag("CDU01", `Pump${i}VFDRunSts`);
    if (on) running += 1;
    const pill = document.getElementById(`pump-pill-${i}`);
    pill.textContent = on ? "RUNNING" : "STANDBY";
    pill.className = on ? "chip" : "chip idle";
    setText(`pump-spd-${i}`, fmt(num("CDU01", `Pump${i}SpdCmd`), 0, "%"));
  }
  const stopped = flag("CDU01", "MasterShutdown");
  const run = document.getElementById("cdu-run");
  run.textContent = stopped || running === 0 ? "STOPPED" : "RUNNING";
  run.className = stopped || running === 0 ? "chip bad" : "chip";
  setText("cdu-pumps", `${running} of 3 pumps`);

  const dpA = num("CDU01", "HeaderADP");
  const dpB = num("CDU01", "HeaderBDP");
  setText("hdr-a-txt", `${fmt(dpA, 1, "psi")} · ${fmt(headerA, 0, "gpm")}`);
  setText("hdr-b-txt", `${fmt(dpB, 1, "psi")} · ${fmt(headerB, 0, "gpm")}`);
  const headerLow = (value) => value != null && dpSp != null && value < dpSp - 1;
  document.getElementById("hdr-a").className = headerLow(dpA) ? "header-box warn" : "header-box";
  document.getElementById("hdr-b").className = headerLow(dpB) ? "header-box warn" : "header-box";

  setText("sec-s", fmt(supply, 1, "°F"));
  setText("sec-r", fmt(num("CDU01", "ServerGlyRetTemp"), 1, "°F"));
  setText("sec-f", fmt(flow, 0, "gpm"));
  setText("sec-p", fmt(num("CDU01", "ServerGlyRetPress"), 1, "psi"));
  setText("pri2-s", fmt(num("CDU01", "PriGlySupTemp"), 1, "°F"));
  setText("pri2-r", fmt(num("CDU01", "PriGlyRetTemp"), 1, "°F"));
  setText("pri2-f", fmt(num("CDU01", "PriGlyFlowMeter"), 0, "gpm"));
  setText("pri2-v", fmt(num("CDU01", "PriGlyValvePosFb"), 0, "%"));
  bar("bar-sec-s", supply, 120);
  bar("bar-sec-r", num("CDU01", "ServerGlyRetTemp"), 120);
  bar("bar-sec-f", flow, 2000);
  bar("bar-sec-p", num("CDU01", "ServerGlyRetPress"), 80);
  bar("bar-valve", num("CDU01", "PriGlyValvePosFb"), 100);

  fillInput("sp-supply", supplySp, 1);
  fillInput("sp-dp", dpSp, 1);
  setText("mode-enable", fmt(num("CDU01", "SystemEnableModeSP"), 0));
  setText("mode-remote", flag("CDU01", "LocalRemoteModeSts") ? "Remote" : "Local");
  setText("mode-auto", flag("CDU01", "ManualAutoModeSts") ? "Auto" : "Manual");
  setText("mode-type", fmt(num("CDU01", "ControllerOperationType"), 0));
  setText("mode-dp", fmt(num("CDU01", "ActiveDPSelection"), 0));
}

function renderPlant() {
  setHtml("mcp-sup", big(num("ChillerMCP", "MasterCHWSupTemp"), 1, "°F"));
  setText("mcp-sup-sub", `Running avg ${fmt(num("ChillerMCP", "RunChillersAvgCHWSupTemp"), 1, "°F")}`);
  setHtml("mcp-ret", big(num("ChillerMCP", "MasterCHWRetTemp"), 1, "°F"));
  setHtml("mcp-flow", big(num("ChillerMCP", "MasterGlyFlowSensor"), 0, "gpm"));
  setText("mcp-flow-sub", `Bypass ${fmt(num("ChillerMCP", "BypassValveFb"), 0, "%")}`);
  setHtml("mcp-oa", big(num("ChillerMCP", "MasterOATempSensor"), 1, "°F"));
  setText("mcp-oa-sub", `Humidity ${fmt(num("ChillerMCP", "MasterOAHumSensor"), 0, "%rh")}`);
  let enabled = 0;
  for (let i = 1; i <= 10; i += 1) {
    const on = flag("ChillerMCP", `CH${pad(i)}Enable`);
    const failed = flag("ChillerMCP", `CH${pad(i)}FailedAlm`);
    if (on && !failed) enabled += 1;
    const card = document.getElementById(`plant-ch-${i}`);
    card.className = failed ? "tile high" : "tile";
    const power = num(`Chiller${pad(i)}`, "ActivePowerTot");
    card.innerHTML = `<div class="title"><span class="dot ${on && !failed ? "" : "off"}"></span>CH-${pad(i)}</div>
      <div>${failed ? "FAILED" : on ? "ENABLED" : "OFF"}</div>
      <div class="sub">${fmt(power, 0, "kW")} · mode ${fmt(num("ChillerMCP", `CH${pad(i)}Mode`), 0)}</div>`;
  }
  setText("plant-count", `${enabled} chillers enabled`);
  fillInput("sp-gly", num("ChillerMCP", "GlySupWaterTempSP"), 1);
  fillInput("sp-mcp-dp", num("ChillerMCP", "DPSP"), 1);
  setText("dp-a", fmt(num("ChillerMCP", "DPSensorA"), 1, "psi"));
  setText("dp-b", fmt(num("ChillerMCP", "DPSensorB"), 1, "psi"));
  setText("tank", fmt(num("ChillerMCP", "ExpansionTankPress"), 1, "psi"));
  setText("bypass", `${fmt(num("ChillerMCP", "BypassValveFb"), 0)} / ${fmt(num("ChillerMCP", "BypassValveCmd"), 0, "%")}`);
}

function renderAir() {
  const zones = [
    ["1A", "Zone1AColdAisleTemp", "Zone1AColdAisleHum", "Zone1AHotAisleDP"],
    ["2A", "Zone2AColdAisleTemp", "Zone2AColdAisleHum", "Zone2AHotAisleDP"],
    ["1B", "Zone1BColdAisleTemp", "Zone1BColdAisleHum", "Zone1BHotAisleDP"],
    ["2B", "Zone2BColdAisleTemp", "Zone2BColdAisleHum", "Zone2BHotAisleDP"],
  ].map(([label, temp, hum, dp]) => ({
    label,
    temp: num("AireBlockMCP", temp),
    hum: num("AireBlockMCP", hum),
    dp: num("AireBlockMCP", dp),
  }));
  const temps = zones.map((zone) => zone.temp).filter((value) => value != null);
  const avg = temps.length ? temps.reduce((sum, value) => sum + value, 0) / temps.length : null;
  let worst = zones[0];
  zones.forEach((zone) => {
    if (worst.temp == null || (zone.temp != null && zone.temp > worst.temp)) worst = zone;
  });
  const cold = num("AireBlockMCP", "ColdAisleAvgTemp");
  setHtml("air-cold", big(cold, 1, "°F"));
  setText("air-worst", worst && worst.temp != null ? `Warmest zone ${worst.label} ${fmt(worst.temp, 1, "°F")}` : "Warmest zone —");
  document.getElementById("air-cold-card").className = worst && avg != null && worst.temp > avg + 3 ? "card warn" : "card";
  setHtml("air-sup", big(num("AireBlockMCP", "CCUSupTempAvg"), 1, "°F"));
  setText("air-sup-sub", `SP ${fmt(num("AireBlockMCP", "CCUSupAirTempSP"), 1, "°F")}`);
  const dpA = num("AireBlockMCP", "DPAAvg");
  const dpB = num("AireBlockMCP", "DPBAvg");
  setHtml("air-dp", `${fmt(dpA, 4)}<small>in/WC</small>`);
  setText("air-dp-sub", `A ${fmt(dpA, 4)} · B ${fmt(dpB, 4)}`);
  setHtml("air-kw", big(num("AireBlockMCP", "CCUTotKW"), 0, "kW"));
  setText("air-tons", `${fmt(num("AireBlockMCP", "CCUTotTons"), 0, "tons")} cooling`);

  let online = 0;
  for (let i = 1; i <= 12; i += 1) {
    const offline = flag("AireBlockMCP", `CCU${pad(i)}Offline`);
    if (!offline) online += 1;
    const tile = document.getElementById(`ccu-${i}`);
    tile.className = offline ? "tile high" : "tile";
    tile.innerHTML = `<div class="title"><span class="dot ${offline ? "off" : ""}"></span>CCU ${pad(i)}</div><div>${offline ? "Offline" : "Run"}</div><div class="sub">${fmt(num("AireBlockMCP", `CCU${pad(i)}SupAirTemp`), 1, "°F")}</div>`;
  }
  setText("air-online", `${online} of 12 CCUs online`);
  zones.forEach((zone) => {
    const tile = document.getElementById(`zone-${zone.label}`);
    const high = avg != null && zone.temp != null && zone.temp > avg + 3;
    tile.className = high ? "tile high" : "tile";
    tile.innerHTML = `<div class="title">Zone ${zone.label}${high ? " · warm" : ""}</div>
      <div class="row"><span>Cold aisle</span><b>${fmt(zone.temp, 1, "°F")}</b></div>
      <div class="row"><span>Humidity</span><b>${fmt(zone.hum, 0, "%rh")}</b></div>
      <div class="row"><span>Hot aisle DP</span><b>${fmt(zone.dp, 4, "in/WC")}</b></div>`;
  });
  fillInput("sp-air", num("AireBlockMCP", "CCUSupAirTempSP"), 1);
  fillInput("sp-air-dp", num("AireBlockMCP", "DPSP"), 3);
  setText("air-dpa", fmt(dpA, 4, "in/WC"));
  setText("air-dpb", fmt(dpB, 4, "in/WC"));
  setText("air-dpmin", fmt(num("AireBlockMCP", "DPMinControlValue"), 4, "in/WC"));
  setText("air-dpmax", fmt(num("AireBlockMCP", "DPMaxControlValue"), 4, "in/WC"));
  setText("air-chw", `${fmt(num("AireBlockMCP", "CHWSupTempA"), 1)} / ${fmt(num("AireBlockMCP", "CHWSupTempB"), 1, "°F")}`);
}

function renderChiller() {
  const cell = chCell();
  setText("ch-title", `CH-${pad(chiller)}`);
  setText("ch-meta", `Chiller ${chiller} of 10 · Modbus TCP/IP`);
  const outlet = num(cell, "ChillerGlyOutletTemp");
  const power = num(cell, "ActivePowerTot");
  const enabled = flag("ChillerMCP", `CH${pad(chiller)}Enable`);
  const failed = flag("ChillerMCP", `CH${pad(chiller)}FailedAlm`);
  const run = document.getElementById("ch-run");
  run.textContent = failed ? "FAILED" : power != null && power > 20 ? "RUNNING" : "STOPPED";
  run.className = failed || !(power > 20) ? "chip bad" : "chip";
  const enable = document.getElementById("ch-enable");
  enable.textContent = enabled ? "ENABLED" : "DISABLED";
  enable.className = enabled ? "chip idle" : "chip warn";
  setHtml("ch-out", big(outlet, 1, "°F"));
  setText("ch-out-sub", `Inlet ${fmt(num(cell, "ChillerGlyInletTemp"), 1, "°F")}`);
  setHtml("ch-cap", big(num(cell, "TotCoolingCapacity"), 0, "kW"));
  setText("ch-cap-sub", `Fluid ${fmt(num(cell, "FluidCoolerCoolingCapacity"), 0)} · Mech ${fmt(num(cell, "MechanicalCoolingCapacity"), 0, "kW")}`);
  setHtml("ch-kw", big(power, 0, "kW"));
  setHtml("ch-mpue", big(num(cell, "MPUE"), 2, ""));
  setText("ch-mode", `Operating mode ${fmt(num(cell, "OperatingMode"), 0)} · chiller mode ${fmt(num(cell, "ChillerMode"), 0)}`);

  const comps = [
    ["HT-1", "HTComp1"],
    ["HT-2", "HTComp2"],
    ["LT-3", "LTComp3"],
    ["LT-4", "LTComp4"],
  ];
  comps.forEach(([label, prefix], index) => {
    const speed = num(cell, `${prefix}ActualSpd`);
    const on = speed != null && speed > 100;
    const card = document.getElementById(`comp-${index}`);
    card.innerHTML = `<div class="title">${label}</div><span class="chip ${on ? "" : "idle"}">${on ? "RUNNING" : "STANDBY"}</span>
      <div class="sub" style="margin-top:8px">Demand ${fmt(num(cell, `${prefix}Demand`), 0, "%")}</div>
      <div class="sub">${fmt(speed, 0, "rpm")} · ${fmt(num(cell, `${prefix}ActualPower`), 0, "kW")}</div>`;
  });
  let fansOn = 0;
  for (let i = 1; i <= 18; i += 1) {
    const speed = num(cell, `CondFan${i}VFDSpdCmd`);
    const on = speed != null && speed > 5;
    if (on) fansOn += 1;
    const fan = document.getElementById(`fan-${i}`);
    fan.className = on ? "fan" : "fan off";
    fan.textContent = pad(i);
  }
  setText("fan-sum", `${fansOn} running · ${18 - fansOn} off`);
  setText("gly-in", fmt(num(cell, "ChillerGlyInletTemp"), 1, "°F"));
  setText("gly-out", fmt(outlet, 1, "°F"));
  setText("gly-flow", fmt(num(cell, "GlyFlow"), 0, "gpm"));
  setText("gly-ret", `${fmt(num(cell, "GlyRetValveFb"), 0)} / ${fmt(num(cell, "GlyRetValveCmd"), 0, "%")}`);
  setText("gly-byp", `${fmt(num(cell, "GlyBypassValveFb"), 0)} / ${fmt(num(cell, "GlyBypassValveCmd"), 0, "%")}`);
  setText("gly-app", fmt(num(cell, "FluidCoolerApproach"), 1, "°F"));
  setText("gly-hours", fmt(num(cell, "ChillerRuntimeHours"), 1, "h"));
  setText("gly-volt", `${fmt(num(cell, "Source1AvgVoltLL"), 0)} / ${fmt(num(cell, "Source2AvgVoltLL"), 0, "V")}`);
}

function renderMini() {
  const temp = num("MiniAireBlock01", "RoomTemp");
  const discharge = num("MiniAireBlock01", "DischargeAirTemp");
  const fan1 = num("MiniAireBlock01", "Fan1KW");
  const fan2 = num("MiniAireBlock01", "Fan2KW");
  const power = fan1 == null && fan2 == null ? null : (fan1 || 0) + (fan2 || 0);
  setHtml("mini-t", big(temp, 1, "°F"));
  setText("mini-t-sub", `SP ${fmt(num("MiniAireBlock01", "RoomTempSP"), 1, "°F")}`);
  setHtml("mini-h", big(num("MiniAireBlock01", "RoomHum"), 0, "%rh"));
  setHtml("mini-d", big(discharge, 1, "°F"));
  setText("mini-d-sub", `Return ${fmt(num("MiniAireBlock01", "RetAirTemp"), 1, "°F")}`);
  setHtml("mini-kw", big(power, 1, "kW"));
  setText("mini-kw-sub", `Fan 1 ${fmt(fan1, 1)} · Fan 2 ${fmt(fan2, 1, "kW")}`);
  const enabled = flag("MiniAireBlock01", "UnitModeEnable");
  const run = document.getElementById("mini-run");
  run.textContent = enabled ? "ENABLED" : "OFF";
  run.className = enabled ? "chip" : "chip idle";
  setText("mini-mode", flag("MiniAireBlock01", "UnitOperatingMode") ? "MODE ON" : "MODE OFF");
  setText("mini-ret", fmt(num("MiniAireBlock01", "RetAirTemp"), 1, "°F"));
  setText("mini-cmd", fmt(num("MiniAireBlock01", "ControlValveCmdSignalOut"), 0, "%"));
  setText("mini-fb", fmt(num("MiniAireBlock01", "ValveFb"), 0, "%"));
  setText("mini-chws", fmt(num("MiniAireBlock01", "CHWSTemp"), 1, "°F"));
  setText("mini-chwr", fmt(num("MiniAireBlock01", "CHWRTemp"), 1, "°F"));
  setText("mini-gpm", fmt(num("MiniAireBlock01", "ControlValveFlowRate"), 0, "gpm"));
  setText("mini-dis", fmt(discharge, 1, "°F"));
  setText("mini-adp", fmt(num("MiniAireBlock01", "AirDP"), 2));
  [1, 2].forEach((index) => {
    const speed = num("MiniAireBlock01", `Fan${index}ActualSpd`);
    const on = speed != null && speed > 50;
    const pill = document.getElementById(`mini-fan-pill-${index}`);
    pill.textContent = on ? "RUNNING" : "OFF";
    pill.className = on ? "chip" : "chip idle";
    setText(`mini-fan-spd-${index}`, `${fmt(speed, 0, "rpm")} · ${fmt(num("MiniAireBlock01", `Fan${index}KW`), 1, "kW")}`);
  });
  setText("m-space", fmt(temp, 1, "°F"));
  setText("m-ctrl", fmt(num("MiniAireBlock01", "ControlTemp"), 1, "°F"));
  setText("m-dis", fmt(discharge, 1, "°F"));
  setText("m-chws", fmt(num("MiniAireBlock01", "CHWSTemp"), 1, "°F"));
  setText("m-chwr", fmt(num("MiniAireBlock01", "CHWRTemp"), 1, "°F"));
  setText("m-flow", fmt(num("MiniAireBlock01", "ControlValveFlowRate"), 0, "gpm"));
  fillInput("sp-room", num("MiniAireBlock01", "RoomTempSP"), 1);
  fillInput("sp-ctrl", num("MiniAireBlock01", "ControlTempSP"), 1);
  fillInput("sp-ret", num("MiniAireBlock01", "RetTempSP"), 1);
  fillInput("sp-fan", num("MiniAireBlock01", "NormalModeFanSpdSP"), 0);
  const leak = flag("MiniAireBlock01", "WaterLeakDetectorAlm");
  const fail = flag("MiniAireBlock01", "UnitFailSts");
  setText("st-en", enabled ? "ON" : "OFF");
  setText("st-a", flag("MiniAireBlock01", "AMechanicalPowerRunState") ? "RUNNING" : "OFF");
  setText("st-b", flag("MiniAireBlock01", "BMechanicalPowerRunState") ? "RUNNING" : "OFF");
  setText("st-leak", leak ? "ALARM" : "NORMAL");
  setText("st-fail", fail ? "FAIL" : "NORMAL");
}

function render() {
  const number = hall.replace("Hall", "");
  setText("hall-title", `Data Hall ${number}`);
  renderAlarms();
  renderCdu();
  renderPlant();
  renderAir();
  renderChiller();
  renderMini();
}

function sampleTrends() {
  TRENDS.forEach(([canvasId, labelId, read, digits, unit]) => {
    const value = read();
    if (value == null) return;
    const series = trends[canvasId] || (trends[canvasId] = []);
    series.push(value);
    if (series.length > 40) series.shift();
    setText(labelId, fmt(value, digits, unit));
    draw(canvasId, series);
  });
}

function draw(id, series) {
  const canvas = document.getElementById(id);
  if (!canvas) return;
  const ratio = window.devicePixelRatio || 1;
  const width = canvas.clientWidth * ratio;
  const height = 72 * ratio;
  if (canvas.width !== width) canvas.width = width;
  canvas.height = height;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, width, height);
  if (series.length < 2) return;
  const min = Math.min(...series);
  const max = Math.max(...series);
  const span = max - min || 1;
  ctx.strokeStyle = "#d5deef";
  ctx.lineWidth = 1.6 * ratio;
  ctx.beginPath();
  series.forEach((value, index) => {
    const x = (index / (series.length - 1)) * (width - 8) + 4;
    const y = height - ((value - min) / span) * (height - 12) - 6;
    if (index === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
}

function discoverHall() {
  const keys = Object.keys(points);
  if (!keys.length) return;
  if (points[key("CDU01", "ServerGlySupTemp")]) return;
  const [foundWing, foundHall] = keys[0].split("/");
  wing = foundWing;
  hall = foundHall;
}

async function write(cell, name, value) {
  await fetch("/api/write", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ wing, hall, cell, name, value }),
  });
}

function bindWrite(id, cell, name, asFloat) {
  document.getElementById(id).addEventListener("change", (event) => {
    const value = asFloat ? Number(event.target.value) : Number(event.target.value);
    if (!Number.isFinite(value)) return;
    write(cell, name, value);
  });
}

function buildRepeats() {
  const pumps = document.getElementById("pump-box");
  for (let i = 1; i <= 3; i += 1) {
    const row = document.createElement("div");
    row.className = "pump";
    row.innerHTML = `<div>P${i}</div><span class="chip idle" id="pump-pill-${i}">—</span><div class="spd" id="pump-spd-${i}">—</div>`;
    pumps.appendChild(row);
  }
  const plant = document.getElementById("plant-grid");
  for (let i = 1; i <= 10; i += 1) {
    const tile = document.createElement("div");
    tile.className = "tile";
    tile.id = `plant-ch-${i}`;
    plant.appendChild(tile);
  }
  const ccus = document.getElementById("ccu-grid");
  for (let i = 1; i <= 12; i += 1) {
    const tile = document.createElement("div");
    tile.className = "tile";
    tile.id = `ccu-${i}`;
    ccus.appendChild(tile);
  }
  const zones = document.getElementById("zone-grid");
  ["1A", "2A", "1B", "2B"].forEach((label) => {
    const tile = document.createElement("div");
    tile.className = "tile";
    tile.id = `zone-${label}`;
    zones.appendChild(tile);
  });
  const comps = document.getElementById("comp-grid");
  for (let i = 0; i < 4; i += 1) {
    const tile = document.createElement("div");
    tile.className = "tile";
    tile.id = `comp-${i}`;
    comps.appendChild(tile);
  }
  const fans = document.getElementById("fan-grid");
  for (let i = 1; i <= 18; i += 1) {
    const fan = document.createElement("div");
    fan.className = "fan off";
    fan.id = `fan-${i}`;
    fans.appendChild(fan);
  }
  const miniFans = document.getElementById("mini-fans");
  [1, 2].forEach((index) => {
    const row = document.createElement("div");
    row.className = "pump";
    row.innerHTML = `<div>Fan ${index}</div><span class="chip idle" id="mini-fan-pill-${index}">—</span>`;
    const speed = document.createElement("div");
    speed.className = "sub";
    speed.id = `mini-fan-spd-${index}`;
    miniFans.appendChild(row);
    miniFans.appendChild(speed);
  });
}

function bindTabs() {
  document.querySelectorAll(".tabs button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tabs button").forEach((item) => item.classList.remove("active"));
      document.querySelectorAll(".tab").forEach((item) => item.classList.remove("show"));
      button.classList.add("active");
      document.getElementById(`tab-${button.dataset.tab}`).classList.add("show");
      const names = { cdu: "CDU", plant: "Chiller Plant", air: "Air Side", chiller: "Chillers", mini: "Mini AireBlock" };
      setText("crumb", `Hall overview / ${names[button.dataset.tab]}`);
      sampleTrends();
    });
  });
  document.getElementById("ch-prev").addEventListener("click", () => {
    chiller = chiller === 1 ? 10 : chiller - 1;
    Object.keys(trends).forEach((id) => { if (id.startsWith("cv-ch-")) trends[id] = []; });
    renderChiller();
  });
  document.getElementById("ch-next").addEventListener("click", () => {
    chiller = chiller === 10 ? 1 : chiller + 1;
    Object.keys(trends).forEach((id) => { if (id.startsWith("cv-ch-")) trends[id] = []; });
    renderChiller();
  });
}

function apply(batch) {
  if (!batch) return;
  if (typeof batch.connected === "boolean") connected = batch.connected;
  if (batch.points) Object.assign(points, batch.points);
  discoverHall();
  dirty = true;
}

async function boot() {
  buildRepeats();
  bindTabs();
  bindWrite("sp-supply", "CDU01", "ServerGlySupTempSP");
  bindWrite("sp-dp", "CDU01", "CHWHeaderDPSPLead");
  bindWrite("sp-gly", "ChillerMCP", "GlySupWaterTempSP");
  bindWrite("sp-mcp-dp", "ChillerMCP", "DPSP");
  bindWrite("sp-air", "AireBlockMCP", "CCUSupAirTempSP");
  bindWrite("sp-air-dp", "AireBlockMCP", "DPSP");
  bindWrite("sp-room", "MiniAireBlock01", "RoomTempSP");
  bindWrite("sp-ctrl", "MiniAireBlock01", "ControlTempSP");
  bindWrite("sp-ret", "MiniAireBlock01", "RetTempSP");
  bindWrite("sp-fan", "MiniAireBlock01", "NormalModeFanSpdSP");
  document.getElementById("cmd-start").addEventListener("click", () => write("CDU01", "LocalStartCmd", true));
  document.getElementById("cmd-stop").addEventListener("click", () => {
    if (window.confirm("Send emergency stop to CDU-01?")) write("CDU01", "EmergencyStopCmd", true);
  });
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
