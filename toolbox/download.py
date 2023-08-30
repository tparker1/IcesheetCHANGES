import itertools
import requests
import os

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# TODO: Functions for downloading data
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


# this function is from the ICESat2 data page
def cmr_filter_urls(search_results):
    """Select only the desired data files from CMR response."""
    if 'feed' not in search_results or 'entry' not in search_results['feed']:
        return []

    entries = [
        e['links'] for e in search_results['feed']['entry'] if 'links' in e
    ]
    # Flatten "entries" to a simple list of links
    links = list(itertools.chain(*entries))

    urls = []
    unique_filenames = set()
    for link in links:
        if 'href' not in link:
            # Exclude links with nothing to download
            continue  # continue jumps to next iteration in the loop
        if 'inherited' in link and link['inherited'] is True:
            # Why are we excluding these links?
            continue
        if 'rel' in link and 'data#' not in link['rel']:
            # Exclude links which are not classified by CMR as "data" or "metadata"
            continue
        if 'title' in link and 'opendap' in link['title'].lower():
            # Exclude OPeNDAP links--they are responsible for many duplicates
            # This is a hack; when the metadata is updated to properly identify
            # non-datapool links, we should be able to do this in a non-hack way
            continue

        filename = link['href'].split('/')[-1]
        if filename in unique_filenames:
            # Exclude links with duplicate filenames (they would overwrite)
            continue
        unique_filenames.add(filename)

        urls.append(link['href'])

    return urls


def cmr_filter_nested_urls(search_results):
    """Select only the desired data files from CMR response."""
    if 'feed' not in search_results or 'entry' not in search_results['feed']:
        return []

    all_urls = []
    for e in search_results['feed']['entry']:
        granule_id = e['producer_granule_id']
        urls = []

        # TODO can generalize this with an if statement for use with non-nested data, ie. measures_antarctic_annual
        urls.append(granule_id)
        for link in e['links']:
            if 'href' not in link:
                # Exclude links with nothing to download
                continue  # continue jumps to next iteration in the loop
            if 'inherited' in link and link['inherited'] is True:
                # Why are we excluding these links?
                continue
            if 'rel' in link and 'data#' not in link['rel']:
                # Exclude links which are not classified by CMR as "data" or "metadata"
                continue
            if 'title' in link and 'opendap' in link['title'].lower():
                # Exclude OPeNDAP links--they are responsible for many duplicates
                # This is a hack; when the metadata is updated to properly identify
                # non-datapool links, we should be able to do this in a non-hack way
                continue
            urls.append(link['href'])
        all_urls.append(urls)

    return all_urls


def get_response(url):
    response = requests.get(url)
    # print error code based on response or return search page
    if response.status_code != 200:
        print('ERROR: {}'.format(response.status_code))
    search_page = response.json()

    # If JSON contains an error message, print the message at the key, 'error'
    if 'errors' in search_page:
        print(search_page['errors'])
        urls = []
    else:
        urls = cmr_filter_urls(search_page)
        print("Successfully obtained {} URLs.".format(len(urls)))

    return urls


## write available file names and links to csv file
def write_to_csv(IC, availible_file_names, availible_file_links):
    if not os.path.exists(IC.metadata_path):
        os.makedirs(IC.metadata_path)

    f = open(os.path.join(IC.metadata_path, IC.short_name + '.csv'), 'w')
    f.write('File_Name,URL')
    for ea in range(len(availible_file_names)):
        f.write('\n' + availible_file_names[ea] + ',' +
                availible_file_links[ea])
    f.close()

    print('CSV file written to ' +
          os.path.join(IC.metadata_path, IC.short_name + '.csv'))

    return


def cmr_api_url(IC):
    # Build and call the CMR API URL
    cmr_query_url = 'https://cmr.earthdata.nasa.gov/search/granules.json?echo_collection_id=' + IC.collection_id + '&page_size=2000'
    response = requests.get(cmr_query_url)

    # print error code based on response
    if response.status_code != 200:
        print('ERROR: {}'.format(response.status_code))
    search_page = response.json()

    # If JSON contains an error message, print the message at the key, 'error'
    if 'errors' in search_page:
        print(search_page['errors'])
    else:
        urls = cmr_filter_urls(search_page)
        print("Successfully obtained {} URLs.".format(len(urls)))

        # Store the file names in a seperate list
        availible_file_links = []
        availible_file_names = []
        for url in urls:
            if not 'xml' in url:
                availible_file_links.append(url)
                url_parts = url.split('/')
                file_name = url_parts[-1]
                availible_file_names.append(file_name)
        write_to_csv(IC, availible_file_names, availible_file_links)

    return availible_file_names, availible_file_links


# check for existing files, get a list of files not on disk
def obtain_download_list(IC, file_names, file_links):

    output_folder = os.path.join(IC.download_path)
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    download_list_names = []
    download_list_links = []
    for file in file_names:
        download_file = True
        if file not in os.listdir(os.path.join(output_folder)):
            for existing_file in os.listdir(os.path.join(output_folder)):
                if file == existing_file:  # this allows for older versions to be kept
                    download_file = False
        else:
            download_file = False

        if download_file:
            download_list_names.append(file)
            download_list_links.append(file_links[file_names.index(file)])

    return (download_list_names, download_list_links)


def download_nc_direct(IC, file_names, file_links):

    print('Downloading ' + str(len(file_names)) + ' file(s)...')

    not_downloaded_names = []
    not_downloaded_links = []

    for i in range(len(file_names)):
        print('Downloading ' + str(i + 1) + '/' + str(len(file_names)) + ': ' +
              file_names[i],
              end='\r')

        # get request (download file)
        r = requests.get(file_links[i], allow_redirects=True)
        if r.status_code != 200:  # 200 is the standard response for successful HTTP requests
            print('ERROR: ' + str(r.status_code) + '\n')
            not_downloaded_names.append(file_names[i])
            not_downloaded_links.append(file_links[i])

        # write content to file
        open(os.path.join(IC.download_path, file_names[i]),
             'wb').write(r.content)
    return (not_downloaded_names, not_downloaded_links)


def run_download_nc_direct(IC, dl_list_names, dl_list_links):
    # Download the files
    not_downloaded_names, not_downloaded_links = download_nc_direct(
        IC, dl_list_names, dl_list_links)

    # Attempt to download any files that were not downloaded the first time
    if len(not_downloaded_names) > 0:
        print('The following files were not downloaded:')
        for i in range(len(not_downloaded_names)):
            print(not_downloaded_names[i] + ': ' + not_downloaded_links[i])

        print('Attempting to download these files once more...')
        not_downloaded_names, not_downloaded_links = download_nc_direct(
            IC, not_downloaded_names, not_downloaded_links)
        if len(not_downloaded_names) > 0:
            print(
                'Please download these files manually and place them in the following folder:'
            )
            print(IC.download_path)


def download_measures_monthly_files(IC, urls):
    not_downloaded = []
    bad_files = 0
    downloaded = 0

    print("Processing " + str(len(urls)) + " folders")

    #for folder in urls:
    for i in range(len(urls)):

        #    not_downloaded.append(folder_name)

        file_name = urls[i].split('/')[-1]

        # if the file exists already, skip it
        if os.path.exists(os.path.join(IC.download_path, file_name)):
            #print('    ' + file_name + ' already exists. Skipping...', end='\n')
            continue

        # only download the tif files
        if file_name.endswith('.tif'):
            print('    Downloading ' + file_name, end='\n')

            r = requests.get(urls[i], allow_redirects=True)
            if r.status_code != 200:  # 200 is the standard response for successful HTTP requests
                print('    ERROR: ' + str(r.status_code) + '\n')
                print('    Could not download ' + urls[i] + '\n')

                # Add the link to the list of files that were not downloaded
                not_downloaded.append(urls[i])
                bad_files += 1
                continue

            # write content to file
            #open(os.path.join(GC.data_folder, GC.region_name, 'Velocity', 'MEaSUREs', GC.collection_key, 'Data', folder_name, file_name), 'wb').write(r.content)
            open(os.path.join(IC.download_path, file_name),
                 'wb').write(r.content)
            downloaded += 1

    if (len(not_downloaded) > 0):
        print('WARNING: ' + str(bad_files) + ' file(s) were not downloaded.')
    else:
        print(str(downloaded) + ' files downloaded successfully.')

    return not_downloaded


def run_download_measures_monthly_files(IC, urls):

    not_downloaded = download_measures_monthly_files(IC, urls)

    # Attempt to download any files that were not downloaded the first time
    if len(not_downloaded) > 0:
        print('Attempting to download these files once more...')
        not_downloaded = download_measures_monthly_files(IC, not_downloaded)
        if len(not_downloaded) > 0:
            print('WARNING: some files were not downloaded.')
            print(
                'Please download the files manually and place in the corresponding folder:'
            )
            print('See file: ' +
                  os.path.join(IC.download_path, 'not_downloaded.txt'))
            print('\n')

            # store the list of files that were not downloaded in a text file
            with open(os.path.join(IC.download_path, 'not_downloaded.txt'),
                      'w') as f:
                for item in not_downloaded:
                    f.write("%s\n" % item)

    elif len(not_downloaded) == 0:
        print('All files downloaded successfully.')

    return not_downloaded


### REVIEW THE FOLLOWING THREE FUNCTIONS FOR REVISION OR REMOVAL
def download_files(IC, urls):
    bad_folders = []
    bad_files = 0
    downloaded = 0

    print("Processing " + str(len(urls)) + " folders")

    #for folder in urls:
    for i in range(len(urls)):
        folder = urls[i]
        folder_name = folder[0]

        # if verbose or verbose_light:
        #     print("Processing folder " + str(i + 1) + "/" + str(len(urls)) +
        #           ": " + folder_name)

        not_downloaded = []
        not_downloaded.append(folder_name)

        for link in folder[1:]:
            file_name = link.split('/')[-1]

            # if the file exists already, skip it
            if os.path.exists(os.path.join(IC.download_path, file_name)):
                #print('    ' + file_name + ' already exists. Skipping...', end='\n')
                continue

            # only download the tif files
            if file_name.endswith('.tif'):
                print('    Downloading ' + file_name, end='\n')

                r = requests.get(link, allow_redirects=True)
                if r.status_code != 200:  # 200 is the standard response for successful HTTP requests
                    print('    ERROR: ' + str(r.status_code) + '\n')
                    print('    Could not download ' + link + '\n')

                    # Add the link to the list of files that were not downloaded
                    not_downloaded.append([link])
                    bad_files += 1
                    continue

                # write content to file
                #open(os.path.join(GC.data_folder, GC.region_name, 'Velocity', 'MEaSUREs', GC.collection_key, 'Data', folder_name, file_name), 'wb').write(r.content)
                open(os.path.join(IC.download_path, file_name),
                     'wb').write(r.content)
                downloaded += 1

        if (len(not_downloaded)) > 1:
            bad_folders.append(not_downloaded)

    if (len(bad_folders) > 0):
        print('WARNING: ' + str(bad_files) + ' file(s) were not downloaded.')
    else:
        print(str(downloaded) + ' files downloaded successfully.')

    return bad_folders


def download_nested_files(IC, urls):
    bad_folders = []
    bad_files = 0
    downloaded = 0

    print("Processing " + str(len(urls)) + " folders")

    #for folder in urls:
    for i in range(len(urls)):
        folder = urls[i]
        folder_name = folder[0]

        # if verbose or verbose_light:
        #     print("Processing folder " + str(i + 1) + "/" + str(len(urls)) +
        #           ": " + folder_name)

        not_downloaded = []
        not_downloaded.append(folder_name)

        for link in folder[1:]:
            file_name = link.split('/')[-1]

            # if the file exists already, skip it
            if os.path.exists(
                    os.path.join(IC.download_path, folder_name, file_name)):
                # if verbose:
                #     print('    ' + file_name + ' already exists. Skipping...',
                #           end='\n')
                continue
            if not file_name.endswith('.tif'):
                # if verbose:
                #     print('    ' + file_name + ' is not a tif. Skipping...',
                #           end='\n')
                continue

            # only download the tif files
            if file_name.endswith('.tif'):
                if not os.path.exists(
                        os.path.join(IC.download_path, folder_name)):
                    os.makedirs(os.path.join(IC.download_path, folder_name))

                #if verbose or verbose_light:
                print('    Downloading ' + file_name, end='\n')

                r = requests.get(link, allow_redirects=True)
                if r.status_code != 200:  # 200 is the standard response for successful HTTP requests
                    print('    ERROR: ' + str(r.status_code) + '\n')
                    print('    Could not download ' + link + '\n')

                    # Add the link to the list of files that were not downloaded
                    not_downloaded.append([link])
                    bad_files += 1
                    continue

                # write content to file
                #open(os.path.join(GC.data_folder, GC.region_name, 'Velocity', 'MEaSUREs', GC.collection_key, 'Data', folder_name, file_name), 'wb').write(r.content)
                open(os.path.join(IC.download_path, folder_name, file_name),
                     'wb').write(r.content)
                downloaded += 1

        if (len(not_downloaded)) > 1:
            bad_folders.append(not_downloaded)

    if (len(bad_folders) > 0):
        print('WARNING: ' + str(bad_files) + ' file(s) were not downloaded.')
    else:
        print(str(downloaded) + ' files downloaded successfully.')

    return bad_folders


def run_download_files(IC, urls, nested):
    # Download the files
    if nested:
        not_downloaded = download_nested_files(IC, urls)
    else:
        not_downloaded = download_files(IC, urls)

    # Attempt to download any files that were not downloaded the first time
    if len(not_downloaded) > 0:
        print('Attempting to download these files once more...')
        if nested:
            not_downloaded = download_nested_files(IC, not_downloaded)
        else:
            not_downloaded = download_files(IC, not_downloaded)
        if len(not_downloaded) > 0:
            print('WARNING: some files were not downloaded.')
            print(
                'Please download the files manually and place in the corresponding folder:'
            )
            print('See file: ' +
                  os.path.join(IC.download_path, 'not_downloaded.txt'))
            print('\n')

            # store the list of files that were not downloaded in a text file
            with open(os.path.join(IC.download_path, 'not_downloaded.txt'),
                      'w') as f:
                for item in not_downloaded:
                    f.write("%s\n" % item)

    if len(not_downloaded) == 0:
        print('All files downloaded successfully.')
    return not_downloaded