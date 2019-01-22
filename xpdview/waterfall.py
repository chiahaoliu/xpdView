import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider


class Waterfall:
    """class holds data and generate watefall plot

    Parameters
    ----------
    fig : matplotlib.Figure
        fig this waterfall plot will be drawn on
    canvas : matplotlib.Canvas
        canvas this waterfall plot will be drawn on
    key_list : list, optional
        list of key names. default to None
    int_data_list : list, optional
        list of 1D reduced data. expect each element to be in (x,y)
        format. default to None
    unit : tuple, optional
        a tuple containing strings of x and y labels
    kwargs :
        keyword arguments for plotting
    """

    def __init__(self, fig=None, canvas=None,
                 key_list=None, int_data_list=None,
                 *, unit=None, **kwargs):
        if int_data_list is None:
            int_data_list = []
        if key_list is None:
            key_list = []
        if not fig:
            fig = plt.figure()
        self.fig = fig
        if not canvas:
            canvas = self.fig.canvas
        self.canvas = canvas
        self.kwargs = kwargs
        self.x_array_list = []
        self.y_array_list = []

        # callback for showing legend
        self.canvas.mpl_connect('pick_event', self.on_plot_hover)
        self.key_list = key_list
        self.int_data_list = int_data_list
        self.ax = self.fig.add_subplot(111)
        self.unit = unit
        self.halt = False
        # add sliders, which store information
        self.ydist = 0
        self.xdist = 0
        y_offset_slider_ax = self.fig.add_axes([0.15, 0.95, 0.3, 0.035])
        self.y_offset_slider = Slider(y_offset_slider_ax,
                                      'y-offset', 0.0, 1.0,
                                      valinit=0.1, valfmt='%1.2f')
        self.y_offset_slider.on_changed(self.update_y_offset)
        x_offset_slider_ax = self.fig.add_axes([0.6, 0.95, 0.3, 0.035])
        self.x_offset_slider = Slider(x_offset_slider_ax,
                                      'x-offset', 0.0, 1.0,
                                      valinit=0., valfmt='%1.2f')
        self.x_offset_slider.on_changed(self.update_x_offset)
        # init
        self.update(self.key_list, self.int_data_list, refresh=True)

    def update(self, key_list, int_data_list, refresh=False):
        """top method to update information carried by class and plot

        Parameters
        ----------
        key_list : list
            list of keys.
        int_data_list : list
            list of 1D data.
        refresh : bool, optional
            option to set refresh or not. default to False.
        """
        # sanity check: stop if no data
        if not int_data_list:
            print("INFO: no reduced data was fed in, "
                  "waterfall plot can't be updated")
            self.halt = True
            return
        # sanity check: both are list
        if not isinstance(key_list, list) & isinstance(int_data_list, list):
            raise TypeError("Expect both key_list and int_data_list to "
                            "be list")
        # sanity check: both are the same length, if key_list is given
        if key_list and len(key_list) != len(int_data_list):
            raise ValueError("Expect key_list and int_data_list "
                             "to be the same length")
        # refresh if specified
        if refresh:
            self.key_list = []
            self.int_data_list = []
        # bookkeeping: assign arrays to class
        self.key_list.extend(key_list)
        self.int_data_list.extend(int_data_list)
        # update dx and dy and x,y array to the class
        self._adapt_data_list()
        # generate plot. it will only plot arrays & keys supplied
        self._update_plot(key_list, int_data_list, refresh)

    def _update_plot(self, key_list, int_data_list, refresh):
        """core method to update x-, y-offset sliders"""
        self.halt = False
        # sanity check: refresh & empty axes
        if refresh and self.ax.lines:
            raise ValueError("Expect empty axes when refresh set"
                             " to True in the update method")
        # update lines to axes
        for ind, (x, y) in enumerate(int_data_list):
            # note: could be better approach
            if key_list:
                k = key_list[ind]
            else:
                k = '' # this will causes warning when plotting legend
            self.ax.plot(x, y, picker=5, label=k, **self.kwargs)
        if self.unit:
            xlabel, ylabel = self.unit
            self.ax.set_xlabel(xlabel)
            self.ax.set_ylabel(ylabel)
        # draw
        self._draw_waterfall()

    def _draw_waterfall(self, x_offset_val=None, y_offset_val=None):
        """core method to draw waterfall plot"""
        # remain current offset if no new value is passed
        if not x_offset_val:
            x_offset_val = self.x_offset_slider.val
        if not y_offset_val:
            y_offset_val = self.y_offset_slider.val
        # update matplotlib line data
        for i, (l, x, y) in enumerate(zip(self.ax.lines,
                                          self.x_array_list,
                                          self.y_array_list)):
            xx = x+self.xdist*i*x_offset_val
            yy = y+self.ydist*i*y_offset_val
            l.set_data(xx, yy)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw_idle()

    def _adapt_data_list(self):
        """method to return statefull information of 1D data list"""
        # parse
        for x, y in self.int_data_list:
            self.xdist = max(np.ptp(x), self.xdist)
            self.ydist = max(np.ptp(y), self.ydist)
            self.x_array_list.append(x)
            self.y_array_list.append(y)

    def on_plot_hover(self, event):
        """callback to show legend when click on one of curves"""
        line = event.artist
        name = line.get_label()
        line.axes.legend([name], handlelength=0,
                         handletextpad=0, fancybox=True)
        line.figure.canvas.draw_idle()

    def update_y_offset(self, val):
        if self.halt:
            return
        self._draw_waterfall(None, val)

    def update_x_offset(self, val):
        if self.halt:
            return
        self._draw_waterfall(val, None)
