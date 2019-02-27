import numpy as np
from datetime import timedelta

DEUTERIUM = "deuterium"
OXYGEN = "oxygen"

D_VSMOW_RATIO = 0.00015576
O18_VSMOW_RATIO = 0.0020052
STANDARD_WATER_MOL_MASS = 18.10106 / 1000  # kg
POP_DIL_SPACE_D = 1.041
POP_DIL_SPACE_O = 1.007
FAT_FREE_MASS_FACTOR = 0.73
HOURS_PER_DAY = 24
LITERS_PER_MOL = 22.414
WEIR_CONSTANT = 5.7425
MJ_PER_KCAL = 4.184 / 1000

D_PLATEAU_LIMIT = 5.0
O18_PLATEAU_LIMIT = 5.0
DIL_SPACE_RATIO_LOW_LIMIT = 1.00
DIL_SPACE_RATIO_HIGH_LIMIT = 1.07
KO_KD_RATIO_LOW_LIMIT = 1.1
KO_KD_RATIO_HIGH_LIMIT = 1.7


class DLWSubject:
    """Class for performing Doubly Labeled Water calculations
       Attributes:
           d_deltas (np.array): deuterium delta values of subject samples
           o_18deltas (np.array): oxygen 18 delta values of subject samples
           sample_datetimes ([datetime]): dates and times of sample collections
           dose_weights ([float]): weights in g of doses administered, deuterium first, 18O second
           mol_masses ([float]): molecular masses in g/mol of doses administered, deuterium first, 18O second
           dose_enrichments ([float]): dose enrichments in ratio of doses administered, deuterium first, 18O second
           subject_weights ([float]): initial and final weights of the subject in kg
           d_ratios (np.array): deuterium ratios of subject samples
           o18_ratios (np.array): 18O ratios of subject samples
           kd_per_hr (float): deuterium turnover rate in 1/hr
           ko_per_hr (float): oxygen turnover rate in 1/hr
           ko_kd_ratio (float): ratio of oxygen and deuterium turnover rates
           nd (dict): dictionary containing all the calculated values of the deuterium dilution space
                plat_4hr_mol (float): calculated by the plateau method using the 4hr sample in mol
                plat_5hr_mol (float): calculated by the plateau method using the 5hr sample in mol
                plat_avg_mol (float): the average of the 4hr and 5hr plateau dilution spaces in mol
                int_4hr_mol (float): calculated by the intercept method using the 4hr sample in mol
                int_5hr_mol (float): calculated by the intercept method using the 5hr sample in mol
                int_avg_mol (float): the average of the 4hr and 5hr intercept dilution spaces in mol
                adj_plat_avg_mol (float): average plateau dilution space adjusted for the subject weight change over
                           the sampling period, in mol
                adj_int_avg_mol (float): average intercept dilution space adjusted for the subject weight change over
                           the sampling period, in mol
                adj_plat_avg_kg (float): average plateau dilution space adjusted for the subject weight change over
                           the sampling period, in kg
                adj_int_avg_kg (float): average intercept dilution space adjusted for the subject weight change over
                           the sampling period, in kg
           no (dict): dictionary containing all the calculated values of the oxygen 18 dilution space
                plat_4hr_mol (float): calculated by the plateau method using the 4hr sample in mol
                plat_5hr_mol (float): calculated by the plateau method using the 5hr sample in mol
                plat_avg_mol (float): the average of the 4hr and 5hr plateau dilution spaces in mol
                int_4hr_mol (float): calculated by the intercept method using the 4hr sample in mol
                int_5hr_mol (float): calculated by the intercept method using the 5hr sample in mol
                int_avg_mol (float): the average of the 4hr and 5hr intercept dilution spaces in mol
                adj_plat_avg_mol (float): average plateau dilution space adjusted for the subject weight change over
                           the sampling period, in mol
                adj_int_avg_mol (float): average intercept dilution space adjusted for the subject weight change over
                           the sampling period, in mol
                adj_plat_avg_kg (float): average plateau dilution space adjusted for the subject weight change over
                           the sampling period, in kg
                adj_int_avg_kg (float): average intercept dilution space adjusted for the subject weight change over
                           the sampling period, in kg
           dil_space_ratio (float): ratio of the 4 hr plateau deuterium and 18O dilution spaces
           total_body_water_d_kg (float): total body water calculated from the average D plateau dilution space, in kg
           total_body_water_o_kg (float): total body water calculated from the average 18O plateau dilution space, in kg
           total_body_water_ave_kg (float): average of total_body_water_d_kg and total_body_water_o_kg, in kg
           fat_free_mass_kg (float): fat free mass of the subject, in kg
           fat_mass_kg (float): fat mass of the subject, in kg
           body_fat_percent (float): body fat percent of the subject, in percent
           schoeller_co2_int (float): CO2 production rate in mol/hr using the equation of Schoeller (equation A6, 1986
                              as updated in 1988) using the weight adjusted, average, intercept dilution spaces
           schoeller_co2_plat (float): CO2 production rate in mol/hr using the equation of Schoeller (equation A6, 1986
                              as updated in 1988) using the weight adjusted, average, plateu dilution spaces
           schoeller_co2_int_mol_day (float): CO2 production rate in mol/day using the equation of Schoeller (equation
                            A6, 1986 as updated in 1988) using the weight adjusted, average, intercept dilution spaces
           schoeller_co2_int_L_day (float): CO2 production rate in L/day using the equation of Schoeller (equation
                            A6, 1986 as updated in 1988) using the weight adjusted, average, intercept dilution spaces
           schoeller_tee_int_kcal_day (float): Total energy expenditure calculated using the equation of Weir (1949) from co2
                            values calculated via Schoeller and the weight adjusted, average, intercept dilution spaces,
                            in kcal/day
           schoeller_tee_plat_kcal_day (float): Total energy expenditure calculated using the equation of Weir (1949) from co2
                              values calculated via Schoeller and the weight adjusted, average, plateau dilution spaces,
                              in kcal/day
           schoeller_tee_int_mj_day (float): Total energy expenditure calculated using the equation of Weir (1949) from
                            co2 values calculated via Schoeller and the weight adjusted, average, intercept dilution
                            spaces, in mj/day
           schoeller_tee_plat_mj_day (float): Total energy expenditure calculated using the equation of Weir (1949) from
                            co2 values calculated via Schoeller and the weight adjusted, average, plateau dilution
                            spaces, in mj/day
           d_ratio_percent (float): Percent difference between the 4hr and 5hr delta measurements of deuterium
           o18_ratio_percent (float): Percent difference between the 4hr and 5hr delta measurements of 18O
           ee_check (float): Data quality check consisting of the percent difference between the TEE (in kcal/day)
                            calculated using the PD4/ED4 pair and the TEE calculated using the PD5/ED5 pair, both with
                            the plateau method.
    """

    def __init__(self, d_deltas, o_18deltas, sample_datetimes, dose_weights, mol_masses, dose_enrichments,
                 subject_weights):
        """Constructor for the DLWSubject class
           :param d_deltas (np.array): deuterium delta values of subject samples
           :param o_18deltas (np.array): oxygen 18 delta values of subject samples
           :param sample_datetimes ([datetime]): dates and times of sample collections
           :param dose_weights ([float]): weights in g of doses administered, deuterium first, 18O second
           :param mol_masses ([float]): molecular masses in g/mol of doses administered, deuterium first, 18O second
           :param dose_enrichments ([float]): dose enrichments in ppm of doses administered, deuterium first, 18O second
           :param subject_weights ([float]): initial and final weights of the subject in kg
        """
        if len(d_deltas) == len(o_18deltas) == len(sample_datetimes) == 5:
            # how to test that dates are in order?
            self.d_deltas = d_deltas
            self.o18_deltas = o_18deltas
            self.sample_datetimes = sample_datetimes
            self.dose_weights = dose_weights
            self.mol_masses = mol_masses
            self.dose_enrichments = np.array(dose_enrichments)/1000000   #convert from ppm to ratio
            self.subject_weights = subject_weights

            self.d_ratios = self.d_deltas_to_ratios()
            self.o18_ratios = self.o18_deltas_to_ratios()

            self.kd_per_hr = self.average_turnover_2pt(self.d_ratios, self.sample_datetimes)
            self.ko_per_hr = self.average_turnover_2pt(self.o18_ratios, self.sample_datetimes)
            self.ko_kd_ratio = self.ko_per_hr / self.kd_per_hr

            self.nd = self.calculate_various_nd(self)
            self.no = self.calculate_various_no(self)

            self.dil_space_ratio = self.nd['plat_4hr_mol'] / self.no['plat_4hr_mol']  # dilution space ratio err flag

            # self.rh2o = (self.nd['adj_plat_avg_kg'] * self.kd_per_hr * HOURS_PER_DAY) / STANDARD_WATER_MOL_MASS

            self.total_body_water_d_kg = self.nd['adj_plat_avg_kg'] / POP_DIL_SPACE_D
            self.total_body_water_o_kg = self.no['adj_plat_avg_kg'] / POP_DIL_SPACE_O
            self.total_body_water_ave_kg = (self.total_body_water_d_kg + self.total_body_water_o_kg) / 2  # average total body water

            self.fat_free_mass_kg = self.total_body_water_ave_kg / FAT_FREE_MASS_FACTOR
            self.fat_mass_kg = self.subject_weights[0] - self.fat_free_mass_kg
            self.body_fat_percent = self.fat_mass_kg / self.subject_weights[0] * 100

            self.schoeller_co2_int = self.calc_schoeller_co2(self.nd['adj_int_avg_mol'], self.no['adj_int_avg_mol'],
                                                             self.kd_per_hr, self.ko_per_hr)
            self.schoeller_co2_plat = self.calc_schoeller_co2(self.nd['adj_plat_avg_mol'], self.no['adj_plat_avg_mol'],
                                                              self.kd_per_hr, self.ko_per_hr)

            self.schoeller_co2_int_mol_day = self.schoeller_co2_int * HOURS_PER_DAY  # rco2 mols/day
            self.schoeller_co2_int_L_day = self.schoeller_co2_int * LITERS_PER_MOL  # r2co2 l/day

            self.schoeller_tee_int_kcal_day = self.co2_to_tee(self.schoeller_co2_int)
            self.schoeller_tee_plat_kcal_day = self.co2_to_tee(self.schoeller_co2_plat)

            self.schoeller_tee_int_mj_day = self.schoeller_tee_int_kcal_day * MJ_PER_KCAL
            self.schoeller_tee_plat_mj_day = self.schoeller_tee_plat_kcal_day * MJ_PER_KCAL

            self.d_ratio_percent = self.percent_difference(self.d_ratios[1]-self.d_ratios[0],
                                                           self.d_ratios[2]-self.d_ratios[0])  # err flag 2 h plateau < 5%
            self.o18_ratio_percent = self.percent_difference(self.o18_ratios[1],
                                                             self.o18_ratios[2])  # err flag o18 plateau
            self.ee_check = self.ee_consistency_check()  # err flag # 4 pd4

        else:
            raise ValueError('Arrays not correct size')

    def d_deltas_to_ratios(self):
        """Convert deuterium delta values to ratios.
           :return: deuterium ratios"""
        return ((self.d_deltas / 1000) + 1) * D_VSMOW_RATIO

    def o18_deltas_to_ratios(self):
        """Convert 18O delta values to ratios.
           :return: 18O ratios"""
        return ((self.o18_deltas / 1000) + 1) * O18_VSMOW_RATIO

    @staticmethod
    def isotope_turnover_2pt(background, initratio, finalratio, elapsedhours):
        """Calculate an isotope turnover rate in 1/hr using the 2pt method
           :param background:  enrichment of the background urine measurement as a ratio
           :param initratio: enrichment of the initial urine measurement as a ratio
           :param finalratio: enrichment of the final urine measurement as a ratio
           :param elapsedhours: elapsed time in hours between the intial and final urine measurements
           :return: istope turnover rate in 1/hr
        """
        if (background < initratio and background < finalratio and finalratio < initratio):
            return (np.log(initratio - background) - np.log(finalratio - background)) / elapsedhours
        else:
            raise ValueError('Isotope ratios do not conform to pattern background < final < plateau')

    def average_turnover_2pt(self, ratios, sampledatetime):
        """Calculate the average isotope turnover rate in 1/hr using the 2pt method
           :param ratios: measured urine isotope ratios
           :param sampledatetime: time and date of urine collections
           :return: average isotope turnover rate in 1/hr"""
        turnovers = np.zeros(4)

        elapsedhours = (timedelta.total_seconds(sampledatetime[3] - sampledatetime[1])) / 3600
        turnovers[0] = self.isotope_turnover_2pt(ratios[0], ratios[1], ratios[3], elapsedhours)

        elapsedhours = (timedelta.total_seconds(sampledatetime[4] - sampledatetime[1])) / 3600
        turnovers[1] = self.isotope_turnover_2pt(ratios[0], ratios[1], ratios[4], elapsedhours)

        elapsedhours = (timedelta.total_seconds(sampledatetime[3] - sampledatetime[2])) / 3600
        turnovers[2] = self.isotope_turnover_2pt(ratios[0], ratios[2], ratios[3], elapsedhours)

        elapsedhours = (timedelta.total_seconds(sampledatetime[4] - sampledatetime[2])) / 3600
        turnovers[3] = self.isotope_turnover_2pt(ratios[0], ratios[2], ratios[4], elapsedhours)
        return np.mean(turnovers)

    @staticmethod
    def calculate_various_nd(self):
        """Calculate the various dilution spaces for nd.
            :return: dict of dilution spaces for deuterium"""

        nd = {}
        nd['plat_4hr_mol'] = self.dilution_space_plateau(self.dose_weights[0], self.mol_masses[0],
                                                         self.dose_enrichments[0], self.d_ratios[1], self.d_ratios[0])
        nd['plat_5hr_mol'] = self.dilution_space_plateau(self.dose_weights[0], self.mol_masses[0],
                                                         self.dose_enrichments[0], self.d_ratios[2], self.d_ratios[0])
        nd['plat_avg_mol'] = (nd['plat_4hr_mol'] + nd['plat_5hr_mol']) / 2

        dosetime = timedelta.total_seconds(self.sample_datetimes[1] - self.sample_datetimes[0]) / 3600
        nd['int_4hr_mol'] = self.dilution_space_intercept(self.dose_weights[0], self.mol_masses[0],
                                                          self.dose_enrichments[0], self.d_ratios[1], self.d_ratios[0],
                                                          self.kd_per_hr, dosetime)
        dosetime = timedelta.total_seconds(self.sample_datetimes[2] - self.sample_datetimes[0]) / 3600
        nd['int_5hr_mol'] = self.dilution_space_intercept(self.dose_weights[0], self.mol_masses[0],
                                                          self.dose_enrichments[0], self.d_ratios[2], self.d_ratios[0],
                                                          self.kd_per_hr, dosetime)
        nd['int_avg_mol'] = (nd['int_4hr_mol'] + nd['int_5hr_mol']) / 2

        nd['adj_plat_avg_mol'] = self.adj_dilution_space(nd['plat_avg_mol'], self.subject_weights)
        nd['adj_int_avg_mol'] = self.adj_dilution_space(nd['int_avg_mol'], self.subject_weights)
        nd['adj_plat_avg_kg'] = nd['adj_plat_avg_mol'] * STANDARD_WATER_MOL_MASS
        nd['adj_int_avg_kg'] = nd['adj_int_avg_mol'] * STANDARD_WATER_MOL_MASS
        return nd

    @staticmethod
    def calculate_various_no(self):
        """Calculate the various dilution spaces for nd.
            :return: dict of dilution spaces for deuterium"""

        no = {}
        no['plat_4hr_mol'] = self.dilution_space_plateau(self.dose_weights[1], self.mol_masses[1],
                                                         self.dose_enrichments[1], self.o18_ratios[1],
                                                         self.o18_ratios[0])
        no['plat_5hr_mol'] = self.dilution_space_plateau(self.dose_weights[1], self.mol_masses[1],
                                                         self.dose_enrichments[1], self.o18_ratios[2],
                                                         self.o18_ratios[0])
        no['plat_avg_mol'] = (no['plat_4hr_mol'] + no['plat_5hr_mol']) / 2

        dosetime = timedelta.total_seconds(self.sample_datetimes[1] - self.sample_datetimes[0]) / 3600
        no['int_4hr_mol'] = self.dilution_space_intercept(self.dose_weights[1], self.mol_masses[1],
                                                          self.dose_enrichments[1], self.o18_ratios[1],
                                                          self.o18_ratios[0], self.ko_per_hr, dosetime)
        dosetime = timedelta.total_seconds(self.sample_datetimes[2] - self.sample_datetimes[0]) / 3600
        no['int_5hr_mol'] = self.dilution_space_intercept(self.dose_weights[1], self.mol_masses[1],
                                                          self.dose_enrichments[1], self.o18_ratios[2],
                                                          self.o18_ratios[0], self.ko_per_hr, dosetime)
        no['int_avg_mol'] = (no['int_4hr_mol'] + no['int_5hr_mol']) / 2

        no['adj_plat_avg_mol'] = self.adj_dilution_space(no['plat_avg_mol'], self.subject_weights)
        no['adj_int_avg_mol'] = self.adj_dilution_space(no['int_avg_mol'], self.subject_weights)
        no['adj_plat_avg_kg'] = no['adj_plat_avg_mol'] * STANDARD_WATER_MOL_MASS
        no['adj_int_avg_kg'] = no['adj_int_avg_mol'] * STANDARD_WATER_MOL_MASS
        return no

    @staticmethod
    def dilution_space_plateau(doseweight, molmass, doseenrichment, plateauenrichment, background):
        """Calculate a dilution space using the plateau method.
           :param doseweight: weight of the does in grams
           :param molmass: moleular mass of the dose in grams/mol
           :param doseenrichment: enrichment of the dose in ppm
           :param plateauenrichment: enrichment of the plateau urine measurement as a ratio
           :param background: enrichment of the background urine measurement as a ratio
           :return: dilution space calculated by the plateau method in mol
        """

        return doseweight / molmass * (doseenrichment - plateauenrichment) / (plateauenrichment - background)

    @staticmethod
    def dilution_space_intercept(doseweight, molmass, doseenrichment, plateauenrichment, background,
                                 turnoverrate, dosetime):
        """Calculate a dilution space using the intercept method.
           :param doseweight: weight of the does in grams
           :param molmass: moleular mass of the dose in grams/mol
           :param doseenrichment: enrichment of the dose in ppm
           :param plateauenrichment: enrichment of the plateau urine measurement in ppm
           :param background: enrichment of the background urine measurement in ppm
           :param turnoverrate: isotope turnover rate in 1/hr
           :param dosetime: time and date of dose administration
           :return: dilution space calculated by the intercept method in mol
        """

        interceptenrichment = (plateauenrichment - background) * np.exp(dosetime * turnoverrate) + background

        return doseweight / molmass * (doseenrichment - interceptenrichment) / (interceptenrichment - background)

    def avg_intercept_dilution_space(self, doseweight, molmass, doseenrichment, turnoverrate, ratios, sampledatetime):
        """Calculate the average of the 4 and 5 hour dilution spaces calculated by the intercept method
           :param doseweight: weight of the does in grams
           :param molmass: moleular mass of the dose in grams/mol
           :param doseenrichment: enrichment of the dose in ppm
           :param turnoverrate: isotope turnover rate in 1/hr
           :param ratios: measured urine isotope ratios
           :param sampledatetime: time and date of urine collections
           :return: average of the 4 and 5 hour dilution spaces calculated by the intercept method in mol
        """
        dilspace = np.zeros(2)
        dosetime = np.zeros(2)

        dosetime[0] = timedelta.total_seconds(sampledatetime[1] - sampledatetime[0]) / 3600
        dilspace[0] = self.dilution_space_intercept(doseweight, molmass, doseenrichment, ratios[1], ratios[0],
                                                    turnoverrate, dosetime[0])

        dosetime[1] = timedelta.total_seconds(sampledatetime[2] - sampledatetime[0]) / 3600
        dilspace[1] = self.dilution_space_intercept(doseweight, molmass, doseenrichment, ratios[2], ratios[0],
                                                    turnoverrate, dosetime[1])
        return np.mean(dilspace)

    @staticmethod
    def adj_dilution_space(dilution_space, subject_weights):
        """Adjust the given dilution space by the beginning and end subject weights to produce an average dilution space.
           :param dilution_space: unadjusted dilution space
           :param subject_weights: array containing before and after subject weights
           :return adj_dilution_space: dilution space in mol adjusted for the subject weight change over the
                                       sampling period
        """
        begin_dilution_spacekg = dilution_space * STANDARD_WATER_MOL_MASS
        end_dilution_spacekg = subject_weights[1] / subject_weights[0] * begin_dilution_spacekg

        adj_dilution_space = ((begin_dilution_spacekg + end_dilution_spacekg) / 2) / STANDARD_WATER_MOL_MASS
        return adj_dilution_space

    @staticmethod
    def calc_schoeller_co2(nd, no, kd, ko):
        """Calculate CO2 production in mol/hr using the equation of Schoeller (equation A6, 1986 as updated in 1988)
                from dilution spaces and isotope turnover rates.
           :param nd: deuterium dilution space in mol
           :param no: oxygen dilution space in mol
           :param kd: deuterium turnover rate in 1/hr
           :param ko: oxygen turnover rate in 1/hr
           :return co2prod: co2 production rate in mol/hr
        """
        n = ((no / 1.01) + (nd / 1.04)) / 2
        co2_prod = (n / 2.078) * (1.01 * ko - 1.04 * kd) - 0.0246 * n * 1.05 * (1.01 * ko - 1.04 * kd)
        # reduces to co2prod = n*(0.459952*ko_per_hr - 0.47362*kd_per_hr)
        return co2_prod

    @staticmethod
    def co2_to_tee(co2):
        """Convert CO2 production to total energy expenditure in using the equation of Weir, J.B. J Physiol., 109(1-2):1-9, 1949
           :param co2: volume of co2 production in mol/hr
           :return: total energy expenditure in kcal/day
        """
        return co2 * LITERS_PER_MOL * HOURS_PER_DAY * WEIR_CONSTANT

    @staticmethod
    def percent_difference(first, second):
        """Calculate the percent difference between two values """
        return ((first - second) / ((first+second)/2) * 100)

    def ee_consistency_check(self):
        """Calculate the percentage difference between the energy expenditure measured using the PD4/ED4 pair and
            the PD5/ED5 pair
            :return: percentage differences"""
        elapsedhours = (timedelta.total_seconds(self.sample_datetimes[3] - self.sample_datetimes[1])) / 3600
        kd_4hr = self.isotope_turnover_2pt(self.d_ratios[0], self.d_ratios[1], self.d_ratios[3], elapsedhours)
        ko_4hr = self.isotope_turnover_2pt(self.o18_ratios[0], self.o18_ratios[1], self.o18_ratios[3], elapsedhours)

        elapsedhours = (timedelta.total_seconds(self.sample_datetimes[4] - self.sample_datetimes[2])) / 3600
        kd_5hr = self.isotope_turnover_2pt(self.d_ratios[0], self.d_ratios[2], self.d_ratios[4], elapsedhours)
        ko_5hr = self.isotope_turnover_2pt(self.o18_ratios[0], self.o18_ratios[2], self.o18_ratios[4], elapsedhours)

        schoeller_4hr = self.calc_schoeller_co2(self.nd['int_4hr_mol'], self.no['int_4hr_mol'], kd_4hr, ko_4hr)
        schoeller_5hr = self.calc_schoeller_co2(self.nd['int_5hr_mol'], self.no['int_5hr_mol'], kd_5hr, ko_5hr)

        tee_4hr = self.co2_to_tee(schoeller_4hr)
        tee_5hr = self.co2_to_tee(schoeller_5hr)

        diff = self.percent_difference(tee_4hr, tee_5hr)
        return diff

    def save_results_csv(self, filename):
        """ Save the results to a csv file
            :param: filename(string), the name of the file to which to save"""
        write_header = 'rCO2_mol/day,rCO2_L/day,EE_kcal/day,EE_MJ/day'
        write_data = np.asarray(
            [[self.schoeller_co2_int_mol_day, self.schoeller_co2_int_L_day, self.schoeller_tee_int_kcal_day,
              self.schoeller_tee_int_mj_day]])
        np.savetxt(filename, write_data, delimiter=',', header=write_header, comments='')
