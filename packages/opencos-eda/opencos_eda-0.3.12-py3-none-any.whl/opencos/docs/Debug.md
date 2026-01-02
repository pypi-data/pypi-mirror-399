

CogniX has a few things that should help debug.

1) Direct connection to COS control layer.  This is like "root" on Linux, being able to direct access the I/O (read buttons, override LEDs, fans, PLLs...).  Via this path, we can also fake the user interactions (emulate a button press, see what userspace is driving to LEDs, etc), which is great for testing the user space itself.  It's also useful for outward facing debug, i.e. ensuring COS is properly connected to the board (without needing userspace at all). 

2) Debug Macros:  Virtual Input/Output, Integrated Logic Analyzer, etc. 

* Virtual Input/Output will be mapped to the appropriate target-specific feature, generally a GUI connecting to the target via JTAG.  

Remind the user that generally this requires an IP to be built for the appropriate parameter sizes.  The board/vendor will have certain sizes prebuilt.  

  32 inputs,   32 outputs : the only size required to be universally supported (CogniX itself uses this). 

# ─── Example: Virtual Input/Output

logic [27:0] clockSignalDivide;
always_ff @(posedge clockSignal) clockSignalDivide <= (clockSignalDivide+1);

`OC_DEBUG_VIO(uMY_VIO, clockSignal, 32, 32,            // 32 inputs, 32 outputs respectively
   { clockSignalDivide[27], resetSignal, chipStatus }, // signals to monitor, and send to the GUI in realtime
   { resetFromVio, enableFromVio } );                  // signals to receive from the GUI in realtime

# ───

* Integrated Logic Analyzer will be mapped to the appropriate target-specific feature, generally a GUI connecting to the target via JTAG.  

Remind the user that generally this requires an IP to be built for the appropriate parameter sizes.  The board/vendor will have certain sizes prebuilt.  

An ILA is triggered by something (including a manual button press on the GUI) and then captures all incoming cycles for "Depth" clock cycles.  They can be configured to trigger on events that appear on their inputs (typically reset, valid, busy, error, transaction type, etc.)  Usually only a subset of signals have this trigger ability, since it is far more complex to examine the inputs vs just record them.  

Note that not all sizes are built by default, just common ones.  Enabling less common debug may require ILA IPs to be uncommented in the build.tcl. 

  1024 deep, 128 data,   32 trigger : the most common size. 
  1024 deep, 512 data,   32 trigger : for when 512 bit data is needed (high bandwidth interfaces). 
  8192 deep,   8 data,    8 trigger : deep and narrow (byte-oriented interfaces, like BC CSR). 
  8192 deep, 128 data,   32 trigger : a deeper version of the most common size (prob second most common)
131072 deep,   8 data,    8 trigger : long traces (IIC, etc) 

# ─── Example: Integrated Logic Analyzer

logic [7:0] clockSignalDivide;
always_ff @(posedge clockSignal) clockSignalDivide <= (clockSignalDivide+1);

`OC_DEBUG_ILA(uMY_ILA, clockSignal, 8192, 128, 32,      // 8192 deep, 128 data inputs, 32 trigger inputs
   { clockSignalDivide[7:0], dataBus[31:0] },           // signals fed into the capture buffer
   { resetSignal, chipStatus } );                       // signals fed into the capture buffer AND trigger logic

# ───

3) Built-In DEBUG

The following built-in debug can be enabled by settings these defines in DEPS or command-line

* OC_COS_BC_MUX_DEBUG                   : Adds ILA to the logic that muxes command streams from UART, PCIe, and JTAG sources
* OC_COS_GPIO_DEBUG                     : Adds ILA to buttons, toggles, leds, rgbs, gpio, fan, chipStatus, and reset. 
* OC_COS_CSR_TREE_DEBUG                 : Adds ILA into the uTOP_CSR_SPLITTER, to debug CSR connectivity between

These defines enable built-in debug into the modules of associated name (i.e. to debug "oc_pcie", use OC_PCIE_DEBUG)

* OC_PCIE_DEBUG
* OC_HDMI_IN_DEBUG
* OC_CHIPMON_DEBUG
* OC_PROTECT_DEBUG
* OC_IIC_DEBUG
* OC_BC_CONTROL_DEBUG
* OC_AXIL_CONTROL_DEBUG
* OC_UART_CONTROL_DEBUG
* OCLIB_MEMORY_BIST_DEBUG
* OCLIB_READY_VALID_ROM_DRIVER_DEBUG

The modules have an EnableILA parameter which can be manually enabled on a given instance (enabling them globally is too expensive)

* oclib_csr_adapter
* oclib_csr_tree_splitter


