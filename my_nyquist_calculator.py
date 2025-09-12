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

def plot_nyquist_criterion(wavelength_nm, objective_mag, additional_mag, pxl_ref, ny_lim):
    """
    Calculate N.A.(objective_mag, pxl_ref)
    """

    num_aprt = 0.61/(ny_lim*1000) * wavelength_nm * objective_mag * additional_mag / pxl_ref

    return num_aprt

def plot_pxl_per_blurr(magnification, num_aprt, wavelength_nm, pxl_ref, additional_mag, xscale="log", yscale='lin'):
    """
    Generate heatmap of pixels-per-blur ratio.
    """
    x_mag, y_na = np.meshgrid(magnification, num_aprt)

    x_plot=magnification

    px_per_blurr = opt_resolution(wavelength_nm, x_mag, y_na, additional_mag) / pxl_ref
    Z = px_per_blurr.reshape(len(num_aprt), len(magnification))

    fig, ax = plt.subplots(figsize=(7, 7))

    im = ax.imshow(
        Z,
        origin="lower",
        extent=[min(magnification), max(magnification),
                min(num_aprt), max(num_aprt)],
        aspect="auto",
        cmap="rainbow_r",
        vmin=0, vmax=4,
        interpolation="none"
    )

    ny_lim_lines = [2.0,2.3,3.0]
    for ny_lim in ny_lim_lines:
        y_plot=[plot_nyquist_criterion(wavelength_nm, i, additional_mag, pxl_ref, ny_lim) for i in magnification]
        plt.plot(x_plot, y_plot, 
             ["-.","-","--"][ny_lim_lines.index(ny_lim)],
             linewidth=1,
             alpha=0.2,
             color='black',
             label=r"$\phi$ = {}".format(ny_lim))

    plt.legend()

    # typ_vals_mag = [4,10,20,40,60,100]
    # typ_cntr_vals_NA = [0.15,0.3,0.57,0.78, 1.1, 1.37]
    # typ_var_NA = [0.05,0.05,0.17,0.17,0.3,0.13]
    # typ_app = ["histology", "cell culture", "cell morphology", "sub cellular",
    #            "live cell", "fine sub-cellular"]
    
    # plt.errorbar(typ_vals_mag,
    #              typ_cntr_vals_NA,
    #              yerr=typ_var_NA,
    #              color='black',
    #              fmt='+', capsize=2, linewidth=0.3, 
    #              #label='typical values'
    #              )

    # # Add text next to each symbol
    # for i in range(len(typ_vals_mag)):
    #     plt.text(typ_vals_mag[i], typ_cntr_vals_NA[i], "{}".format(typ_app[i]),
    #              fontsize=5, rotation = 90, va='center', ha='right', color='black')
        
    ax.set_xlabel("Magnification M")
    ax.set_ylabel("Numerical Aperture N.A.")
    ax.set_title("Optical Sampling Performance:\n \n"
                 f"Settings: {pxl_ref:.1f} µm pixels | {wavelength_nm:.0f} nm | Add. Magn. {additional_mag:.1f}×\n")
    ax.grid(True, linestyle="-", alpha=0.4)
    ax.minorticks_on()
    ax.grid(which='minor', linestyle='dotted', alpha = 0.4)
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    ax.set_ylim(0.1,1.4)

    # Colorbar
    cbar = fig.colorbar(im, ax=ax, orientation="horizontal", pad=0.15)
    cbar.set_label(r"Pixels per Resolution Limit $\phi$")
    cbar.set_ticks([0, 1, 2, 3, 4])
    cbar.set_ticklabels(["0", "1", "2", "3", ">4"])

    cbar.ax.text(0.1, -1.5, "Undersampling", transform=cbar.ax.transAxes,
                 ha='center', va='top', color="black", fontsize=9)
    cbar.ax.text(0.9, -1.5, "Oversampling", transform=cbar.ax.transAxes,
                 ha='center', va='top', color="black", fontsize=9)

    return fig


# ------------------- STREAMLIT APP -------------------
st.title("pco.calculator - Nyquist Sampling")

st.write("""This is a small application to figure out which pixelsize best suits your microscope system. 
Use the slider bars on the sidebar to the left to set the illumination wavelength and the pixel pitch of your camera of interest, e.g. 2.5 µm 
for pco.panda 26, 4.6 µm for pco.edge 9.4 bi or 6.5 µm for pco.edge 4.2.
Further, you can account for any possible additional magnification within the optical path. You can change the scaling of the axes from
linear to logarithmic according to your preferences.""")

#st.write("""For ideal sampling performance it is generally understod that the optical resolution limit of the microscope should
#be 2 to 2.4 times the pixel pitch, which relates to a green to yellow color coding in the graph below. Under this condition,
#or system configuration, respectively, we speek of 'Nyquist Sampling'.""")

# Sidebar controls
st.sidebar.header("Controls")

wavelength = st.sidebar.slider("Wavelength [nm]", 200, 900, 500, step=10)
pxl_ref = st.sidebar.slider("Pixel size [µm]", 1.0, 13.0, 6.5, step=0.1)
add_mag = st.sidebar.slider("Additional Magnification", 1.0, 5.0, 1.0, step=0.1)
xscale_choice = st.sidebar.radio("Magnification axis scale", ["log", "linear"], index=0)
yscale_choice = st.sidebar.radio("NA axis scale", ["log", "linear"], index=1)


# Compute and plot
magnification = list(np.linspace(1, 101, 400))
num_aprt = list(np.arange(0.095, 1.6, 0.02))

fig = plot_pxl_per_blurr(magnification, num_aprt, wavelength, pxl_ref, add_mag, xscale=xscale_choice, yscale=yscale_choice)
st.pyplot(fig)

st.subheader("About the Nyquist Theorem")

st.write("""Resolution is the ability of an objective to definitively resolve an object, or group of objects, as a single entity(s). 
         Magnification plays no part in the ability of an objective to resolve an object of a given size. While magnification will 
         make an image bigger, it will not necessarily make it clearer. Resolution is governed solely by the Numerical Aperture (NA)
         of the objective, the wavelength of light and for axial resolution, the refractive index of the sample. Magnification will 
         affect how much light the objective can collect. Higher magnification objectives collect less light, so where possible use 
         the highest NA, lowest magnification objective available.

It is important when discriminating small structures that the Nyquist Sampling Criteria is satisfied. Nyquist Sampling dictates 
        that to optimally represent an analogue signal in digital space, the analogue signal needs to be sampled at least 2.3 times. 
        In microscopy terms this means that the pixel size of an image needs to be at least 2.3 times smaller than the object that is 
        being resolved.

If you are attempting to capture the highest resolution image possible with a given microscope configuration (objective, camera/scanner, 
         excitation and emission wavelength etc) then you must ensure that the pixel size is at least 2.3 times smaller than the 
         calculated resolution of the objective.

On a wide field microscope equipped with a digital camera the pixel size is usually fixed for each objective and cannot be adjusted. 
         The software used to take an image with the camera will show what the pixel size is, usually it is small enough to achieve 
         the theoretical maximum resolution of the objective. It is important to make sure you are aware of the pixel size for widefield 
         imaging. [...]

Microscope vendors tend to use 2x oversampling instead of the recommended 2.3x to 3x oversampling required for image deconvolution, 
         so you may want to reduce the step size a bit smaller than recommended [...].
         
Source: University of Queensland - Institute of Molecular Bioscience [https://imb.uq.edu.au/]""")

st.subheader("Rayleigh Criterion")

st.write("""In microscopy, a function termed the “Rayleigh criterion” describes the minimum distance between two objects and the ability 
         to separate them as a function of the numerical aperture (NA) of the objective and the spectral wavelength of the light that 
         should be detected. In a simplif ed way it is given by: """)

st.latex(r' \sigma = \dfrac{0.61 \cdot \lambda}{NA}')

st.write(r"""with resolution limit $\sigma$, wavelength $\lambda$ and numerical aperture NA of the objective. The major parameters of 
         each microscope objective are the total magnifation $M_{tot}$ and the numerical aperture NA. If we now take also the pixel pitch
         into consideration we define $\phi$ as the number of pixels relative to the resolution.""")

st.image("images/Airy_disk_spacing_near_Rayleigh_criterion.png", caption="""Airy diffraction patterns generated by light 
         from two point sources passing through a circular aperture, such as the pupil of the eye. Points far apart (top) or meeting the 
         Rayleigh criterion (middle) can be distinguished. Points closer than the Rayleigh criterion (bottom) are difficult to 
         distinguish. Image taken from: https://en.wikipedia.org/wiki/Angular_resolution#The_Rayleigh_criterion""")

st.write("""Since the time of Abbe and Rayleigh, microscopy has been digitized and optical limitations are no longer the
         sole determinants of the resolution. The human eye has largely been supplanted by electronic point
         detectors or camera sensors. All of which sample continuous image data as a discrete grid of pixels, i.e. a 
         bitmap. Each pixel in a digital image covers a specific area of the sample and the average intensity of light
         originating from that area is typically represented by an integral value.

In the ideal case, the number of pixels in a digital image would be infinitely large and the physical area
         represented by each pixel would be infinitesimally small. This way, no information would be lost in the
         sampling process and resolution of the final image would only be limited by optics. If on the other hand,
         only a single pixel would be used to represent all the information contained within the field of view of a 
         microscope, the image would just be a grey plane. The only information that could be recorded in this case 
         would be the average intensity of the sample.

In light of these considerations it becomes apparent that proper choice of pixel numbers and their size
         is instrumental to maximizing the full resolving power of a microscope. Here, the Nyquist-Shannon sampling 
         theorem dictates that a continuous analog signal should be oversampled by at least a factor of two to
         obtain an accurate digital representation. Therefore, to image with a resolution of e.g. 250 nanometers, 
         pixels should be smaller than 125 nanometers. This way, the intensity drop between two  overlapping Airy functions 
         can be detected as to satisfy the Rayleigh criterion. One could always use more pixels than needed according to the 
         theorem, i.e. oversample. However, a point emitter only emits a finite number of photons, spreading these out over too 
         many pixels would ultimately render them indistinguishable from the noise level.
         
Source: Vangindertael et al., "An Introduction to optical super-resolution microscopy for the adventurous biologist", Methods Appl. Fluoresc.
         6 (2018) 022003""")







