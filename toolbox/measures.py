def monthStringToInt(month_as_string):
    months = {
        'Jan': 1,
        'Feb': 2,
        'Mar': 3,
        'Apr': 4,
        'May': 5,
        'Jun': 6,
        'Jul': 7,
        'Aug': 8,
        'Sep': 9,
        'Oct': 10,
        'Nov': 11,
        'Dec': 12,
    }
    return (months[month_as_string])


def measures_fileID_to_date_pair(fileID):
    #print(fileID)
    date1 = fileID.split('_')[4]
    date2 = fileID.split('_')[5]
    #print(date1, date2)

    year1 = int('20' + date1[-2:])
    month1 = monthStringToInt(date1[2:-2])
    day1 = int(date1[:2])

    year2 = int('20' + date2[-2:])
    month2 = monthStringToInt(date2[2:-2])
    day2 = int(date2[:2])

    datePair = str(year1) + "{:02d}".format(int(month1)) + "{:02d}".format(
        int(day1)) + '-' + str(year2) + "{:02d}".format(
            int(month2)) + "{:02d}".format(int(day2))
    return (datePair)


#import toolbox.measures as measures
def create_velocity_stack(IC_object, measures_mosaic_file_names):
    from osgeo import gdal
    import os
    import numpy as np
    import toolbox.compile_interp as interp
    import toolbox.store_nc as store

    print("test")

    # get the x, y to create the empty np arrays
    def get_x_y(file):
        print("Getting x and y")
        vx_file = os.path.join(IC_object.download_path, file)
        ds = gdal.Open(vx_file)
        vx_array = np.array(ds.GetRasterBand(1).ReadAsArray())

        transform = ds.GetGeoTransform()
        ds = None

        x = np.arange(transform[0],
                      transform[0] + np.shape(vx_array)[1] * transform[1],
                      transform[1])
        y = np.arange(transform[3],
                      transform[3] + np.shape(vx_array)[0] * transform[5],
                      transform[5])
        print("transform[1], x resolution: ", transform[1])
        print("transform[5], y resolution: ", transform[5])

        xIndices = np.logical_and(x >= IC_object.extents[0],
                                  x <= IC_object.extents[2])
        yIndices = np.logical_and(y >= IC_object.extents[1],
                                  y <= IC_object.extents[3])

        x = x[xIndices]
        y = y[yIndices]

        return x, y, xIndices, yIndices

    measures_mosaic_folder = IC_object.download_path

    # get all the date pairs (in the form: "20141201-20141231")
    date_pairs = []
    for file_name in measures_mosaic_file_names:
        date_pair = measures_fileID_to_date_pair(file_name)
        if date_pair not in date_pairs:
            date_pairs.append(date_pair)

    # find list of file IDs which contain all necessary files (vx, vy, ex, ey)
    file_sets = []
    fileIDs = []
    for date_pair in date_pairs:
        for file_name in measures_mosaic_file_names:

            fileID = file_name[:-13]
            fileID = fileID.split('/')[-1]
            date = measures_fileID_to_date_pair(fileID)
            if date_pair == date:
                if fileID not in fileIDs:
                    vx_found = False
                    vy_found = False
                    ex_found = False
                    ey_found = False
                    for file_name_check in os.listdir(
                            os.path.join(measures_mosaic_folder)):
                        if fileID + '_vx' in file_name_check:
                            vx_file = file_name_check
                            vx_found = True
                        if fileID + '_vy' in file_name_check:
                            vy_file = file_name_check
                            vy_found = True
                        if fileID + '_ex' in file_name_check:
                            ex_file = file_name_check
                            ex_found = True
                        if fileID + '_ey' in file_name_check:
                            ey_file = file_name_check
                            ey_found = True
                    if vx_found and vy_found and ex_found and ey_found:
                        fileIDs.append(fileID)
                        file_sets.append([vx_file, vy_file, ex_file, ey_file])

    output_date_pairs = []
    start_dates = []
    end_dates = []

    x, y, xIndices, yIndices = get_x_y(file_sets[0][0])
    vx_grid = np.zeros((len(date_pairs), len(y), len(x)))
    vy_grid = np.zeros((len(date_pairs), len(y), len(x)))
    ex_grid = np.zeros((len(date_pairs), len(y), len(x)))
    ey_grid = np.zeros((len(date_pairs), len(y), len(x)))
    v_grid = np.zeros((len(date_pairs), len(y), len(x)))
    e_grid = np.zeros((len(date_pairs), len(y), len(x)))

    vx_grid[::] = np.nan
    vy_grid[::] = np.nan
    ex_grid[::] = np.nan
    ey_grid[::] = np.nan
    v_grid[::] = np.nan
    e_grid[::] = np.nan

    for dd in range(len(date_pairs)):
        date_pair = date_pairs[dd]
        fileID = fileIDs[dd]
        file_set = file_sets[dd]

        message = '            Looking for velocity points in ' + date_pair + ' (file ' + str(
            dd + 1) + ' of ' + str(len(date_pairs)) + ')'
        IC_object.output_summary += '\n' + message
        if IC_object.print_sub_outputs:
            print(message)

        start_date = date_pair.split('-')[0]
        end_date = date_pair.split('-')[1]
        start_dates.append(start_date)
        end_dates.append(end_date)

        vx_file_name = file_set[0]
        vy_file_name = file_set[1]
        ex_file_name = file_set[2]
        ey_file_name = file_set[3]

        vx_file = os.path.join(IC_object.download_path, vx_file_name)
        ds = gdal.Open(vx_file)
        vx_array = np.array(ds.GetRasterBand(1).ReadAsArray())
        ds = None

        vx_array = vx_array[yIndices, :]
        vx_array = vx_array[:, xIndices]
        vx_array[vx_array < -1.e+09] = np.nan
        vx_grid[dd] = vx_array

        vy_file = os.path.join(IC_object.download_path, vy_file_name)
        ds = gdal.Open(vy_file)
        vy_array = np.array(ds.GetRasterBand(1).ReadAsArray())
        ds = None

        vy_array = vy_array[yIndices, :]
        vy_array = vy_array[:, xIndices]
        vy_array[vy_array < -1.e+09] = np.nan
        vy_grid[dd] = vy_array

        ex_file = os.path.join(IC_object.download_path, ex_file_name)
        ds = gdal.Open(ex_file)
        ex_array = np.array(ds.GetRasterBand(1).ReadAsArray())
        ds = None

        ex_array = ex_array[yIndices, :]
        ex_array = ex_array[:, xIndices]

        ex_array[ex_array < 0] = np.nan
        ex_grid[dd] = ex_array

        ey_file = os.path.join(IC_object.download_path, ey_file_name)
        ds = gdal.Open(ey_file)
        ey_array = np.array(ds.GetRasterBand(1).ReadAsArray())
        ds = None

        ey_array = ey_array[yIndices, :]
        ey_array = ey_array[:, xIndices]
        ey_array[ey_array < 0] = np.nan
        ey_grid[dd] = ey_array

        v_array = (vx_array**2 + vy_array**2)**0.5
        v_grid[dd] = v_array

        e_array = (ex_array**2 + ey_array**2)**0.5
        e_grid[dd] = e_array

        output_date_pairs.append(date_pair)

    return x, y, vx_grid, vy_grid, v_grid, ex_grid, ey_grid, e_grid, output_date_pairs