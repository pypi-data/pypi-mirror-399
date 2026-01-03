"""
Abstraction layer for the GW Instek GPP-series power supplies.

Supports GPP-3060, GPP-6030, GPP-3650.
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any, NamedTuple, cast

import pyvisa
import logging

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())

from pyvisa.resources import Resource as VisaResource

if TYPE_CHECKING:
    from types import TracebackType
    from typing import Literal, Type

RELAY_DELAY = 2.0  # Seconds to wait after relay operations

# --- Data Structures ---
class Measurement(NamedTuple):
    """
    Container for measurement results.

    :param voltage: Measured voltage (V).
    :param current: Measured current (A).
    :param power: Measured power (W).
    """

    voltage: float
    current: float
    power: float

    def __str__(self) -> str:
        """Return a string representation of the measurement."""
        return f"{self.voltage:.4f}V, {self.current:.4f}A, {self.power:.2f}W"


@dataclass
class ProtectionStatus:
    """
    Container for OVP/OCP levels.

    :param ovp_enabled: True if OVP is enabled, False otherwise.
    :param ovp_value: OVP trigger level (V).
    :param ocp_enabled: True if OCP is enabled, False otherwise.
    :param ocp_value: OCP trigger level (A).
    """

    ovp_enabled: bool
    ovp_value: float | None
    ocp_enabled: bool
    ocp_value: float | None

    def __str__(self) -> str:
        """Return a string representation of the protection status."""
        return (
            f"OVP: {self.ovp_enabled} @ {self.ovp_value}V | "
            f"OCP: {self.ocp_enabled} @ {self.ocp_value}A"
        )


@dataclass(frozen=True)
class ChannelLimits:
    """
    Hardware limits for a specific channel. Values depend on the GPP model.

    :param max_voltage: Maximum allowable voltage setting (V).
    :param max_current: Maximum allowable current setting (A).
    """

    max_voltage: float
    max_current: float


class ChannelMode(Enum):
    """Operating modes for the power supply channels."""

    SOURCE = "SOURCE"
    LOAD_CC = "LOAD_CC"
    LOAD_CV = "LOAD_CV"
    LOAD_CR = "LOAD_CR"

    def __repr__(self):
        return f"ChannelMode.{self.name}"

    def __str__(self):
        return self.name


class TrackingMode(Enum):
    """Tracking modes for combining channels."""

    INDEPENDENT = 0
    SERIES = 1  # only supported in SOURCE mode
    PARALLEL = 2  # only supported in SOURCE mode

    def __repr__(self):
        return f"TrackingMode.{self.name}"

    def __str__(self):
        return self.name

class Terminal(Enum):
    """Modes for routing to the Front and Rear terminals."""

    FRONT = "FRONT"
    REAR = "REAR"

# --- Channel Classes ---
class ChannelBase(ABC):
    """Base class for all channels (CH1, CH2, CH3)."""

    def __init__(self, parent: "GPP", index: int):
        """
        Initialize the channel.

        :param parent: The GPP instance controlling this channel.
        :param index: The channel number (1, 2, or 3).
        """
        self._parent = parent
        self.index = index

    def _write(self, cmd: str) -> None:
        """Execute a pyvisa `write` command."""
        self._parent.write(cmd)

    def _query(self, cmd: str) -> str:
        """Execute a pyvisa `query` command."""
        return self._parent.query(cmd)

    def enable(self) -> None:  
        """Turn the output of this channel on."""
        self._write(f":OUTPut{self.index}:STATe ON")

    def disable(self) -> None:  
        """Turn the output of this channel off."""
        self._write(f":OUTPut{self.index}:STATe OFF")

    def set_output(self, state: bool) -> None:  
        """
        Set the output state on or off.

        :param state: True or 1 for ON; False or 0 for OFF.
        """
        self._write(f":OUTPut{self.index}:STATe {int(state)}")

    def is_enabled(self) -> bool:  
        """
        Query the output state.

        :return: True if output is ON, False otherwise.
        """
        return self._query(f":OUTPut{self.index}:STATe?").strip() in ("ON", "1")

    @abstractmethod
    def set_voltage(self, voltage: float) -> None:
        """
        Set the source voltage.

        For CH1/CH2: This sets the Output Voltage (Source Mode) or CV Level (Load CV Mode).
        For CH3: This sets the fixed output level (1.8V, 2.5V, 3.3V, 5V)
        :param voltage: Target voltage (V).
        """
        pass

    @abstractmethod
    def set_ovp(self) -> None:
        """
        Enable/disable OVP protection for this channel.

        CH3 has a fixed value.
        """
        pass

    def is_ovp_enabled(self) -> bool:  
        """
        Get the on/off status of the OVP.

        :return: True if OVP is ON, False otherwise.
        """
        return self._query(f":OUTPut{self.index}:OVP:STATe?").strip() in ("ON", "1")

    def get_ovp_level(self) -> float | None:  
        """
        Query the OVP level (V).

        :return: The set OVP level.
        """
        return float(self._query(f":OUTPut{self.index}:OVP?"))


class Channel(ChannelBase):
    """
    Represents fully programmable channels (CH1, CH2).

    with Source/Load modes and advanced protection.
    Includes limit checking.
    """

    MAX_LOAD_POWER_W = 50.0  # Maximum power dissipation in Load mode

    def __init__(self, parent: "GPP", index: int, limits: ChannelLimits):
        """
        Initialize the channel.

        :param parent: The GPP instance.
        :param index: Channel index (1 or 2).
        :param limits: ChannelLimits object defining hardware max values.
        """
        super().__init__(parent, index)
        self.channel_mode: ChannelMode | None = None
        self.tracking_mode: TrackingMode | None = None
        self.limits = limits

    def measure_voltage(self) -> float:  
        """
        Read the actual output voltage.

        :return: Measured voltage in Volts.
        """
        return float(self._query(f":MEASure{self.index}:VOLTage?"))

    def measure_current(self) -> float:  
        """
        Read the actual output current.

        :return: Measured current in Amperes.
        """
        return float(self._query(f":MEASure{self.index}:CURRent?"))

    def measure_power(self) -> float:  
        """
        Read the actual output power.

        :return: Measured power in Watts.
        """
        return float(self._query(f":MEASure{self.index}:POWEr?"))

    def measure(self, wait: float = 0.1) -> Measurement:  
        """
        Read Voltage, Current, and Power.

        :param wait: The time in (s) to wait before measuring.
        :return: Measurement object containing V, I, P.
        """
        if wait > 0:
            time.sleep(wait)
        response = self._query(f":MEASure{self.index}:ALL?")
        try:
            parts = response.split(",")
            if len(parts) != 3:
                raise ValueError(f"Expected 3 values, got {len(parts)}: {response}")
            voltage, current, power = map(float, parts)
            return Measurement(voltage, current, power)

        except ValueError as e:
            raise ValueError(f"Failed to parse measurement response: {e}") from e

    def _check_voltage(self, value: float) -> None:
        if value > self.limits.max_voltage:
            raise ValueError(
                f"Voltage {value}V exceeds channel limit of {self.limits.max_voltage}V"
            )
        if value < 0:
            raise ValueError(f"Voltage cannot be negative: {value}V")

    def _check_current(self, value: float) -> None:
        if value > self.limits.max_current:
            raise ValueError(
                f"Current {value}A exceeds channel limit of {self.limits.max_current}A"
            )
        if value < 0:
            raise ValueError(f"Current cannot be negative: {value}A")

    def set_mode(self, mode: ChannelMode) -> None:
        """
        Set the operating mode of the channel.

        The mode is stored as a class attribute.

        :param mode: The desired GPPMode (SOURCE, LOAD_CC, etc.).
        """
        logger.info(f"Setting CH{self.index} to {mode}...")
        if self.channel_mode == mode:
            logger.debug(f"CH{self.index} already in {mode}. Skipping.")
            return
        match mode:
            case ChannelMode.SOURCE:
                hw_mode = self.get_mode_str().upper()
                if "CC" in hw_mode:
                    self._write(f":LOAD{self.index}:CC OFF")
                elif "CV" in hw_mode:
                    self._write(f":LOAD{self.index}:CV OFF")
                elif "CR" in hw_mode:
                    self._write(f":LOAD{self.index}:CR OFF")
            case ChannelMode.LOAD_CC:
                self._write(f":LOAD{self.index}:CC ON")
            case ChannelMode.LOAD_CV:
                self._write(f":LOAD{self.index}:CV ON")
            case ChannelMode.LOAD_CR:
                self._write(f":LOAD{self.index}:CR ON")
        self.channel_mode = mode
        time.sleep(RELAY_DELAY)  # wait before next commands

    def get_mode_str(self) -> str:
        """
        Query the actual working mode.

        :return: Mode string (e.g., 'SER', 'PAR', 'IND', 'CV', 'CC', 'CR').
        """
        return self._query(f":MODE{self.index}?").strip()

    def get_channel_mode(self) -> ChannelMode:
        """
        Query the channel operating mode.

        :return: ChannelMode
        """
        resp = self.get_mode_str().upper()
        match resp:
            case "SER" | "PAR" | "IND":
                self.channel_mode =  ChannelMode.SOURCE
            case "CV":
                self.channel_mode = ChannelMode.LOAD_CV
            case "CC":
                self.channel_mode = ChannelMode.LOAD_CC
            case "CR":
                self.channel_mode = ChannelMode.LOAD_CR
            case _:
                raise RuntimeError(f"Unexpected ChannelMode response: {resp}")
        return self.channel_mode


    def get_tracking_mode(self) -> TrackingMode:
        """
        Query the channel tracking mode.

        :return: TrackingMode
        """
        resp = self.get_mode_str().upper()
        match resp:
            case "IND" | "CV" | "CC" | "CR":
                self.tracking_mode = TrackingMode.INDEPENDENT
            case "SER":
                self.tracking_mode = TrackingMode.SERIES
            case "PAR":
                self.tracking_mode = TrackingMode.PARALLEL
            case _:
                raise RuntimeError(f"Unexpected TrackingMode response: {resp}")
        return self.tracking_mode


    # --- Settings with Limit Checking ---

    def set_voltage(self, voltage: float) -> None:  
        """
        Set output voltage (Source) or CV level (Load).

        :param voltage: Target voltage (V).
        :raises ValueError: If voltage exceeds hardware limits.
        """
        # if in Load mode, but not CV, setting voltage won't work
        if self.channel_mode in (ChannelMode.LOAD_CC, ChannelMode.LOAD_CR):
            raise RuntimeError(
                f"Cannot set voltage: Channel must be in LOAD_CV mode. "
                f"Current mode: {self.channel_mode.name}. "
                f"Use set_mode(ChannelMode.LOAD_CV) first."
            )
        logger.debug(f"CH{self.index}: Setting voltage to {voltage}V")
        self._check_voltage(voltage)
        self._write(f":SOURce{self.index}:VOLTage {voltage}")

    def get_voltage_setting(self) -> float:
        """
        Get the set voltage.

        :return: Set voltage (V).
        """
        return float(self._query(f":SOURce{self.index}:VOLTage?"))

    def set_current(self, current: float) -> None:  
        """
        Set current limit (Source) or constant current level (Load).

        :param current: Target current (A).
        :raises ValueError: If current exceeds hardware limits.
        """
        # if in Load mode, but not CC, setting current won't work
        if self.channel_mode in (ChannelMode.LOAD_CV, ChannelMode.LOAD_CR):
            raise RuntimeError(
                f"Cannot set current: Channel must be in LOAD_CC mode. "
                f"Current mode: {self.channel_mode.name}. "
                f"Use set_mode(ChannelMode.LOAD_CC) first."
            )

        logger.debug(f"CH{self.index}: Setting current to {current}A")
        self._check_current(current)
        self._write(f":SOURce{self.index}:CURRent {current}")

    def get_current_setting(self) -> float:  
        """
        Get the set current limit level.

        :return: Set current (A).
        """
        return float(self._query(f":SOURce{self.index}:CURRent?"))

    def current_limit_reached(self) -> bool:  
        """
        Return True if the current limit has been reached.

        NOTE: At output off or Load mode, the return value is 0.
        """
        return bool(int(self._query(f":SOURce{self.index}:CURRent:LIMit:STATe?").strip()))

    def set_resistance(self, resistance: float) -> None:  
        """
        Set the resistance level for Load mode.

        :param resistance: Target resistance (1 Ω - 1000 Ω).
        :raises ValueError: If resistance is out of range.
        """
        if self.channel_mode != ChannelMode.LOAD_CR:
            raise RuntimeError(
                f"Cannot set resistance: Channel must be in LOAD_CR mode. "
                f"Current mode: {self.channel_mode.name}. "
                f"Use set_mode(ChannelMode.LOAD_CR) first."
            )
        logger.debug(f"CH{self.index}: Setting resistance to {resistance}Ω")
        if not (1 <= resistance <= 1000):
            raise ValueError("Resistance must be between 1 and 1000 Ohms")
        if self.channel_mode == ChannelMode.SOURCE:
            self._write(f":SOURce{self.index}:RESistor {resistance}")
        else:
            self._write(f":LOAD{self.index}:RESistor {resistance}")

    def get_resistance_setting(self) -> float:   #
        """
        Get the set resistance for Source or Load mode.

        :return: Set resistance (Ω).
        """
        if self.channel_mode == ChannelMode.SOURCE:
            return float(self._query(f":SOURce{self.index}:RESistor?"))
        return float(self._query(f":LOAD{self.index}:RESistor?"))

    # --- Protection with Limit Checking ---

    def set_ovp(self, level: float | None = None, enable: bool = True) -> None:  
        """
        Set overvoltage protection level and state.

        :param level: OVP trigger level (V). Optional if just enabling/disabling.
        :param enable: Whether to enable OVP immediately (default True).
        :raises ValueError: If the level is provided but exceeds hardware limits.
        """
        # If a level is given, validate and set it
        if level is not None:
            self._check_voltage(level)
            self._write(f":OUTPut{self.index}:OVP {level}")

        # Set the state
        self._write(f":OUTPut{self.index}:OVP:STATe {'ON' if enable else 'OFF'}")

    def set_ocp(self, level: float | None = None, enable: bool = True) -> None:  
        """
        Set overcurrent protection level and state.

        :param level: OCP trigger level (A). Optional if just enabling/disabling.
        :param enable: Whether to enable OCP immediately (default True).
        :raises ValueError: If the level is provided but exceeds hardware limits.
        """
        # If a level is given, validate and set it
        if level is not None:
            self._check_current(level)
            self._write(f":OUTPut{self.index}:OCP {level}")

        # Set the state
        self._write(f":OUTPut{self.index}:OCP:STATe {'ON' if enable else 'OFF'}")

    def get_protection_status(self) -> ProtectionStatus:
        """Get the current OVP and OCP status."""
        ovp_enabled = self._query(f":OUTPut{self.index}:OVP:STATe?").strip() in ("ON", "1")
        ocp_enabled = self._query(f":OUTPut{self.index}:OCP:STATe?").strip() in ("ON", "1")
        ovp_level = float(self._query(f":OUTPut{self.index}:OVP?"))
        ocp_level = float(self._query(f":OUTPut{self.index}:OCP?"))
        return ProtectionStatus(ovp_enabled, ovp_level, ocp_enabled, ocp_level)


class Channel3(ChannelBase):
    """
    Represents CH3.

    Inherits all basic Output/Measurement methods.
    Supports basic voltage settings.
    """

    def set_ovp(self, enable: bool = True) -> None:  
        """Enable or disable overvoltage protection for CH3."""
        self._write(f":OUTPut3:OVP:STATe {int(enable)}")

    def set_voltage(self, voltage: float) -> None:  
        """
        Set CH3 voltage. Supported voltages: 1.8V, 2.5V, 3.3V, 5V.

        :param voltage: Target voltage in Volts.
        """
        logger.debug(f"CH{self.index}: Setting voltage to {voltage}V")
        if voltage not in (1.8, 2.5, 3.3, 5.0):
            raise ValueError(f"Voltage {voltage}V is not supported for CH3")
        self._write(f":SOURce3:VOLTage {voltage}")


# --- Main Instrument Classes ---


class GPP:
    """
    Generic Base Class for GW-Instek GPP Series.

    Usage:
        with GPP[model_name](params) as psu:
            ...
    """

    def __enter__(self) -> "GPP":
        """Enter the runtime context related to this object."""
        self.connect()
        return self

    def __exit__(
        self,
        exc_type: "Type[BaseException] | None",
        exc: "BaseException | None",
        tb: "TracebackType | None",
    ) -> "Literal[False]":
        """Exit the runtime context related to this object."""
        self.close()
        return False

    def __init__(
        self, address: str, ch_limits: ChannelLimits, baud_rate: int, force_shutdown: bool = True
    ):
        """
        Initialize the GPP instrument.

        :param address: VISA resource address (e.g., 'ASRL3::INSTR').
        :param ch_limits: Limits for Channel 1 and 2.
        :param baud_rate: Baud rate for VISA connection.
        :param force_shutdown: If True, all outputs are turned off after use.
        """
        logger.debug(f"Initializing GPP instance at {address}...")
        self.visa_address: str = address
        self.baud_rate: int = baud_rate
        self.force_shutdown: bool = force_shutdown
        self.rm = pyvisa.ResourceManager()
        self.inst: VisaResource | None = None
        self.tracking_mode: TrackingMode | None = None

        # Initialize Channels with limits
        self.ch1 = Channel(self, 1, ch_limits)
        self.ch2 = Channel(self, 2, ch_limits)
        self.ch3 = Channel3(self, 3)

    def connect(self) -> None:
        """Establish connection to the instrument via PyVISA."""
        logger.info(f"Connecting to GPP at {self.visa_address}...")
        try:
            self.inst = self.rm.open_resource(
                self.visa_address,
                baud_rate=self.baud_rate,
                write_termination="\n",  # TODO check if necessary
                read_termination="\n",
            )
            self.inst.timeout = 5000
            idn = self.query("*IDN?")
            logger.info(f"Successfully connected to: {idn.strip()}")
            self.write("*CLS") # Clears all the event registers
            self.get_channel_modes()
            self.get_tracking_mode()
        except Exception as e:
            logger.error(f"Failed to connect to GPP at {self.visa_address}: {e}")
            raise

    def get_channel_modes(self) -> tuple[ChannelMode, ChannelMode]:
        """Get the channel modes for ch1/ch2."""
        return self.ch1.get_channel_mode(), self.ch2.get_channel_mode()

    def get_tracking_mode(self) -> TrackingMode:
        """Get the tracking mode for the psu."""
        self.tracking_mode = self.ch1.get_tracking_mode()
        return self.tracking_mode


    def write(self, cmd: str) -> None:
        """Write an SCPI command to the instrument."""
        if self.inst:
            logger.debug(f"WRITE: {cmd}")
            cast(Any, self.inst).write(cmd)  # cast for type issues

    def query(self, cmd: str) -> str | Any:
        """Write an SCPI command and reads the response."""
        if self.inst:
            logger.debug(f"QUERY: {cmd}")
            response = cast(Any, self.inst).query(cmd)
            logger.debug(f"RESPONSE: {response.strip()}")
            return response
        return ""

    def close(self) -> None:
        """Close the VISA connection."""
        if self.inst:
            try:
                if self.force_shutdown:
                    self.disable_all_outputs()
                self.inst.close()
            except Exception as e:
                logger.error(f"Failed to close GPP connection: {e}")
                raise
            finally:
                self.inst = None
        logger.info("Successfully disconnected.")

    # --- System Commands ---

    def reset(self) -> None:
        """Reset the instrument to factory default output settings (*RST)."""
        logger.info("Resetting instrument...")
        self.write("*RST")
        time.sleep(RELAY_DELAY) # give time to reset

    def get_error(self) -> str:
        """
        Read the last error from the error queue.

        :return: Error string.
        """
        return self.query(":SYSTem:ERRor?").strip()

    def enable_all_outputs(self) -> None:  
        """Turn the output for all channels on."""
        logger.info("Enabling all outputs.")
        self.write(":ALLOUTON")

    def disable_all_outputs(self) -> None:  
        """Turn the output for all channels off."""
        logger.info("Disabling all outputs.")
        self.write(":ALLOUTOFF")

    def set_terminals(self, terminal: Terminal) -> None:  
        """
        Route the output to the specified terminal set.

        :param terminal: 'FRONT' or 'REAR'
        """
        self.write(f":ROUTe:TERMinals {terminal.value}")

    def select_front_terminals(self) -> None:
        """Convenience method: route to the front terminal set."""
        self.set_terminals(Terminal.FRONT)

    def select_rear_terminals(self) -> None:
        """Convenience method: route to the rear terminal set."""
        self.set_terminals(Terminal.REAR)

    def get_terminals(self) -> Terminal:
        """
        Query the current output terminal routing.

        :return: Current terminal selection
        """
        resp = self.query(":ROUTe:TERMinals?").strip().upper()
        try:
            return Terminal(resp)
        except ValueError:
            raise RuntimeError(f"Unexpected terminal response: {resp}")

    def set_tracking_mode(self, mode: TrackingMode) -> None:  
        """
        Set the tracking mode between Independent, Series, and Parallel.

        CAUTION: This changes the wiring configuration physically (via relays).

        :param mode: Desired TrackingMode.
        """
        if mode in (TrackingMode.SERIES, TrackingMode.PARALLEL):
            # Must be in SOURCE mode for series/parallel
            for ch in (self.ch1, self.ch2):
                if ch.get_channel_mode() != ChannelMode.SOURCE:
                    logger.warning(f"CH{ch.index} not in SOURCE mode, switching...")
                    self.ch1.set_mode(ChannelMode.SOURCE)
        logger.info(f"Setting tracking mode to {mode}...")
        self.write(f"TRACK{mode.value}")
        time.sleep(RELAY_DELAY) # give time to settle

    def beep(self, state: bool) -> None:
        """
        Control the system beeper.

        :param state: True to enable, False to disable.
        """
        self.write(f":SYSTem:BEEPer:STATe {'ON' if state else 'OFF'}")

    def lock(self) -> None:
        """Enable remote control lock (Remote mode)."""
        self.write(":SYSTem:REMote")

    def local(self) -> None:
        """Return control to the front panel (Local mode)."""
        self.write(":SYSTem:LOCal")

    def save_memory(self, location: int) -> None:
        """
        Save the current setup to memory.

        :param location: Memory location (0-9).
        :raises ValueError: If the location is out of range.
        """
        if not 0 <= location <= 9:
            raise ValueError("Memory location must be 0-9")
        self.write(f"*SAV {location}")

    def recall_memory(self, location: int) -> None:
        """
        Recall setup from memory.

        :param location: Memory location (0-9).
        :raises ValueError: If the location is out of range.
        """
        if not 0 <= location <= 9:
            raise ValueError("Memory location must be 0-9")
        self.write(f"*RCL {location}")


class GPP3060(GPP):
    """
    GPP-3060 PSU.

    30V / 6A per channel (Setting range approx 32V / 6.2A).
    """

    def __init__(
        self,
        address: str,
        baud_rate: int = 115200,
        **kwargs: "Any",
    ):
        """
        Initialize the GPP-3060 instrument.

        :param address: VISA resource address.
        :param baud_rate: Baud rate for VISA connection.
        :param kwargs: Additional arguments for GPP base class.
        """
        super().__init__(address, ChannelLimits(32.0, 6.2), baud_rate, **kwargs)


class GPP6030(GPP):
    """
    GPP-6030 PSU.

    60V / 3A per channel (Setting range approx 62V / 3.2A).
    """

    def __init__(
        self,
        address: str,
        baud_rate: int = 115200,
        **kwargs: "Any",
    ):
        """
        Initialize the GPP-6030 instrument.

        :param address: VISA resource address.
        :param baud_rate: Baud rate for VISA connection.
        :param kwargs: Additional arguments for GPP base class.
        """
        super().__init__(address, ChannelLimits(64.0, 3.1), baud_rate, **kwargs)


class GPP3650(GPP):
    """
    GPP-3650 PSU.

    36V / 5A per channel (Setting range approx 38V / 5.2A).
    """

    def __init__(
        self,
        address: str,
        baud_rate: int = 115200,
        **kwargs: "Any",
    ):
        """
        Initialize the GPP-3650 instrument.

        :param address: VISA resource address.
        :param baud_rate: Baud rate for VISA connection.
        :param kwargs: Additional arguments for GPP base class.
        """
        super().__init__(
            address,
            ChannelLimits(38.0, 5.1),
            baud_rate,
            **kwargs,
        )
