# labbench-comm

**labbench-comm** is an asynchronous Python framework for communicating with LabBench hardware devices over serial connections.  
It provides a robust, testable, and extensible protocol stack with concrete device implementations, starting with the **CPAR+** device.

The package is designed for:
- Scientific and clinical research setups
- Hardware control and automation
- Deterministic, protocol-driven device communication
- Async-first Python applications (`asyncio`)

---

## Features

- **Async-first architecture** using `asyncio`
- **Robust serial communication** built on `pyserial`
- **Protocol abstraction** (framing, packets, checksums, dispatch)
- **Typed device functions and messages**
- **Extensible device model** for adding new LabBench devices
- **Unit tests + hardware integration tests**
- **CPAR+ device support** (functions, messages, waveform control)

---

## Supported Devices

- **CPAR+** (pressure stimulation device)

Additional devices can be added by implementing new `Device`, `DeviceFunction`, and `DeviceMessage` classes.

---

## Requirements

- Python **3.12+**
- Supported platforms: Windows, Linux, macOS (serial access required)

---

## Installation

Install from PyPI:

```bash
pip install labbench-comm
