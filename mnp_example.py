##################################################
###         Manipulator examples 			   ###
##################################################
# Examples for every feature (open specific line):	
# current_case = 'SELF PLOTTED GRAPH'
# current_case = 'MULTIPLE GRAPHS'
current_case = 'SINGLE GRAPH'
# 
##################################################
# Detailed explanation:
# current_case = 'SINGLE GRAPH'
# 	in this case the function needs to propogate input X
#	and return Y on every recalculation. It happens every 
#	100 milliseconds or on each change of a parameter
#	[X_list, Y_list] = gui.m_func = user_implemented_function(Xo)
# 	user_implemented_function.__doc__ is a Graph name
# 	mnp.grf_title overwrites the title
#	Additional functionalities:  
# 	* to bind external functions to specific key use command
# 	  mnp.root.bind("<space>", your_specific_function).
# 	  Try to press spase in this case
# 	* connect to the manipulator axis - show/turn off the grid
#   * to invert Slider (Tk.Scale) direction change values of limit values:
#     mnp.set_parameter_slider(prm_MIN=USER_MAX_VALUE,prm_MAX=USER_MIN_VALUE,...
#     see case 'SELF PLOTTED GRAPH'
#   * to copy figure into the clipboard press Ctrl+C. The quality is mnp.dpi4fig
#     The function works in Windows. 
#   * UPDATE_AFTER_RELEASE = True postpones the update after the release of the sliders
# 	  for heavy applications
#
# current_case = 'SELF PLOTTED GRAPH'
# 	in this case the function needs 
# 	to plot the graph by itself, see parabola(ax) function
# 	with mnp.axis of the plot as input.
# 	Must set mnp.SELF_PLOT_FUNCTION = True.
# 	mnp.root.title("examples for manipulator Ver. %s"%mnp.__version__)
# 	mnp.m_func = parabola		
# 	mnp.set_parameter_slider(prm_MIN=-5.,prm_MAX=5.,prm_VAL=1,prm_res=0.001,prm_name='a')
# 	* the last parameter in mnp.set_parameter_slider() is tickinterval. Default is 0, see param "c"
#
# current_case = 'MULTIPLE GRAPHS'
# 	in this case the function needs 
# 	mnp.Xo = arange(0.0, 1.0, 0.001)
# 	mnp.grf_title = '$N_{th}$ iteration of Bernoulli map; '
# 	mnp.X_label = '$X_{ N}$'
# 	mnp.Y_label = '$X_{N+1}$'
# 	mnp.grf_stile =['-b',':r','-']
# 	mnp.m_func = [bernoulli_N_iteration,same_val]
# 	mnp.set_parameter_slider(prm_MIN=1,prm_MAX=10,prm_VAL=2,prm_res=1,prm_name='iter')
# 	mnp.set_parameter_slider(prm_MIN=-10.,prm_MAX=23.,prm_VAL=0.,prm_res=0.01,prm_name='r')
#
# 
# git: https://github.com/glebkarmi/Manipulator/
# email: gleb.phd@gmail.com; Write in the Subject: "manipulator.py"

from matplotlib import use
use('TkAgg')
# from matplotlib.pyplot import plot, show, xlabel, ylabel, title, subplots, \
# 	draw, figure, contour, clabel, scatter
import tkinter as Tk	
import manipulator as mnp
from numpy import arange, sqrt, copy as np_copy, fmod, linspace
grid_status = True
def parabola(ax):
	global grid_status
	a = mnp.param['a']['scale'].get()
	b = mnp.param['b']['scale'].get()
	c = mnp.param['c']['scale'].get()
	LIM = 10.
	X = arange(-LIM, LIM, 20/1000)
	Y =  a*X*X+b*X+c
	ax.plot([-LIM,LIM],[0,0],'-.k')
	ax.plot([0,0],[min(Y),max(Y)],'-.k')
	ax.plot(X, Y)
	ax.scatter(0,c,c='b',s = 30) # y-axis intersection
	if a !=0: 
		if b*b >= 4*c*a:		
			d = sqrt( abs(b*b - 4*c*a))			
			x1 = (-b - d)/2/a # 
			x2 = (-b + d)/2/a
			x3 = (x1+x2)/2
			if abs(x1) < LIM:
				ax.scatter(x1,a*x1*x1+b*x1+c,c='r',s = 30) # root 1
			if abs(x2) < LIM:
				ax.scatter(x2,a*x2*x2+b*x2+c,c='r',s = 30) # root 2
			if abs(x3) < LIM:				
				ax.scatter(x3,a*x3*x3+b*x3+c,c='g',s = 30) # vertex

	ax.grid(grid_status)	
	ax.set_xlabel(r'a=%.1f; b=%.1f; c=%.1f;'%(a,b,c) +  '                       x' )
	ax.set_ylabel('y' )

	txt = 	r'''   parabola graph
	y(x) = a $x^2$ + bx + c'''

	ax.set_title(txt)

def toggle_grid(event):
	global grid_status
	grid_status = not grid_status
	ax = mnp.get_manip_axis()
	ax.grid(grid_status)
	xc, yc = mnp.coursor_position()
	print('X=%s; Y=%s'%(str(xc), str(yc)))	
	mnp.canvas.draw()


def bernoulli_map(x):
	'''$ X_{N+1} = 2 X_{N}$ mod 1 ''' 
	return fmod(2.*x ,1.)

def same_val(x):
	return x 

def bernoulli_N_iteration(x,N=0):
	'''N iteration of bernoulli map ''' 	

	if N == 0:
		N=mnp.param['iter']['scale'].get()
	xn = np_copy(x)
	for i in range(N):
		y = bernoulli_map(xn)
		xn = np_copy(y)
	return y


def LogisticMap(x,r):
	return r * x * (1.0 - x)



def LogisticMapBifurcation(dummy):	
	'''Bifurcation diagram of Logistic map f(x)=rx(1-x)'''
	transient_iterations = 200
	actual_iterations = 250
	r_resolution = 800. # points in the list ot r vector
	
	r_low=mnp.param['r_low']['scale'].get()
	mnp.update_scale(prm_name='r_upp',prm_MIN=r_low+1e-5)# , prm_VAL=r_low+1
	r_upp=mnp.param['r_upp']['scale'].get()

	r_list =  linspace(r_low, r_upp+1e-10,r_resolution)
	Xn_list = []; r_sweep = []
	for r in r_list:
		Xn = mnp.param['Xo']['scale'].get()
		for i  in range(transient_iterations):
			Xn = LogisticMap(Xn, r)
			if Xn > 1.0 :
				Xn = 1.0
			elif Xn < 0.0:
				Xn = 0.

		for i  in range(actual_iterations):
			Xn = LogisticMap(Xn, r)
			if Xn > 1.0 :
				Xn = 1.0
			elif Xn < 0.0:
				Xn = 0.
			r_sweep.append(r)
			Xn_list.append(Xn)

	return [r_sweep, Xn_list]

##################################################
###                 #  MAIN #                  ###
##################################################

if current_case is 'SELF PLOTTED GRAPH':
	mnp.SELF_PLOT_FUNCTION = True
	mnp.root.title("examples for manipulator Ver. %s"%mnp.__version__)
	mnp.m_func = parabola		
	mnp.set_parameter_slider(prm_MIN=5.,prm_MAX=-5.,prm_VAL=1,prm_res=0.001,prm_name='a')
	mnp.set_parameter_slider(prm_MIN=20.,prm_MAX=-20.,prm_VAL=0.0,prm_res=0.001,prm_name='b')
	mnp.set_parameter_slider(prm_MIN=30.,prm_MAX=-30.,prm_VAL=0.0,prm_res=0.001,prm_name='c',tickinterval=10)

	mnp.root.bind("<space>", toggle_grid)

if current_case is 'MULTIPLE GRAPHS':
	mnp.Xo = arange(0.0, 1.0, 0.001)
	mnp.grf_title = '$N_{th}$ iteration of Bernoulli map; '
	mnp.X_label = '$X_{ N}$'
	mnp.Y_label = '$X_{N+1}$'
	mnp.grf_stile =['-b',':r','-']
	mnp.m_func = [bernoulli_N_iteration,same_val]
	mnp.set_parameter_slider(prm_MIN=1,prm_MAX=10,prm_VAL=2,prm_res=1,prm_name='iter')
	mnp.set_parameter_slider(prm_MIN=-10.,prm_MAX=23.,prm_VAL=0.,prm_res=0.01,prm_name='r')

if current_case is 'SINGLE GRAPH':
	mnp.grf_title = 'Bifurcation diagram of Logistic map f(x)=rx(1-x); '
	mnp.X_label = 'r'
	mnp.Y_label = '$X_{N}$'
	mnp.aliased=True
	mnp.UPDATE_AFTER_RELEASE = True
	mnp.grf_stile =['b,'] # a one pixel plot
	mnp.set_parameter_slider(prm_MIN=0.,prm_MAX=1.0,prm_VAL=0.33,prm_res=0.01,prm_name='Xo')
	mnp.set_parameter_slider(prm_MIN=0.01,prm_MAX=4.,prm_VAL=2.8,prm_res=0.0001,prm_name='r_low')
	mnp.set_parameter_slider(prm_MIN=3.0,prm_MAX=4.3,prm_VAL=3.8,prm_res=0.0001,prm_name='r_upp')
	mnp.m_func = LogisticMapBifurcation

Tk.mainloop()
