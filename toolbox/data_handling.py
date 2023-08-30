import os
import netCDF4 as nc
import os
import toolbox.compile_interp as compile_interp
import toolbox.store_nc as store
import toolbox.measures as measures


def handle_measures(IC_object):
    if os.path.exists(IC_object.download_path):
        file_names = [
            file for file in os.listdir(IC_object.download_path)
            if file.endswith('.tif')
        ]
    else:
        print(
            "Error: download path does not exist. Please check that the data has been downloaded and is in the correct folder."
        )
        print(IC_object.download_path)
        print("Exiting...")
        return

    x, y, vx_grids, vy_grids, v_grids, ex_grids, ey_grids, e_grids, output_date_pairs = measures.create_velocity_stack(
        IC_object, file_names)
    store.output_data_stack_measures(IC_object, x, y, vx_grids, vy_grids,
                                     v_grids, ex_grids, ey_grids, e_grids,
                                     output_date_pairs)

    return
    #output_folder =  os.path.join(IC_object.data_folder, 'Quilted Grids', IC_object.icesheet_name, IC_object.region_name)
    #file = os.path.join(output_folder, IC_object.short_name + "_stack.nc")


def handle_atl(IC_object):
    # check if IC_object.download_path exists
    if os.path.exists(IC_object.download_path):
        if IC_object.icesheet_name == 'Greenland':
            download_path = IC_object.download_path
            files = [
                file for file in os.listdir(IC_object.download_path)
                if file.endswith('.nc') and '_01km_' in file and 'GL' in file
            ]
        elif IC_object.icesheet_name == 'Antarctic':
            download_path = IC_object.download_path
            files = [
                file for file in os.listdir(IC_object.download_path)
                if file.endswith('.nc') and '_01km_' in file and 'AA' in file
            ]
        else:
            print('Error: icesheet not recognized')
            return
    else:
        files = []

    # if the data was not found, check if it is in the other icesheet folder
    if len(files) == 0:
        print('Data not found in ' + IC_object.icesheet_name +
              ' folder. Checking other icesheet folder.')
        if IC_object.icesheet_name == 'Greenland':
            download_path = os.path.join(IC_object.data_folder, 'Antarctic',
                                         IC_object.data_type.title(),
                                         IC_object.short_name, 'Data')
            if os.path.exists(download_path):
                files = [
                    file for file in os.listdir(download_path) if
                    file.endswith('.nc') and '_01km_' in file and 'GL' in file
                ]
        elif IC_object.icesheet_name == 'Antarctic':
            download_path = os.path.join(IC_object.data_folder, 'Greenland',
                                         IC_object.data_type.title(),
                                         IC_object.short_name, 'Data')
            if os.path.exists(download_path):
                files = [
                    file for file in os.listdir(download_path) if
                    file.endswith('.nc') and '_01km_' in file and 'GL' in file
                ]
        else:
            print('Error: icesheet not recognized')
            return
        if len(files) == 0:
            print('Data not found in ' + IC_object.icesheet_name +
                  ' folder. Exiting.')
            return
        if len(files) >= 1:
            print('Data found. Continuing...')
        if len(files) > 1:
            print(
                'Warning: multiple files found. Using the first one. See toolbox.data_handling.handle_atl to change this behavior.'
            )

    # There is only one file per icesheet for 1km resolution
    file = os.path.join(download_path, files[0])

    # crop the data
    x, y, time, delta_h_um = compile_interp.crop_data(IC_object, file)

    time_stack, delta_h_stack = compile_interp.interpolate_atl15(
        IC_object, x, y, time, delta_h_um)

    #x_14, y_14, h_14, h_sigma_14 = get_atl14_data(IC_object)
    #IC_object.collection_info('ATL15 Antarctic Elevation')

    #store.output_data_stack_atl(IC_object, IC_object, time_stack, delta_h_stack) #, x_14, y_14, h_14, h_sigma_14)
    store.output_data_stack_atl_timedim(IC_object, time_stack, delta_h_stack)


def get_atl14_data(IC_object):
    og_short_name = IC_object.short_name
    IC_object.collection_info('ATL14 Antarctic Elevation')

    download_path = IC_object.download_path

    # check if IC_object.download_path exists
    if os.path.exists(IC_object.download_path):
        if IC_object.icesheet_name == 'Greenland':
            files = [
                file for file in os.listdir(IC_object.download_path)
                if file.endswith('.nc') and 'ATL14' in file and 'GL' in file
            ]
        elif IC_object.icesheet_name == 'Antarctic':
            files = [
                file for file in os.listdir(IC_object.download_path)
                if file.endswith('.nc') and 'ATL14' in file and 'AA' in file
            ]
        else:
            print('Error: icesheet not recognized')
            return
    else:
        files = []

    # if the data was not found, check if it is in the other icesheet folder
    if len(files) == 0:
        print('Data not found in ' + IC_object.icesheet_name +
              ' folder. Checking other icesheet folder.')
        if IC_object.icesheet_name == 'Greenland':
            download_path = os.path.join(IC_object.data_folder, 'Antarctic',
                                         IC_object.data_type.title(),
                                         IC_object.short_name, 'Data')
            if os.path.exists(download_path):
                files = [
                    file for file in os.listdir(download_path)
                    if file.endswith('.nc') and 'GL' in file
                ]
        elif IC_object.icesheet_name == 'Antarctic':
            download_path = os.path.join(IC_object.data_folder, 'Greenland',
                                         IC_object.data_type.title(),
                                         IC_object.short_name, 'Data')
            if os.path.exists(download_path):
                files = [
                    file for file in os.listdir(download_path)
                    if file.endswith('.nc') and 'GL' in file
                ]
        else:
            print('Error: icesheet not recognized')
            return
        if len(files) == 0:
            print('Data not found in ' + IC_object.icesheet_name +
                  ' folder. Exiting.')
            return
        if len(files) >= 1:
            print('Data found. Continuing...')
        if len(files) > 1:
            print(
                'Warning: multiple files found. Using the first one. See toolbox.data_handling.handle_atl to change this behavior.'
            )

    # There is only one file per icesheet
    file = os.path.join(download_path, files[0])

    ds = nc.Dataset(file, 'r')
    x = ds.variables['x'][:]
    y = ds.variables['y'][:]
    h = ds.variables['h'][:]
    h_sigma = ds.variables['h_sigma'][:]

    ds.close()

    IC_object.collection_info(og_short_name)

    return x, y, h, h_sigma
