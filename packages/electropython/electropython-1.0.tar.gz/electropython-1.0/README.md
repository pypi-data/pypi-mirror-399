# ElectroPython V1.0

*Easy to use library that can handle Electronic Calculations. Resistor values, Current, voltage and many more calculations included all-in-one package with Basic and Advaced electronic calculations*

> A Simple and Lightweight library that helps you to do calculations with Electronics.

---

## Features

- #### Resistor series - parallel, resistance calculations
- #### ADC - DAC calculations
- #### Time and Frequancy calculations
- #### Easy to Use Functions
- #### Built for Electronics Calculations

---

## Installation

### Install it via pip:

> pip install electropython

---

## Usage

> from electropython import *

### Example usage
```
value = Basic.LED.voltage_drop_across_series(5,2)
print(value)
```

---

## Examples

### Example 1: Calculate resistance with V and I: 
> .Basic.resistance(5,2)

### Example 2: Calculate LED power dissapation with ILED and R:
> Basic.LED.led_pow_diss_resistor(0.02,5)

---

## License
```
This project is licensed under the MIT License – see the [LICENSE](./LICENSE) file for details.
```