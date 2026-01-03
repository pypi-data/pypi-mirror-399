===============
Audio Connected
===============

Watches PulseAudio events for new sinks connected, and if the name matches the configured name, make that sink the default sink.

Installation
============

Probably works best when installed with pipx_ ``pipx install audio-connected`` or uv_ ``uv tool install audio-connected``.

To make it run on startup, you can add a XDG Autostart entry in `$XDG_CONFIG_HOME/autostart` (`~/.config/autostart` by default).
An example `audio-connected.desktop` file is included in the source distribution, and can be copied to the autostart directory.

Example:

.. code:: ini

    [Desktop Entry]
    Version=1.5
    Type=Application
    Name=Audio Connected
    Comment=Set EPOS ADAPT 660 headset as default sink when connected
    Exec=audio-connected "EPOS ADAPT 660"
    OnlyShowIn=XFCE;
    StartupNotify=false
    Terminal=false
    Hidden=false


.. _pipx: https://pypa.github.io/pipx/
.. _uv: https://docs.astral.sh/uv/
