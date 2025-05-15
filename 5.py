import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button, CheckButtons
from scipy.signal import butter, filtfilt

INIT_AMPLITUDE = 1.0
INIT_FREQUENCY = 2.0
INIT_PHASE = 0.0
INIT_NOISE_MEAN = 0.0
INIT_NOISE_STD = 0.3
INIT_CUTOFF = 0.05

TIME = np.linspace(0, 2 * np.pi, 1000)
noise = None 

def generate_harmonic(amplitude, frequency, phase):
    return amplitude * np.sin(frequency * TIME + phase)

def generate_noise(mean, std):
    return np.random.normal(mean, std, TIME.shape)

def filter_signal(signal, cutoff):
    b, a = butter(N=3, Wn=cutoff)
    return filtfilt(b, a, signal)

def update(val):
    global noise

    amp = s_amp.val
    freq = s_freq.val
    ph = s_phase.val
    n_mean = s_noise_mean.val
    n_std = s_noise_std.val
    cutoff = s_cutoff.val

    y_clean = generate_harmonic(amp, freq, ph)

    if noise is None or val == "noise":
        noise = generate_noise(n_mean, n_std)

    y_noisy = y_clean + noise
    y_filtered = filter_signal(y_noisy, cutoff)

    l_clean.set_ydata(y_clean)
    l_noisy.set_ydata(y_noisy)
    l_filtered.set_ydata(y_filtered)

    l_noisy.set_visible(cb.get_status()[0])
    l_filtered.set_visible(cb_filter.get_status()[0])

    fig.canvas.draw_idle()

def reset(event):
    global noise
    noise = None
    s_amp.reset()
    s_freq.reset()
    s_phase.reset()
    s_noise_mean.reset()
    s_noise_std.reset()
    s_cutoff.reset()
    if not cb.get_status()[0]: cb.set_active(0)
    if cb_filter.get_status()[0]: cb_filter.set_active(0)
    update(None)

fig, ax = plt.subplots(figsize=(10, 6))
plt.subplots_adjust(left=0.3, bottom=0.5)

ax.set_title("Інтерактивна гармоніка з шумом та фільтрацією")
l_clean, = ax.plot(TIME, generate_harmonic(INIT_AMPLITUDE, INIT_FREQUENCY, INIT_PHASE),
                   label='Чиста гармоніка', color='blue', linestyle='--')
l_noisy, = ax.plot(TIME, np.zeros_like(TIME), label='Гармоніка з шумом', color='orange')
l_filtered, = ax.plot(TIME, np.zeros_like(TIME), label='Відфільтрований сигнал', color='green')

ax.legend(loc='upper right')
ax.set_ylim(-2, 2)
ax.grid(True)

axcolor = 'lightgoldenrodyellow'
s_axes = {
    'amp': plt.axes([0.3, 0.42, 0.6, 0.03], facecolor=axcolor),
    'freq': plt.axes([0.3, 0.37, 0.6, 0.03], facecolor=axcolor),
    'phase': plt.axes([0.3, 0.32, 0.6, 0.03], facecolor=axcolor),
    'noise_mean': plt.axes([0.3, 0.27, 0.6, 0.03], facecolor=axcolor),
    'noise_std': plt.axes([0.3, 0.22, 0.6, 0.03], facecolor=axcolor),
    'cutoff': plt.axes([0.3, 0.17, 0.6, 0.03], facecolor=axcolor)
}

s_amp = Slider(s_axes['amp'], 'Амплітуда', 0.1, 2.0, valinit=INIT_AMPLITUDE)
s_freq = Slider(s_axes['freq'], 'Частота', 0.5, 10.0, valinit=INIT_FREQUENCY)
s_phase = Slider(s_axes['phase'], 'Фаза', 0, 2 * np.pi, valinit=INIT_PHASE)
s_noise_mean = Slider(s_axes['noise_mean'], 'Середнє шуму', -1.0, 1.0, valinit=INIT_NOISE_MEAN)
s_noise_std = Slider(s_axes['noise_std'], 'Дисперсія шуму', 0.0, 1.0, valinit=INIT_NOISE_STD)
s_cutoff = Slider(s_axes['cutoff'], 'Частота зрізу', 0.01, 0.3, valinit=INIT_CUTOFF)

reset_ax = plt.axes([0.75, 0.05, 0.15, 0.04])
button = Button(reset_ax, 'Скинути', color='lightcoral', hovercolor='0.975')

cb_ax = plt.axes([0.05, 0.6, 0.2, 0.15])
cb = CheckButtons(cb_ax, ['Показати шум'], [True])
cb_filter_ax = plt.axes([0.05, 0.45, 0.2, 0.15])
cb_filter = CheckButtons(cb_filter_ax, ['Показати фільтр'], [False])

s_amp.on_changed(update)
s_freq.on_changed(update)
s_phase.on_changed(update)
s_noise_mean.on_changed(lambda val: update("noise"))
s_noise_std.on_changed(lambda val: update("noise"))
s_cutoff.on_changed(update)
button.on_clicked(reset)
cb.on_clicked(lambda val: update(None))
cb_filter.on_clicked(lambda val: update(None))

update(None)
plt.show()
