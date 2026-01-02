from .SpikeSafeEnums import LoadImpedance, RiseTime

class PulseWidthCorrection:
    """
    Class for calculating optimal pulse width correction for SpikeSafe.
    
    Methods
    -------
    PulseWidthCorrection.get_optimum_pulse_width_correction(spikesafe_model_max_current_amps, set_current_amps, load_impedance, rise_time)
        Returns the optimum pulse width correction value in microseconds formatted as a string with three decimal places
    """

    @staticmethod
    def get_optimum_pulse_width_correction(
        spikesafe_model_max_current_amps: float,
        set_current_amps: float,
        load_impedance: LoadImpedance,
        rise_time: RiseTime
    ) -> str:
        """
        This function returns the optimum correction for the SpikeSafe Pulse Width Adjustment (PWA) algorithm, using a polynomial equation. The polynomial is only evaluated if the set current is below the tested maximum current setting. Above the maximum test current, the function will evaluate the polynomial at the maximum test value. In most cases the pulse width error is small and relatively constant with current at that point. 

        Parameters
        ----------
        spikesafe_model_max_current_amps : float
            Maximum current of the SpikeSafe model.
        set_current_amps : float
            Current to be set on SpikeSafe.
        load_impedance : LoadImpedance
            Load Impedance compensation value. This should be an instance of the LoadImpedance IntEnum from SpikeSafeEnums.
        rise_time : RiseTime
            Rise Time compensation value. This should be an instance of the RiseTime IntEnum from SpikeSafeEnums.
        
        Returns
        -------
        str
            Correction value in microseconds formatted as a string with three decimal places.
        
        Remarks
        -------
        This function assumes the set current is operating on the optimized current range. If operating on the high range with a set current normally programmed on the low range, the correction value will not be optimal. See online specification for range limits.

        Raises
        ------
        ValueError
            If set_current_amps is greater than spikesafe_model_max_current_amps.
        """
        default_correction = "1.250"

        # Test to see if the current is above the model capability
        if set_current_amps > spikesafe_model_max_current_amps:
            raise ValueError(f'Measurement current {set_current_amps}A exceeds SpikeSafe model maximum current capability of {spikesafe_model_max_current_amps}A.')
        
        # Dictionary to store values for different model max currents, arranged by max current of model number. The 9th order coefficient is first.
        model_params = PulseWidthCorrection.__get_optimum_pulse_width_correction_table()
    
        # Check if the given spikesafe_model_max_current_amps is in the model_params, if it is not, just return the default correction
        if spikesafe_model_max_current_amps not in model_params:
            return default_correction
        
        # Determine if we are in the high or low range
        low_current_range_maximum = model_params[spikesafe_model_max_current_amps]['low_current_range_maximum']
        if set_current_amps > low_current_range_maximum:
            current_range = 'HIGH'
        else:
            current_range = 'LOW'

        # Retrieve dictionary
        dictionary = model_params[spikesafe_model_max_current_amps][(current_range, load_impedance, rise_time)]

        # Check if the set current exceeds the max test current, if it does evaluate polynomial at max test current
        if set_current_amps > dictionary['max_test_current']:
            set_current_amps = dictionary['max_test_current']

        # Retrieve the polynomial coefficients for the given conditions, if there is no definition for these conditions, return the default correction value
        try:
            coefficient_data = model_params[spikesafe_model_max_current_amps][(current_range, load_impedance, rise_time)]
            # Extract nested coefficients
            polynomial_coefficients = coefficient_data['coefficients']
        except KeyError:
            return default_correction
        
        # Convert to floats
        polynomial_coefficients = [float(c) for c in polynomial_coefficients]
        
        # Evaluate the polynomial
        correction_value = sum(c * (set_current_amps ** i) for i, c in enumerate(reversed(polynomial_coefficients)))
        
        # If needed, coerce the Pulse Width Correction Value to be within firmware programmable limits
        if correction_value > 50:
            correction_value = 50
        if correction_value < 0: # do not allow negative correction, usually this is caused by polynomial calculation issues
            correction_value = 0

        return f"{correction_value:.3f}"

    @staticmethod
    def __get_optimum_pulse_width_correction_table():
        table = {
            # 50mA model data.
            #
            #   Test date: - This is dummy data
            #   Firmware Versions
            #   Low Range load:
            #   High Range load:
            #
            0.05: {
                'low_current_range_maximum': 0.004,
                ('LOW', LoadImpedance.HIGH, RiseTime.FAST): {
                    'max_test_current': 0.004,
                    'coefficients': [
                        -9.871149607577702e-06,  
                        4.925729768052306e-04,   
                        -1.0513586679354699e-02, 
                        2.535298344948773e-02,   
                        -9.150150198876271e-01,  
                        4.217950150868910e+00,   
                        -1.2236178766013357e+01, 
                        2.159451915110982e+01,   
                        -2.1427844737913496e+01, 
                        1.1371764096320065e+01   
                    ]
                },
                ('LOW', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 0.004,
                    'coefficients': [
                        -9.871149607577702e-06,  
                        4.925729768052306e-04,   
                        -1.0513586679354699e-02, 
                        9.2535298344948773e-01,  
                        -9.150150198876271e-01,  
                        4.217950150868910e+00,   
                        -1.2236178766013357e+01, 
                        2.159451915110982e+01,   
                        -2.1427844737913496e+01, 
                        1.1371764096320065e+01   
                    ]
                },
                ('LOW', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 0.004,
                    'coefficients': [
                        -9.871149607577702e-06,  
                        4.925729768052306e-04,   
                        -1.0513586679354699e-02, 
                        1.2535298344948773e-01,  
                        -9.150150198876271e-01,  
                        9.217950150868910e+00,   
                        -1.2236178766013357e+01,
                        2.159451915110982e+01,   
                        -2.1427844737913496e+01, 
                        1.1371764096320065e+01   
                    ]
                }
            },
            # 500mA model data.
            #
            #   Test date: - 8/15/2024, Low range VL,S tested on 8/19/24
            #   Firmware Versions Vektrex, SpikeSafe Mini, Rev 3.0.7.2, Ch 1: DSP 2.0.52, CPLD C.3, Last Cal Date: 14 AUG 2024, SN: 18015, HwRev: E, Model: MINI-PRF-05-01US
            #   Low Range load: Lumileds small blue LED
            #   High Range load: Lumileds small blue LED
            #
            0.5: {
                'low_current_range_maximum': 0.04,
                # low range coefficients 
                ('LOW', LoadImpedance.HIGH, RiseTime.FAST): {
                    'max_test_current': 0.016,
                    'coefficients': [
                        -2.124104439974309e+20,
                        1.776561551706255e+19,
                        -6.382403472260180e+17,
                        1.288895088356794e+16,
                        -1.608552096044944e+14,
                        1.285614060966992e+12,
                        -6.604629621777224e+09,
                        2.135022289213960e+07,
                        -4.123863980898969e+04,
                        4.317998178356265e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.FAST): {
                    'max_test_current': 0.038,
                    'coefficients': [
                        -2.206889020232475e+17,
                        4.190481500874759e+16,
                        -3.396007891340986e+15,
                        1.533583668399047e+14,
                        -4.227322658809802e+12,
                        7.328105774477026e+10,
                        -7.940404922282956e+08,
                        5.176217824271372e+06,
                        -1.873506462184650e+04,
                        3.308466258103995e+01,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.FAST): {
                    'max_test_current': 0.031,
                    'coefficients': [
                        -7.524152802273400e+17,
                        1.202133960408860e+17,
                        -8.267236980377875e+15,
                        3.203539950428214e+14,
                        -7.688335019080609e+12,
                        1.182522703017928e+11,
                        -1.164709969569115e+09,
                        7.111832081271512e+06,
                        -2.497144116008219e+04,
                        4.407737012708094e+01,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.FAST): {
                    'max_test_current': 0.031,
                    'coefficients': [
                        -1.791755617855699e+18,
                        2.788553708113473e+17,
                        -1.855593007006357e+16,
                        6.898175449735451e+14,
                        -1.571231641035961e+13,
                        2.263640362526625e+11,
                        -2.057015156146311e+09,
                        1.141160206254207e+07,
                        -3.599000281924385e+04,
                        5.672485587883239e+01,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 0.016,
                    'coefficients': [
                        -1.814396751941975e+20,
                        1.446178100024719e+19,
                        -4.963820087939536e+17,
                        9.634568572462926e+15,
                        -1.168537461180945e+14,
                        9.240926898832191e+11,
                        -4.819051846373339e+09,
                        1.629702425467697e+07,
                        -3.376939128226111e+04,
                        3.852434224652870e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.MEDIUM): {
                    'max_test_current': 0.031,
                    'coefficients': [
                        -1.277999231682892e+18,
                        1.990406861318311e+17,
                        -1.327052315794609e+16,
                        4.949744379802502e+14,
                        -1.132708790092439e+13,
                        1.640860242017560e+11,
                        -1.498023917491710e+09,
                        8.307283513355660e+06,
                        -2.581832108313362e+04,
                        3.905046092108660e+01,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.031,
                    'coefficients': [
                        -1.296485828364726e+18,
                        2.039127276754042e+17,
                        -1.375643754631326e+16,
                        5.205355211452806e+14,
                        -1.212687414758681e+13,
                        1.796649583536355e+11,
                        -1.687472061191908e+09,
                        9.696795565966150e+06,
                        -3.148779446525317e+04,
                        5.005735435035513e+01,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.031,
                    'coefficients': [
                        -1.934512161906122e+18,
                        3.010841932165210e+17,
                        -2.003743686496899e+16,
                        7.450613493382062e+14,
                        -1.697663974249525e+13,
                        2.446712469157505e+11,
                        -2.223086906221694e+09,
                        1.230418291193225e+07,
                        -3.847671133569660e+04,
                        5.929510432867392e+01,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 0.016,
                    'coefficients': [
                        -1.714435036686525e+20,
                        1.465236126918560e+19,
                        -5.400881725975538e+17,
                        1.124394154985440e+16,
                        -1.454428773943597e+14,
                        1.211696586666538e+12,
                        -6.521316532020711e+09,
                        2.211675675802868e+07,
                        -4.440643567692902e+04,
                        4.677015416913173e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.SLOW): {
                    'max_test_current': 0.031,
                    'coefficients': [
                        -8.732841386976362e+17,
                        1.377044152883874e+17,
                        -9.311248878627632e+15,
                        3.531150215117591e+14,
                        -8.247851292319105e+12,
                        1.226672928967459e+11,
                        -1.159769557159039e+09,
                        6.740393136538269e+06,
                        -2.226311748735486e+04,
                        3.624828934018751e+01,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.SLOW): {
                    'max_test_current': 0.031,
                    'coefficients': [
                        -1.975451755134529e+18,
                        3.066665149822119e+17,
                        -2.033350048130572e+16,
                        7.520775218883598e+14,
                        -1.700710591978648e+13,
                        2.424586947606402e+11,
                        -2.169040391508505e+09,
                        1.174749616920685e+07,
                        -3.569169715221348e+04,
                        5.319671801924596e+01,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.SLOW): {
                    'max_test_current': 0.031,
                    'coefficients': [
                        -1.629727935355740e+18,
                        2.515205237893737e+17,
                        -1.659462443149780e+16,
                        6.117656244010750e+14,
                        -1.382876913684384e+13,
                        1.980542309338124e+11,
                        -1.794758833485741e+09,
                        9.975786664487300e+06,
                        -3.168065746329150e+04,
                        5.044595231344829e+01,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.02,
                    'coefficients': [
                        -3.367790292853545e+19,
                        3.496090329864526e+18,
                        -1.556420331440899e+17,
                        3.883914724829934e+15,
                        -5.961965973016592e+13,
                        5.819239119802949e+11,
                        -3.612067457570044e+09,
                        1.388551877779093e+07,
                        -3.119761068946101e+04,
                        3.744669684482326e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.031,
                    'coefficients': [
                        -1.119719135937775e+18,
                        1.742087016045205e+17,
                        -1.160724276987695e+16,
                        4.329567483470832e+14,
                        -9.920632105977426e+12,
                        1.441926325822307e+11,
                        -1.325004365462114e+09,
                        7.428638110285422e+06,
                        -2.347670602264593e+04,
                        3.661881951634768e+01,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.031,
                    'coefficients': [
                        -1.592144563994109e+18,
                        2.491536921037580e+17,
                        -1.668431811047595e+16,
                        6.246147499882972e+14,
                        -1.433427616264319e+13,
                        2.080521281390337e+11,
                        -1.902616290289874e+09,
                        1.058893220137188e+07,
                        -3.326531614765420e+04,
                        5.149206524254805e+01,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.037000000000000005,
                    'coefficients': [
                        -2.109877831898894e+17,
                        4.857783118053694e+16,
                        -4.896376165018995e+15,
                        2.832636420852712e+14,
                        -1.035255046478355e+13,
                        2.475459535130649e+11,
                        -3.867503840049191e+09,
                        3.802765661797782e+07,
                        -2.135200333705588e+05,
                        5.254704434803635e+02,
                    ]
                },
                # high range coefficients
                    ('HIGH', LoadImpedance.HIGH, RiseTime.FAST): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        -3.543171344650626e+06,
                        9.507906302587956e+06,
                        -1.099811935887072e+07,
                        7.155825509513956e+06,
                        -2.861571982206451e+06,
                        7.194661167480827e+05,
                        -1.109193031524624e+05,
                        9.559537493913558e+03,
                        -3.471461532440301e+02,
                        5.544760303757805e-01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.FAST): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        3.122886113533613e+07,
                        -9.508307917609058e+07,
                        1.272692749185845e+08,
                        -9.824137458182836e+07,
                        4.817165394438895e+07,
                        -1.555233437856894e+07,
                        3.304557664906801e+06,
                        -4.454450315694725e+05,
                        3.455755234943322e+04,
                        -1.174209759393620e+03,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.FAST): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        3.110741677241822e+07,
                        -9.383331565550502e+07,
                        1.244013793873498e+08,
                        -9.508338438843586e+07,
                        4.614487337745728e+07,
                        -1.473691044419633e+07,
                        3.095240048658997e+06,
                        -4.120582968492735e+05,
                        3.153659462423970e+04,
                        -1.055527769332296e+03,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.FAST): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        -8.800722454325056e+07,
                        2.740627257324715e+08,
                        -3.750248988798726e+08,
                        2.958730476072583e+08,
                        -1.482668170335087e+08,
                        4.892539977303776e+07,
                        -1.062786591683657e+07,
                        1.465078352643161e+06,
                        -1.162696457206007e+05,
                        4.047809018087278e+03,
                    ]
                },
                ('HIGH', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        -5.180827947045477e+06,
                        1.484570788895283e+07,
                        -1.859078938905891e+07,
                        1.334780254157521e+07,
                        -6.054906799818715e+06,
                        1.800432171018487e+06,
                        -3.513137748624423e+05,
                        4.346083572060722e+04,
                        -3.102166702791727e+03,
                        9.885007888855182e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.MEDIUM): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        -7.966890128873179e+06,
                        2.471054794531704e+07,
                        -3.372967236341089e+07,
                        2.660348893217267e+07,
                        -1.336828381363085e+07,
                        4.440936155556028e+06,
                        -9.759015584658376e+05,
                        1.368752956165500e+05,
                        -1.112334521526994e+04,
                        4.002964079623423e+02,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        6.256110667109133e+07,
                        -1.864906767154600e+08,
                        2.444437656175807e+08,
                        -1.848292771396070e+08,
                        8.880123362462324e+07,
                        -2.809928694383751e+07,
                        5.852870588544330e+06,
                        -7.734133788556547e+05,
                        5.880194805053731e+04,
                        -1.957579051176375e+03,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        -8.897254687891397e+07,
                        2.743507529300871e+08,
                        -3.715251314855924e+08,
                        2.898586005305462e+08,
                        -1.435138796296305e+08,
                        4.674309453998300e+07,
                        -1.001126738168626e+07,
                        1.359164580746538e+06,
                        -1.061107752469466e+05,
                        3.630206034622667e+03,
                    ]
                },
                ('HIGH', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        5.045233308534672e+06,
                        -1.650991767416990e+07,
                        2.371512275481151e+07,
                        -1.960868458008595e+07,
                        1.027586138062580e+07,
                        -3.536166123709079e+06,
                        7.983938477608240e+05,
                        -1.139589557143931e+05,
                        9.324607313681116e+03,
                        -3.319486044705320e+02,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.SLOW): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        2.979254104638709e+06,
                        -8.962012952213805e+06,
                        1.183792206449256e+07,
                        -8.987770042015584e+06,
                        4.307153501112441e+06,
                        -1.344758867344345e+06,
                        2.718088156198438e+05,
                        -3.399016502156199e+04,
                        2.352617610047517e+03,
                        -6.583150908185677e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.SLOW): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        -3.086152576193491e+07,
                        9.809792054490770e+07,
                        -1.372956126722852e+08,
                        1.110177660720153e+08,
                        -5.714165528265703e+07,
                        1.940979929961511e+07,
                        -4.349961280397045e+06,
                        6.200658793786113e+05,
                        -5.100028057720975e+04,
                        1.844866714580662e+03,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.SLOW): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        6.192003150186326e+07,
                        -1.924808402960538e+08,
                        2.631205164049934e+08,
                        -2.074864811824805e+08,
                        1.039562524807664e+08,
                        -3.430071098179015e+07,
                        7.449769548637194e+06,
                        -1.026618290259872e+06,
                        8.143000065841146e+04,
                        -2.830845083767870e+03,
                    ]
                },
                    ('HIGH', LoadImpedance.HIGH, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        3.730768239135603e+07,
                        -1.124171722590155e+08,
                        1.490213262297989e+08,
                        -1.140151094128413e+08,
                        5.546065394114193e+07,
                        -1.777961023228553e+07,
                        3.754841754953764e+06,
                        -5.035352959506935e+05,
                        3.889397111340240e+04,
                        -1.316865163875197e+03,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        -2.939298433089579e+06,
                        9.201923295795396e+06,
                        -1.263515994738116e+07,
                        1.000357942001328e+07,
                        -5.042453986352665e+06,
                        1.681798690757767e+06,
                        -3.719648045204118e+05,
                        5.270770117292427e+04,
                        -4.349007643711367e+03,
                        1.604922480054188e+02,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        1.917854284721523e+07,
                        -5.936039083194588e+07,
                        8.079500381042457e+07,
                        -6.342256282520299e+07,
                        3.161745014624762e+07,
                        -1.037249960626658e+07,
                        2.237616191937922e+06,
                        -3.058746148906901e+05,
                        2.402658820333041e+04,
                        -8.246556060619685e+02,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.47100000000000003,
                    'coefficients': [
                        2.843842582151349e+07,
                        -9.021326953780043e+07,
                        1.260319309495063e+08,
                        -1.016735559133777e+08,
                        5.214797115824099e+07,
                        -1.761886796457781e+07,
                        3.918206496699629e+06,
                        -5.526933443560424e+05,
                        4.484753905625143e+04,
                        -1.593080252649353e+03,
                    ]
                }
            },
            # 4 A model data.
            #
            #   Copied from 5A data
            #
            4: {
                'low_current_range_maximum': 0.2,
                # low range coefficients 
                ('LOW', LoadImpedance.HIGH, RiseTime.FAST): {
                    'max_test_current': 0.060000000000000005,
                    'coefficients': [
                        -1.346050118059396e+16,
                        3.971534786952294e+15,
                        -4.980098335463114e+14,
                        3.460216623460693e+13,
                        -1.456545349194948e+12,
                        3.817592064574935e+10,
                        -6.174266512522117e+08,
                        5.915050742899591e+06,
                        -3.102236860315020e+04,
                        7.819161798723077e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.FAST): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -3.385380854906639e+14,
                        1.643183713621474e+14,
                        -3.382641101529811e+13,
                        3.847055753023389e+12,
                        -2.638788980780445e+11,
                        1.118840276575873e+10,
                        -2.890603995096654e+08,
                        4.320420370795928e+06,
                        -3.368768110398375e+04,
                        1.136077638452640e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.FAST): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -1.366154386470470e+12,
                        1.247672877767095e+12,
                        -4.829837139584489e+11,
                        1.032162555557400e+11,
                        -1.329113838273269e+10,
                        1.056620865834404e+09,
                        -5.109029164371984e+07,
                        1.424808706025186e+06,
                        -2.060017659503259e+04,
                        1.267837082401824e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.FAST): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -5.051983701613303e+11,
                        4.769237607886802e+11,
                        -1.921403336973865e+11,
                        4.312051643729930e+10,
                        -5.903090893901936e+09,
                        5.076192523318032e+08,
                        -2.723543613166079e+07,
                        8.769494762265848e+05,
                        -1.564330815484816e+04,
                        1.340839849754989e+02,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 0.060000000000000005,
                    'coefficients': [
                        -2.482043974277968e+16,
                        7.297739202206802e+15,
                        -9.115547160264341e+14,
                        6.305010714330649e+13,
                        -2.638912108943889e+12,
                        6.860300585411143e+10,
                        -1.094576420702193e+09,
                        1.021404706407295e+07,
                        -5.051832151781477e+04,
                        1.099597312160674e+02,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.MEDIUM): {
                    'max_test_current': 0.08,
                    'coefficients': [
                        -2.314938982959861e+15,
                        9.015753718365151e+14,
                        -1.490413459903048e+14,
                        1.362722133064804e+13,
                        -7.527121359037218e+11,
                        2.576545145752576e+10,
                        -5.396622136324562e+08,
                        6.589274392312742e+06,
                        -4.262729711194123e+04,
                        1.233402266611764e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -9.742352913262319e+11,
                        8.951419097953198e+11,
                        -3.490470424374945e+11,
                        7.526250547160979e+10,
                        -9.801089245600431e+09,
                        7.906251205509747e+08,
                        -3.899064785649614e+07,
                        1.118402112167394e+06,
                        -1.688568301737710e+04,
                        1.119632863643297e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -4.282396839826701e+11,
                        4.069594731657604e+11,
                        -1.651274345885627e+11,
                        3.735050265367628e+10,
                        -5.159224865401846e+09,
                        4.484585543093485e+08,
                        -2.439688724146008e+07,
                        8.006865389544981e+05,
                        -1.468335902602957e+04,
                        1.307658146673328e+02,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -1.967619869770918e+14,
                        9.585565939636867e+13,
                        -1.982375308289848e+13,
                        2.267822444287320e+12,
                        -1.567533363945053e+11,
                        6.715004759042689e+09,
                        -1.759643963215615e+08,
                        2.683287311601079e+06,
                        -2.152403288411121e+04,
                        7.544428618503153e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.SLOW): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -3.178100781253410e+14,
                        1.541299286750301e+14,
                        -3.170869474335161e+13,
                        3.605096304166213e+12,
                        -2.473473473776891e+11,
                        1.050040096211649e+10,
                        -2.720652153510821e+08,
                        4.089308071726532e+06,
                        -3.221297119291520e+04,
                        1.108810028038511e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.SLOW): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -1.143916315864790e+12,
                        1.047618282049638e+12,
                        -4.068578792650527e+11,
                        8.728422848156628e+10,
                        -1.129304186871249e+10,
                        9.032641626666660e+08,
                        -4.404075424930316e+07,
                        1.243616055024067e+06,
                        -1.836763528370090e+04,
                        1.181230657421344e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.SLOW): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -2.747939900618490e+11,
                        2.682319370311515e+11,
                        -1.121741756153237e+11,
                        2.625290719004314e+10,
                        -3.768791716393783e+09,
                        3.421685070216345e+08,
                        -1.954778715809422e+07,
                        6.774097415824316e+05,
                        -1.318209634318136e+04,
                        1.250394517343262e+02,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -2.405549732240165e+14,
                        1.167837640019307e+14,
                        -2.404796138930253e+13,
                        2.736055908650182e+12,
                        -1.877743338308835e+11,
                        7.967120635474062e+09,
                        -2.059951582855897e+08,
                        3.080109945253149e+06,
                        -2.397196269160914e+04,
                        8.021857408474315e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -2.963332214847434e+14,
                        1.440766702909983e+14,
                        -2.971768086027597e+13,
                        3.387619944142139e+12,
                        -2.330225378964038e+11,
                        9.915737481846994e+09,
                        -2.574481347348072e+08,
                        3.877538006027492e+06,
                        -3.068340576420075e+04,
                        1.077748735609755e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -1.167590532457576e+12,
                        1.069095240602807e+12,
                        -4.151373971944171e+11,
                        8.905111590047061e+10,
                        -1.152069289205055e+10,
                        9.213523976520650e+08,
                        -4.490655882375965e+07,
                        1.266781046016748e+06,
                        -1.866173714537442e+04,
                        1.194480769356166e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -2.712582002954995e+11,
                        2.653820872982494e+11,
                        -1.112890555050700e+11,
                        2.613166419509599e+10,
                        -3.765578801089605e+09,
                        3.432550061312052e+08,
                        -1.968253279700688e+07,
                        6.836194382782832e+05,
                        -1.329026644680350e+04,
                        1.255026439537286e+02,
                    ]
                },
                # high range coefficients
                    ('HIGH', LoadImpedance.HIGH, RiseTime.FAST): {
                    'max_test_current': 2.4010000000000002,
                    'coefficients': [
                        -8.349919235781944e-01,
                        1.039904839768393e+01,
                        -5.626193100165604e+01,
                        1.738986040543417e+02,
                        -3.395456012492874e+02,
                        4.366500952765751e+02,
                        -3.731272727823065e+02,
                        2.077594020429532e+02,
                        -7.129901678878961e+01,
                        1.366174456979344e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.FAST): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -5.298041392614392e-03,
                        1.313741391899646e-01,
                        -1.392836310013559e+00,
                        8.248464735021857e+00,
                        -2.992425170927050e+01,
                        6.867088720079614e+01,
                        -9.949319685655072e+01,
                        8.818626353657028e+01,
                        -4.434190210071176e+01,
                        1.168533878777404e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.FAST): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -6.511236777731059e-03,
                        1.610480673895236e-01,
                        -1.700837010536228e+00,
                        1.001426155624970e+01,
                        -3.602170823561189e+01,
                        8.165320087600392e+01,
                        -1.163148466046148e+02,
                        1.009719790845807e+02,
                        -4.985208300999298e+01,
                        1.313939041281141e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.FAST): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -7.429787007314345e-03,
                        1.830547665733368e-01,
                        -1.924310630074372e+00,
                        1.126569014786845e+01,
                        -4.023243784758038e+01,
                        9.035880297530576e+01,
                        -1.272369645222522e+02,
                        1.090956370885688e+02,
                        -5.350960918298943e+01,
                        1.417380033988433e+01,
                    ]
                },
                ('HIGH', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 2.4010000000000002,
                    'coefficients': [
                        -3.389071504605420e-01,
                        4.583283345025817e+00,
                        -2.726758662778486e+01,
                        9.369613604442044e+01,
                        -2.048312059284663e+02,
                        2.952326822529656e+02,
                        -2.809781640764689e+02,
                        1.720108229526907e+02,
                        -6.392340245507512e+01,
                        1.327159765777585e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.MEDIUM): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -5.530183791044002e-03,
                        1.373704475359414e-01,
                        -1.458476681879541e+00,
                        8.643372864006619e+00,
                        -3.133705175361751e+01,
                        7.169412653759314e+01,
                        -1.031581979952576e+02,
                        9.041597000032043e+01,
                        -4.507699622256555e+01,
                        1.198019247725060e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.MEDIUM): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -6.972928378872987e-03,
                        1.725255466760724e-01,
                        -1.822123650165002e+00,
                        1.072286066759571e+01,
                        -3.851211222718927e+01,
                        8.701364532076717e+01,
                        -1.232037100065870e+02,
                        1.059996380096502e+02,
                        -5.207566429364107e+01,
                        1.374561689250352e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.MEDIUM): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -9.653940172868625e-03,
                        2.371452269787625e-01,
                        -2.483804748807191e+00,
                        1.447382846998532e+01,
                        -5.137197223774567e+01,
                        1.143768626995842e+02,
                        -1.589354508578273e+02,
                        1.334272411264732e+02,
                        -6.352459354893918e+01,
                        1.599542087968989e+01,
                    ]
                },
                ('HIGH', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 3.1510000000000002,
                    'coefficients': [
                        -1.384621693662251e-01,
                        2.293142342197918e+00,
                        -1.634140861795118e+01,
                        6.557305215066359e+01,
                        -1.628582781287659e+02,
                        2.592760016296956e+02,
                        -2.652065536123731e+02,
                        1.701690692404656e+02,
                        -6.490855471154056e+01,
                        1.372860161695055e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -6.011679623138138e-03,
                        1.489316368197851e-01,
                        -1.576613049184617e+00,
                        9.313649289864360e+00,
                        -3.364816595670963e+01,
                        7.667802969521497e+01,
                        -1.098323388318898e+02,
                        9.577066364707657e+01,
                        -4.757937896295044e+01,
                        1.261953169571481e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -6.906398839747214e-03,
                        1.708638585813413e-01,
                        -1.805187808566978e+00,
                        1.063264140288788e+01,
                        -3.824792689077097e+01,
                        8.662087820633974e+01,
                        -1.230408061418719e+02,
                        1.062871664948087e+02,
                        -5.256010680725497e+01,
                        1.402960666359996e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -8.842364248185595e-03,
                        2.182039868616192e-01,
                        -2.297999213409589e+00,
                        1.348000943374765e+01,
                        -4.823033825868505e+01,
                        1.084422220021972e+02,
                        -1.525221387883837e+02,
                        1.299532960102399e+02,
                        -6.301745283915842e+01,
                        1.620253111523653e+01,
                    ]
                },
                    ('HIGH', LoadImpedance.HIGH, RiseTime.VERY_SLOW): {
                    'max_test_current': 3.6510000000000002,
                    'coefficients': [
                        -5.991011372927736e-02,
                        1.119394276045402e+00,
                        -8.972737569950064e+00,
                        4.034845039350325e+01,
                        -1.117526565965485e+02,
                        1.970882282319305e+02,
                        -2.212470064791923e+02,
                        1.537905458332121e+02,
                        -6.248548608394316e+01,
                        1.387655755000602e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.VERY_SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -6.380828826864308e-03,
                        1.576593461673382e-01,
                        -1.664169722484375e+00,
                        9.799072468619494e+00,
                        -3.527146177472453e+01,
                        8.003394703280284e+01,
                        -1.140697099389440e+02,
                        9.892201743814057e+01,
                        -4.896026195128184e+01,
                        1.302586051890165e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -7.763881258823291e-03,
                        1.912824591058450e-01,
                        -2.011418594436677e+00,
                        1.178393875706286e+01,
                        -4.212949944647846e+01,
                        9.473560098470453e+01,
                        -1.334450953995660e+02,
                        1.141000277836704e+02,
                        -5.571448563723253e+01,
                        1.463455485659118e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -9.462445948575529e-03,
                        2.328320380491477e-01,
                        -2.443727918457600e+00,
                        1.427770679129041e+01,
                        -5.084562757461649e+01,
                        1.136966809066923e+02,
                        -1.588974628477956e+02,
                        1.344472982353016e+02,
                        -6.486872782855856e+01,
                        1.673528173681577e+01,
                    ]
                }
            },
            # 5 A model data.
            #
            #   Test date:7_30_2024
            #   Firmware Version
            #   MCV Setting
            #   Low Range load: Osram Projector LED
            #   High Range load: Osram Projector LED
            #
            5: {
                'low_current_range_maximum': 0.2,
                # low range coefficients 
                ('LOW', LoadImpedance.HIGH, RiseTime.FAST): {
                    'max_test_current': 0.060000000000000005,
                    'coefficients': [
                        -1.346050118059396e+16,
                        3.971534786952294e+15,
                        -4.980098335463114e+14,
                        3.460216623460693e+13,
                        -1.456545349194948e+12,
                        3.817592064574935e+10,
                        -6.174266512522117e+08,
                        5.915050742899591e+06,
                        -3.102236860315020e+04,
                        7.819161798723077e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.FAST): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -3.385380854906639e+14,
                        1.643183713621474e+14,
                        -3.382641101529811e+13,
                        3.847055753023389e+12,
                        -2.638788980780445e+11,
                        1.118840276575873e+10,
                        -2.890603995096654e+08,
                        4.320420370795928e+06,
                        -3.368768110398375e+04,
                        1.136077638452640e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.FAST): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -1.366154386470470e+12,
                        1.247672877767095e+12,
                        -4.829837139584489e+11,
                        1.032162555557400e+11,
                        -1.329113838273269e+10,
                        1.056620865834404e+09,
                        -5.109029164371984e+07,
                        1.424808706025186e+06,
                        -2.060017659503259e+04,
                        1.267837082401824e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.FAST): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -5.051983701613303e+11,
                        4.769237607886802e+11,
                        -1.921403336973865e+11,
                        4.312051643729930e+10,
                        -5.903090893901936e+09,
                        5.076192523318032e+08,
                        -2.723543613166079e+07,
                        8.769494762265848e+05,
                        -1.564330815484816e+04,
                        1.340839849754989e+02,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 0.060000000000000005,
                    'coefficients': [
                        -2.482043974277968e+16,
                        7.297739202206802e+15,
                        -9.115547160264341e+14,
                        6.305010714330649e+13,
                        -2.638912108943889e+12,
                        6.860300585411143e+10,
                        -1.094576420702193e+09,
                        1.021404706407295e+07,
                        -5.051832151781477e+04,
                        1.099597312160674e+02,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.MEDIUM): {
                    'max_test_current': 0.08,
                    'coefficients': [
                        -2.314938982959861e+15,
                        9.015753718365151e+14,
                        -1.490413459903048e+14,
                        1.362722133064804e+13,
                        -7.527121359037218e+11,
                        2.576545145752576e+10,
                        -5.396622136324562e+08,
                        6.589274392312742e+06,
                        -4.262729711194123e+04,
                        1.233402266611764e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -9.742352913262319e+11,
                        8.951419097953198e+11,
                        -3.490470424374945e+11,
                        7.526250547160979e+10,
                        -9.801089245600431e+09,
                        7.906251205509747e+08,
                        -3.899064785649614e+07,
                        1.118402112167394e+06,
                        -1.688568301737710e+04,
                        1.119632863643297e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -4.282396839826701e+11,
                        4.069594731657604e+11,
                        -1.651274345885627e+11,
                        3.735050265367628e+10,
                        -5.159224865401846e+09,
                        4.484585543093485e+08,
                        -2.439688724146008e+07,
                        8.006865389544981e+05,
                        -1.468335902602957e+04,
                        1.307658146673328e+02,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -1.967619869770918e+14,
                        9.585565939636867e+13,
                        -1.982375308289848e+13,
                        2.267822444287320e+12,
                        -1.567533363945053e+11,
                        6.715004759042689e+09,
                        -1.759643963215615e+08,
                        2.683287311601079e+06,
                        -2.152403288411121e+04,
                        7.544428618503153e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.SLOW): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -3.178100781253410e+14,
                        1.541299286750301e+14,
                        -3.170869474335161e+13,
                        3.605096304166213e+12,
                        -2.473473473776891e+11,
                        1.050040096211649e+10,
                        -2.720652153510821e+08,
                        4.089308071726532e+06,
                        -3.221297119291520e+04,
                        1.108810028038511e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.SLOW): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -1.143916315864790e+12,
                        1.047618282049638e+12,
                        -4.068578792650527e+11,
                        8.728422848156628e+10,
                        -1.129304186871249e+10,
                        9.032641626666660e+08,
                        -4.404075424930316e+07,
                        1.243616055024067e+06,
                        -1.836763528370090e+04,
                        1.181230657421344e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.SLOW): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -2.747939900618490e+11,
                        2.682319370311515e+11,
                        -1.121741756153237e+11,
                        2.625290719004314e+10,
                        -3.768791716393783e+09,
                        3.421685070216345e+08,
                        -1.954778715809422e+07,
                        6.774097415824316e+05,
                        -1.318209634318136e+04,
                        1.250394517343262e+02,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -2.405549732240165e+14,
                        1.167837640019307e+14,
                        -2.404796138930253e+13,
                        2.736055908650182e+12,
                        -1.877743338308835e+11,
                        7.967120635474062e+09,
                        -2.059951582855897e+08,
                        3.080109945253149e+06,
                        -2.397196269160914e+04,
                        8.021857408474315e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -2.963332214847434e+14,
                        1.440766702909983e+14,
                        -2.971768086027597e+13,
                        3.387619944142139e+12,
                        -2.330225378964038e+11,
                        9.915737481846994e+09,
                        -2.574481347348072e+08,
                        3.877538006027492e+06,
                        -3.068340576420075e+04,
                        1.077748735609755e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -1.167590532457576e+12,
                        1.069095240602807e+12,
                        -4.151373971944171e+11,
                        8.905111590047061e+10,
                        -1.152069289205055e+10,
                        9.213523976520650e+08,
                        -4.490655882375965e+07,
                        1.266781046016748e+06,
                        -1.866173714537442e+04,
                        1.194480769356166e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.189,
                    'coefficients': [
                        -2.712582002954995e+11,
                        2.653820872982494e+11,
                        -1.112890555050700e+11,
                        2.613166419509599e+10,
                        -3.765578801089605e+09,
                        3.432550061312052e+08,
                        -1.968253279700688e+07,
                        6.836194382782832e+05,
                        -1.329026644680350e+04,
                        1.255026439537286e+02,
                    ]
                },
                # high range coefficients
                    ('HIGH', LoadImpedance.HIGH, RiseTime.FAST): {
                    'max_test_current': 2.4010000000000002,
                    'coefficients': [
                        -8.349919235781944e-01,
                        1.039904839768393e+01,
                        -5.626193100165604e+01,
                        1.738986040543417e+02,
                        -3.395456012492874e+02,
                        4.366500952765751e+02,
                        -3.731272727823065e+02,
                        2.077594020429532e+02,
                        -7.129901678878961e+01,
                        1.366174456979344e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.FAST): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -5.298041392614392e-03,
                        1.313741391899646e-01,
                        -1.392836310013559e+00,
                        8.248464735021857e+00,
                        -2.992425170927050e+01,
                        6.867088720079614e+01,
                        -9.949319685655072e+01,
                        8.818626353657028e+01,
                        -4.434190210071176e+01,
                        1.168533878777404e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.FAST): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -6.511236777731059e-03,
                        1.610480673895236e-01,
                        -1.700837010536228e+00,
                        1.001426155624970e+01,
                        -3.602170823561189e+01,
                        8.165320087600392e+01,
                        -1.163148466046148e+02,
                        1.009719790845807e+02,
                        -4.985208300999298e+01,
                        1.313939041281141e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.FAST): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -7.429787007314345e-03,
                        1.830547665733368e-01,
                        -1.924310630074372e+00,
                        1.126569014786845e+01,
                        -4.023243784758038e+01,
                        9.035880297530576e+01,
                        -1.272369645222522e+02,
                        1.090956370885688e+02,
                        -5.350960918298943e+01,
                        1.417380033988433e+01,
                    ]
                },
                ('HIGH', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 2.4010000000000002,
                    'coefficients': [
                        -3.389071504605420e-01,
                        4.583283345025817e+00,
                        -2.726758662778486e+01,
                        9.369613604442044e+01,
                        -2.048312059284663e+02,
                        2.952326822529656e+02,
                        -2.809781640764689e+02,
                        1.720108229526907e+02,
                        -6.392340245507512e+01,
                        1.327159765777585e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.MEDIUM): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -5.530183791044002e-03,
                        1.373704475359414e-01,
                        -1.458476681879541e+00,
                        8.643372864006619e+00,
                        -3.133705175361751e+01,
                        7.169412653759314e+01,
                        -1.031581979952576e+02,
                        9.041597000032043e+01,
                        -4.507699622256555e+01,
                        1.198019247725060e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.MEDIUM): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -6.972928378872987e-03,
                        1.725255466760724e-01,
                        -1.822123650165002e+00,
                        1.072286066759571e+01,
                        -3.851211222718927e+01,
                        8.701364532076717e+01,
                        -1.232037100065870e+02,
                        1.059996380096502e+02,
                        -5.207566429364107e+01,
                        1.374561689250352e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.MEDIUM): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -9.653940172868625e-03,
                        2.371452269787625e-01,
                        -2.483804748807191e+00,
                        1.447382846998532e+01,
                        -5.137197223774567e+01,
                        1.143768626995842e+02,
                        -1.589354508578273e+02,
                        1.334272411264732e+02,
                        -6.352459354893918e+01,
                        1.599542087968989e+01,
                    ]
                },
                ('HIGH', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 3.1510000000000002,
                    'coefficients': [
                        -1.384621693662251e-01,
                        2.293142342197918e+00,
                        -1.634140861795118e+01,
                        6.557305215066359e+01,
                        -1.628582781287659e+02,
                        2.592760016296956e+02,
                        -2.652065536123731e+02,
                        1.701690692404656e+02,
                        -6.490855471154056e+01,
                        1.372860161695055e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -6.011679623138138e-03,
                        1.489316368197851e-01,
                        -1.576613049184617e+00,
                        9.313649289864360e+00,
                        -3.364816595670963e+01,
                        7.667802969521497e+01,
                        -1.098323388318898e+02,
                        9.577066364707657e+01,
                        -4.757937896295044e+01,
                        1.261953169571481e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -6.906398839747214e-03,
                        1.708638585813413e-01,
                        -1.805187808566978e+00,
                        1.063264140288788e+01,
                        -3.824792689077097e+01,
                        8.662087820633974e+01,
                        -1.230408061418719e+02,
                        1.062871664948087e+02,
                        -5.256010680725497e+01,
                        1.402960666359996e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -8.842364248185595e-03,
                        2.182039868616192e-01,
                        -2.297999213409589e+00,
                        1.348000943374765e+01,
                        -4.823033825868505e+01,
                        1.084422220021972e+02,
                        -1.525221387883837e+02,
                        1.299532960102399e+02,
                        -6.301745283915842e+01,
                        1.620253111523653e+01,
                    ]
                },
                    ('HIGH', LoadImpedance.HIGH, RiseTime.VERY_SLOW): {
                    'max_test_current': 3.6510000000000002,
                    'coefficients': [
                        -5.991011372927736e-02,
                        1.119394276045402e+00,
                        -8.972737569950064e+00,
                        4.034845039350325e+01,
                        -1.117526565965485e+02,
                        1.970882282319305e+02,
                        -2.212470064791923e+02,
                        1.537905458332121e+02,
                        -6.248548608394316e+01,
                        1.387655755000602e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.VERY_SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -6.380828826864308e-03,
                        1.576593461673382e-01,
                        -1.664169722484375e+00,
                        9.799072468619494e+00,
                        -3.527146177472453e+01,
                        8.003394703280284e+01,
                        -1.140697099389440e+02,
                        9.892201743814057e+01,
                        -4.896026195128184e+01,
                        1.302586051890165e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -7.763881258823291e-03,
                        1.912824591058450e-01,
                        -2.011418594436677e+00,
                        1.178393875706286e+01,
                        -4.212949944647846e+01,
                        9.473560098470453e+01,
                        -1.334450953995660e+02,
                        1.141000277836704e+02,
                        -5.571448563723253e+01,
                        1.463455485659118e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 4.901,
                    'coefficients': [
                        -9.462445948575529e-03,
                        2.328320380491477e-01,
                        -2.443727918457600e+00,
                        1.427770679129041e+01,
                        -5.084562757461649e+01,
                        1.136966809066923e+02,
                        -1.588974628477956e+02,
                        1.344472982353016e+02,
                        -6.486872782855856e+01,
                        1.673528173681577e+01,
                    ]
                }
            },
            # 10 A mini model data
            #
            #   Test date:7_25_2024
            #   Firmware Version
            #   MCV Setting
            #   Low Range load: Osram Projector LED
            #   High Range load: Osram Projector LED
            #
            10: {
                'low_current_range_maximum': 0.4,
                # low range coefficients 
                ('LOW', LoadImpedance.HIGH, RiseTime.FAST): {
                    'max_test_current': 0.060000000000000005,
                    'coefficients': [
                        -3.258521550700538e+16,
                        9.591298107680680e+15,
                        -1.199554650707500e+15,
                        8.309748227600092e+13,
                        -3.484918033604314e+12,
                        9.085501531734283e+10,
                        -1.456351904161133e+09,
                        1.371307344889785e+07,
                        -6.933803748799293e+04,
                        1.615058849979316e+02,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.FAST): {
                    'max_test_current': 0.12000000000000001,
                    'coefficients': [
                        -4.117543731920220e+13,
                        2.417696895695370e+13,
                        -6.046310362375818e+12,
                        8.405942552896761e+11,
                        -7.114434022243034e+10,
                        3.775409957793374e+09,
                        -1.248066117192360e+08,
                        2.471763335518205e+06,
                        -2.704391192780124e+04,
                        1.418324558262326e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.FAST): {
                    'max_test_current': 0.379,
                    'coefficients': [
                        6.357177654964466e+08,
                        -1.097634088479439e+09,
                        7.853363791759822e+08,
                        -2.984101432348501e+08,
                        6.338735112919418e+07,
                        -6.926729282708092e+06,
                        1.913045308097489e+05,
                        3.525715869023554e+04,
                        -3.626374260592418e+03,
                        1.220697770007988e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.FAST): {
                    'max_test_current': 0.379,
                    'coefficients': [
                        1.394969019864158e+09,
                        -2.461070631816973e+09,
                        1.818926600380376e+09,
                        -7.284990977418138e+08,
                        1.703186797494717e+08,
                        -2.312714709591909e+07,
                        1.652397600396404e+06,
                        -3.781421322526436e+04,
                        -1.903559370678101e+03,
                        1.121306119163075e+02,   
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 0.060000000000000005,
                    'coefficients': [
                        -2.252682434604322e+16,
                        6.666715394563125e+15,
                        -8.396280641899350e+14,
                        5.869014032700945e+13,
                        -2.490295749161832e+12,
                        6.593456131766326e+10,
                        -1.079235193650751e+09,
                        1.046659041720443e+07,
                        -5.531856495653895e+04,
                        1.389319317465935e+02,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.MEDIUM): {
                    'max_test_current': 0.199,
                    'coefficients': [
                        -4.221656055243906e+11,
                        4.147800485643973e+11,
                        -1.733601724988036e+11,
                        4.018926234739027e+10,
                        -5.649978130375907e+09,
                        4.948737679409335e+08,
                        -2.673339771637067e+07,
                        8.523428933094353e+05,
                        -1.469228047443109e+04,
                        1.169952406820143e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.379,
                    'coefficients': [
                        1.216563783275557e+09,
                        -2.135791337216223e+09,
                        1.567309329179844e+09,
                        -6.211120871372771e+08,
                        1.428064875659277e+08,
                        -1.881735032906941e+07,
                        1.249783084971160e+06,
                        -1.691997830199993e+04,
                        -2.417035665716759e+03,
                        1.140354716205144e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.379,
                    'coefficients': [
                        1.282488364536335e+09,
                        -2.233087612862272e+09,
                        1.624410930952399e+09,
                        -6.378156396979182e+08,
                        1.452485598292911e+08,
                        -1.895857364142633e+07,
                        1.249253486165365e+06,
                        -1.704055817438720e+04,
                        -2.388092703376240e+03,
                        1.157740791395719e+02,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 0.060000000000000005,
                    'coefficients': [
                        -2.661967601864944e+16,
                        7.859082847531381e+15,
                        -9.867652430250670e+14,
                        6.870630611487989e+13,
                        -2.900890371238193e+12,
                        7.632520931083356e+10,
                        -1.239469039159943e+09,
                        1.190410663161818e+07,
                        -6.222123996448444e+04,
                        1.542733228150167e+02,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.SLOW): {
                    'max_test_current': 0.100,
                    'coefficients': [
                        8.007e+13,
                        -3.491e+13,
                        6.152e+12,
                        -5.469e+11,
                        2.348e+10,
                        -1.668e+8,
                        -2.708e+07,
                        1.143e+6,
                        -1.893e+04,
                        1.313e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.SLOW): {
                    'max_test_current': 0.379,
                    'coefficients': [
                        9.868248461565001e+08,
                        -1.729243447107423e+09,
                        1.264500624261060e+09,
                        -4.977322559642811e+08,
                        1.128727439158334e+08,
                        -1.440274732770590e+07,
                        8.618907915596046e+05,
                        2.151315398749731e+03,
                        -2.877361206553458e+03,
                        1.183166689102373e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.SLOW): {
                    'max_test_current': 0.379,
                    'coefficients': [
                        1.254916893163028e+09,
                        -2.225678309304050e+09,
                        1.657152633573157e+09,
                        -6.710466188347523e+08,
                        1.596149638918117e+08,
                        -2.230387183933393e+07,
                        1.681482085577114e+06,
                        -4.582344929432369e+04,
                        -1.631777519688525e+03,
                        1.166195186781487e+02,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.060000000000000005,
                    'coefficients': [
                        -2.101410331233956e+16,
                        6.253658131035759e+15,
                        -7.930259667488379e+14,
                        5.591286112743923e+13,
                        -2.398771632447011e+12,
                        6.442506983590874e+10,
                        -1.074238950736929e+09,
                        1.066491512801945e+07,
                        -5.790937256354689e+04,
                        1.489970392316854e+02,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.1,
                    'coefficients': [
                        -9.827755033004400e+13,
                        5.006847391691189e+13,
                        -1.092156611482018e+13,
                        1.333121164517928e+12,
                        -9.988940150010924e+10,
                        4.742903222825021e+09,
                        -1.422311014688345e+08,
                        2.602901462142200e+06,
                        -2.702918070694028e+04,
                        1.407502491199906e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.379,
                    'coefficients': [
                        6.464139470703996e+08,
                        -1.099414372094237e+09,
                        7.712777667328111e+08,
                        -2.848332433354220e+08,
                        5.759231416975830e+07,
                        -5.563133181807133e+06,
                        7.848386012374059e+03,
                        4.854304351434942e+04,
                        -4.033446331259382e+03,
                        1.214465919980773e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.379,
                    'coefficients': [
                        1.192528594371335e+09,
                        -2.104207424903100e+09,
                        1.555388861007829e+09,
                        -6.227460905787362e+08,
                        1.453021141791303e+08,
                        -1.958315694648302e+07,
                        1.358894918101822e+06,
                        -2.428971153261444e+04,
                        -2.239122364939700e+03,
                        1.161289597523726e+02,
                    ]
                },
                # high range coefficients
                    ('HIGH', LoadImpedance.HIGH, RiseTime.FAST): {
                    'max_test_current': 2.351,
                    'coefficients': [
                        4.804071255985023e-01,
                        -5.570000039529265e+00,
                        2.673563805117900e+01,
                        -6.733672933893966e+01,
                        8.975668147451344e+01,
                        -4.344434344367748e+01,
                        -4.264791607648090e+01,
                        8.050510912144078e+01,
                        -5.286861819961454e+01,
                        1.683255442228802e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.FAST): {
                    'max_test_current': 7.851,
                    'coefficients': [
                        -5.956541458697444e-05,
                        2.395650485928003e-03,
                        -4.134702253943497e-02,
                        4.005201973417868e-01,
                        -2.391453035925051e+00,
                        9.103983788323196e+00,
                        -2.210092336784332e+01,
                        3.322893669220942e+01,
                        -2.877593824529233e+01,
                        1.337696774703609e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.FAST): {
                    'max_test_current': 7.851,
                    'coefficients': [
                        -1.084459689353366e-04,
                        4.306768204811102e-03,
                        -7.319761549863893e-02,
                        6.956455180884418e-01,
                        -4.054145081456712e+00,
                        1.495533734851114e+01,
                        -3.482991836998864e+01,
                        4.963757586757409e+01,
                        -4.052535483749196e+01,
                        1.857219148745716e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.FAST): {
                    'max_test_current': 9.501,
                    'coefficients': [
                        -2.021936535146625e-05,
                        9.672154858669599e-04,
                        -1.978466871082459e-02,
                        2.260586832570357e-01,
                        -1.581813385244910e+00,
                        6.994637782349338e+00,
                        -1.948944243997074e+01,
                        3.315818236297756e+01,
                        -3.225268749921501e+01,
                        1.787516509391996e+01,
                    ]
                },
                ('HIGH', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 2.601,
                    'coefficients': [
                        -2.166764370050402e-01,
                        3.136662546798741e+00,
                        -1.992363551572533e+01,
                        7.288442044915259e+01,
                        -1.693669815868604e+02,
                        2.600938464376411e+02,
                        -2.663488869475086e+02,
                        1.794123664070116e+02,
                        -7.625490209151701e+01,
                        1.925004448464693e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.MEDIUM): {
                    'max_test_current': 9.501,
                    'coefficients': [
                        -1.248889189464484e-05,
                        6.024195779281091e-04,
                        -1.245266165122354e-02,
                        1.441632430586427e-01,
                        -1.025356283432070e+00,
                        4.626474970765760e+00,
                        -1.321408854822010e+01,
                        2.315644486103067e+01,
                        -2.321011652439488e+01,
                        1.253117541181267e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.MEDIUM): {
                    'max_test_current': 9.501,
                    'coefficients': [
                        -1.885057231780745e-05,
                        9.038094583938330e-04,
                        -1.851416360717151e-02,
                        2.115593014558755e-01,
                        -1.477414309184838e+00,
                        6.499830705514239e+00,
                        -1.794108786850976e+01,
                        3.010358557321403e+01,
                        -2.892676791222046e+01,
                        1.606567799854043e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.MEDIUM): {
                    'max_test_current': 9.501,
                    'coefficients': [
                        -2.299291154676606e-05,
                        1.110165119436016e-03,
                        -2.293024167769042e-02,
                        2.645650644887503e-01,
                        -1.868114637785881e+00,
                        8.319161490568348e+00,
                        -2.324267055865977e+01,
                        3.933794687206591e+01,
                        -3.765338439972368e+01,
                        1.986495727646545e+01,
                    ]
                },
                ('HIGH', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 3.101,
                    'coefficients': [
                        -1.384813456462725e-01,
                        2.327822318946717e+00,
                        -1.691319528397424e+01,
                        6.959328036438934e+01,
                        -1.785460489722455e+02,
                        2.964667703095233e+02,
                        -3.203663315863519e+02,
                        2.209541093806519e+02,
                        -9.261399764730849e+01,
                        2.207392633701492e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.SLOW): {
                    'max_test_current': 9.501,
                    'coefficients': [
                        -1.279523645163110e-05,
                        6.167139096048981e-04,
                        -1.273121595209635e-02,
                        1.470824486325001e-01,
                        -1.042898921638562e+00,
                        4.684732814157363e+00,
                        -1.329721048733581e+01,
                        2.311848859004952e+01,
                        -2.306838557041375e+01,
                        1.260535167692070e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.SLOW): {
                    'max_test_current': 9.501,
                    'coefficients': [
                        -2.856273466945566e-05,
                        1.362315546307608e-03,
                        -2.774559168517252e-02,
                        3.149597885432291e-01,
                        -2.182061811650772e+00,
                        9.500117436927011e+00,
                        -2.582249914971879e+01,
                        4.222736997960487e+01,
                        -3.873201086211464e+01,
                        1.931744508399682e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.SLOW): {
                    'max_test_current': 9.501,
                    'coefficients': [
                        -3.127539233757810e-05,
                        1.483681928291920e-03,
                        -3.003981859844669e-02,
                        3.388183301005926e-01,
                        -2.331143712228596e+00,
                        1.007574435271789e+01,
                        -2.719377013946817e+01,
                        4.422411298279754e+01,
                        -4.055482428735694e+01,
                        2.055927538606278e+01,
                    ]
                },
                    ('HIGH', LoadImpedance.HIGH, RiseTime.VERY_SLOW): {
                    'max_test_current': 3.351,
                    'coefficients': [
                        -2.731013263238350e-02,
                        5.106895861991256e-01,
                        -4.141047849108750e+00,
                        1.911215632809807e+01,
                        -5.543073373418120e+01,
                        1.053236110928281e+02,
                        -1.326818595178828e+02,
                        1.095711459262900e+02,
                        -5.692484740661617e+01,
                        1.762742263523948e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.VERY_SLOW): {
                    'max_test_current': 8.351,
                    'coefficients': [
                        -4.477182912602952e-05,
                        1.903651732767878e-03,
                        -3.469529037060549e-02,
                        3.542906421834376e-01,
                        -2.223906303404624e+00,
                        8.860870552178417e+00,
                        -2.235505053287034e+01,
                        3.460077936273932e+01,
                        -3.075153644608471e+01,
                        1.477901930094953e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 8.601,
                    'coefficients': [
                        -8.532499193676807e-05,
                        3.680013691000676e-03,
                        -6.775638987213052e-02,
                        6.950748042064695e-01,
                        -4.349150260876576e+00,
                        1.708393966276691e+01,
                        -4.181899236819626e+01,
                        6.136103000167200e+01,
                        -5.014812231921736e+01,
                        2.188235824705471e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 9.501,
                    'coefficients': [
                        -2.154992444854056e-05,
                        1.035594534292853e-03,
                        -2.128799019360574e-02,
                        2.445073667019119e-01,
                        -1.720057462519692e+00,
                        7.644588989788752e+00,
                        -2.138855658530301e+01,
                        3.649869771698984e+01,
                        -3.577698260578126e+01,
                        1.985753034337597e+01,
                    ]
                }
            },# 20A model data
            #
            #   Test date:8_13_2024
            #   Firmware Version
            #   MCV Setting 35
            #   Low Range load: Osram Blue Projector
            #   High Range load: Osram Blue Projector
            #
            20: {
                'low_current_range_maximum': 0.4,
                # low range coefficients 
                ('LOW', LoadImpedance.HIGH, RiseTime.FAST): { #Needs updating, missing data
                    'max_test_current': 0.78,
                    'coefficients': [
                        -2.662506087427484e+05,
                        1.029765700717237e+06,
                        -1.696079384203786e+06,
                        1.552083073991240e+06,
                        -8.635636176423125e+05,
                        3.005534929640736e+05,
                        -6.490969889332316e+04,
                        8.351720663960847e+03,
                        -5.888746200228287e+02,
                        2.029569120353516e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.FAST): {
                    'max_test_current': 0.51,
                    'coefficients': [
                        1.677577485518190e+07,
                        -2.809810010406030e+07,
                        1.263172492740946e+07,
                        4.618322866142599e+06,
                        -6.847244158816427e+06,
                        2.943553616575149e+06,
                        -6.481556224779004e+05,
                        7.787822601939387e+04,
                        -4.870912786928722e+03,
                        1.387292451343364e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.FAST): {
                    'max_test_current': 0.51,
                    'coefficients': [
                        2.747505183084645e+07,
                        -7.525981881877042e+07,
                        8.813958790277390e+07,
                        -5.745361656162842e+07,
                        2.270153772041014e+07,
                        -5.532471655342422e+06,
                        8.021529190282683e+05,
                        -6.078369053607239e+04,
                        1.286110672168762e+03,
                        9.227916481372183e+01,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.FAST): {
                    'max_test_current': 0.63,
                    'coefficients': [
                        1.523273126770681e+07,
                        -4.603077740121746e+07,
                        5.909321901371842e+07,
                        -4.201691071304345e+07,
                        1.807048314109806e+07,
                        -4.808140134373487e+06,
                        7.713100080999318e+05,
                        -6.725840246413118e+04,
                        2.077761976303538e+03,
                        8.524046238068438e+01,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 0.75,
                    'coefficients': [
                        -9.904306803740136e+05,
                        3.632368893355543e+06,
                        -5.656126179674726e+06,
                        4.873348550159836e+06,
                        -2.538173848503632e+06,
                        8.198736917086386e+05,
                        -1.621737274075189e+05,
                        1.869645199825879e+04,
                        -1.136886038267831e+03,
                        3.084739573751301e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.MEDIUM): {
                    'max_test_current': 0.51,
                    'coefficients': [
                        -3.848022992460588e+07,
                        9.283429603597966e+07,
                        -9.504089806557386e+07,
                        5.385460714106493e+07,
                        -1.848201912357826e+07,
                        3.955138515956691e+06,
                        -5.258717792698010e+05,
                        4.248767724673742e+04,
                        -2.059885314526628e+03,
                        6.440635119659493e+01,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.51,
                    'coefficients': [
                        2.939640655963729e+07,
                        -8.535203389869101e+07,
                        1.050703551997189e+08,
                        -7.139630951428524e+07,
                        2.916555922502438e+07,
                        -7.290754418768418e+06,
                        1.078028940466137e+06,
                        -8.371925748907856e+04,
                        2.084066307372299e+03,
                        8.781861711934913e+01,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.MEDIUM): {
                    'max_test_current': 0.63,
                    'coefficients': [
                        1.233240811216241e+07,
                        -3.857920109684788e+07,
                        5.138775322915902e+07,
                        -3.796660983638558e+07,
                        1.696292580901699e+07,
                        -4.673213096357467e+06,
                        7.700182555193842e+05,
                        -6.807380943345516e+04,
                        2.102572944151871e+03,
                        8.496151904238671e+01,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 0.75,
                    'coefficients': [
                        -8.831704696157723e+05,
                        3.243468824750071e+06,
                        -5.059996328066275e+06,
                        4.370875575146805e+06,
                        -2.284620979013260e+06,
                        7.417958587581416e+05,
                        -1.478815150480017e+05,
                        1.726219821462699e+04,
                        -1.071878251643100e+03,
                        3.024170626425371e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.SLOW): {
                    'max_test_current': 0.51,
                    'coefficients': [
                        -7.957241012728700e+07,
                        2.014294473680571e+08,
                        -2.173046840959060e+08,
                        1.303782474164847e+08,
                        -4.762397896208023e+07,
                        1.090243112396131e+07,
                        -1.553749591715114e+06,
                        1.328303414011188e+05,
                        -6.352159045305169e+03,
                        1.529381957953913e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.SLOW): {
                    'max_test_current': 0.51,
                    'coefficients': [
                        9.483944700975309e+07,
                        -2.343520089696061e+08,
                        2.458270150073036e+08,
                        -1.425481952718133e+08,
                        4.979340009822476e+07,
                        -1.067118920004808e+07,
                        1.355923211185596e+06,
                        -9.029987775270476e+04,
                        1.804902792782752e+03,
                        9.128920861390250e+01,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.SLOW): {
                    'max_test_current': 0.6900000000000001,
                    'coefficients': [
                        3.886397168937285e+06,
                        -1.343506033509004e+07,
                        1.977286281415514e+07,
                        -1.614419665888303e+07,
                        7.979403290216353e+06,
                        -2.438072852628740e+06,
                        4.473319537029376e+05,
                        -4.402660179524907e+04,
                        1.405212422301309e+03,
                        9.040872620371188e+01,
                    ]
                },            
                ('LOW', LoadImpedance.HIGH, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.75,
                    'coefficients': [
                        -1.186184085558267e+06,
                        4.332878849944776e+06,
                        -6.714938490268333e+06,
                        5.752702388349105e+06,
                        -2.975415821726909e+06,
                        9.528999424023548e+05,
                        -1.864768089610946e+05,
                        2.121026757294939e+04,
                        -1.268723329063479e+03,
                        3.389747856172383e+01,
                    ]
                },
                ('LOW', LoadImpedance.MEDIUM, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.51,
                    'coefficients': [
                        -5.610315282644275e+07,
                        1.476444296332659e+08,
                        -1.660751302063362e+08,
                        1.042167167901133e+08,
                        -3.994951034005091e+07,
                        9.631258004380707e+06,
                        -1.449732377474842e+06,
                        1.308080516539484e+05,
                        -6.504204871352068e+03,
                        1.551558432423511e+02,
                    ]
                },
                ('LOW', LoadImpedance.LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.51,
                    'coefficients': [
                        5.162992273433466e+06,
                        -1.710158016087002e+07,
                        2.308699084179584e+07,
                        -1.681238945753422e+07,
                        7.266276158671440e+06,
                        -1.904433448977445e+06,
                        2.888650926825557e+05,
                        -2.047579462119279e+04,
                        -1.648200246351119e+02,
                        1.031799239310314e+02,
                    ]
                },
                ('LOW', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 0.75,
                    'coefficients': [
                        2.198744691029628e+06,
                        -8.067102589190313e+06,
                        1.258869872681748e+07,
                        -1.087786149769932e+07,
                        5.670094230761514e+06,
                        -1.815691780931848e+06,
                        3.452971542246486e+05,
                        -3.443265899334586e+04,
                        9.790128007754849e+02,
                        9.412614894968571e+01,
                    ]
                },
                # high range coefficients
                    ('HIGH', LoadImpedance.HIGH, RiseTime.FAST): {
                    'max_test_current': 9.201,
                    'coefficients': [
                        -9.905318167306186e-06,
                        4.725561305889877e-04,
                        -9.681155364062211e-03,
                        1.114677317167871e-01,
                        -7.932206693845958e-01,
                        3.618317888428181e+00,
                        -1.064352171996836e+01,
                        1.986721937037220e+01,
                        -2.252305225249101e+01,
                        1.450759949085866e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.FAST): {
                    'max_test_current': 16,
                    'coefficients': [
                        -2.113100465819061e-08,
                        2.063939272119128e-06,
                        -8.630281592849254e-05,
                        2.018411390503740e-03,
                        -2.895382543835247e-02,
                        2.629602218140340e-01,
                        -1.507979820799190e+00,
                        5.283682845347832e+00,
                        -1.046570274380166e+01,
                        1.091951016846316e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.FAST): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -1.363411312384961e-07,
                        1.129046413832590e-05,
                        -3.998631370391634e-04,
                        7.913398817033495e-03,
                        -9.597362442487749e-02,
                        7.362080773928846e-01,
                        -3.559791657412912e+00,
                        1.047743725017372e+01,
                        -1.731589158563779e+01,
                        1.471892220465373e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.FAST): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -1.951507031650237e-08,
                        1.877380587710653e-06,
                        -7.835565324937937e-05,
                        1.851760214461079e-03,
                        -2.713643536067400e-02,
                        2.540671768574094e-01,
                        -1.511661980964671e+00,
                        5.508503332307148e+00,
                        -1.132159006208122e+01,
                        1.238409299411667e+01,
                    ]
                },
                ('HIGH', LoadImpedance.HIGH, RiseTime.MEDIUM): {
                    'max_test_current': 9.201,
                    'coefficients': [
                        -8.182224909432018e-06,
                        3.970552301133145e-04,
                        -8.283237019790387e-03,
                        9.720564924788669e-02,
                        -7.054357342126331e-01,
                        3.281751076716117e+00,
                        -9.836434275065583e+00,
                        1.867374791916738e+01,
                        -2.154592581114032e+01,
                        1.442585797564473e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.MEDIUM): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -7.957425082869602e-08,
                        6.706182385456090e-06,
                        -2.423313948452636e-04,
                        4.908894588060039e-03,
                        -6.118127093387914e-02,
                        4.846965436880588e-01,
                        -2.436067966908914e+00,
                        7.523605915458287e+00,
                        -1.329292753517049e+01,
                        1.252273751733291e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.MEDIUM): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -6.930936217903154e-08,
                        5.770088819271973e-06,
                        -2.059949319557628e-04,
                        4.126378918349830e-03,
                        -5.097268775756974e-02,
                        4.020814539592772e-01,
                        -2.028913261360681e+00,
                        6.380281336939084e+00,
                        -1.174594231556333e+01,
                        1.211093970356602e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.MEDIUM): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -5.936578722687930e-08,
                        5.042897792671105e-06,
                        -1.841522714438601e-04,
                        3.783258235576940e-03,
                        -4.806215266969620e-02,
                        3.908901638133451e-01,
                        -2.037083346621070e+00,
                        6.612700838754392e+00,
                        -1.251721686583071e+01,
                        1.315666254222885e+01,
                    ]
                },
                ('HIGH', LoadImpedance.HIGH, RiseTime.SLOW): {
                    'max_test_current': 9.201,
                    'coefficients': [
                        -1.027534028980478e-05,
                        4.923984453662351e-04,
                        -1.014236272410911e-02,
                        1.175229174789699e-01,
                        -8.423780411949875e-01,
                        3.872300458898997e+00,
                        -1.146894980938150e+01,
                        2.146739686872334e+01,
                        -2.425225665894565e+01,
                        1.571633988217236e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.SLOW): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -3.268667580133973e-08,
                        2.910775616338320e-06,
                        -1.118000231578117e-04,
                        2.422773269140013e-03,
                        -3.252845496312826e-02,
                        2.796816311913449e-01,
                        -1.537998506962649e+00,
                        5.247808082271495e+00,
                        -1.040044044569385e+01,
                        1.136448434500285e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.SLOW): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -1.265118454121027e-07,
                        1.060975497370612e-05,
                        -3.809231615204997e-04,
                        7.646278825753347e-03,
                        -9.401893552744973e-02,
                        7.297762719866804e-01,
                        -3.556835723655615e+00,
                        1.050697265536022e+01,
                        -1.752901166618452e+01,
                        1.543416888478838e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.SLOW): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -1.524400566354344e-07,
                        1.272294571179368e-05,
                        -4.544594929090207e-04,
                        9.076757432396039e-03,
                        -1.111469091171114e-01,
                        8.608825728939539e-01,
                        -4.200404625448668e+00,
                        1.246181620515581e+01,
                        -2.084581715452448e+01,
                        1.799646493347011e+01,
                    ]
                },
                    ('HIGH', LoadImpedance.HIGH, RiseTime.VERY_SLOW): {
                    'max_test_current': 9.201,
                    'coefficients': [
                        -7.444788504716885e-06,
                        3.600832331779001e-04,
                        -7.503587302236716e-03,
                        8.824572519366609e-02,
                        -6.448480910473928e-01,
                        3.040721113228657e+00,
                        -9.315594159073601e+00,
                        1.822958689473152e+01,
                        -2.180270049155778e+01,
                        1.522565173026146e+01,
                    ]
                },
                ('HIGH', LoadImpedance.MEDIUM, RiseTime.VERY_SLOW): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -8.165697706668343e-08,
                        6.916771371836974e-06,
                        -2.513423107232770e-04,
                        5.122316636897987e-03,
                        -6.424819309184424e-02,
                        5.122167815726253e-01,
                        -2.588941053786974e+00,
                        8.030175299945574e+00,
                        -1.427098038577958e+01,
                        1.362047930597407e+01,
                    ]
                },
                ('HIGH', LoadImpedance.LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -9.511068785986297e-08,
                        7.906654307935331e-06,
                        -2.817317280677804e-04,
                        5.628751331165666e-03,
                        -6.926910546347666e-02,
                        5.431708654942268e-01,
                        -2.712873484689867e+00,
                        8.372514429098397e+00,
                        -1.492917587153561e+01,
                        1.448013256268278e+01,
                    ]
                },
                ('HIGH', LoadImpedance.VERY_LOW, RiseTime.VERY_SLOW): {
                    'max_test_current': 16.401,
                    'coefficients': [
                        -1.005517590983015e-07,
                        8.633815099123881e-06,
                        -3.178723942773212e-04,
                        6.559029565897861e-03,
                        -8.320403334802987e-02,
                        6.696413470840022e-01,
                        -3.405569239613937e+00,
                        1.056362422513403e+01,
                        -1.854974743653316e+01,
                        1.703826828240962e+01,
                    ]
                }
            },        
        }

        return table
    
def get_optimum_pulse_width_correction(
    spikesafe_model_max_current_amps: float,
    set_current_amps: float,
    load_impedance: LoadImpedance,
    rise_time: RiseTime
) -> str:
    """
    Obsolete: use PulseWidthCorrection.get_optimum_pulse_width_correction() instead
    """
    return PulseWidthCorrection.get_optimum_pulse_width_correction(spikesafe_model_max_current_amps, set_current_amps, load_impedance, rise_time)