##################################################
###  The Manipulator works with Python 3 only  ###
##################################################
__version__= '0.04.00 (19/03/2020)'
from matplotlib import use
use('TkAgg')

from numpy import arange, sin, pi, linspace,fmod, copy as np_copy
try:
	from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
except :
	from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk #Agg

# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
from matplotlib.pyplot import connect
import matplotlib.pyplot as plt
import tkinter as Tk
global Tk, m_func, Xo, window_title, ax
# print(help(Tk))
UPDATE_AFTER_RELEASE = False
window_title = ''
dpi4fig = 200
Xo = arange(0,1,1);param={};prm_tot = 0;prm_prev={};X_label='X';Y_label='Y'
root = Tk.Tk()
root.wm_title("Embedding MatplotLib in TK, Manipulator Ver. %s"%__version__)

#  Stretch definition for the Figure
root.columnconfigure(10,weight=1);root.columnconfigure(11,weight=1);root.columnconfigure(12,weight=1)
root.columnconfigure(40,pad=1)
root.rowconfigure(1, weight=0);root.rowconfigure(4, weight=1)
root.rowconfigure(30, pad=7)
grf_title = None
grf_stile = ['-b',':r','-'] # the last is the default # ',' is a pixel
aliased = False
grid_on = False
xLim = [None, None]
yLim = [None, None]
SELF_PLOT_FUNCTION = False
Xc,Yc = 0,0

def copy2clipboard(event, figure=None):
	global fig, dpi4fig
	from io import BytesIO as StringIO
	from time import sleep
	from PIL import Image
	import win32clipboard

	if figure:
	    fig = figure
    
	output = StringIO()
	# fig.savefig(output, format='bmp') # bmp not supported
	dpi = fig.get_dpi()
	fig.set_dpi(dpi4fig)  
	fig.canvas.draw()
	buf = fig.canvas.buffer_rgba()
	w = int(fig.get_figwidth() * fig.dpi)
	h = int(fig.get_figheight() * fig.dpi)

	im = Image.frombuffer('RGBA', (w,h), buf, 'raw', 'RGBA', 0, 1)
	im.save(output, "BMP") # "JPEG")#

	data = output.getvalue()[14:] # The file header off-set of BMP is 14 bytes
	output.close()

	try:
	    win32clipboard.OpenClipboard()
	    win32clipboard.EmptyClipboard()
	    # win32clipboard.SetClipboardData(win32clipboard.CF_BITMAP, data) # did not work!
	    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data) # DIB = device independent bitmap 
	    win32clipboard.CloseClipboard()
	except:
	    sleep(0.2)
	    copy2clipboard(event, fig)
	fig.set_dpi(dpi)  
	fig.canvas.draw()

def a_line(x):
	'''a simple line'''
	return x;
m_func = a_line 

def coursor_position():	
	global Xc, Yc 
	return [Xc,Yc]

def get_manip_axis():
	return ax	

def coursor_position_self(event):	
	global Xc, Yc 
	Xc, Yc = event.xdata, event.ydata  
	# print('X=%f; Y=%f'%(Xc,Yc))
	return [Xc,Yc]

def set_parameter_slider(prm_MIN,prm_MAX,prm_VAL,prm_res,prm_name,tickinterval=0):
	global prm_tot,canvas,ax
	prm_tot +=1 
	param[prm_name] = {}
	param[prm_name]['min'] = prm_MIN
	param[prm_name]['max'] = prm_MAX
	param[prm_name]['val'] = prm_VAL
	param[prm_name]['res'] = prm_res
	
	param[prm_name]['lbl'] = Tk.Label(root, text=prm_name)
	param[prm_name]['lbl'].grid(column=prm_tot, row=1, sticky=Tk.S) 
	param[prm_name]['min_lbl'] =  Tk.Label(root, text=prm_MIN)
	param[prm_name]['min_lbl'].grid(column=prm_tot, row=2, sticky=Tk.S) 
	param[prm_name]['max_lbl'] =  Tk.Label(root, text=prm_MAX)
	param[prm_name]['max_lbl'].grid(column=prm_tot, row=25, sticky=Tk.S) 
	# param[prm_name]['scale'] = Tk.Scale(root, from_=prm_MAX, to=prm_MIN, orient=Tk.VERTICAL, length=450,
	param[prm_name]['scale'] = Tk.Scale(root, from_=prm_MIN, to=prm_MAX, orient=Tk.VERTICAL, length=450,
			label='', resolution=prm_res,showvalue=0,tickinterval=tickinterval)
	param[prm_name]['scale'].set(prm_VAL)
	param[prm_name]['scale'].grid(column=prm_tot, row=4, columnspan=1, rowspan=20,padx=5, sticky=Tk.E+Tk.W+Tk.S+Tk.N)
	prm_prev[prm_name] = prm_VAL - 1
	if UPDATE_AFTER_RELEASE:
		param[prm_name]['scale'].bind("<ButtonRelease-1>",   lambda event: update(canvas,ax))


def update_scale(prm_name,prm_MIN=None,prm_MAX=None,prm_res=None,prm_VAL=None): # 
	if prm_MIN:
		param[prm_name]['min_lbl']['text'] = '%.3f'%prm_MIN
		if param[prm_name]['scale'].get() < prm_MIN:
			param[prm_name]['scale'].set(prm_MIN)
		param[prm_name]['scale'].configure(from_=prm_MIN)
	if prm_MAX:
		param[prm_name]['min_lbl']['text'] = '%.3f'%prm_MIN
		param[prm_name]['scale'].configure(to=prm_MAX)
	if prm_res:
		param[prm_name]['scale'].configure(resolution=prm_res)
	if prm_VAL:
		param[prm_name]['scale'].set(prm_VAL)

def update(canvas,ax,eval_now=False):
	global param, prm_prev , root, Xo,SELF_PLOT_FUNCTION, Xc,Yc, grf_title
	X = Xo
	for prm_name in param.keys():
		if (prm_prev[prm_name] != param[prm_name]['scale'].get()) or  eval_now:
			prm_prev[prm_name] = param[prm_name]['scale'].get()
			prm_string = ''
			for prm_name in param.keys():
				prm_string += prm_name+'='+str(param[prm_name]['scale'].get())+';'
			ax.clear()
			if SELF_PLOT_FUNCTION:
				# the m_func(ax) is updating the graph. No other inputs to the function
				# all the parameters are globals
				m_func(ax) 
			else:
				if grf_title == None:
					if m_func.__doc__ == None:
						grf_title = "Manipulator Ver. %s; Add your title via grf_title parameter."%__version__
					else:
						grf_title = m_func.__doc__

				if type(m_func) is list:			
					for grf in range(len(m_func)):
						y = m_func[grf](X)	# X[grf]
						if len(y) == 2:
							X,y = y[0], y[1]
						ax.plot(X, y,grf_stile[min(grf,len(grf_stile)-1)], antialiased=aliased)
					ax.set_title( grf_title+'\n'+prm_string)
				else:
					y = m_func(X)
					if len(y) == 2:
						X,Y = y[0], y[1]
					grf = 0
					ax.plot(X, Y,grf_stile[min(grf,len(grf_stile)-1)], antialiased=aliased)
					ax.set_title( grf_title+'\n'+prm_string)
				ax.grid(grid_on)
				if xLim[0]:
					ax.set_xlim(xLim)
				if yLim[0]:
					ax.set_ylim(yLim)
				ax.set_xlabel(X_label )
				ax.set_ylabel(Y_label )

	canvas.draw()
	if not UPDATE_AFTER_RELEASE:
		# call update function every 100ms with params *(canvas,ax)
		root.after(100, update,*(canvas,ax)) 

#############################################################
fig = Figure(figsize=(8, 6))#, dpi=100
ax = fig.add_subplot(111)
fr = Tk.Frame()
fr.grid(row=3, column=10, columnspan=30, rowspan=27, sticky=Tk.E+Tk.W+Tk.S+Tk.N)

canvas = FigureCanvasTkAgg(fig, master=fr)
fig.canvas.mpl_connect('motion_notify_event', coursor_position_self)# after FigureCanvasTkAgg

#canvas.show()
canvas.draw()

try:	
	toolbar = NavigationToolbar2TkAgg(canvas, fr)
except:
	toolbar = NavigationToolbar2Tk(canvas, fr)
toolbar.update()
update(canvas,ax)

canvas.get_tk_widget().pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)
# root.bind("<space>", dummy_function)
root.bind("<Control-c>", copy2clipboard )

## Unit TEST ##################################################################
if __name__ == '__main__':
	def bernoulli_map(x):
		'''$ X_{N+1} = 2 X_{N}$ mod 1 ''' 
		return fmod(2.*x ,1.)

	def same_val(x):
		return x 

	def bernoulli_N_iteration(x,N=0):
		'''N iteration of bernoulli map ''' 	
		if N == 0:
			N=param['iter']['scale'].get()
		xn = np_copy(x)
		for i in range(N):
			y = bernoulli_map(xn)
			xn = np_copy(y)
		return y

	Xo = arange(0.0, 1.0, 0.001)
	grf_title = '$N_{th}$ iteration of Bernoulli map; '
	X_label = '$X_{ N}$'
	Y_label = '$X_{N+1}$'
	grf_stile =['-b',':r','-']
	set_parameter_slider(prm_MIN=1,prm_MAX=10,prm_VAL=2,prm_res=1,prm_name='iter')
	set_parameter_slider(prm_MIN=-10.,prm_MAX=23.,prm_VAL=0.,prm_res=0.01,prm_name='r')
	#m_func = bernoulli_N_iteration
	m_func = [bernoulli_N_iteration,same_val]
	Tk.mainloop()

## TBDs & Questions ###########################	
