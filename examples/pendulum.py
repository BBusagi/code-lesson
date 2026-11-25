"""Simple pendulum: compare two integrators by how well they keep the energy constant.
Explicit Euler gains energy every step; semi-implicit (symplectic) Euler stays close to the start value.
"""

import math

# ---- 1. Parameters ----
G, L = 9.81, 1.0          # gravity [m/s^2], rod length [m]
DT, T_END = 0.01, 20.0    # time step and duration [s]
THETA0 = math.radians(30)  # start angle, released from rest


def energy(theta, omega):
    """Total energy per unit mass [J/kg]: kinetic + potential."""
    return 0.5 * (L * omega) ** 2 + G * L * (1 - math.cos(theta))


# ---- 2. Integrators: one step of theta'' = -(g/L) sin(theta) ----
def explicit_euler(theta, omega):
    return theta + DT * omega, omega - DT * G / L * math.sin(theta)


def semi_implicit_euler(theta, omega):
    omega = omega - DT * G / L * math.sin(theta)  # ★ update velocity first ...
    return theta + DT * omega, omega              # ... then use the new velocity for the position


# ---- 3. Run both and print the energy drift every 5 s ----
E0 = energy(THETA0, 0.0)
for name, step in (("explicit", explicit_euler), ("semi-implicit", semi_implicit_euler)):
    theta, omega = THETA0, 0.0
    for k in range(1, round(T_END / DT) + 1):
        theta, omega = step(theta, omega)
        if k % round(5.0 / DT) == 0:
            drift = (energy(theta, omega) - E0) / E0 * 100
            print(f"{name:13s} t={k * DT:5.1f}s  angle={math.degrees(theta):7.2f} deg  energy drift={drift:+7.2f} %")
