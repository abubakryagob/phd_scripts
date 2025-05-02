import matplotlib.pyplot as plt
import numpy as np
import sys
import math

#Reading the data
flux = sys.argv[1]
Data = np.loadtxt(flux)


MJD = Data[:,0]
F = Data[:,1]
F_lower_error = Data[:,2]
F_upper_error = Data[:,3]
obs_name = Data[:,4]


# After changing the format of the date (start+end)/2
# To calculate the fux obtained from xspec 10eflux
print('### Initial flux values:\n', F)

# Get the natuaral logrithm for thr flux uncertunity
f_unc_lower = math.log(10) * F * F_lower_error
f_unc_upper = math.log(10) * F * F_upper_error

print('### Lower uncertunities of the flux:\n', f_unc_lower)
print('### Upper uncertunities of the flux:\n', f_unc_upper)


Flux_lower = F + f_unc_lower
Flux_upper = F + f_unc_upper

print('### Flux with lower uncertunities:\n', Flux_lower)
print('### Flux with upper uncertunities:\n', Flux_upper)


#======================================================
		# Calculate the luminosity
#======================================================
d = 3.086e22 #units
L_best = 4 * np.pi * F * d**2
print('### Best Luminosity:\n', L_best)

L_lower = 4 * np.pi * Flux_lower * d**2
L_upper = 4 * np.pi * Flux_upper * d**2

print('### Luminosity with lower uncertunities:\n', L_lower)
print('### Luminosity with upper uncertunities:\n', L_upper)


label = obs_name
#Flux Plot
plt.figure()
plt.xlabel("Time [MJD]")
plt.ylabel(r"Flux [erg cm$^{-2}$s$^{-1}$]")
plt.title("De-absorbed flux")
plt.errorbar(MJD, F, yerr=[Flux_lower,Flux_upper], fmt='.k', ecolor='black', marker='o')# elinewidth=1,  mfc='k')
plt.gca().set_yscale('log')
plt.grid(which='both')
#plt.legend(p, label)

plt.savefig("deabsorbed_flux.png")
plt.show()

'''
#Plot
plt.figure()
plt.xlabel("Time [MJD]")
plt.ylabel(r"Luminosity [erg s$^{-1}$]")
plt.title("Luminosity")
plt.errorbar(MJD, L_best, yerr=[L_lower,L_upper], fmt='.k', ecolor='black')# elinewidth=5,  mfc='k')
plt.gca().set_yscale('log')
plt.grid(which='both')
plt.savefig("luminosity.png")
plt.show()





delcomp 3 
addcomp 2 bbodyrad 
newpar 5 0,-1 
addcomp 2 powerlaw 

ln(10)*Fx*sigma_Fx 
ln(10)*2.54e-11*(-0.046)
'''


