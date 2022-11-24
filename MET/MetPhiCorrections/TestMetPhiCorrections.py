import sys
import correctionlib
import numpy as np
import matplotlib.pyplot as plt

rng = np.random.default_rng()

correction_label = sys.argv[1]
infile = sys.argv[2]

is_data = None

if ("mc" in correction_label) and (not ("data" in correction_label)):
    is_data = False
elif ("data" in correction_label) and (not ("mc" in correction_label)):
    is_data = True
else:
    print("first argument needs to contain either 'mc' or 'data'")
    exit()

ceval = correctionlib.CorrectionSet.from_file(infile)

print(list(ceval.keys()))
print(list(ceval.values()))

for corr in ceval.values():
    print(f"Correction {corr.name}")
    print(f"Version {corr.version}")

pts = rng.uniform(low=0.0, high=1000.0, size=1000000)
phis = rng.uniform(low=-3.14, high=3.14, size=1000000)
npvs = rng.integers(low=0, high=200, size=1000000)
runs = None
if is_data:
    runs = rng.integers(low=272007, high=325274, size=1000000)
else:
    runs = rng.integers(low=0, high=100000, size=1000000)

print("uncorrected pts:", pts[1:11])
print("uncorrected phis:", phis[1:11])
print("number of vertices:", npvs[1:11])
print("run numbers:", runs[1:11])

corrected_pts = ceval["pt_{}".format(correction_label)].evaluate(pts, phis, npvs, runs)
corrected_phis = ceval["phi_{}".format(correction_label)].evaluate(pts, phis, npvs, runs)

print("corrected pts:", corrected_pts[1:11])
print("corrected phis:", corrected_phis[1:11])

fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)
axs[0].set(xlabel="uncorrected phi")
axs[0].hist(phis, bins=32)
axs[1].set(xlabel="corrected phi")
axs[1].hist(corrected_phis, bins=32)

# plt.show()
plt.savefig("{}_1D.pdf".format(correction_label))
print("{}_1D.pdf saved".format(correction_label))

fig, axs = plt.subplots(1, 2, tight_layout=True, sharey=True)

axs[0].hist2d(npvs, phis, bins=(20, 16))
axs[0].set(xlabel="number of primary vertices", ylabel="uncorrected phi")
axs[1].hist2d(npvs, corrected_phis, bins=(20, 16))
axs[1].set(xlabel="number of primary vertices", ylabel="corrected phi")

# plt.show()
plt.savefig("{}_2D.pdf".format(correction_label))
print("{}_2D.pdf saved".format(correction_label))

# fig, ax = plt.subplots(tight_layout=True)

# ax.hist2d(phis, corrected_phis, bins=(32,32))

# plt.show()
