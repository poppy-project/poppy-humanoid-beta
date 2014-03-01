import json
import numpy

from scipy import interpolate

t_cycle = numpy.linspace(0, 1, num=10, endpoint=False)
gain_output = 0.6

hip_y_joint = -1 * numpy.array([32, 31, 26, 15, 3, -6, -12, -4, 27, 30])
knee_joint = numpy.array([0, 17, 19, 10, 1, 8, 30, 62, 60, 25])
ankle_joint = numpy.array([-3, -7, -3, 2, 5, 7, 4.5, -15, -16.5, -4])

for i in range(2):
    hip_y_joint = numpy.append(hip_y_joint, hip_y_joint)
    knee_joint = numpy.append(knee_joint, knee_joint)
    ankle_joint = numpy.append(ankle_joint, ankle_joint)

    t_cycle = numpy.append(t_cycle, t_cycle + t_cycle[-1] + numpy.diff(t_cycle[0:2]))

t_interp = numpy.arange(start=0, step=0.01, stop=t_cycle[-1])
lambda_interp = lambda (x): interpolate.splev(t_interp, interpolate.splrep(t_cycle ,x ,s=0) ,der=0)

hip_y_interp = lambda_interp(hip_y_joint)
knee_interp =  lambda_interp(knee_joint)
ankle_interp = lambda_interp(ankle_joint)

# jambe droite phase = 0
t0_r = numpy.where(t_interp >= 1)[0][0]
tend_r = numpy.where(t_interp >= 2)[0][0] -1

lambda_trunc_r = lambda (x): gain_output * x[t0_r:tend_r]

r_hip_y = lambda_trunc_r(hip_y_interp)
r_knee_y = lambda_trunc_r(knee_interp)
r_ankle_y = lambda_trunc_r(ankle_interp)


# jambe gauche phase = 50
t0_l = numpy.where(t_interp >= 1.5)[0][0]
tend_l = tend_r = numpy.where(t_interp >= 2.5)[0][0] -1  #0==100

lambda_trunc_l = lambda (x): gain_output*x[t0_l:tend_l]

l_hip_y = lambda_trunc_l(hip_y_interp)
l_knee_y = lambda_trunc_l(knee_interp)
l_ankle_y = lambda_trunc_l(ankle_interp)

t_norm = numpy.linspace(0, 1, num=r_hip_y.size, endpoint=False)
n_elem = t_norm.size

r_ankle_compliance = numpy.zeros(n_elem)
r_ankle_compliance[round(0.2*n_elem) : round(0.4*n_elem)] = 1
l_ankle_compliance = numpy.zeros(n_elem)
l_ankle_compliance[round(0.7*n_elem) : round(0.9*n_elem)] = 1

r_knee_compliance_extension = (((numpy.gradient(r_knee_y)<0) & (r_knee_y<20)))
r_knee_compliance_flexion = ((numpy.gradient(r_knee_y)>0) & (r_knee_y>30))
l_knee_compliance_extension = (((numpy.gradient(l_knee_y)<0) & (l_knee_y<20)))
l_knee_compliance_flexion = ((numpy.gradient(l_knee_y)>0) & (l_knee_y>30))


list_of_variable_names = ['r_hip_y', 'l_hip_y', 'r_ankle_compliance', 'r_knee_y', 'l_ankle_y', 'r_ankle_y', 'r_knee_compliance_extension', 'l_knee_y', 'r_knee_compliance_flexion', 'l_knee_compliance_flexion', 'l_knee_compliance_extension', 'l_ankle_compliance', 'n_elem']
WALKING_CPG = dict((name, eval(name)) for name in list_of_variable_names)

if __name__ == '__main__':
    from poppytools.utils.conversion import NumpyAwareJSONEncoder
    with open("walking_cpg.json", "w") as f:
        s = json.dump(WALKING_CPG, f, cls=NumpyAwareJSONEncoder)
