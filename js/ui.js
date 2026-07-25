/** Shared UI rendering, navigation, and feedback helpers. */
import { query } from './utils.js';

const TONE_OPTIONS = [['classic-bell', 'Classic Bell'], ['digital-alarm', 'Digital Alarm'], ['morning-birds', 'Morning Birds'], ['soft-piano', 'Soft Piano'], ['nature', 'Nature'], ['electronic', 'Electronic'], ['gentle-chime', 'Gentle Chime'], ['sunrise', 'Sunrise']];
const NAV_ITEMS = [['home', '⌂', 'Home'], ['alarm', '◷', 'Alarm'], ['clock', '◴', 'Clock'], ['stopwatch', '◉', 'Stopwatch'], ['timer', '⌛', 'Timer'], ['settings', '⚙', 'Settings']];

/** @param {string} message @param {'info'|'success'|'error'} [kind] */
export function showToast(message, kind = 'info') {
  const region = query('#toast-region');
  const toast = document.createElement('div');
  toast.className = 'toast'; toast.dataset.kind = kind; toast.setAttribute('role', kind === 'error' ? 'alert' : 'status');
  const icon = kind === 'error' ? '!' : kind === 'success' ? '✓' : 'i';
  toast.innerHTML = `<span class="toast-icon" aria-hidden="true">${icon}</span><span class="toast-message"></span>`;
  query('.toast-message', toast).textContent = message;
  region.append(toast);
  window.setTimeout(() => toast.remove(), 4200);
}

/** Applies the stored appearance selection without changing application behavior. */
export function applyAppearance(settings) {
  document.documentElement.dataset.theme = settings.theme;
  document.documentElement.dataset.motion = settings.animationsEnabled === false ? 'reduced' : 'full';
}

const toneOptions = () => TONE_OPTIONS.map(([id, name]) => `<option value="${id}">${name}</option>`).join('');
const navMarkup = (className, id = '') => `<nav ${id ? `id="${id}"` : ''} class="${className}" aria-label="Primary navigation">${NAV_ITEMS.map(([page, icon, label]) => `<button class="nav-item" type="button" data-page="${page}" aria-label="${label}" aria-current="false"><span class="nav-icon" aria-hidden="true">${icon}</span><span>${label}</span></button>`).join('')}</nav>`;

/** @param {{settings: object}} state */
export function renderFoundation(state) {
  applyAppearance(state.settings);
  const ticks = Array.from({ length: 12 }, (_, index) => `<span class="clock-tick" style="--rotation:${index * 30}deg" aria-hidden="true"></span>`).join('');
  query('#app').innerHTML = `
    <div class="app-frame">
      <aside class="sidebar"><a class="brand" href="#home" aria-label="Smart Alarm home"><span class="brand-mark" aria-hidden="true">◷</span><span><strong class="brand-name">Smart Alarm</strong><span class="brand-caption">Wake beautifully</span></span></a>${navMarkup('sidebar-nav')}<p class="sidebar-foot">Your time, your rhythm.</p></aside>
      <div class="app-shell">
        <header class="app-header"><a class="brand compact-brand" href="#home" aria-label="Smart Alarm home"><span class="brand-mark" aria-hidden="true">◷</span><strong class="brand-name">Smart Alarm</strong></a><span id="header-date" class="header-status"></span><button id="menu-toggle" class="menu-toggle" type="button" aria-label="Open navigation menu" aria-controls="mobile-navigation" aria-expanded="false"><span></span><span></span><span></span></button></header>
        <main id="main-content" class="app-main" tabindex="-1">
          <section class="app-page home-page" data-view="home" aria-labelledby="home-title">
            <div class="home-hero"><div><p class="eyebrow" id="home-greeting">Good day</p><div class="hero-watch" aria-hidden="true"><span class="hero-watch-face"><i class="hero-watch-hour"></i><i class="hero-watch-minute"></i><b></b></span></div><h1 id="home-title" class="home-title">Make the next hour count.</h1><time id="home-time" class="home-time"></time><p id="home-date" class="home-date"></p></div><div class="next-alarm-card"><span class="eyebrow">Next alarm</span><strong id="home-next-alarm">No alarm scheduled</strong><span id="home-next-detail">Create an alarm when you are ready.</span><button class="button button-primary" type="button" data-go="alarm">Manage alarms</button></div></div>
            <section class="home-section" aria-labelledby="quick-title"><div class="page-heading"><div><h2 id="quick-title">Quick actions</h2><p>Jump straight into your most-used tools.</p></div></div><div class="quick-grid"><button type="button" class="quick-action" data-go="alarm"><span>◷</span>Alarm</button><button type="button" class="quick-action" data-go="timer"><span>⌛</span>Timer</button><button type="button" class="quick-action" data-go="stopwatch"><span>◉</span>Stopwatch</button><button type="button" class="quick-action" data-go="clock"><span>◴</span>Clock</button></div></section>
            <div class="dashboard-grid"><section class="home-section"><div class="page-heading"><div><h2>Upcoming alarms</h2><p>Your next scheduled moments.</p></div><button class="text-button" type="button" data-go="alarm">View all</button></div><ul id="home-upcoming" class="dashboard-list"></ul></section><section class="home-section"><div class="page-heading"><div><h2>Recent activity</h2><p>This session’s latest actions.</p></div></div><ul id="home-activity" class="dashboard-list"></ul></section></div>
          </section>

          <section class="app-page" data-view="alarm" aria-labelledby="alarms-title" hidden><div class="page-heading page-heading-large"><div><p class="eyebrow">Wake-up schedule</p><h1 id="alarms-title">Alarms</h1><p>Create a rhythm that fits your life.</p></div><button id="add-alarm" class="button button-primary" type="button">+ Add alarm</button></div><section class="alarms-panel"><form id="alarm-form" class="alarm-form" hidden novalidate><h2 id="alarm-form-title">New alarm</h2><div class="form-grid"><label class="field">Time<input id="alarm-time" type="time" required /></label><label class="field">Label<input id="alarm-label" type="text" maxlength="60" autocomplete="off" placeholder="Morning routine" /></label><div class="field"><span>Tone</span><div class="tone-control"><select id="alarm-tone" aria-label="Alarm tone">${toneOptions()}</select><button id="tone-play" class="icon-button" type="button" aria-label="Play selected ringtone" aria-pressed="false">▶</button><button id="tone-pause" class="icon-button" type="button" aria-label="Pause or resume selected ringtone" aria-pressed="false">Ⅱ</button><button id="tone-stop" class="icon-button" type="button" aria-label="Stop selected ringtone">■</button></div></div><label class="field">Repeat<select id="alarm-repeat"><option value="once">Once</option><option value="everyday">Every day</option><option value="weekdays">Weekdays</option><option value="weekends">Weekends</option><option value="custom">Custom days</option></select></label></div><fieldset id="custom-days" class="repeat-days" hidden><legend class="sr-only">Repeat on</legend>${['S', 'M', 'T', 'W', 'T', 'F', 'S'].map((day, index) => `<label class="day-option"><input type="checkbox" name="days" value="${index}" /><span>${day}</span></label>`).join('')}</fieldset><div class="form-actions"><button id="cancel-alarm" class="button button-secondary" type="button">Cancel</button><button class="button button-primary" type="submit">Save alarm</button></div></form><ul id="alarm-list" class="alarm-list" aria-live="polite"></ul></section></section>

          <section class="app-page clock-page" data-view="clock" aria-labelledby="clock-title" hidden><div class="page-heading page-heading-large"><div><p class="eyebrow">Right now</p><h1 id="clock-title">Clock</h1><p>Stay centered in the present moment.</p></div></div><section class="foundation-panel clock-layout"><div class="clock-card" role="img" aria-label="Current analog time"><div class="analog-clock">${ticks}<span class="clock-hand hour-hand"></span><span class="clock-hand minute-hand"></span><span class="clock-hand second-hand"></span><span class="clock-center"></span></div></div><div class="clock-copy"><time id="digital-time" class="digital-time" aria-live="off"></time><p class="clock-date"><strong id="clock-day"></strong><span id="clock-date"></span></p><p class="clock-status">Clock synchronized</p></div></section></section>

          <section class="app-page tool-page" data-view="stopwatch" aria-labelledby="stopwatch-title" hidden><div class="page-heading page-heading-large"><div><p class="eyebrow">Elapsed time</p><h1 id="stopwatch-title">Stopwatch</h1><p>Track every focused moment.</p></div></div><section class="tool-panel solo-tool"><time id="stopwatch-display" class="tool-display" aria-live="off">00:00:00<small>.00</small></time><div class="tool-actions centered-actions"><button id="stopwatch-start" class="button button-primary" type="button" aria-label="Start stopwatch">Start</button><button id="stopwatch-lap" class="button button-secondary" type="button">Lap</button><button id="stopwatch-reset" class="button button-secondary" type="button">Reset</button></div><ol id="lap-list" class="laps" aria-live="polite"><li class="lap-empty">No laps recorded yet.</li></ol></section></section>

          <section class="app-page tool-page" data-view="timer" aria-labelledby="timer-title" hidden><div class="page-heading page-heading-large"><div><p class="eyebrow">Focused time</p><h1 id="timer-title">Countdown timer</h1><p>Set aside a little time for what matters.</p></div></div><section class="tool-panel solo-tool"><time id="timer-display" class="tool-display" aria-live="off">00:00:00</time><div class="timer-inputs"><label class="timer-input">Hours<input id="timer-hours" data-timer-input type="number" inputmode="numeric" min="0" max="99" value="0" /></label><label class="timer-input">Minutes<input id="timer-minutes" data-timer-input type="number" inputmode="numeric" min="0" max="59" value="5" /></label><label class="timer-input">Seconds<input id="timer-seconds" data-timer-input type="number" inputmode="numeric" min="0" max="59" value="0" /></label></div><div class="tool-actions centered-actions"><button id="timer-start" class="button button-primary" type="button" aria-label="Start countdown timer">Start</button><button id="timer-reset" class="button button-secondary" type="button">Reset</button></div></section></section>

          <section class="app-page" data-view="settings" aria-labelledby="settings-title" hidden><div class="page-heading page-heading-large"><div><p class="eyebrow">Personalize</p><h1 id="settings-title">Settings</h1><p>Fine-tune Smart Alarm around your rhythm.</p></div></div><section class="settings-panel"><div class="settings-grid"><div class="setting-row"><div class="setting-copy"><strong>24-hour time</strong><span>Use military time across the application.</span></div><button id="setting-time-format" class="setting-switch" type="button" role="switch" aria-checked="false" aria-label="Use 24-hour time"></button></div><div class="setting-row"><div class="setting-copy"><strong>Appearance mode</strong><span>Choose Dark, Light, or System Default.</span></div><div id="theme-choices" class="theme-choices" role="group" aria-label="Appearance mode"><button class="theme-choice" type="button" data-theme="dark" aria-label="Use dark mode">Dark</button><button class="theme-choice" type="button" data-theme="light" aria-label="Use light mode">Light</button><button class="theme-choice" type="button" data-theme="system" aria-label="Use system default appearance">System</button></div></div><div class="setting-row"><div class="setting-copy"><strong>Default snooze</strong><span>How long should a snoozed alarm wait?</span></div><select id="setting-snooze" aria-label="Default snooze duration"><option value="1">1 minute</option><option value="5">5 minutes</option><option value="10">10 minutes</option><option value="15">15 minutes</option><option value="30">30 minutes</option></select></div><div class="setting-row"><div class="setting-copy"><strong>Default ringtone</strong><span>Used for timers and new alarms.</span></div><select id="setting-tone" aria-label="Default ringtone">${toneOptions()}</select></div><div class="setting-row"><div class="setting-copy"><strong>Sound volume</strong><span>Controls all generated sounds.</span></div><div class="volume-control"><input id="setting-volume" type="range" min="0" max="1" step=".01" aria-label="Alarm volume" /><output id="setting-volume-output"></output></div></div><div class="setting-row"><div class="setting-copy"><strong>Notifications</strong><span>Show a browser notification when an alarm rings.</span></div><button id="setting-notifications" class="setting-switch" type="button" role="switch" aria-checked="false" aria-label="Enable alarm notifications"></button></div><div class="setting-row"><div class="setting-copy"><strong>Animations</strong><span>Enable motion and page transitions.</span></div><button id="setting-animations" class="setting-switch" type="button" role="switch" aria-checked="true" aria-label="Enable animations"></button></div></div></section></section>
        </main>
      </div>
      <div id="menu-scrim" class="menu-scrim" hidden></div>
      <aside id="mobile-navigation" class="mobile-drawer" aria-label="Mobile navigation" aria-hidden="true"><div class="mobile-drawer-header"><strong>Navigate</strong><button id="menu-close" class="icon-button" type="button" aria-label="Close navigation menu">×</button></div>${navMarkup('mobile-nav')}</aside>
    </div>`;
  document.body.insertAdjacentHTML('beforeend', `<div id="ringing-overlay" class="ringing-overlay" role="dialog" aria-modal="true" aria-labelledby="ring-label" hidden><section class="ringing-card"><div class="ringing-bell" aria-hidden="true">♩</div><p class="eyebrow">Alarm ringing</p><h2 id="ring-label">Alarm</h2><p id="ring-tone" class="ringing-label"></p><time id="ring-time" class="ringing-time"></time><div class="ringing-actions"><button id="ring-snooze" class="button button-secondary" type="button">Snooze</button><button id="ring-dismiss" class="button button-primary" type="button">Dismiss</button><button id="ring-stop" class="button button-secondary button-danger" type="button">Stop</button></div></section></div>`);
}

/** UI-only navigation and home-dashboard presentation. */
export class NavigationController {
  /** @param {{alarms: Array}} state */
  constructor(state) { this.state = state; this.activity = ['Dashboard ready']; this.bind(); this.navigate(location.hash.slice(1) || 'home', false); }
  bind() {
    document.addEventListener('click', (event) => { const target = event.target.closest('[data-page], [data-go]'); if (!target) return; this.navigate(target.dataset.page || target.dataset.go); this.closeMenu(); });
    window.addEventListener('hashchange', () => this.navigate(location.hash.slice(1) || 'home', false));
    query('#menu-toggle').addEventListener('click', () => this.toggleMenu());
    query('#menu-close').addEventListener('click', () => this.closeMenu());
    query('#menu-scrim').addEventListener('click', () => this.closeMenu());
    document.addEventListener('keydown', (event) => { if (event.key === 'Escape') this.closeMenu(); });
    query('#alarm-form').addEventListener('submit', () => this.record('Alarm saved'));
    query('#alarm-list').addEventListener('click', (event) => { if (event.target.closest('[data-action]')) this.record('Alarm updated'); });
  }
  navigate(page, writeHash = true) {
    const validPage = NAV_ITEMS.some(([id]) => id === page) ? page : 'home';
    if (writeHash && location.hash !== `#${validPage}`) { location.hash = validPage; return; }
    for (const view of document.querySelectorAll('[data-view]')) view.hidden = view.dataset.view !== validPage;
    for (const item of document.querySelectorAll('[data-page]')) item.setAttribute('aria-current', item.dataset.page === validPage ? 'page' : 'false');
    if (validPage === 'home') this.refreshDashboard();
    query('#main-content').focus({ preventScroll: true });
  }
  record(message) { this.activity.unshift(`${message} · just now`); this.activity = this.activity.slice(0, 4); }
  toggleMenu() { const drawer = query('#mobile-navigation'); drawer.classList.contains('is-open') ? this.closeMenu() : this.openMenu(); }
  openMenu() { query('#mobile-navigation').classList.add('is-open'); query('#mobile-navigation').setAttribute('aria-hidden', 'false'); query('#menu-scrim').hidden = false; query('#menu-toggle').setAttribute('aria-expanded', 'true'); query('#menu-toggle').setAttribute('aria-label', 'Close navigation menu'); }
  closeMenu() { const drawer = query('#mobile-navigation'); drawer.classList.remove('is-open'); drawer.setAttribute('aria-hidden', 'true'); query('#menu-scrim').hidden = true; query('#menu-toggle').setAttribute('aria-expanded', 'false'); query('#menu-toggle').setAttribute('aria-label', 'Open navigation menu'); }
  refreshDashboard() {
    const now = new Date(); const greeting = now.getHours() < 12 ? 'Good morning' : now.getHours() < 18 ? 'Good afternoon' : 'Good evening';
    query('#home-greeting').textContent = greeting; query('#header-date').textContent = new Intl.DateTimeFormat('en-US', { weekday: 'short', month: 'short', day: 'numeric' }).format(now);
    const upcoming = this.state.alarms.filter((alarm) => alarm.enabled).map((alarm) => ({ alarm, when: nextOccurrence(alarm, now) })).filter((item) => item.when).sort((a, b) => a.when - b.when);
    const next = upcoming[0]; query('#home-next-alarm').textContent = next ? formatAlarmTime(next.alarm, this.state.settings.timeFormat) : 'No alarm scheduled'; query('#home-next-detail').textContent = next ? `${next.alarm.label || 'Alarm'} · ${relativeAlarmDate(next.when, now)}` : 'Create an alarm when you are ready.';
    renderTextList('#home-upcoming', upcoming.slice(0, 3).map(({ alarm, when }) => `${formatAlarmTime(alarm, this.state.settings.timeFormat)} · ${alarm.label || 'Alarm'} · ${relativeAlarmDate(when, now)}`), 'No upcoming alarms.');
    renderTextList('#home-activity', this.activity, 'No recent activity.');
  }
}

function formatAlarmTime(alarm, format) { const hour = format === '24' ? alarm.hour : (alarm.hour % 12 || 12); return `${String(hour).padStart(2, '0')}:${String(alarm.minute).padStart(2, '0')}${format === '12' ? ` ${alarm.hour >= 12 ? 'PM' : 'AM'}` : ''}`; }
function repeatLabel(alarm) { return ({ once: 'Once', everyday: 'Every day', weekdays: 'Weekdays', weekends: 'Weekends', custom: 'Custom days' })[alarm.repeat] ?? 'Once'; }
function renderTextList(selector, items, empty) { const list = query(selector); list.replaceChildren(); for (const item of items.length ? items : [empty]) { const entry = document.createElement('li'); entry.textContent = item; list.append(entry); } }
function nextOccurrence(alarm, now) { for (let offset = 0; offset < 8; offset += 1) { const candidate = new Date(now); candidate.setDate(now.getDate() + offset); candidate.setHours(alarm.hour, alarm.minute, 0, 0); if (candidate <= now || !matchesDisplaySchedule(alarm, candidate)) continue; return candidate; } return null; }
function matchesDisplaySchedule(alarm, date) { const day = date.getDay(); return alarm.repeat === 'once' || alarm.repeat === 'everyday' || (alarm.repeat === 'weekdays' && day >= 1 && day <= 5) || (alarm.repeat === 'weekends' && (day === 0 || day === 6)) || (alarm.repeat === 'custom' && (alarm.days ?? []).includes(day)); }
function relativeAlarmDate(date, now) { const days = Math.round((new Date(date.getFullYear(), date.getMonth(), date.getDate()) - new Date(now.getFullYear(), now.getMonth(), now.getDate())) / 86400000); return days === 0 ? 'Today' : days === 1 ? 'Tomorrow' : new Intl.DateTimeFormat('en-US', { weekday: 'long' }).format(date); }
