#!/usr/bin/env python

"""Listen for new sinks connected, and if it is the requested sink, make it the default sink."""

import argparse

import pulsectl


def get_sink_by_desc(pulse, desc):
    try:
        return [s for s in pulse.sink_list() if desc in s.description][-1]
    except IndexError:
        return None


class Switcher:
    def __init__(self, sink):
        self._triggered = False
        self._sink = sink

    def callback(self, ev):
        self._triggered = ev.t == pulsectl.PulseEventTypeEnum.new
        raise pulsectl.PulseLoopStop

    def switch(self, pulse):
        if self._triggered:
            if pulse_sink := get_sink_by_desc(pulse, self._sink):
                pulse.default_set(pulse_sink)
        self._triggered = False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sink", help="Sink to switch to when connected")
    options = parser.parse_args()
    switcher = Switcher(options.sink)
    with pulsectl.Pulse("audio-connected") as pulse:
        pulse.event_mask_set("sink")
        pulse.event_callback_set(switcher.callback)
        while True:
            pulse.event_listen(timeout=60)
            switcher.switch(pulse)


if __name__ == "__main__":
    main()
