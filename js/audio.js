/** Built-in ringtone synthesis and playback controller. */

/**
 * Small offline ringtone engine. Sound is generated on-device with Web Audio,
 * avoiding network, licensing, and missing-file failure modes.
 */
export class AudioController {
  /** @param {number} volume */
  constructor(volume = 0.7) { this.volume = volume; this.context = null; this.master = null; this.nodes = new Set(); this.cycleId = null; this.activeTone = null; this.paused = false; }

  supported() { return Boolean(window.AudioContext || window.webkitAudioContext); }
  setVolume(value) { this.volume = Math.max(0, Math.min(1, Number(value))); if (this.master) this.master.gain.setTargetAtTime(this.volume, this.context.currentTime, .04); }

  async ensureContext() {
    if (!this.supported()) throw new Error('Audio playback is not supported by this browser.');
    if (!this.context) {
      const Context = window.AudioContext || window.webkitAudioContext;
      this.context = new Context(); this.master = this.context.createGain(); this.master.gain.value = this.volume; this.master.connect(this.context.destination);
    }
    if (this.context.state === 'suspended') await this.context.resume();
  }

  /** @param {string} tone */
  async play(tone) {
    await this.ensureContext();
    if (this.activeTone === tone && this.paused) { this.paused = false; this.scheduleCycle(); return; }
    if (this.activeTone === tone && !this.paused) return;
    this.stop(); this.activeTone = tone; this.paused = false; this.scheduleCycle();
  }

  async pause() {
    if (!this.context || !this.activeTone || this.paused) return;
    this.paused = true; window.clearTimeout(this.cycleId); this.cycleId = null;
    await this.context.suspend();
  }

  async resume() { if (this.activeTone && this.paused) await this.play(this.activeTone); }

  stop() {
    window.clearTimeout(this.cycleId); this.cycleId = null;
    for (const node of this.nodes) { try { node.stop?.(); node.disconnect?.(); } catch { /* Nodes may have ended naturally. */ } }
    this.nodes.clear(); this.activeTone = null; this.paused = false;
  }

  scheduleCycle() {
    if (!this.context || !this.activeTone || this.paused) return;
    const duration = this.playCycle(this.activeTone);
    this.cycleId = window.setTimeout(() => this.scheduleCycle(), duration * 1000);
  }

  /** @param {string} tone @returns {number} seconds */
  playCycle(tone) {
    const now = this.context.currentTime + .02;
    const recipes = {
      'classic-bell': () => { this.notes([784, 988, 784], now, .28, 'sine'); return 1.35; },
      'digital-alarm': () => { this.notes([880, 880, 1047, 880], now, .13, 'square'); return .95; },
      'morning-birds': () => { this.chirp(1200, 2200, now); this.chirp(1800, 2850, now + .34); return 1.6; },
      'soft-piano': () => { this.notes([523.25, 659.25, 783.99], now, .52, 'triangle', .13); return 2.05; },
      nature: () => { this.noise(now, 1.15, .055); this.notes([392, 493.88], now + .22, .6, 'sine', .06); return 1.7; },
      electronic: () => { this.notes([440, 660, 880, 660], now, .11, 'sawtooth', .12); return .9; },
      'gentle-chime': () => { this.notes([1046.5, 1318.5], now, .68, 'sine', .12); return 2.1; },
      sunrise: () => { this.notes([261.63, 329.63, 392, 523.25], now, .36, 'triangle', .1); return 1.85; },
    };
    return (recipes[tone] ?? recipes['classic-bell'])();
  }

  /** @param {number[]} frequencies @param {number} start @param {number} duration @param {OscillatorType} type @param {number} [level] */
  notes(frequencies, start, duration, type, level = .18) { frequencies.forEach((frequency, index) => this.tone(frequency, start + index * duration, duration * .78, type, level)); }
  tone(frequency, start, duration, type, level) {
    const oscillator = this.context.createOscillator(); const gain = this.context.createGain(); oscillator.type = type; oscillator.frequency.setValueAtTime(frequency, start);
    gain.gain.setValueAtTime(.0001, start); gain.gain.exponentialRampToValueAtTime(level, start + .018); gain.gain.exponentialRampToValueAtTime(.0001, start + duration);
    oscillator.connect(gain).connect(this.master); this.track(oscillator); oscillator.start(start); oscillator.stop(start + duration + .03);
  }
  chirp(from, to, start) { const oscillator = this.context.createOscillator(); const gain = this.context.createGain(); oscillator.type = 'sine'; oscillator.frequency.setValueAtTime(from, start); oscillator.frequency.exponentialRampToValueAtTime(to, start + .22); gain.gain.setValueAtTime(.0001, start); gain.gain.exponentialRampToValueAtTime(.12, start + .02); gain.gain.exponentialRampToValueAtTime(.0001, start + .26); oscillator.connect(gain).connect(this.master); this.track(oscillator); oscillator.start(start); oscillator.stop(start + .3); }
  noise(start, duration, level) { const buffer = this.context.createBuffer(1, Math.ceil(this.context.sampleRate * duration), this.context.sampleRate); const data = buffer.getChannelData(0); for (let i = 0; i < data.length; i += 1) data[i] = (Math.random() * 2 - 1) * .25; const source = this.context.createBufferSource(); const gain = this.context.createGain(); source.buffer = buffer; gain.gain.setValueAtTime(.0001, start); gain.gain.exponentialRampToValueAtTime(level, start + .08); gain.gain.exponentialRampToValueAtTime(.0001, start + duration); source.connect(gain).connect(this.master); this.track(source); source.start(start); source.stop(start + duration + .03); }
  track(node) { this.nodes.add(node); node.addEventListener('ended', () => this.nodes.delete(node), { once: true }); }
}
