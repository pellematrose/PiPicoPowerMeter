# PiPicoPowerMeter
Check out my project site at [hackaday.io](https://hackaday.io/project/189359-pi-pico-power-meter)

![PPPM_view1](https://github.com/pellematrose/PiPicoPowerMeter/blob/main/PPPM_view1.png)

Use the latest Micropython release.
Copy the content of the "RP2040 Pi Pico Code_int_log" folder to the root directory of the RP2040.

## Configuration ##
The PPPM comes pre programmed ready to go to measure up to 26V and 3.2A.

If you need other / better performance on your measured object you can change the settings in the code.
Everything is done in this function:
```python
ina.configure(SHUNT_OHMS, VBUS_RANGE_16, VSHUNT_MAX_2, BADC_12BIT, SADC_12BIT, MODE_SHUNT_BUS_C)
```
Here's how to go:
1. Estimate your maximum voltage
	1. VBUS_RANGE_32 for max. 26V
	2. VBUS_RANGE_16 for max. 16V
2. Estimate the maximum current (with 0.1Ohms shunt) and set the gain
	1. VSHUNT_MAX_1 for range +-0.04mV -> Imax = 0.4A
	2. VSHUNT_MAX_2 for range +-0.08mV -> Imax = 0.8A
	3. VSHUNT_MAX_4 for range +-0.16mV -> Imax = 1.6A
	4. VSHUNT_MAX_8 for range +-0.32mV -> Imax = 3.2A
This will change the value of the LSB and thus change the precision.
The LSB is calculated like this: $LSB = \frac{maxcurrent}{2^{15}}$
If you soldered a different shunt the max. current changes to: $I=\frac{range}{shunt}$
3. Conversion speed (the faster the less accurate) Valid for BADC (Bus voltage)and SADC (Shunt voltage)
	1. BADC_9BIT for 9bit values in 84µs
	2. BADC_10BIT for 10bit values in 148µs
	3. BADC_11BIT for 11bit values in 276µs
	4. BADC_12BIT for 12bit values in 532µs
	5. BADC_2S for 2 Samples in 1.06ms
	6. BADC_4S for 4 Samples in 2.13ms
	7. BADC_8S for 8 Samples in 4.26ms
	8. BADC_16S for 16 Samples in 8.51ms
	9. BADC_32S for 32 Samples in 17.02ms
	10. BADC_64S for 64 Samples in 34.05ms
	11. BADC_128S for 128 Samples in 68.1ms
4. Choose the mode you need
	1. MODE_POWER_DOWN compleatly off
	2. MODE_SHUNT_TRIG only shunt, triggered
	3. MODE_VOLT_TRIG  only voltage, triggered
	4. MODE_SHUNT_BUS_T shunt and voltage, triggered
	5. MODE_ADC_OFF only adc off
	6. MODE_SHUNT_C only shunt, continuous
	7. MODE_VOLT_C only voltage, continuous
	8. MODE_SHUNT_BUS_C shunt and voltage, continuous
