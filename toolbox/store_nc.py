import os
import netCDF4 as nc
import datetime as dt
import xarray as xr
import numpy as np


def output_data_stack_atl_timedim(IC_object, time_stack, delta_h_stack):
    import datetime

    output_folder = os.path.join(IC_object.data_folder, 'Output',
                                 IC_object.icesheet_name,
                                 IC_object.region_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_file = os.path.join(output_folder,
                               IC_object.short_name + "_stack.nc")
    #if file exists, delete it
    if os.path.exists(output_file):
        #print("        Overwriting existing file...") #: " + output_file)
        #os.remove(output_file)
        print("        Skipping existing file...")  #: " + output_file)
        return

    ds = nc.Dataset(output_file, "w", format="NETCDF4")

    ds.createDimension('y', len(IC_object.velocity_grid_y))
    ds.createDimension('x', len(IC_object.velocity_grid_x))
    xvar = ds.createVariable('x', 'f4', ("x", ))
    yvar = ds.createVariable('y', 'f4', ("y", ))

    xvar[:] = IC_object.elevation_grid_x
    yvar[:] = IC_object.elevation_grid_y

    ds.createDimension('time', len(time_stack))
    timevar = ds.createVariable('time', 'f4', ("time", ))
    # convert time_stack to a float representation
    time_stack = [datetime.datetime.timestamp(t) for t in time_stack]
    timevar[:] = time_stack
    # create a variable for delta_h that has a time dimension
    delta_h = ds.createVariable('delta_h', 'f4', ("time", "y", "x"))
    delta_h[:, :, :] = delta_h_stack

    #create attribute title with IC.region_name
    ds.title = IC_object.region_name + ' ' + IC_object.short_name

    ds.close()

    message = '        Saved file to ' + output_file
    IC_object.output_summary += '\n' + message
    print(message)

    return


def output_grid_with_geo_reference_timedim(output_file,
                                           time,
                                           x,
                                           y,
                                           grid,
                                           grid_name,
                                           resolution=50):

    if os.path.isfile(output_file):
        os.remove(output_file)
    else:
        #create the path but not the file
        path = os.path.dirname(output_file)
        if not os.path.exists(path):
            os.makedirs(path)

    data_vars = {}
    data_vars[grid_name] = (['t', 'y', 'x'], grid)
    data_vars['projection'] = chr(0)

    # create dataset with variables t, y, x

    dataset = xr.Dataset(data_vars,
                         coords={
                             't': (('t'), time),
                             'y': y,
                             'x': x
                         })

    dataset['x'].attrs['long_name'] = 'Cartesian x-coordinate'
    dataset['x'].attrs['standard_name'] = 'projection_x_coordinate'
    dataset['x'].attrs['units'] = 'meters'
    dataset['x'].attrs['axis'] = 'X'
    dataset['x'].attrs['coverage_content_type'] = 'coordinate'
    dataset['x'].attrs['valid_min'] = np.min(x)
    dataset['x'].attrs['valid_max'] = np.max(x)
    dataset['x'].attrs[
        'comment'] = 'Projected horizontal coordinates of the grid'

    dataset['y'].attrs['long_name'] = 'Cartesian y-coordinate'
    dataset['y'].attrs['standard_name'] = 'projection_y_coordinate'
    dataset['y'].attrs['units'] = 'meters'
    dataset['y'].attrs['axis'] = 'Y'
    dataset['y'].attrs['coverage_content_type'] = 'coordinate'
    dataset['y'].attrs['valid_min'] = np.min(y)
    dataset['y'].attrs['valid_max'] = np.max(y)
    dataset['y'].attrs[
        'comment'] = 'Projected vertical coordinates of the grid'

    # dataset['projection'].attrs['grid_boundary_top_projected_y'] = np.max(y)
    # dataset['projection'].attrs['grid_boundary_bottom_projected_y'] = np.min(y)
    # dataset['projection'].attrs['grid_boundary_right_projected_x'] = np.max(x)
    # dataset['projection'].attrs['grid_boundary_left_projected_x'] = np.min(x)
    # dataset['projection'].attrs['parent_grid_cell_row_subset_start'] = int(0.0)
    # dataset['projection'].attrs['parent_grid_cell_row_subset_end'] = int(float(len(y)))
    # dataset['projection'].attrs['parent_grid_cell_column_subset_start'] = int(0.0)
    # dataset['projection'].attrs['parent_grid_cell_column_subset_end'] = int(float(len(x)))
    # dataset['projection'].attrs['spatial_ref'] = 'PROJCS["WGS 84 / NSIDC Sea Ice Polar Stereographic North",'\
    #                                               'GEOGCS["WGS 84",'\
    #                                                     'DATUM["WGS_1984",'\
    #                                                         'SPHEROID["WGS 84",6378137,298.257223563,'\
    #                                                            'AUTHORITY["EPSG","7030"]],'\
    #                                                         'AUTHORITY["EPSG","6326"]],'\
    #                                                     'PRIMEM["Greenwich",0,'\
    #                                                         'AUTHORITY["EPSG","8901"]],'\
    #                                                     'UNIT["degree",0.01745329251994328,'\
    #                                                         'AUTHORITY["EPSG","9122"]],'\
    #                                                     'AUTHORITY["EPSG","4326"]],'\
    #                                                 'UNIT["metre",1,'\
    #                                                     'AUTHORITY["EPSG","9001"]],'\
    #                                                 'PROJECTION["Polar_Stereographic"],'\
    #                                                 'PARAMETER["latitude_of_origin",70],'\
    #                                                 'PARAMETER["central_meridian",-45],'\
    #                                                 'PARAMETER["scale_factor",1],'\
    #                                                 'PARAMETER["false_easting",0],'\
    #                                                 'PARAMETER["false_northing",0],'\
    #                                                 'AUTHORITY["EPSG","3413"],'\
    #                                                 'AXIS["X",UNKNOWN],'\
    #                                                 'AXIS["Y",UNKNOWN]]'

    # dataset['projection'].attrs['grid_mapping_name'] = "polar_stereographic"
    # dataset['projection'].attrs['proj4text'] = '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
    # dataset['projection'].attrs['srid'] = 'urn:ogc:def:crs:EPSG::3413'
    # dataset['projection'].attrs['GeoTransform'] = str(np.min(x)) + ' ' + str(resolution) + ' 0 ' + str(np.max(y)) + ' 0 ' + str(-resolution)
    # dataset['projection'].attrs['grid_mapping_name'] = "polar_stereographic"
    # dataset['projection'].attrs['latitude_of_projection_origin'] = int(70)
    # dataset['projection'].attrs['longitude_of_projection_origin'] = int(-45)
    # dataset['projection'].attrs['scaling_factor'] = 1
    # dataset['projection'].attrs['false_easting'] = 0.0
    # dataset['projection'].attrs['false_northing'] = 0.0
    # dataset['projection'].attrs['units'] = "meters"

    dataset.to_netcdf(output_file)
    return


def add_atl14_to_nc(IC_object, output_file):
    import toolbox.data_handling as data
    ds = nc.Dataset(output_file, 'a')
    x, y, h, h_sigma = data.get_atl14_data(IC_object)

    #agg group called atl14
    atl14 = ds.createGroup('ATL14')
    #dimension is y by x
    atl14.createDimension('x', len(x))
    atl14.createDimension('y', len(y))

    #variables
    atl14.createVariable('x', 'f4', ('x', ))
    atl14.createVariable('y', 'f4', ('y', ))
    atl14.createVariable('h', 'f4', ('y', 'x'))
    atl14.createVariable('h_sigma', 'f4', ('y', 'x'))

    #attributes
    atl14['x'].units = 'meters'
    atl14['x'].long_name = 'Cartesian x-coordinate'
    atl14['x'].standard_name = 'projection_x_coordinate'
    atl14['x'].axis = 'X'

    atl14['y'].units = 'meters'
    atl14['y'].long_name = 'Cartesian y-coordinate'
    atl14['y'].standard_name = 'projection_y_coordinate'
    atl14['y'].axis = 'Y'

    atl14['h'].units = 'meters'
    atl14['h'].long_name = 'Elevation'
    atl14['h'].standard_name = 'surface_altitude'

    atl14['h_sigma'].units = 'meters'
    atl14['h_sigma'].long_name = 'Elevation uncertainty'
    atl14['h_sigma'].standard_name = 'surface_altitude_uncertainty'

    #data
    atl14['x'][:] = x
    atl14['y'][:] = y
    atl14['h'][:] = h
    atl14['h_sigma'][:] = h_sigma

    ds.close()

    return


def output_grid_with_geo_reference_timedim_atl(IC_object,
                                               output_file,
                                               time,
                                               x,
                                               y,
                                               grid,
                                               grid_name,
                                               resolution=50):

    if os.path.isfile(output_file):
        os.remove(output_file)
    else:
        #create the path but not the file
        path = os.path.dirname(output_file)
        if not os.path.exists(path):
            os.makedirs(path)

    data_vars = {}
    data_vars[grid_name] = (['t', 'y', 'x'], grid)
    data_vars['projection'] = chr(0)

    dataset = xr.Dataset(data_vars,
                         coords={
                             't': (('t'), time),
                             'y': y,
                             'x': x
                         })

    dataset.attrs[
        'title'] = IC_object.icesheet_name + ' ' + IC_object.data_type.title(
        ) + ' ' + IC_object.nickname + ' ' + 'Stack'

    dataset['t'].attrs['long_name'] = 'Time'
    dataset['t'].attrs['standard_name'] = 'time'
    dataset['t'].attrs['comment'] = 'datetime timestamp'

    dataset['x'].attrs['long_name'] = 'Cartesian x-coordinate'
    dataset['x'].attrs['standard_name'] = 'projection_x_coordinate'
    dataset['x'].attrs['units'] = 'meters'
    dataset['x'].attrs['axis'] = 'X'
    dataset['x'].attrs['coverage_content_type'] = 'coordinate'
    dataset['x'].attrs['valid_min'] = np.min(x)
    dataset['x'].attrs['valid_max'] = np.max(x)
    dataset['x'].attrs[
        'comment'] = 'Projected horizontal coordinates of the grid'

    dataset['y'].attrs['long_name'] = 'Cartesian y-coordinate'
    dataset['y'].attrs['standard_name'] = 'projection_y_coordinate'
    dataset['y'].attrs['units'] = 'meters'
    dataset['y'].attrs['axis'] = 'Y'
    dataset['y'].attrs['coverage_content_type'] = 'coordinate'
    dataset['y'].attrs['valid_min'] = np.min(y)
    dataset['y'].attrs['valid_max'] = np.max(y)
    dataset['y'].attrs[
        'comment'] = 'Projected vertical coordinates of the grid'

    dataset['projection'].attrs['grid_boundary_top_projected_y'] = np.max(y)
    dataset['projection'].attrs['grid_boundary_bottom_projected_y'] = np.min(y)
    dataset['projection'].attrs['grid_boundary_right_projected_x'] = np.max(x)
    dataset['projection'].attrs['grid_boundary_left_projected_x'] = np.min(x)
    dataset['projection'].attrs['parent_grid_cell_row_subset_start'] = int(0.0)
    dataset['projection'].attrs['parent_grid_cell_row_subset_end'] = int(
        float(len(y)))
    dataset['projection'].attrs['parent_grid_cell_column_subset_start'] = int(
        0.0)
    dataset['projection'].attrs['parent_grid_cell_column_subset_end'] = int(
        float(len(x)))
    # dataset['projection'].attrs['spatial_ref'] = 'PROJCS["WGS 84 / NSIDC Sea Ice Polar Stereographic North",'\
    #                                               'GEOGCS["WGS 84",'\
    #                                                     'DATUM["WGS_1984",'\
    #                                                         'SPHEROID["WGS 84",6378137,298.257223563,'\
    #                                                            'AUTHORITY["EPSG","7030"]],'\
    #                                                         'AUTHORITY["EPSG","6326"]],'\
    #                                                     'PRIMEM["Greenwich",0,'\
    #                                                         'AUTHORITY["EPSG","8901"]],'\
    #                                                     'UNIT["degree",0.01745329251994328,'\
    #                                                         'AUTHORITY["EPSG","9122"]],'\
    #                                                     'AUTHORITY["EPSG","4326"]],'\
    #                                                 'UNIT["metre",1,'\
    #                                                     'AUTHORITY["EPSG","9001"]],'\
    #                                                 'PROJECTION["Polar_Stereographic"],'\
    #                                                 'PARAMETER["latitude_of_origin",70],'\
    #                                                 'PARAMETER["central_meridian",-45],'\
    #                                                 'PARAMETER["scale_factor",1],'\
    #                                                 'PARAMETER["false_easting",0],'\
    #                                                 'PARAMETER["false_northing",0],'\
    #                                                 'AUTHORITY["EPSG","3413"],'\
    #                                                 'AXIS["X",UNKNOWN],'\
    #                                                 'AXIS["Y",UNKNOWN]]'

    # dataset['projection'].attrs['grid_mapping_name'] = "polar_stereographic"
    # dataset['projection'].attrs['proj4text'] = '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
    # dataset['projection'].attrs['srid'] = 'urn:ogc:def:crs:EPSG::3413'
    # dataset['projection'].attrs['GeoTransform'] = str(np.min(x)) + ' ' + str(resolution) + ' 0 ' + str(np.max(y)) + ' 0 ' + str(-resolution)
    # dataset['projection'].attrs['grid_mapping_name'] = "polar_stereographic"
    # dataset['projection'].attrs['latitude_of_projection_origin'] = int(70)
    # dataset['projection'].attrs['longitude_of_projection_origin'] = int(-45)
    # dataset['projection'].attrs['scaling_factor'] = 1
    # dataset['projection'].attrs['false_easting'] = 0.0
    # dataset['projection'].attrs['false_northing'] = 0.0
    # dataset['projection'].attrs['units'] = "meters"

    dataset.to_netcdf(output_file)
    dataset.close()

    if IC_object.short_name == 'ATL15 Antarctic Elevation':
        add_atl14_to_nc(IC_object, output_file)

    return


def output_grid_with_geo_reference_timedim_measures(IC_object,
                                                    output_file,
                                                    time,
                                                    x,
                                                    y,
                                                    grid,
                                                    grid_name,
                                                    resolution=50):

    if os.path.isfile(output_file):
        os.remove(output_file)

    else:
        #create the path but not the file
        path = os.path.dirname(output_file)
        if not os.path.exists(path):
            os.makedirs(path)

    data_vars = {}
    data_vars[grid_name] = (['t', 'y', 'x'], grid)
    data_vars['projection'] = chr(0)

    dataset = xr.Dataset(data_vars,
                         coords={
                             't': (('t'), time),
                             'y': y,
                             'x': x
                         })

    dataset.attrs[
        'title'] = IC_object.icesheet_name + ' ' + IC_object.data_type.title(
        ) + ' ' + IC_object.nickname + ' ' + 'Stack'

    dataset['t'].attrs['long_name'] = 'Time'
    dataset['t'].attrs['standard_name'] = 'time'
    dataset['t'].attrs['comment'] = 'datetime timestamp'

    dataset['x'].attrs['long_name'] = 'Cartesian x-coordinate'
    dataset['x'].attrs['standard_name'] = 'projection_x_coordinate'
    dataset['x'].attrs['units'] = 'meters'
    dataset['x'].attrs['axis'] = 'X'
    dataset['x'].attrs['coverage_content_type'] = 'coordinate'
    dataset['x'].attrs['valid_min'] = np.min(x)
    dataset['x'].attrs['valid_max'] = np.max(x)
    dataset['x'].attrs[
        'comment'] = 'Projected horizontal coordinates of the grid'

    dataset['y'].attrs['long_name'] = 'Cartesian y-coordinate'
    dataset['y'].attrs['standard_name'] = 'projection_y_coordinate'
    dataset['y'].attrs['units'] = 'meters'
    dataset['y'].attrs['axis'] = 'Y'
    dataset['y'].attrs['coverage_content_type'] = 'coordinate'
    dataset['y'].attrs['valid_min'] = np.min(y)
    dataset['y'].attrs['valid_max'] = np.max(y)
    dataset['y'].attrs[
        'comment'] = 'Projected vertical coordinates of the grid'

    dataset['projection'].attrs['grid_boundary_top_projected_y'] = np.max(y)
    dataset['projection'].attrs['grid_boundary_bottom_projected_y'] = np.min(y)
    dataset['projection'].attrs['grid_boundary_right_projected_x'] = np.max(x)
    dataset['projection'].attrs['grid_boundary_left_projected_x'] = np.min(x)
    dataset['projection'].attrs['parent_grid_cell_row_subset_start'] = int(0.0)
    dataset['projection'].attrs['parent_grid_cell_row_subset_end'] = int(
        float(len(y)))
    dataset['projection'].attrs['parent_grid_cell_column_subset_start'] = int(
        0.0)
    dataset['projection'].attrs['parent_grid_cell_column_subset_end'] = int(
        float(len(x)))
    # dataset['projection'].attrs['spatial_ref'] = 'PROJCS["WGS 84 / NSIDC Sea Ice Polar Stereographic North",'\
    #                                               'GEOGCS["WGS 84",'\
    #                                                     'DATUM["WGS_1984",'\
    #                                                         'SPHEROID["WGS 84",6378137,298.257223563,'\
    #                                                            'AUTHORITY["EPSG","7030"]],'\
    #                                                         'AUTHORITY["EPSG","6326"]],'\
    #                                                     'PRIMEM["Greenwich",0,'\
    #                                                         'AUTHORITY["EPSG","8901"]],'\
    #                                                     'UNIT["degree",0.01745329251994328,'\
    #                                                         'AUTHORITY["EPSG","9122"]],'\
    #                                                     'AUTHORITY["EPSG","4326"]],'\
    #                                                 'UNIT["metre",1,'\
    #                                                     'AUTHORITY["EPSG","9001"]],'\
    #                                                 'PROJECTION["Polar_Stereographic"],'\
    #                                                 'PARAMETER["latitude_of_origin",70],'\
    #                                                 'PARAMETER["central_meridian",-45],'\
    #                                                 'PARAMETER["scale_factor",1],'\
    #                                                 'PARAMETER["false_easting",0],'\
    #                                                 'PARAMETER["false_northing",0],'\
    #                                                 'AUTHORITY["EPSG","3413"],'\
    #                                                 'AXIS["X",UNKNOWN],'\
    #                                                 'AXIS["Y",UNKNOWN]]'

    # dataset['projection'].attrs['grid_mapping_name'] = "polar_stereographic"
    # dataset['projection'].attrs['proj4text'] = '+proj=stere +lat_0=90 +lat_ts=70 +lon_0=-45 +k=1 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs'
    # dataset['projection'].attrs['srid'] = 'urn:ogc:def:crs:EPSG::3413'
    # dataset['projection'].attrs['GeoTransform'] = str(np.min(x)) + ' ' + str(resolution) + ' 0 ' + str(np.max(y)) + ' 0 ' + str(-resolution)
    # dataset['projection'].attrs['grid_mapping_name'] = "polar_stereographic"
    # dataset['projection'].attrs['latitude_of_projection_origin'] = int(70)
    # dataset['projection'].attrs['longitude_of_projection_origin'] = int(-45)
    # dataset['projection'].attrs['scaling_factor'] = 1
    # dataset['projection'].attrs['false_easting'] = 0.0
    # dataset['projection'].attrs['false_northing'] = 0.0
    # dataset['projection'].attrs['units'] = "meters"

    dataset.to_netcdf(output_file)
    dataset.close()

    return


def output_data_stack_measures(IC_object, x, y, vx_grids, vy_grids, v_grids,
                               ex_grids, ey_grids, e_grids, date_pairs):

    #output_folder =  os.path.join(IC_object.data_folder, 'Quilted Grids', IC_object.icesheet_name, IC_object.region_name)
    output_folder = os.path.join(IC_object.data_folder, 'Output',
                                 IC_object.icesheet_name,
                                 IC_object.region_name)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    output_file = os.path.join(output_folder,
                               IC_object.short_name + "_stack.nc")
    #if output_file exists, delete it
    if os.path.exists(output_file):
        os.remove(output_file)

    starts = []
    ends = []

    for i in range(len(date_pairs)):
        start_date = date_pairs[i].split('-')[0]
        end_date = date_pairs[i].split('-')[1]
        start_date = dt.datetime.strptime(start_date, '%Y%m%d')
        end_date = dt.datetime.strptime(end_date, '%Y%m%d')
        starts.append(start_date)
        ends.append(end_date)

    # convert to datetime timestamp integer
    start_stack = [dt.datetime.timestamp(t) for t in starts]
    end_stack = [dt.datetime.timestamp(t) for t in ends]

    # sort start_stack and then sort end_stack in the same way
    start_stack = np.array(start_stack)
    end_stack = np.array(end_stack)
    date_pairs = np.array(date_pairs)

    sort_index = np.argsort(start_stack)

    start_stack = start_stack[sort_index]
    end_stack = end_stack[sort_index]
    vx_grids = vx_grids[sort_index]
    vy_grids = vy_grids[sort_index]
    v_grids = v_grids[sort_index]
    ex_grids = ex_grids[sort_index]
    ey_grids = ey_grids[sort_index]
    e_grids = e_grids[sort_index]
    date_pairs = date_pairs[sort_index]

    # code to convert back to datetime
    #start_stack = [dt.datetime.fromtimestamp(t) for t in start_stack]
    #end_stack = [dt.datetime.fromtimestamp(t) for t in end_stack]

    data = nc.Dataset(output_file, "w", format="NETCDF4")

    data.createDimension('y', len(y))
    data.createDimension('x', len(x))
    data.createDimension('time', len(date_pairs))

    xvar = data.createVariable('x', 'f4', ("x", ))
    yvar = data.createVariable('y', 'f4', ("y", ))
    start_time_var = data.createVariable('time_start', 'f4', ('time', ))
    end_time_var = data.createVariable('time_end', 'f4', ('time', ))

    start_time_var[:] = start_stack
    end_time_var[:] = end_stack
    xvar[:] = x  #IC_object.velocity_grid_x
    yvar[:] = y  #IC_object.velocity_grid_y

    vx = data.createVariable('VX', 'f4', ("time", "y", "x"))
    vy = data.createVariable('VY', 'f4', ("time", "y", "x"))
    v = data.createVariable('V', 'f4', ("time", "y", "x"))
    ex = data.createVariable('EX', 'f4', ("time", "y", "x"))
    ey = data.createVariable('EY', 'f4', ("time", "y", "x"))
    e = data.createVariable('E', 'f4', ("time", "y", "x"))

    vx[:, :, :] = vx_grids
    vy[:, :, :] = vy_grids
    v[:, :, :] = v_grids
    ex[:, :, :] = ex_grids
    ey[:, :, :] = ey_grids
    e[:, :, :] = e_grids

    data.close()

    message = '        Saved MEaSUREs Quarterly Mosaic file to ' + output_file
    #IC_object.output_summary += '\n' + message
    #if IC_object.print_sub_outputs:
    #    print(message)

    return