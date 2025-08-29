# app.py
# -*- coding: utf-8 -*-
"""
Streamlit Web App for Interactive Microscope Sampling Performance Visualization
"""

import numpy as np
import matplotlib.pyplot as plt
import streamlit as st


def opt_resolution(wavelength_nm, objective_mag, numerical_aperture, additional_mag=1):
    """
    Calculate the ideal camera pixel size for a microscope system.
    """
    wavelength_um = wavelength_nm / 1000.0
    resolution_um = 0.61 * wavelength_um / numerical_aperture
    total_mag = objective_mag * additional_mag
    camera_res_um = resolution_um * total_mag
    return camera_res_um


def plot_pxl_per_blurr(magnification, num_aprt, wavelength_nm, pxl_ref, additional_mag, xscale="log"):
    """
    Generate heatmap of pixels-per-blur ratio.
    """
    x_mag, y_na = np.meshgrid(magnification, num_aprt)
    px_per_blurr = opt_resolution(wavelength_nm, x_mag, y_na, additional_mag) / pxl_ref
    Z = px_per_blurr.reshape(len(num_aprt), len(magnification))

    fig, ax = plt.subplots(figsize=(7, 7))

    #plt.style.use('dark_background')

    im = ax.imshow(
        Z,
        origin="lower",
        extent=[min(magnification), max(magnification),
                min(num_aprt), max(num_aprt)],
        aspect="auto",
        cmap="rainbow",
        vmin=0, vmax=4,
        interpolation="none"
    )

    ax.set_xlabel("Magnification")
    ax.set_ylabel("Numerical Aperture")
    ax.set_title(f"Optical Sampling Performance:\n "
                 f"{pxl_ref:.1f} µm pixels, {wavelength_nm:.0f} nm, add. mag {additional_mag:.1f}×\n")
    ax.grid(True, linestyle="dotted")
    ax.minorticks_on()
    ax.set_xscale(xscale)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, orientation="horizontal", pad=0.15)
    cbar.set_label("Pixels per blur element")
    cbar.set_ticks([0, 1, 2, 3, 4])
    cbar.set_ticklabels(["0", "1", "2 (Nyquist)", "3", ">4"])

    cbar.ax.text(0.1, -1.5, "Undersampling", transform=cbar.ax.transAxes,
                 ha='center', va='top', color="black", fontsize=9)
    cbar.ax.text(0.9, -1.5, "Oversampling", transform=cbar.ax.transAxes,
                 ha='center', va='top', color="black", fontsize=9)

    return fig


# ------------------- STREAMLIT APP -------------------
st.title("pco.calculator - Nyquist Sampling")

# Sidebar controls
st.sidebar.header("Controls")

wavelength = st.sidebar.slider("Wavelength [nm]", 200, 900, 500, step=10)
pxl_ref = st.sidebar.slider("Pixel size [µm]", 1.0, 13.0, 3.8, step=0.1)
add_mag = st.sidebar.slider("Additional Magnification", 1.0, 5.0, 1.0, step=0.1)
xscale_choice = st.sidebar.radio("X-axis scale", ["log", "linear"], index=0)

# Compute and plot
magnification = list(np.linspace(1, 101, 400))
num_aprt = list(np.arange(0.095, 1.6, 0.02))

fig = plot_pxl_per_blurr(magnification, num_aprt, wavelength, pxl_ref, add_mag, xscale=xscale_choice)
st.pyplot(fig)


