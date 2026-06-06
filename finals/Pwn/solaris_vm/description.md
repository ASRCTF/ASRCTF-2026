Challenge Title: Solaris JIT<br>
Author: Chthonic Cream<br>
Description:<br>
The Solaris Space Station relies on high-speed thruster telemetry loops to maintain orbital stability. To maximize efficiency and ensure microsecond responsiveness, the telemetry supervisor uses a custom virtual machine with an active range-analysis JIT optimizer.<br>
<br>
The compiler audit report marks this as a constant-folding integer overflow. Craft large immediate values, force MUL/ADD wraparound during optimization, and use the wrapped bound to pass the stack access verifier before emitting native code.<br>
<br>
Prove them wrong. Break out of the telemetry sandbox and take control of the station.
