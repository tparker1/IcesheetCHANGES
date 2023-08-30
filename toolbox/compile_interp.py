import numpy as np
import netCDF4 as nc
import datetime as dt
from scipy.interpolate import griddata

def get_crop_indicies(IC_object, x, y):
    # get the index closest to the bounds of the grid (or extents)
    # add/subtract indicies to make sure the grid is larger than the extents

    if IC_object.data_type.lower() == 'velocity':
        xgrid = IC_object.velocity_grid_x
        ygrid = IC_object.velocity_grid_y
    elif IC_object.data_type.lower() == 'elevation':
        xgrid = IC_object.elevation_grid_x
        ygrid = IC_object.elevation_grid_y
    else:
        print('Error: data type not recognized. Exiting...')
        return

    x_index_min = np.argmin(np.abs(x - xgrid[0])) 
    if x_index_min <= 10: x_index_min = 0
    else: x_index_min = x_index_min - 10

    x_index_max = np.argmin(np.abs(x - xgrid[-1])) + 10
    if x_index_max >= len(x): x_index_max = len(x)
    else: x_index_max = x_index_max + 10

    y_index_min = np.argmin(np.abs(y - ygrid[0]))  - 10
    if y_index_min <= 10: y_index_min = 0
    else: y_index_min = y_index_min - 10

    y_index_max = np.argmin(np.abs(y - ygrid[-1])) + 10
    if y_index_max >= len(y): y_index_max = len(y)
    else: y_index_max = y_index_max + 10

    return x_index_min, x_index_max, y_index_min, y_index_max

def crop_data(IC_object, file):
    ds = nc.Dataset(file, 'r')

    if IC_object.short_name == 'ATL15 Antarctic Elevation':
        x = ds.groups['delta_h'].variables['x'][:]
        y = ds.groups['delta_h'].variables['y'][:]
        time = ds.groups['delta_h'].variables['time'][:]  
        delta_h = ds.groups['delta_h'].variables['delta_h'][:]

        # get the index closest to the bounds of the grid (or extents)
        x_index_min, x_index_max, y_index_min, y_index_max = get_crop_indicies(IC_object, x, y)

        # crop the data
        x = x[x_index_min:x_index_max]
        y = y[y_index_min:y_index_max]
        delta_h = delta_h[:, y_index_min:y_index_max, x_index_min:x_index_max]

        # set masked values of delta_h to nan (scipy.interpolate.griddata does not work with masked arrays)
        delta_h_um = np.ma.filled(delta_h, np.nan)

        ds.close()

        return x, y, time, delta_h_um
    
    if IC_object.short_name == 'MEaSUREs Greenland Monthly Velocity':
        x = ds.variables['x'][:]
        y = ds.variables['y'][:]
        dates = ds.variables['dates'][:]

        v = ds.variables['V'][:]
        e = ds.variables['E'][:]
        vx = ds.variables['VX'][:]
        vy = ds.variables['VY'][:]
        ex = ds.variables['EX'][:]
        ey = ds.variables['EY'][:]

        # get the index closest to the bounds of the grid (or extents)
        x_index_min, x_index_max, y_index_min, y_index_max = get_crop_indicies(IC_object, x, y)

        # crop the data
        x = x[x_index_min:x_index_max]
        y = y[y_index_min:y_index_max]
        e = e[y_index_min:y_index_max, x_index_min:x_index_max]
        v = v[y_index_min:y_index_max, x_index_min:x_index_max]
        vx = vx[y_index_min:y_index_max, x_index_min:x_index_max]
        vy = vy[y_index_min:y_index_max, x_index_min:x_index_max]
        ex = ex[y_index_min:y_index_max, x_index_min:x_index_max]
        ey = ey[y_index_min:y_index_max, x_index_min:x_index_max]

        ds.close()

        return x, y, dates, v, e, vx, vy, ex, ey

    ## TODO: check/delete atl14 crop if still unused
    if IC_object.short_name == 'ATL14 Antarctic Elevation':
        x = ds.variables['x'][:]
        y = ds.variables['y'][:]
        h = ds.variables['h'][:]
        h_sigma = ds.variables['h_sigma'][:]

        x_index_min, x_index_max, y_index_min, y_index_max = get_crop_indicies(IC_object, x, y)

        x = x[x_index_min:x_index_max]
        y = y[y_index_min:y_index_max]
        h = h[y_index_min:y_index_max, x_index_min:x_index_max]
        h_sigma = h_sigma[y_index_min:y_index_max, x_index_min:x_index_max]

        ds.close()

        return x, y, h, h_sigma

    
    else:
        print('source not recognized')
        return
    
def interpolate_measures(IC_object, x, y, time, vx, vy, ex, ey):
    return

def interpolate_atl15(IC_object, x, y, time, delta_h_um):

    time_stack = []
    delta_h_stack = []

    Lat, Lon = np.meshgrid(x, y)   
    points = np.column_stack((Lat.ravel(), Lon.ravel()))

    XC, YC = np.meshgrid(IC_object.elevation_grid_x, IC_object.elevation_grid_y)
    C_pts = np.column_stack((XC.ravel(), YC.ravel()))

    for t in range(len(time)):
        time_stack.append(dt.datetime(2018,1,1) + dt.timedelta(days=float(time[t])))

        # TODO: Should array be initialized to the nan value -99999? 
        delta_h_array = np.zeros((len(IC_object.elevation_grid_y), len(IC_object.elevation_grid_x)))
        delta_h_array[:] = np.nan   

        # interpolate the data
        values = delta_h_um[t, :].ravel()
        interp_grid = griddata(points, values, C_pts)

        # reshape the data to the grid
        interp_grid = np.reshape(interp_grid, (len(IC_object.elevation_grid_y), len(IC_object.elevation_grid_x)))

        delta_h_stack.append(interp_grid)

    return time_stack, delta_h_stack


