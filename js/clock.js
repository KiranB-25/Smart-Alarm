/** Real-time digital and analog clock controller. */
import { query } from './utils.js';

const DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];

/** Creates and manages both clock displays from one time source. */
export class ClockController {
  /** @param {'12'|'24'} timeFormat */
  constructor(timeFormat = '12') { this.timeFormat = timeFormat; this.timerId = null; }

  start() { this.update(); this.scheduleNextTick(); }
  stop() { window.clearTimeout(this.timerId); this.timerId = null; }
  /** @param {'12'|'24'} format */
  setFormat(format) { this.timeFormat = format === '24' ? '24' : '12'; this.update(); }

  scheduleNextTick() {
    const delay = 1000 - (Date.now() % 1000) + 8;
    this.timerId = window.setTimeout(() => { this.update(); this.scheduleNextTick(); }, delay);
  }

  update() {
    const now = new Date();
    const hour24 = now.getHours();
    const hour = this.timeFormat === '24' ? hour24 : (hour24 % 12 || 12);
    query('#digital-time').innerHTML = `<span class="time-value">${String(hour).padStart(2, '0')} : ${String(now.getMinutes()).padStart(2, '0')} : ${String(now.getSeconds()).padStart(2, '0')}</span>${this.timeFormat === '12' ? `<span class="time-period">${hour24 >= 12 ? 'PM' : 'AM'}</span>` : ''}`;
    query('#clock-day').textContent = DAYS[now.getDay()];
    query('#clock-date').textContent = new Intl.DateTimeFormat('en-US', { month: 'long', day: 'numeric', year: 'numeric' }).format(now);
    const homeTime = document.querySelector('#home-time');
    const homeDate = document.querySelector('#home-date');
    if (homeTime) homeTime.innerHTML = `${String(hour).padStart(2, '0')}:${String(now.getMinutes()).padStart(2, '0')}${this.timeFormat === '12' ? `<span class="time-period">${hour24 >= 12 ? 'PM' : 'AM'}</span>` : ''}`;
    if (homeDate) homeDate.textContent = new Intl.DateTimeFormat('en-US', { weekday: 'long', month: 'long', day: 'numeric' }).format(now);
    query('.hour-hand').style.setProperty('--hand-rotation', `${(hour24 % 12) * 30 + now.getMinutes() * .5 + now.getSeconds() / 120}deg`);
    query('.minute-hand').style.setProperty('--hand-rotation', `${now.getMinutes() * 6 + now.getSeconds() * .1}deg`);
    query('.second-hand').style.setProperty('--hand-rotation', `${now.getSeconds() * 6}deg`);
  }
}
