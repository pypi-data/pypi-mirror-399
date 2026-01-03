"""
Python bindings for the C++ orcaSDK
"""

from __future__ import annotations
import typing

__all__ = [
    "Actuator",
    "ConstF",
    "Damper",
    "ForceMode",
    "HapticEffect",
    "HapticMode",
    "Inertia",
    "KinematicMode",
    "MessagePriority",
    "MotorMode",
    "OrcaError",
    "OrcaResultInt16",
    "OrcaResultInt32",
    "OrcaResultList",
    "OrcaResultMotorMode",
    "OrcaResultUInt16",
    "Osc0",
    "Osc1",
    "OscillatorType",
    "PositionMode",
    "Pulse",
    "Sine",
    "SleepMode",
    "Spring0",
    "Spring1",
    "Spring2",
    "SpringCoupling",
    "StreamData",
    "both",
    "important",
    "not_important",
    "positive",
]

class Actuator:
    """Abstraction representing an ORCA series linear motor."""

    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    
    def __init__(self, name: str = "", modbus_server_address: int = 1) -> None:
        """Constructs an actuator object.

        :param str name: The name of the actuator, also available through the public member variable Actuator.name.
        :param int modbus_server_address: The modbus server address. Defaults to 1.
        """
        ...

    def begin_serial_logging(self, log_name: str) -> OrcaError:
        """Begins logging serial communication to a file, between this application and the motor.

        :param str log_name: The name of the file to be written to. Assumes relative path of the built executable file.
        """
        ...

    def clear_errors(self) -> OrcaError:
        """Clears the motor's active errors. If the condition causing the errors remains, the errors will appear immediately again."""
        ...

    def close_serial_port(self) -> None:
        """Closes open serial ports, releasing all associated handles."""
        ...

    def disable_stream(self) -> None:
        """Disables command streaming with the ORCA. See enable_stream()"""
        ...

    def enable_haptic_effects(self, effects: int) -> OrcaError:
        """Sets the haptic effect to enabled or disabled according to the input bits.

        :param int effects: The bitmask representing which haptic effects to enable. This value is a bitwise combination of HapticEffect enum values.

        Note:
            Refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.
        """
        ...

    def enable_stream(self) -> None:
        """Enables command streaming with the ORCA.

        Command streaming is the main form of asynchronous communication with the Orca.
        When enabled, the motor object automatically injects command stream messages when Actuator.run() is called, unless the object is waiting on an active message.
        Returned data is stored in the public stream_cache member of type StreamData.

        See also :func:`Actuator.get_stream_data`

        Note:
            See the ORCA Series Modbus User Guide, ORCA-specific Function Codes section for details on command streaming.
        """
        ...

    def get_errors(self) -> OrcaResultUInt16:
        """Returns the bitmask representing the motor's active errors.

        :return: Bitmask representing the motor's active errors.

        Note:
            To check for a specific error, a bitwise AND can be combined with the value of the error of interest.
            See the ORCA Reference Manual, Errors: Active and Latched Error Registers, for further details on error types.
        """
        ...

    def get_force_mN(self) -> OrcaResultInt32:
        """Returns the total amount of force sensed by the motor.

        :return: Force in millinewtons.
        """
        ...

    def get_latched_errors(self) -> OrcaResultUInt16:
        """Returns all errors that have been encountered since the last time the errors were manually cleared."""
        ...

    def get_major_version(self) -> OrcaResultUInt16:
        """Returns the firmware's major version.

        :return: Firmware's major version.
        """
        ...

    def get_mode(self) -> OrcaResultMotorMode:
        """Requests the current mode of operation from the motor.

        :return: The ORCA's current mode of operation.
        """
        ...

    def get_position_um(self) -> OrcaResultInt32:
        """Returns the position of the motor's shaft in micrometers. The position is based on the distance from the zero position.

        :return: Position in micrometers.
        """
        ...

    def get_power_W(self) -> OrcaResultUInt16:
        """Returns the amount of power drawn by the motor, in Watts.

        :return: Power in Watts.
        """
        ...

    def get_release_state(self) -> OrcaResultUInt16:
        """Returns the firmware release state (minor version).

        :return: Firmware's minor version.
        """
        ...

    def get_revision_number(self) -> OrcaResultUInt16:
        """Returns the firmware's revision number.

        :return: Firmware's revision number.
        """
        ...

    def get_serial_number(self) -> OrcaResultInt32:
        """Returns the actuator's serial number.

        :return: The actuator's serial number.
        """
        ...

    def get_stream_data(self) -> StreamData:
        """Provides access to the stream_cache member variable.

        See also :func:`Actuator.enable_stream`

        :return: Returns an object containing the most recently obtained stream cache from the command stream.
        """
        ...

    def get_temperature_C(self) -> OrcaResultUInt16:
        """Returns the motor's temperature, in Celsius, as measured by the motor's onboard sensor.

        :return: The motor's onboard sensor temperature in Celsius.
        """
        ...

    def get_voltage_mV(self) -> OrcaResultUInt16:
        """Returns the motor's voltage, in millivolts, as measured by the motor's onboard sensor.

        :return: The voltage detected by the motor's onboard sensor.
        """
        ...

    @typing.overload
    def open_serial_port(
        self, port_number: int, baud_rate: int = 19200, interframe_delay: int = 2000
    ) -> OrcaError:
        """Opens serial port using port number.

        :param int port_number: The port number of the RS422 cable that connects to the desired device.
        :param int baud_rate: The speed of data transmission between the connected device and the motor, defaults to 19200 bps.
        :param int interframe_delay: The time gap between sending consecutive frames in a sequence of data while streaming, defaults to 2000 microseconds.
        """
        ...

    @typing.overload
    def open_serial_port(
        self, port_path: str, baud_rate: int = 19200, interframe_delay: int = 2000
    ) -> OrcaError:
        """Opens serial port using port path.

        :param str port_path: The file path of the RS422 cable that connects to the desired device.
        :param int baud_rate: The speed of data transmission between the connected device and the motor, defaults to 19200 bps.
        :param int interframe_delay: The time gap between sending consecutive frames in a sequence of data while streaming, defaults to 2000 microseconds.
        """
        ...

    def read_multiple_registers_blocking(
        self,
        reg_start_address: int,
        num_registers: int,
        priority: MessagePriority = ...,
    ) -> OrcaResultList:
        """Reads multiple registers from the motor.

        :param int reg_start_address: The starting register address.
        :param int num_registers: How many registers to read.
        :param MessagePriority priority: Whether the message is high-priority, indicated with a 0, or not_important, indicated with a 1.
        """
        ...

    def read_register_blocking(
        self, reg_address: int, priority: MessagePriority = ...
    ) -> OrcaResultUInt16:
        """Reads a register from the motor.

        :param int reg_address: The register to read.
        :param MessagePriority priority: Whether the message is high-priority, indicated with a 0, or not_important, indicated with a 1.
        """
        ...

    def read_wide_register_blocking(
        self, reg_address: int, priority: MessagePriority = ...
    ) -> OrcaResultInt32:
        """Reads a double-wide (32-bit) register from the motor.

        :param int reg_address: The register to read.
        :param MessagePriority priority: Whether the message is high-priority, indicated with a 0, or not_important, indicated with a 1.
        """
        ...

    def run(self) -> None:
        """Performs command streaming related work with the ORCA.

        Checks for incoming serial data and sends any queued data.
        If communicating with the motor asynchronously, call this function in a regular loop.
        When using a high-speed stream and no messages are queued, this injects stream commands based on the motor mode set by the most recent call to set_mode().
        """
        ...

    def set_constant_force(self, force: int) -> OrcaError:
        """Sets the constant force value in Haptic Mode.

        :param int force: Force in millinewtons.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.
        """
        ...

    def set_constant_force_filter(self, force_filter: int) -> OrcaError:
        """Sets the constant force filter value in Haptic Mode.

        :param int force_filter: Amount to filter the constant force inputs.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.
        """
        ...

    def set_damper(self, damping: int) -> OrcaError:
        """Sets the damping value in Haptic Mode.

        :param int damping: The damping gain, in 4 Ns/mm.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.
        """
        ...

    def set_inertia(self, inertia: int) -> OrcaError:
        """Sets the inertia value in Haptic Mode.

        :param int inertia: The inertia gain, in 64 Ns^2/mm.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.
        """
        ...

    def set_kinematic_motion(
        self,
        id: int,
        position: int,
        time: int,
        delay: int,
        type: int,
        auto_next: int,
        next_id: int = -1,
    ) -> OrcaError:
        """Triggers a kinematic motion, and will run any chained motions. This function will only return a result if the motor is in Kinematic mode.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Kinematic Controller for details.

        :param int id: The ID of the motion to trigger.
        :param int position: The position to start at, in micrometers.
        :param int time: The duration of the motion, in milliseconds.
        :param int delay: The delay following the motion, in milliseconds.
        :param int type: 0 = minimizes power, 1 = maximizes smoothness.
        :param int auto_next: 0 = stop after the current motion executes, 1 = execute the next motion after the current one finishes.
        :param int next_id: Represents the motion that should be completed next, if the previous variable is set to true.
        """
        ...

    def set_max_force(self, max_force: int) -> OrcaError:
        """Sets the maximum force allowed by the motor.

        :param int max_force: Maximum force in millinewtons.
        """
        ...

    def set_max_power(self, set_max_power: int) -> OrcaError:
        """Sets the maximum power allowed by the motor.

        :param int max_power: Maximum power in Watts.
        """
        ...

    def set_max_temp(self, max_temp: int) -> OrcaError:
        """Sets the maximum temperature allowed by the motor.

        :param int max_temp: Maximum temperature in Celsius.
        """
        ...

    def set_mode(self, orca_mode: MotorMode) -> OrcaError:
        """Writes to the ORCA control register to change the motor's mode of operation.
        Also Changes the type of command stream that will be sent during high-speed streaming.
        """
        ...

    def set_osc_effect(
        self,
        osc_id: int,
        amplitude: int,
        frequency_dhz: int,
        duty: int,
        type: OscillatorType,
    ) -> OrcaError:
        """Configures the oscillation effect, based on the provided parameters.

        :param int osc_id: ID of the oscillation effect.
        :param int amplitude: Amplitude of the oscillation effect.
        :param int frequency_dhz: Frequency, in decihertz, of the oscillation effect.
        :param int duty: Duty-cycle of the oscillation effect. Only relevant for pulse type effects.
        :param OscillatorType type: Type of oscillation effect to create. Pulse = 0, is the default,
        """
        ...

    def set_pctrl_tune_softstart(self, t_in_ms: int) -> OrcaError:
        """Sets the fade period when changing the tune of the position controller in miliseconds.

        :param int t_in_ms: Time period in milliseconds.
        """
        ...

    def set_safety_damping(self, max_safety_damping: int) -> OrcaError:
        """Sets the damping gain value to use when communication is interrupted.

        :param int max_safety_damping: The maximum safety damping value.
        """
        ...

    def set_spring_effect(
        self,
        spring_id: int,
        gain: int,
        center: int,
        dead_zone: int = 0,
        saturation: int = 0,
        coupling: SpringCoupling = ...,
    ) -> OrcaError:
        """Configures a spring effect, based on the provided parameters.

        Note:
            Please refer to the ORCA Series Reference Manual, section Controllers: Haptic Controller for details.

        :param int spring_id: The ID of the spring effect to configure.
        :param int gain: The gain amount, or force per distance from spring center, for the spring effect.
        :param int center: The center of the spring effect.
        :param int dead_zone: The radius of the dead zone for the spring. For any position within the radius of the dead zone from the spring center, no spring force will be applied.
        :param int saturation: The maximum force that can be applied by the spring.
        :param SpringCoupling coupling: The direction from the center where the spring force applies. Defaults to SpringCoupling.both
        """
        ...

    def set_streamed_force_mN(self, force: int) -> None:
        """Sets or adjusts the force that the motor exerts when in motor_command stream mode.

        :param int force: The force in millinewtons.
        """
        ...

    def set_streamed_position_um(self, position: int) -> None:
        """Sets or adjusts the position that the motor is aiming for when in motor_command stream mode.

        
            :param int position: The position in micrometers.
        """
        ...

    def time_since_last_response_microseconds(self) -> int:
        """Returns the time, in microseconds, since the last successful message the motor completed.

        
        :return: Time in microseconds since the last message completed successfully.
        """
        ...

    def trigger_kinematic_motion(self, id: int) -> OrcaError:
        """Triggers the start of a kinematic motion, if the motor is in Kinematic mode, including any chained motions.

            :param int id: The ID of the motion to be triggered.
        """
        ...

    def tune_position_controller(
        self, pgain: int, igain: int, dvgain: int, sat: int, dgain: int = 0
    ) -> None:
        """Sets the PID controller tuning values for the motor's position controller.

        Note: The position controller's PID tuning affects the behaviour of the motor in position and kinematic control modes.
        Please refer to the ORCA Series Reference Manual, section Controllers: Position Controller for details.

        :param int pgain: Proportional gain.
        :param int igain: Integral gain.
        :param int dvgain: Derivative gain with respect to velocy.
        :param int sat: Maximum force (set for safety purposes).
        :param int dgain: Derivative gain with respect to error.
        """
        ...

    def update_haptic_stream_effects(self, effects: int) -> None:
        """Update which haptic effects will be set through the motor's command frame.

            :param int effects: The bitmap describing which haptic effects should be enabled or disabled.
        """
        ...

    def write_register_blocking(
        self, reg_address: int, write_data: int, priority: MessagePriority = ...
    ) -> OrcaError:
        """Writes a register value to the motor.

            :param int reg_address: The register address to write to.
            :param int write_data: The data to write to the register (must fit in a 16 bit integer).
            :param MessagePriority priority: Whether the message is high-priority, indicated with a 0, or not_important, indicated with a 1.
        """
        ...

    def write_wide_register_blocking(
        self, reg_address: int, write_data: int, priority: MessagePriority = ...
    ) -> OrcaError:
        """Writes a double-wide (32-bit) register to the motor.

            :param int reg_address: The register address to write to.
            :param int write_data: The data to write to the register.
            :param MessagePriority priority: Whether the message is high-priority - indicated with a 0, or not_important - indicated with a 1.
        """
        ...

    def write_multiple_registers_blocking(
        self, reg_start_address: int, write_data: list[int], priority: MessagePriority = ...
    ) -> OrcaError:
        """Writes a series of registers to the motor.

            :param int reg_start_address: The starting register address.
            :param list[int] write_data: A list containing all the values, in order, to write to the motor.
            :param MessagePriority priority: Whether the message is high-priority, indicated with a 0, or not_important, indicated with a 1.
        """

    def read_write_multiple_registers_blocking(
        self, read_starting_address: int, read_num_registers: int, write_starting_address: int, write_data: list[int], priority: MessagePriority = ...
    ) -> OrcaResultList:
        """Simulataneously reads a set of registers from the device while writing to a set of registers.

            :param int read_starting_address: The starting address to read from.
            :param int read_num_registers: The number of registers to read.
            :param int write_starting_address: The starting address to write to.
            :param list[int] write_data: A list containing all the values, in order, to write to the motor.
            :param MessagePriority priority: Whether the message is high-priority, indicated with a 0, or not_important, indicated with a 1.
        """

    def zero_position(self) -> OrcaError:
        """Sets the motor's zero position to its currently sensed position."""
        ...

    @property
    def name(self) -> str: ...

class HapticEffect:
    """
    Represents a set of predefined haptic effects that can be applied to the motor.
    """

    ConstF: typing.ClassVar[HapticEffect]  # value = <HapticEffect.ConstF: 1>
    """Constant force effect."""
    Damper: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Damper: 16>
    """Damping effect; applies a force opposing the motor's current movement."""
    Inertia: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Inertia: 32>
    """Inertia effect; applies a force to reduce acceleration of the motor."""
    Osc0: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Osc0: 64>
    """Oscillatory effect 0."""
    Osc1: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Osc1: 128>
    """Oscillatory effect 1."""
    Spring0: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Spring0: 2>
    """Spring effect 0."""
    Spring1: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Spring1: 4>
    """Spring effect 1."""
    Spring2: typing.ClassVar[HapticEffect]  # value = <HapticEffect.Spring2: 8>
    """Spring effect 2."""
    __members__: typing.ClassVar[
        dict[str, HapticEffect]
    ]  # value = {'ConstF': <HapticEffect.ConstF: 1>, 'Spring0': <HapticEffect.Spring0: 2>, 'Spring1': <HapticEffect.Spring1: 4>, 'Spring2': <HapticEffect.Spring2: 8>, 'Damper': <HapticEffect.Damper: 16>, 'Inertia': <HapticEffect.Inertia: 32>, 'Osc0': <HapticEffect.Osc0: 64>, 'Osc1': <HapticEffect.Osc1: 128>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class MessagePriority:
    """
    Represents the 'priority level' of a message, indicating whether the SDK should retry the message if it fails to receive a correct response. Messages are marked important by default.
    """

    __members__: typing.ClassVar[
        dict[str, MessagePriority]
    ]  # value = {'important': <MessagePriority.important: 0>, 'not_important': <MessagePriority.not_important: 1>}
    important: typing.ClassVar[
        MessagePriority
    ]  # value = <MessagePriority.important: 0>
    """Will automatically retry failed messages."""
    not_important: typing.ClassVar[
        MessagePriority
    ]  # value = <MessagePriority.not_important: 1>
    """Will not retry failed messages."""
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class MotorMode:
    """
    Represents the operating mode of the motor.
    """

    AutoZeroMode: typing.ClassVar[MotorMode] # value = <MotorMode.AutoZeroMode: 55>
    """Auto Zeroes motor, putting it into a routine that will retract the shaft until reaching a hard stop and set the zero position to that location."""
    ForceMode: typing.ClassVar[MotorMode]  # value = <MotorMode.ForceMode: 2>
    """Uses the force controller to achieve the commanded force."""
    HapticMode: typing.ClassVar[MotorMode]  # value = <MotorMode.HapticMode: 4>
    """Uses the haptic controller to generate force commands."""
    KinematicMode: typing.ClassVar[MotorMode]  # value = <MotorMode.KinematicMode: 5>
    """Uses the kinematic controller to set position targets."""
    PositionMode: typing.ClassVar[MotorMode]  # value = <MotorMode.PositionMode: 3>
    """Calculates and applies force to reach positions based on the configured PID tuning, set point, and current shaft position."""
    SleepMode: typing.ClassVar[MotorMode]  # value = <MotorMode.SleepMode: 1>
    """Force and position commands are ignored. Entering sleep mode will clear persistent errors."""

    __members__: typing.ClassVar[dict[str, MotorMode]]  # value = {'SleepMode': <MotorMode.SleepMode: 1>, 'ForceMode': <MotorMode.ForceMode: 2>, 'PositionMode': <MotorMode.PositionMode: 3>, 'HapticMode': <MotorMode.HapticMode: 4>, 'KinematicMode': <MotorMode.KinematicMode: 5>, <MotorMode.AutoZeroMode: 55>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class OrcaError:
    """To determine if an instance of this type represents an error, convert it to a boolean. If the boolean evalues to true, then an error has occured, whose details can be found through the OrcaError.what() function.
    If the conversion evaluates to false, then no error has occured and the operation that returned this type resulted in a success."""
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __bool__(self) -> bool: 
        """Evaluates to True if an error has occurred."""
        ...
    def __init__(self, failure_type: int, error_message: str = "") -> None: ...
    def __repr__(self) -> str: ...
    def what(self) -> str:
        """The error message. Contains a human-readable account of what went wrong with the transaction, from the perspective of the SDK."""
        ...

class OrcaResultInt16:
    """An OrcaResult object holding a signed 16 bit int."""
    error: OrcaError
    """The error object. Check if this has an error before accessing the value member."""
    value: int
    """The value. Only read if the error member evaluates to false."""
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

class OrcaResultInt32:
    """An OrcaResult object holding a signed 32 bit int."""
    error: OrcaError
    """The error object. Check if this has an error before accessing the value member."""
    value: int
    """The value. Only read if the error member evaluates to false."""
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

class OrcaResultList:
    """An OrcaResult object holding a list of unsigned 16 bit ints."""
    error: OrcaError
    """The error object. Check if this has an error before accessing the value member."""
    value: list[int]
    """The value. Only read if the error member evaluates to false."""
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

class OrcaResultMotorMode:
    """An OrcaResult object holding a MotorMode object."""
    error: OrcaError
    """The error object. Check if this has an error before accessing the value member."""
    value: MotorMode
    """The value. Only read if the error member evaluates to false."""
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

class OrcaResultUInt16:
    """An OrcaResult object holding an unsigned 16 bit int."""
    error: OrcaError
    """The error object. Check if this has an error before accessing the value member."""
    value: int
    """The value. Only read if the error member evaluates to false."""
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

class OscillatorType:
    """Represents the shape of the oscillator waveform."""

    Pulse: typing.ClassVar[OscillatorType]  # value = <OscillatorType.Pulse: 0>
    """Pulse oscillation. Or square wave."""
    Sine: typing.ClassVar[OscillatorType]  # value = <OscillatorType.Sine: 1>
    """Sine wave."""
    Triangle: typing.ClassVar[OscillatorType]  # value = <OscillatorType.Triangle: 2>
    """Triangle wave."""
    Saw: typing.ClassVar[OscillatorType]  # value = <OscillatorType.Saw: 3>
    """Sawtooth wave."""
    __members__: typing.ClassVar[
        dict[str, OscillatorType]
    ]  # value = {'Pulse': <OscillatorType.Pulse: 0>, 'Sine': <OscillatorType.Sine: 1>, 'Triangle ': <OscillatorType.Triangle : 2>, 'Saw  ': <OscillatorType.Saw  : 3>}
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class SpringCoupling:
    """Valid options for Spring Coupling Settings."""

    __members__: typing.ClassVar[
        dict[str, SpringCoupling]
    ]  # value = {'both': <SpringCoupling.both: 0>, 'positive': <SpringCoupling.positive: 1>, 'negative ': <SpringCoupling.negative : 2>}
    both: typing.ClassVar[SpringCoupling]  # value = <SpringCoupling.both: 0>
    """Apply the spring in both directions."""
    positive: typing.ClassVar[SpringCoupling]  # value = <SpringCoupling.positive: 1>
    """Apply the spring only in the positive direction."""
    negative: typing.ClassVar[SpringCoupling]  # value = <SpringCoupling.negative: 2>
    """Apply the spring only in the negative direction."""
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...
    def __eq__(self, other: typing.Any) -> bool: ...
    def __getstate__(self) -> int: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __ne__(self, other: typing.Any) -> bool: ...
    def __repr__(self) -> str: ...
    def __setstate__(self, state: int) -> None: ...
    def __str__(self) -> str: ...
    @property
    def name(self) -> str: ...
    @property
    def value(self) -> int: ...

class StreamData:
    """Contains cached data returned from the motor while command streaming. 
    
    See also :func:`Actuator.enable_stream`"""
    errors: int
    """Active errors."""
    force: int
    """Sensed force."""
    position: int
    """Sensed position."""
    power: int
    """Sensed power draw."""
    temperature: int
    """Motor temperature (coil or board, whatever is higher)."""
    voltage: int
    """Sensed supply voltage."""
    @staticmethod
    def _pybind11_conduit_v1_(*args, **kwargs): ...

ConstF: HapticEffect  # value = <HapticEffect.ConstF: 1>
Damper: HapticEffect  # value = <HapticEffect.Damper: 16>
ForceMode: MotorMode  # value = <MotorMode.ForceMode: 2>
HapticMode: MotorMode  # value = <MotorMode.HapticMode: 4>
Inertia: HapticEffect  # value = <HapticEffect.Inertia: 32>
KinematicMode: MotorMode  # value = <MotorMode.KinematicMode: 5>
Osc0: HapticEffect  # value = <HapticEffect.Osc0: 64>
Osc1: HapticEffect  # value = <HapticEffect.Osc1: 128>
PositionMode: MotorMode  # value = <MotorMode.PositionMode: 3>
Pulse: OscillatorType  # value = <OscillatorType.Pulse: 0>
Sine: OscillatorType  # value = <OscillatorType.Sine: 1>
Triangle: OscillatorType  # value = <OscillatorType.Triangle: 2>
Saw: OscillatorType  # value = <OscillatorType.Saw: 3>
SleepMode: MotorMode  # value = <MotorMode.SleepMode: 1>
Spring0: HapticEffect  # value = <HapticEffect.Spring0: 2>
Spring1: HapticEffect  # value = <HapticEffect.Spring1: 4>
Spring2: HapticEffect  # value = <HapticEffect.Spring2: 8>
both: SpringCoupling  # value = <SpringCoupling.both: 0>
important: MessagePriority  # value = <MessagePriority.important: 0>
not_important: MessagePriority  # value = <MessagePriority.not_important: 1>
positive: SpringCoupling  # value = <SpringCoupling.positive: 1>
negative: SpringCoupling  # value = <SpringCoupling.negative: 2>