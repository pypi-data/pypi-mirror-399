class Basic():

    def resistance(V: float | int = None, I: float | int  = None):
        V = float(V)
        I = float(I)
        R = V / I
        return R

    def current(V: float | int  = None, R: float | int = None):
        V = float(V)
        R = float(R)
        I = V / R
        return I

    def voltage(I: float | int = None , R: float | int = None):
        V = I * R
        return V

    def power(V: float | int = None, I: float | int = None, R: float | int = None):
        if V and I and R != None:
            raise ValueError("Only 2 parameters can be inserted")
        if V and I != None:
            P = V * I
            return P
        if I and R != None:
            P = (I*I) * R
            return P
        if V and R != None:
            P = (V*V) / R
            return P

    class Resistor():
        def series(*args: float | int ):
            Rtotal = sum(args)
            return Rtotal

        def parallel(*args: float | int):
            R = []
            values = args
            for i in values:
                R.append(1/i)
            Total = sum(R)
            Rtotal = 1/Total
            return Rtotal

        def voltage_divider(Vin: float | int, R1: float | int, R2: float | int):
            Vout = Vin * (R2 / ( R1 + R2 ))
            return Vout

    class Capacitor():
        def parallel(*args):
            Ctotal = sum(args)
            return Ctotal

        def series(*args):
            C = []
            values = args
            for i in values:
                C.append(1 / i)
            Total = sum(C)
            Ctotal = 1 / Total
            return Ctotal

    class LED():
        def led_currunt_limit(Vsupply: float = None, Vled: float = None, Iled: float = None):
            R = (Vsupply - Vled) / Iled
            return R

        def led_pow_diss_resistor(ILED: float | int, R: float | int):
            P = (ILED*ILED) * R
            return P

        def led_pow_cons(Vled: float | int, Iled: float | int):
            Pled = Vled * Iled
            return Pled

        def voltage_drop_across_series(Vled: float | int, LEDnum: float | int):
            Vtotal = Vled * LEDnum
            return Vtotal

    class Power():
        def linear_regulator_power_loss(Vin: float | int, Vout: float | int, I: float | int):
            Ploss = -(Vin - Vout) * I
            return Ploss

        def regulator_effeciancy(Vin: float | int, Vout: float | int):
            n = (Vout/Vin) * 100
            return n

    class Battery():
        def battery_life(CapacitymAh: float | int ,CurrentmA: float | int):
            t = CapacitymAh / CurrentmA
            return t

class Advanced():
    class Time_Fequancy():
        def RC_tconst(R: float | int, C: float | int):
            t = R * C
            return t

        def frequancy(T: float | int):
            f = 1 / T
            return f

        def pwm_duty_cycle(ton: float | int,T: float | int):
            duty = (ton / T) * 100
            return duty

    class Capacitor():
        def capacitor_charge_discharge(Vmax: float | int,t: float | int, R: float | int, C: float | int):
            e = 2.718281828459045
            Vt = Vmax * (1 - e ** (-t / (R * C )))
            return Vt

    class ADC_DAC():
        def ADC_res(Vref: float | int, n: float | int):
            Resolution = Vref / (2**n)
            return Resolution

        def ADC_voltage(ADC: float | int, Vref: float | int, n: float | int):
            V = ADC * (Vref / (2**n - 1))
            return V

        def Voltage_to_ADC(V: float | int, Vref: float | int, n: float | int):
            ADC = V * ((2**n - 1) / Vref)
            return ADC

    class Digital_Signal():
        def pullup_resistor_current(V: float | int, R: float | int):
            I = V / R
            return I

        def debounce_RC_filter(R: float | int, C: float | int):
            pi = 3.141592653589793
            fc = 1 / (2 * pi * R * C)
            return fc


