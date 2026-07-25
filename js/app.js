/** Application bootstrap and module orchestration. */
import { loadState, saveState } from './storage.js';
import { NavigationController, renderFoundation, showToast } from './ui.js';
import { ClockController } from './clock.js';
import { AlarmManager } from './alarms.js';
import { AudioController } from './audio.js';
import { AlarmScheduler } from './alarms.js';
import { RingingController } from './ringing.js';
import { NotificationService } from './notifications.js';
import { StopwatchController } from './stopwatch.js';
import { TimerController } from './timer.js';
import { SettingsController } from './settings.js';

function initialize() {
  try {
    const state = loadState();
    renderFoundation(state);
    const clock = new ClockController(state.settings.timeFormat); clock.start();
    const audio = new AudioController(state.settings.volume);
    const alarmManager = new AlarmManager(state, () => saveState(state), audio);
    new StopwatchController();
    const timerAudio = new AudioController(state.settings.volume);
    new TimerController(timerAudio, state);
    const notifications = new NotificationService();
    new SettingsController(state, () => saveState(state), { clock, alarmManager, alarmAudio: audio, timerAudio, notifications });
    new NavigationController(state);
    let scheduler;
    const ringing = new RingingController(audio, state, (alarm) => scheduler.snooze(alarm));
    scheduler = new AlarmScheduler(state, async (alarm) => {
      const started = await ringing.ring(alarm);
      if (started && state.settings.notificationsEnabled) {
        const hour = state.settings.timeFormat === '24' ? alarm.hour : (alarm.hour % 12 || 12);
        const alarmTime = `${String(hour).padStart(2, '0')}:${String(alarm.minute).padStart(2, '0')}${state.settings.timeFormat === '12' ? ` ${alarm.hour >= 12 ? 'PM' : 'AM'}` : ''}`;
        notifications.notify({ title: alarm.label || 'Alarm', body: 'Your alarm is ringing now.', alarmTime });
      }
    }, () => saveState(state));
    scheduler.start();
  }
  catch (error) { console.error('Smart Alarm could not start.', error); showToast('Smart Alarm could not start. Please refresh the page.', 'error'); }
}

initialize();
