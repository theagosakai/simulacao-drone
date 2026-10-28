const throttle = document.getElementById("throttle");
const pitch = document.getElementById("pitch");
const yaw = document.getElementById("yaw");
const droneWrap = document.getElementById("droneWrap");
const scene = document.getElementById("scene");
const partCard = document.getElementById("partCard");
const takeoffBtn = document.getElementById("takeoffBtn");

let flying = false;
let baseAlt = 42.8;
let baseSpeed = 18.4;

function createBars(containerId, count, seed) {
  const el = document.getElementById(containerId);
  for (let i = 0; i < count; i++) {
    const bar = document.createElement("i");
    bar.style.height = `${6 + Math.abs(Math.sin((i + seed) * 1.37)) * 11}px`;
    el.appendChild(bar);
  }
}
createBars("altBars", 12, 1);
createBars("speedBars", 12, 4);

function updateControls() {
  const throttleValue = Number(throttle.value);
  const pitchValue = Number(pitch.value);
  const yawValue = Number(yaw.value);
  document.getElementById("throttleLabel").textContent = `${throttleValue}%`;
  document.getElementById("pitchLabel").textContent = `${pitchValue}°`;
  document.getElementById("yawLabel").textContent = `${yawValue}°`;
  document.getElementById("yawValue").textContent = String(yawValue).padStart(3, "0");

  const pitchMove = pitchValue * 1.1;
  const xMove = (yawValue - 180) / 18;
  droneWrap.style.transform = `translate(-50%, -50%) rotate(${pitchValue / 4}deg) translate(${xMove}px, ${-Math.abs(pitchMove / 2)}px)`;

  if (flying) {
    const acceleration = (throttleValue - 48) / 20;
    baseAlt = Math.max(0, baseAlt + acceleration * 0.012);
    baseSpeed = Math.max(0, throttleValue * 0.27 + Math.abs(pitchValue) * 0.08);
    document.getElementById("acceleration").textContent = Math.abs(acceleration).toFixed(1);
  }
  document.getElementById("altitude").textContent = baseAlt.toFixed(1);
  document.getElementById("speed").textContent = baseSpeed.toFixed(1);
  document.getElementById("loadValue").innerHTML = `${throttleValue}<small>%</small>`;
  document.getElementById("loadRing").style.background = `conic-gradient(var(--lime) 0 ${throttleValue}%, #293536 ${throttleValue}% 100%)`;
}

[throttle, pitch, yaw].forEach((input) => input.addEventListener("input", updateControls));

takeoffBtn.addEventListener("click", () => {
  flying = !flying;
  takeoffBtn.classList.toggle("active", flying);
  takeoffBtn.querySelector("span").textContent = flying ? "POUSAR DRONE" : "INICIAR VOO";
  document.querySelector(".recording").innerHTML = flying ? "<i></i> VOO ATIVO" : "<i></i> GRAVANDO";
});

document.querySelectorAll(".view-tabs button").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".view-tabs button").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    scene.classList.toggle("inspection", button.dataset.mode === "inspection");
    if (button.dataset.mode === "flight") partCard.classList.remove("open");
  });
});

const parts = {
  motores: ["Motores brushless X280", "4 × 1500 KV", "98%"],
  motor2: ["Motor brushless M2", "1500 KV · 12 cm", "96%"],
  motor3: ["Motor brushless M3", "1500 KV · 12 cm", "97%"],
  motor4: ["Motor brushless M4", "1500 KV · 12 cm", "99%"],
  camera: ["Câmera stabilizada 4K", "Sensor 1/2, 4K/60fps", "OK"],
  bateria: ["Bateria LiPo inteligente", "6S · 22.2V · 5200mAh", "86%"],
  gps: ["Módulo GPS / GNSS", "12 satélites · RTK ready", "FIX"],
  esc: ["Controladores ESC", "4 × 40A BLHeli · 6S", "OK"],
  led: ["LED de estado", "RGB · posição · emergência", "OK"]
};
function showPart(partId) {
    const [name, spec, status] = parts[partId];
    document.getElementById("partName").textContent = name;
    document.getElementById("partSpec").textContent = spec;
    document.getElementById("partStatus").textContent = status;
    partCard.classList.add("open");
    document.querySelectorAll(".inspection-list button").forEach((button) =>
      button.classList.toggle("active", button.dataset.part === partId));
}
document.querySelectorAll(".hotspot, .inspection-list button").forEach((button) => {
  button.addEventListener("click", () => showPart(button.dataset.part));
});
document.getElementById("closePart").addEventListener("click", () => partCard.classList.remove("open"));

let dragStart = null;
scene.addEventListener("pointerdown", (event) => {
  if (event.target.closest(".hotspot")) return;
  dragStart = { x: event.clientX, y: event.clientY, yaw: Number(yaw.value), pitch: Number(pitch.value) };
  scene.classList.add("dragging");
  scene.setPointerCapture(event.pointerId);
});
scene.addEventListener("pointermove", (event) => {
  if (!dragStart) return;
  yaw.value = Math.round((dragStart.yaw + (event.clientX - dragStart.x) / 3 + 360) % 360);
  pitch.value = Math.max(-30, Math.min(30, Math.round(dragStart.pitch + (event.clientY - dragStart.y) / 4)));
  updateControls();
});
scene.addEventListener("pointerup", () => { dragStart = null; scene.classList.remove("dragging"); });

window.addEventListener("keydown", (event) => {
  const key = event.key.toLowerCase();
  if (["w","a","s","d","arrowup","arrowdown","arrowleft","arrowright"].includes(key)) event.preventDefault();
  if (key === "w" || key === "arrowup") throttle.value = Math.min(100, Number(throttle.value) + 3);
  if (key === "s" || key === "arrowdown") throttle.value = Math.max(0, Number(throttle.value) - 3);
  if (key === "a" || key === "arrowleft") yaw.value = (Number(yaw.value) - 3 + 360) % 360;
  if (key === "d" || key === "arrowright") yaw.value = (Number(yaw.value) + 3) % 360;
  if (key === " ") { event.preventDefault(); takeoffBtn.click(); }
  updateControls();
});

document.getElementById("resetBtn").addEventListener("click", () => {
  throttle.value = 68;
  pitch.value = 12;
  yaw.value = 34;
  baseAlt = 42.8;
  baseSpeed = 18.4;
  updateControls();
});

let battery = 86;
setInterval(() => {
  if (flying) {
    battery = Math.max(5, battery - 0.02);
    document.getElementById("battery").textContent = Math.floor(battery);
    document.getElementById("autonomy").textContent = `${Math.max(1, Math.floor(battery / 3))} min`;
  }
  const time = new Date();
  document.querySelector(".mission-status b").textContent = time.toLocaleTimeString("pt-BR", { hour12: false });
}, 1000);

updateControls();
