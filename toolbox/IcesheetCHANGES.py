# This file contains the class IcesheetCHANGES, which is the parent class for the AntarcticCHANGES and GreenlandCHANGES classes.
# The IcesheetCHANGES class is not intended to be used directly, but only to be inherited by the AntarcticCHANGES and GreenlandCHANGES classes.

import os
import toolbox.collection as collection


class IcesheetCHANGES:
    def __init__(self, project_folder, data_folder):

        self.project_folder = project_folder
        self.data_folder = data_folder

        self.region_name = ""
        self.glacier_name = ""
        self.nickname = "Unnamed"

        self.metadata_path = os.path.join(self.project_folder,
                                          self.region_name, 'Metadata')

        self.velocity_grid_x = []
        self.velocity_grid_y = []
        self.elevation_grid_y = []
        self.elevation_grid_x = []

        self.grid_dict = {}

        self.extents = []

        self.cells = []

        self.output_summary = ""

        self.print_sub_outputs = True

    def print_attributes(self):
        print("Metadata path:\t", self.metadata_path)
        return

    def print_collection_info(self):
        print("Collection ID: ", self.collection_id)
        print("Collection long name:\t", self.long_name)
        print("Collection short name:\t", self.short_name)
        print("Data type:\t\t", self.data_type)
        print("Download path:\t\t", self.download_path)

        return

    def collection_info(self, collection_key):
        self.collection_key = collection_key
        self.collection_id = collection.collection(collection_key)
        self.long_name, self.short_name = collection.get_names(
            self.collection_key)
        self.data_type = collection.get_data_type(self.collection_id).title()

        self.download_path = os.path.join(self.data_folder, self.icesheet_name,
                                          self.data_type, self.short_name,
                                          'Data')
        self.print_collection_info()

        return

    # To be removed. only here as example of how to set and get attributes
    # Projections are defined by EPSG codes (https://epsg.io/)

    def set_projection(self, projection):
        self.projection = projection

    def get_projection(self):
        return self.projection


class AntarcticCHANGES(IcesheetCHANGES):
    def __init__(self, project_folder, data_folder):
        super().__init__(project_folder, data_folder)

        self.posting = 100
        self.epsg = 3031
        self.icesheet_name = 'Antarctic'

        self.velocity_grid_posting = 100  # in km
        self.velocity_grid_epsg = 3031
        self.elevation_grid_posting = 100  # in km
        self.elevation_grid_epsg = 3031

    def print_attributes(self):
        super().print_attributes()
        print("Icesheet name:\t", self.icesheet_name)
        print("Posting:\t", self.posting, "km")
        print("EPSG:\t\t", self.epsg)

    def test(self):
        print('testAC')


class GreenlandCHANGES(IcesheetCHANGES):
    # Extents(boundary) of the icesheet stored in grid_generation.grid_bounds
    def __init__(self, project_folder, data_folder):
        super().__init__(project_folder, data_folder)

        self.posting = 50
        self.epsg = 3413
        self.icesheet_name = 'Greenland'

        self.velocity_grid_posting = 50  # in km
        self.velocity_grid_epsg = 3413
        self.elevation_grid_posting = 50  # in km
        self.elevation_grid_epsg = 3413

    def print_attributes(self):
        super().print_attributes()
        print("Icesheet name:\t", self.icesheet_name)
        print("Posting:\t", self.posting, "km")
        print("EPSG:\t\t", self.epsg)

    def test(self):
        print('testGC')
