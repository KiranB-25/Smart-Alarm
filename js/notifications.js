/** Browser notifications integration. */
/** Browser notification capability wrapper with permission-aware failure handling. */
export class NotificationService {
  supported() { return 'Notification' in window; }
  get permission() { return this.supported() ? Notification.permission : 'denied'; }
  async requestPermission() {
    if (!this.supported()) throw new Error('Notifications are not supported by this browser.');
    return Notification.requestPermission();
  }
  /** @param {{title: string, body: string, alarmTime: string}} details */
  notify({ title, body, alarmTime }) {
    if (this.permission !== 'granted') return false;
    try {
      const notification = new Notification(title, { body: `${body}\n${alarmTime}`, icon: 'assets/icons/alarm-icon.svg', badge: 'assets/icons/alarm-icon.svg', tag: 'smart-alarm-active', renotify: true, silent: true });
      notification.onclick = () => { window.focus(); window.location.hash = '#alarm'; notification.close(); };
      return true;
    }
    catch (error) { console.warn('Notification could not be displayed.', error); return false; }
  }
}
