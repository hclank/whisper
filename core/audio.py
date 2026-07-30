import queue
import sounddevice as sd


class AudioRecorder:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stream = None

    def _callback(self, indata, frame, time_info, status):
        if self.is_recording:
            self.audio_queue.put(indata.copy())

    def start(self):
        if self.is_recording:
            return
        self.is_recording = True
        while not self.audio_queue.empty():
            self.audio_queue.get()
        self.stream = sd.InputStream(
            samplerate=self.sample_rate, channels=1, callback=self._callback
        )
        self.stream.start()

    def stop(self):
        if not self.is_recording:
            return []
        if self.stream:
            self.stream.stop()
            self.stream.close()

        audio_data = []
        while not self.audio_queue.empty():
            audio_data.append(self.audio_queue.get())
        return audio_data
