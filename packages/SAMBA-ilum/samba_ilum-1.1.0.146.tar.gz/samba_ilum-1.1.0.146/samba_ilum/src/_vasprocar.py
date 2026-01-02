# SAMBA_ilum Copyright (C) 2025
# GNU GPL-3.0 license

import os
import sys
import site
import shutil
import subprocess                                                   

print("#############################################################################")
print("# VASProcar: A Python toolkit for automated post-processing of VASP ------- #")
print("#                                 electronic-structure calculations ------- #")
print("# Authors: Augusto de Lelis Araujo and Renan da Paixao Maciel ------------- #")
print("# ------------------------------------------------------------------------- #")
print("# VASProcar is an open-source package written in the Python 3, which aims   #")
print("# to provide an intuitive tool for the post-processing of the output files  #")
print("# produced by the DFT VASP/QE codes, through an interactive user interface. #")
# print("# ========================================================================= #")
# print("# For more information, visit the link:                                     #")
# print("# https://github.com/Augusto-de-Lelis-Araujo/SAMBA-ilum/blob/main/README.md #")
print("#############################################################################")

print(" ")
print("============================================================================")
print("[0] RUN VASProcar Code                                                      ")
print("[1] Install/Update the VASProcar python module                              ")
print("[2] Exit                                                                    ")
print("============================================================================")
modulo = input(" "); modulo = int(modulo)
print(" ")

if (modulo == 0):
   subprocess.run(["python3", "-m", "vasprocar", dir_files])

if (modulo == 1):
   subprocess.run(["pip", "install", "--upgrade", "vasprocar"])
