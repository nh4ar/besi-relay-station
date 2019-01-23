# Relay-Nodes
The code for the relay nodes of the BESI system [1].

The relay nodes are implemented on an embedded computer board, the Beaglebone Black. 
The board features an ARM Cortex-A8 processor, 512 MB of RAM, and 4GB of flash memory. 
It provides interfaces like GPIO, ADC, SPI, and I2C for peripheral devices 
and is capable of incorporating both BT and Wi-Fi connectivity. 
The processor runs Debian, a Linux-based operating system. 
Each node is equipped with a 32 GB SD card to facilitate data collection for long periods.

a) Relays connect with the Pebble watch using BT. 
Libpebble2 provides implementation of the data logging protocol.
ZeroMQ library is also incorporated for handling data reception. 
The developed processes run in parallel on the relays and store data on the SD card.

b) Each node utilizes its 12-bit ADC channels to sample signals from 
the microphone at 10 kHz and from the temperature sensor at 1 Hz. 
It uses two separate I2C channels for collecting data from the light and 
the humidity/pressure sensors respectively both at 1 Hz. 
Sensing tasks are implemented as parallel independent processes to store data on the SD card.

c) Relay nodes are programmed to perform additional data processing tasks 
on the collected sensor data, like filtering, noise removal from the sensed data, 
temporal synchronization, calibration, and offset adjustments. 
Any new process can be easily implemented without affecting the performance of existing processes.

d) Supervisor, the process manager, runs on each relay to monitor and manage 
the sensing, connectivity, and logging processes. 
New processes can be easily added to the Supervisor watch-list.

e) A relay node connects with the base-station [1] over Wi-Fi. 
Each relay measures some statistical parameters of the collected data 
that represents the status and performance of the sensing system 
and sends that to the base-station at a lower frequency like a ‘Heartbeat’. 
Links between relay nodes and the base-station are used for remote monitoring and maintenance purposes.


<h4>References:</h4>
<ol>
<li cite="https://dl.acm.org/citation.cfm?id=3204117">
Alam, Ridwan, et al. "BESI: reliable and heterogeneous sensing and intervention for in-home health applications." Proceedings of the Second IEEE/ACM International Conference on Connected Health: Applications, Systems and Engineering Technologies. IEEE Press, 2017.
</li>
</ol>
