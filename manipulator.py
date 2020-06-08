#################################################
###                Manipulator                ###
###       by Gleb Karmi - MIT License         ###
##################################################
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


class CManipulator:
	__version__= '01.00.00 (01/06/2020)'
	UPDATE_AFTER_RELEASE = False
	dpi4fig = 200
	Xo = arange(0,1,1);param={};prm_tot = 0;prm_prev={};X_label='X';Y_label='Y'
	root = Tk.Tk()
	root.wm_title("Embedding MatplotLib in TK, Manipulator Ver. %s"%__version__)
	prm_string = ''
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

	def __init__(self):
		self.evaluate_now=True
		self.m_func = self.a_line 
		self.fig = Figure(figsize=(8, 6))#, dpi=100
		# ax = fig.add_subplot(111)
		self.fr = Tk.Frame()
		self.fr.grid(row=25, column=10, columnspan=30, rowspan=30, sticky=Tk.E+Tk.W+Tk.S+Tk.N)

		# canvas = FigureCanvasTkAgg(fig, master=fr) # for pack geometry method 
		self.canvas = FigureCanvasTkAgg(self.fig, master=CManipulator.root) # for grid geometry method
		self.fig.canvas.mpl_connect('motion_notify_event', self.coursor_position_self)# after FigureCanvasTkAgg
		#canvas.show()
		self.canvas.draw()

		try:	
			self.toolbar = NavigationToolbar2TkAgg(self.canvas, self.fr)
		except:
			self.toolbar = NavigationToolbar2Tk(self.canvas, self.fr)
		self.toolbar.update()
		self.update(self.canvas,self.fig)

		self.canvas.get_tk_widget().grid(row=3, column=10, columnspan=30, rowspan=20, sticky=Tk.E+Tk.W+Tk.S+Tk.N)
		# root.bind("<space>", dummy_function)
		CManipulator.root.bind("<Control-c>", self.copy2clipboard )

	def clear_mnp_params(self):
		self.evaluate_now=False 
		#! Must turn the flag On before usage. With False value update() is not working !#
		try: 	
			for prm_name in self.param.keys():		
				self.param[prm_name]['lbl']	   .destroy() #
				self.param[prm_name]['min_lbl'].destroy() #
				self.param[prm_name]['max_lbl'].destroy() #
				self.param[prm_name]['scale']  .destroy() #
		except Exception as e:
			pass	
				
		self.param, self.prm_prev = {}, {}
		self.prm_tot = 0		

	# copy a matplotlib figure to clipboard as BMP on windows
	# http://stackoverflow.com/questions/7050448/write-image-to-windows-clipboard-in-python-with-pil-and-win32clipboard
	def copy2clipboard(self,event, figure=None):
		from io import BytesIO as StringIO
		from time import sleep
		from PIL import Image
		import win32clipboard

		if figure:
		    self.fig = figure
	    
		output = StringIO()
		# fig.savefig(output, format='bmp') # bmp not supported
		dpi = self.fig.get_dpi()
		self.fig.set_dpi(self.dpi4fig)  
		self.fig.canvas.draw()
		buf = self.fig.canvas.buffer_rgba()
		w = int(self.fig.get_figwidth() * self.fig.dpi)
		h = int(self.fig.get_figheight() * self.fig.dpi)
		# im = Image.frombuffer('RGBA', (w,h), buf)
		# II = im.transpose(Image.FLIP_TOP_BOTTOM).convert("RGB")
		# II.save(output, "BMP") # "JPEG")# 
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
		    self.copy2clipboard(event, fig)
		self.fig.set_dpi(dpi)  
		self.fig.canvas.draw()

	def a_line(self,x):
		'''a simple line'''
		return x;	

	def coursor_position(self):			
		return [self.Xc,self.Yc]

	def get_manip_axis(self):
		return self.fig.gca()	

	def get_manip_frame(self):
		return self.fr
		
	def coursor_position_self(self,event):	
		self.Xc, self.Yc = event.xdata, event.ydata  
		return [self.Xc,self.Yc]

	def set_parameter_slider(self,prm_MIN,prm_MAX,prm_VAL,prm_res,prm_name,tickinterval=0):
		self.prm_tot +=1 
		self.param[prm_name] = {}
		self.param[prm_name]['min'] = prm_MIN
		self.param[prm_name]['max'] = prm_MAX
		self.param[prm_name]['val'] = prm_VAL
		self.param[prm_name]['res'] = prm_res
		
		self.param[prm_name]['lbl'] = Tk.Label(CManipulator.root, text=prm_name)
		self.param[prm_name]['lbl'].grid(column=self.prm_tot, row=1, sticky=Tk.S) 
		self.param[prm_name]['min_lbl'] =  Tk.Label(CManipulator.root, text=prm_MIN)
		self.param[prm_name]['min_lbl'].grid(column=self.prm_tot, row=2, sticky=Tk.S) 
		self.param[prm_name]['max_lbl'] =  Tk.Label(CManipulator.root, text=prm_MAX)
		self.param[prm_name]['max_lbl'].grid(column=self.prm_tot, row=25, sticky=Tk.S) 
		self.param[prm_name]['scale'] = Tk.Scale(CManipulator.root, from_=prm_MIN, to=prm_MAX, orient=Tk.VERTICAL, length=450,
			label='', resolution=prm_res,showvalue=0,tickinterval=tickinterval)
		self.param[prm_name]['scale'].set(prm_VAL)
		self.param[prm_name]['scale'].grid(column=self.prm_tot, row=4, columnspan=1, rowspan=20,padx=5, sticky=Tk.E+Tk.W+Tk.S+Tk.N)
		
		self.prm_prev[prm_name] = self.param[prm_name].copy(); 
		# prm_prev[prm_name] = prm_VAL - 1
		if self.UPDATE_AFTER_RELEASE:
			self.param[prm_name]['scale'].bind("<ButtonRelease-1>",   lambda event: self.update(self.canvas,self.fig))

		self.evaluate_now = True

	def update_scale(self,prm_name,prm_MIN=None,prm_MAX=None,prm_res=None,prm_VAL=None): # 
		if prm_MIN:
			self.param[prm_name]['min_lbl']['text'] = '%.3f'%prm_MIN
			if self.param[prm_name]['scale'].get() < prm_MIN:
				self.param[prm_name]['scale'].set(prm_MIN)
			self.param[prm_name]['scale'].configure(from_=prm_MIN)
		if prm_MAX:
			param[prm_name]['min_lbl']['text'] = '%.3f'%prm_MIN
			param[prm_name]['scale'].configure(to=prm_MAX)
		if prm_res:
			param[prm_name]['scale'].configure(resolution=prm_res)
		if prm_VAL:
			param[prm_name]['scale'].set(prm_VAL)

	def update(self,canvas,fig):
		X = self.Xo
		ax = self.fig.gca() # valid for all cases except SELF_PLOT_FUNCTION
		self.prm_string = ''
		need_an_update_this_time = False
		for prm_name in self.param.keys():
			self.prm_string += prm_name+'='+str(self.param[prm_name]['scale'].get())+';'
			if self.evaluate_now and (self.prm_prev[prm_name] != self.param[prm_name]['scale'].get()):
				self.prm_prev[prm_name] = self.param[prm_name]['scale'].get()
				ax.clear()
				need_an_update_this_time = True # Some parameters were updated & evaluate_now is valid
			
		if need_an_update_this_time:
			if self.SELF_PLOT_FUNCTION:
				# the self.m_func(ax) is updating the graph. No other inputs to the function
				# all the parameters are globals
				self.m_func(self.fig) 
			else:
				if type(self.m_func) is list:			
					if self.grf_title == None:
						if self.m_func[0].__doc__ == None:
							self.grf_title = "Manipulator Ver. %s; Add your title via grf_title parameter."%__version__
						else:
							self.grf_title = self.m_func[0].__doc__

					for grf in range(len(self.m_func)):
						y = self.m_func[grf](X)	# X[grf]
						if len(y) == 2:
							X,y = y[0], y[1]
						ax.plot(X, y,self.grf_stile[min(grf,len(self.grf_stile)-1)], antialiased=self.aliased)
					ax.set_title( self.grf_title+'\n'+self.prm_string)

				else:
					if self.grf_title == None:
						if self.m_func.__doc__ == None:
							self.grf_title = "Manipulator Ver. %s; Add your title via grf_title parameter."%__version__
						else:
							self.grf_title = self.m_func.__doc__

					y = self.m_func(X)
					if len(y) == 2:
						X,Y = y[0], y[1]
					grf = 0
					ax.plot(X, Y,self.grf_stile[min(grf,len(self.grf_stile)-1)], antialiased=self.aliased)
					ax.set_title( self.grf_title+'\n'+self.prm_string)

				ax.grid(self.grid_on)
				if self.xLim[0]:
					ax.set_xlim(self.xLim)
				if self.yLim[0]:
					ax.set_ylim(self.yLim)
				ax.set_xlabel(self.X_label )
				ax.set_ylabel(self.Y_label )			
 	
		canvas.draw()
		if not CManipulator.UPDATE_AFTER_RELEASE:
			# call update function every 100ms with params *(canvas,self.fig)
			CManipulator.root.after(100, self.update,*(canvas,self.fig)) 


## Unit TEST ##################################################################
# if __name__ == '__main__':
# 	def bernoulli_map(x):
# 		'''$ X_{N+1} = 2 X_{N}$ mod 1 ''' 
# 		return fmod(2.*x ,1.)

# 	def same_val(x):
# 		return x 

# 	def bernoulli_N_iteration(x,N=0):		
# 		'''N iteration of bernoulli map ''' 	
# 		global gui
# 		if N == 0:
# 			N=gui.param['iter']['scale'].get()
# 		xn = np_copy(x)
# 		for i in range(N):
# 			y = bernoulli_map(xn)
# 			xn = np_copy(y)
# 		return y

# 	gui = CManipulator()

# 	gui.Xo = arange(0.0, 1.0, 0.001)
# 	gui.grf_title = '$N_{th}$ iteration of Bernoulli map; '
# 	gui.X_label = '$X_{ N}$'
# 	gui.Y_label = '$X_{N+1}$'
# 	gui.grf_stile =['-b',':r','-']
# 	gui.set_parameter_slider(prm_MIN=1,prm_MAX=10,prm_VAL=2,prm_res=1,prm_name='iter')
# 	gui.set_parameter_slider(prm_MIN=-10.,prm_MAX=23.,prm_VAL=0.,prm_res=0.01,prm_name='r')
# 	gui.m_func = [bernoulli_N_iteration,same_val]
# 	Tk.mainloop()


## Updates ########################################################	
# 
# - Now all the app is with grid instead of pack geometry method 
# - Object Oriented implementation of Manipulator
# 
## TBDs ############################################################	
# - self.evaluate_now True review
# - MIT Licence
# - Status line: "Ctrl+C for copying figure; Space bar for toggle grid
# - Settings window