import math
import functools

import numpy as np


def tsai_hill(
        mat,
        sigma1: float,
        sigma2: float,
        sigma3: float,
        tau12: float,
        tau13: float,
        tau23: float,
):
    X = mat.T1 if sigma1 >= 0 else mat.C1
    Y = mat.T2 if sigma2 >= 0 else mat.C2
    S = mat.SC
    mode = None
    # Return failure index
    fail_index = (
            (sigma1 ** 2) / (X ** 2)
            - (sigma1 * sigma2) / (X ** 2)
            + (sigma2 ** 2) / (Y ** 2)
            + (tau12 ** 2) / (S ** 2)
    )
    uc = fail_index ** 0.5
    return fail_index, mode


def tsai_wu(
        mat,
        sigma1: float,
        sigma2: float,
        sigma3: float,
        tau12: float,
        tau13: float,
        tau23: float,
):
    # TODO: needs checking
    Xt = mat.T1
    Xc = mat.C1
    Yt = mat.T2
    Yc = mat.C2
    S21 = mat.S12

    f11 = 1 / (Xt * Xc)
    f22 = 1 / (Yt * Yc)
    f12 = -1 / (2 * (Xt * Xc * Yt * Yc) ** (1 / 2))
    f66 = 1 / (S21 ** 2)
    f1 = 1 / Xt - 1 / Xc
    f2 = 1 / Yt - 1 / Yc

    a = f11 * sigma1 ** 2 + f22 * sigma2 ** 2 + f66 * tau12 ** 2 + 2 * f12 * sigma1 * sigma2
    b = f1 * sigma1 + f2 * sigma2

    fail_index = (-b + (b ** 2 + 4 * a) ** (1 / 2)) / (2 * a)
    mode = None
    uc = None
    return fail_index, mode


class IsoMaterial:
    def __init__(self, name, E, nu, G, rho):
        self.name = name
        self.E = E
        self.nu = nu
        self.G = G
        self.rho = rho


class OrthoMaterial:
    def __init__(self, name, E1, E2, nu12, G12, rho, T1=None, C1=None, T2=None, C2=None, SC=None, vf=None):
        nu21 = (nu12 * E2) / E1
        self.name = name
        self.vf = vf

        self.E1 = E1
        self.E2 = E2
        self.E3 = E2
        self.nu12 = nu12
        self.nu13 = nu12
        self.nu23 = 0.4
        self.G12 = G12
        self.G13 = G12
        self.G23 = 3500
        self.rho = rho

        self.nu21 = nu21
        self.nu31 = self.nu13 * (self.E3 / self.E1)
        self.nu32 = self.nu23 * (self.E3 / self.E2)
        self.G21 = self.E2 / (2 * (1 + self.nu21))
        self.G31 = self.E3 / (2 * (1 + self.nu31))
        self.G32 = self.E3 / (2 * (1 + self.nu32))

        self.T1 = T1
        self.T2 = T2
        self.C1 = C1
        self.C2 = C2
        self.SC = SC

        self.Q = (1 / (1-nu12*nu21)) * np.array([[E1, E1*nu21, 0], [E2*nu12, E2, 0], [0, 0, G12]])

@functools.lru_cache(maxsize=512)
def cs(angle):
    a = math.radians(angle)
    c, s = math.cos(a), math.sin(a)
    return c, s


@functools.lru_cache(maxsize=512)
def transformation_matrix(angle):
    c, s = cs(angle)
    return np.array(
        [
            [c ** 2, s ** 2, -2 * s * c],
            [s ** 2, c ** 2, 2 * s * c],
            [s * c, -s * c, c ** 2 - s ** 2],
        ]
    )


@functools.lru_cache(maxsize=512)
def stress_transformation_matrix(angle):
    # Kollar 2.9.1
    # global (xy) -> local (12)
    c, s = cs(angle)
    return np.array(
        [
            [c ** 2, s ** 2, 2 * s * c],
            [s ** 2, c ** 2, -2 * s * c],
            [-s * c, s * c, c ** 2 - s ** 2],
        ]
    )


@functools.lru_cache(maxsize=512)
def strain_transformation_matrix(angle):
    # global (xy) -> local (12)
    c, s = cs(angle)
    return np.array(
        [
            [c ** 2, s ** 2, s * c],
            [s ** 2, c ** 2, -s * c],
            [-2 * s * c, 2 * s * c, c ** 2 - s ** 2],
        ]
    )


def ABD_matrix(laminate):
    A, B, D = np.zeros((3, 3)), np.zeros((3, 3)), np.zeros((3, 3))
    zs = len(laminate.plies) * [0]  # mid plane of ply
    zs[0] = laminate.t/2 - laminate.plies[0].t / 2

    for i in range(len(laminate.plies)-1):
        zs[i+1] = zs[i] - laminate.plies[i].t/2 - laminate.plies[i+1].t/2

    for z, ply in zip(zs, laminate.plies):
        Qbar = ply.Qbar
        t= ply.t
        A += Qbar * t
        B += Qbar * t * z
        D += Qbar * t * (t*t/12 + z*z)

    # Finish the matrices, discarding very small numbers in ABD.
    A[(A < 1e-6)] = 0.0
    B[(B < 1e-6)] = 0.0
    D[(D < 1e-6)] = 0.0

    return np.bmat([[A, B], [B, D]])


class AnglePly:
    def __init__(self, material: OrthoMaterial, angle, t, fail_criterion=None):
        self.material = material
        self.angle = angle
        self.t = t
        self.fail_criterion = fail_criterion

    @property
    def rho(self):
        return self.material.rho

    @property
    def vf(self):
        return self.material.vf

    def failure(self, sigma1, sigma2, sigma3, tau12, tau13, tau23):
        return self.fail_criterion(self.material, sigma1, sigma2, sigma3, tau12, tau13, tau23)

    def apply_global_strain(self, global_strain):
        self.strain = self.T_strain.dot(global_strain)
        self.stress = self.Q.dot(self.strain)

    @property
    def T(self):
        return transformation_matrix(self.angle)

    @property
    def T_stress(self):
        return stress_transformation_matrix(self.angle)

    @property
    def T_strain(self):
        return strain_transformation_matrix(self.angle)

    @property
    def Q(self):
        return self.material.Q

    @property
    def Qbar(self):
        return self.T.dot(self.Q).dot(self.T.T)

    def rotated(self, angle):
        return AnglePly(self.material, self.angle + angle, self.t, fail_criterion=self.fail_criterion)


class Laminate:
    def __init__(self, name, plies, poisson=True):
        self.name = name
        self.plies = plies
        self.t = sum(p.t for p in self.plies)
        self.poisson = poisson
        self.update()

    def __repr__(self):
        return f"<Laminate '{self.name}': {len(self.plies)} plies, thickness={self.t}"

    def update(self):
        self.ABD = ABD_matrix(self)
        self.abd = np.linalg.inv(self.ABD)

    @property
    def Ex(self):
        abd = self.abd
        return 1 / (abd[0,0] * self.t)

    @property
    def Ey(self):
        abd = self.abd
        return 1 / (abd[1,1] * self.t)

    @property
    def Gxy(self):
        abd = self.abd
        return 1 / (abd[2,2] * self.t)

    @property
    def nuxy(self):
        abd = self.abd
        return -abd[0,1] / abd[0,0]

    @property
    def nuyx(self):
        abd = self.abd
        return -abd[0,1] / abd[1,1]

    def rotated(self, angle):
        return Laminate(self.name, [ply.rotated(angle) for ply in self.plies], poisson=self.poisson)

    def copy(self):
        return Laminate(self.name, [AnglePly(ply.material, ply.angle, ply.t, fail_criterion=ply.fail_criterion) for ply in self.plies], poisson=self.poisson)

    def apply_load(self, F):
        # evaluate only stress at mid point -> for progressive failure analysis sufficient
        global_strain = self.abd.dot(F)

        h = -self.t / 2
        for ply in self.plies:
            ply.apply_global_strain(global_strain[0:3] + (h + ply.t / 2) * global_strain[3:6])
            h += ply.t

    def calculate_monoaxial_strength(self, lpf=False):

        loads = {
            "x":  (1, 0, 0, 0, 0, 0),
            "y":  (0, 1, 0, 0, 0, 0),
            "xy": (0, 0, 1, 0, 0, 0)
        }
        for direction, load in loads.items():
            fail_stresses, fail_strains = progressive_failure(*load, signs=(-1, 1))
            setattr(self, f"S{direction}", fail_stresses)


    @property
    def rho(self):
        return sum(ply.rho * ply.t for ply in self.plies) / sum(ply.t for ply in self.plies)

    @property
    def vf(self):
        return sum(ply.vf * ply.t for ply in self.plies) / sum(ply.t for ply in self.plies)


def progressive_failure(laminate, *load, stepsizes=(25, 5, 1), progressive=False):
    def has_failed(laminate):
        for ply in laminate.plies:
            if not ply.failed:
                return False
        return True

    def failed_material(material, fail_mode):
        m = material
        return OrthoMaterial(m.name, E1=m.E1 / 1000, E2=m.E2 / 1000, nu12=m.nu12, G12=m.G12 / 1000, rho=m.rho)

    stepsize = stepsizes[0]
    F = np.array(load).T
    dF = stepsize * F / np.linalg.norm(F)
    F = dF

    # perform the analysis on a copy (we will alter ply properties in the process)
    laminate = laminate.copy()

    # add a flag to indicate ply failure
    for ply in laminate.plies:
        ply.failed = False

    fail_stresses = []
    while not has_failed(laminate):
        laminate.apply_load(F)

        damage = False
        refine_step = False
        for ply in laminate.plies:
            # failure is evaluated at mid-plane
            if not ply.failed:  # not already failed in previous step -> potentially new damage
                fail_index, fail_mode = ply.failure(sigma1=ply.stress[0, 0], sigma2=ply.stress[1, 0], sigma3=0,
                                                    tau12=ply.stress[2, 0], tau13=0, tau23=0)

                if fail_index > 1:  # failed
                    if stepsize == stepsizes[-1]:  # finest step
                        ply.failed = True
                        ply.material = failed_material(ply.material, fail_mode)
                        damage = True
                    else:
                        refine_step = True

        if damage:
            laminate.update()
            fail_stresses.append(tuple((np.linalg.norm(F / laminate.t) * dF.T)[0]))
            stepsize = stepsizes[0]
            if not progressive:  # not actually increasing the stress
                return fail_stresses
        else:
            if refine_step:
                F = F - dF  # step back
                stepsize = stepsizes[stepsizes.index(stepsize) - 1]  # refine step
                dF = stepsize * F / np.linalg.norm(F)
            F = F + dF  # increase load

    return fail_stresses


def monoaxial_strength(laminate, progressive=False):
    xt = progressive_failure(laminate, (1, 0, 0, 0, 0, 0), progressive=progressive)
    xc = progressive_failure(laminate, (-1, 0, 0, 0, 0, 0), progressive=progressive)
    yt = progressive_failure(laminate, (0, 1, 0, 0, 0, 0), progressive=progressive)
    yc = progressive_failure(laminate, (0, -1, 0, 0, 0, 0), progressive=progressive)
    xy = progressive_failure(laminate, (0, 0, 1, 0, 0, 0), progressive=progressive)
    fpf = {"xt": xt[0][0], "yt": yt[0][1], "xc": xc[0][0], "yc": yc[0][1], "xy": xy[0][2]}  # 1st index: step, 2nd index: direction (x=0, y=1, xy=2)
    if progressive:
       lpf = {"xt": xt[-1][0], "yt": yt[-1][1], "xc": xc[-1][0], "yc": yc[-1][1], "xy": xy[-1][2]}
    else:
        lpf = None

    return fpf, lpf

def quad_angle_laminate(name, material, *, t, p0, p90, p45, p0c=0, carbon=None, poisson=True, fail_criterion=tsai_hill):
    if carbon is None:
        p0c = 0

    ptot = p0 + p90 + 2 * p45 + p0c
    ply0 = AnglePly(material, 0, p0 / ptot * t / 2, fail_criterion=fail_criterion)
    ply90 = AnglePly(material, 90, p90 / ptot * t / 2, fail_criterion=fail_criterion)
    plyp45 = AnglePly(material, 45, p45 / ptot * t / 2, fail_criterion=fail_criterion)
    plym45 = AnglePly(material, -45, p45 / ptot * t / 2, fail_criterion=fail_criterion)
    if carbon is not None and p0c / ptot > 0.01:
        ply0c = AnglePly(carbon, 0, p0c / ptot * t / 2, fail_criterion=fail_criterion)
        stack = [ply0, ply0c, ply90, plyp45, plym45, plym45, plyp45, ply90, ply0c, ply0]
    else:
        stack = [ply0, ply90, plyp45, plym45, plym45, plyp45, ply90, ply0]

    return Laminate(name, stack, poisson=poisson)


def polar_data(laminate, angle_step=1):
    angle = 0
    angles, Ex, Ey, Gxy = [], [], [], []
    while angle < 360 + angle_step:
        angle_laminate = laminate.rotated(angle)
        angles.append(angle)
        Ex.append(angle_laminate.Ex)
        Ey.append(angle_laminate.Ey)
        Gxy.append(angle_laminate.Gxy)
        angle += angle_step
    return {'angles': angles, 'Ex': Ex, 'Ey': Ey, 'Gxy': Gxy}


def strength_data(laminate, x, y, angle_step=1, progressive=False):
    index = {"x": 0, "y": 1, "xy": 2}
    angle = 0
    fpf = []
    if progressive:
        lpf = []
    else:
        lpf = None
    while angle < 360 + angle_step:
        load = [0, 0, 0, 0, 0, 0]
        ix = index[x]
        iy = index[y]
        load[ix] = math.cos(math.radians(angle))
        load[iy] = math.sin(math.radians(angle))

        fail_stresses = progressive_failure(laminate, load, progressive=progressive)
        fpf.append((fail_stresses[0][ix], fail_stresses[0][iy]))
        if progressive:
            lpf.append((fail_stresses[-1][ix], fail_stresses[-1][iy]))

        angle += angle_step
    return {"fpf": fpf, "lpf": lpf}

def polar_plot(laminate, fig=None):
    if fig is None:
        import plotly.graph_objects as go
        fig = go.Figure()

    plot_data = polar_data(laminate)
    Ex = go.Scatterpolar(r=plot_data['Ex'], theta=plot_data['angles'], thetaunit="degrees", name="Ex")
    Ey = go.Scatterpolar(r=plot_data['Ey'], theta=plot_data['angles'], thetaunit="degrees", name="Ey")
    Gxy = go.Scatterpolar(r=plot_data['Gxy'], theta=plot_data['angles'], thetaunit="degrees", name="Gxy")
    fig.layout.polar.angularaxis.rotation = 90
    fig.add_trace(Ex)
    fig.add_trace(Ey)
    fig.add_trace(Gxy)
    return fig


def strength_plot(laminate, x, y, angle_step=1, progressive=False, fig=None):
    if fig is None:
        import plotly.graph_objects as go
        fig = go.Figure()
    data = strength_data(laminate, x, y, angle_step=angle_step, progressive=progressive)
    fpf_line = go.Scatter(
        x=[s[0] for s in data["fpf"]], y=[s[1] for s in data["fpf"]], name="FPF"
    )
    lpf_line = go.Scatter(
        x=[s[0] for s in data["lpf"]], y=[s[1] for s in data["lpf"]], name="LPF"
    )
    fig.add_trace(fpf_line)
    fig.add_trace(lpf_line)
    return fig

if __name__ == "__main__":
    tonne = 1
    mm = 1
    N = 1
    kg = 0.001 * tonne
    m = 1000 * mm
    kN = 1000 * N

    rho_m = 1200 * kg / m ** 3
    rho_eg = 2570 * kg / m ** 3
    rho_c = 1800 * kg / m ** 3

    MPa = 1 * N/(mm*mm)
    GPa = 1000 * MPa

    CFRP = OrthoMaterial("CFRP", E1=148*GPa, E2=9.65*GPa, nu12=0.3, G12=4.55*GPa,
                                    rho=0.6 * rho_eg + 0.4 * rho_m, T1=800, C1=600, T2=100, C2=100, SC=50)

    def create_laminate(name, material, angles, thicknesses, fail_criterion=tsai_hill):
        plies = []
        for a, t in zip(angles, thicknesses):
            p = AnglePly(material, a, t, fail_criterion=fail_criterion)
            plies.append(p)
        return Laminate(name, plies, poisson=True)

    lam = create_laminate("test", CFRP, (0, 90, 45, -45, -45, 45, 90, 0), (1, 2, 2, 3, 3, 2, 2, 1))
    print(lam.ABD)
    print(lam.plies[0].Q)
    print("Ex:  ", lam.Ex)
    print("Ey:  ", lam.Ey)
    print("Gxy: ", lam.Gxy)
    print("nuxy:", lam.nuxy)
    print("nuyx:", lam.nuyx)

    # print(clt.progressive_failure(topskin, (1, 0, 0, 0, 0, 0), progressive=False))
    # print(clt.monoaxial_strength(topskin, progressive=False))