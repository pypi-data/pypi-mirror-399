from urllib.request import urlopen, urlretrieve
from pathlib import Path
import shutil
from bs4 import BeautifulSoup as bs
import requests
import os
from glob import glob
from shutil import rmtree
import json
import re

def get_WORM_demo(demo_name, URL):
    
    # check to see if this notebook is being run inside of the read-only WORM Library folder
    cwd = os.getcwd()
    
    # main and raw URL prefixes for the WORM library
    URL_main_prefix = 'https://github.com/worm-portal/WORM-Library/tree/master/'
    URL_raw_prefix = 'https://raw.githubusercontent.com/worm-portal/WORM-Library/master/'
    
    # delete demo folder if it exists
    dirpath = Path(demo_name)
    if dirpath.exists() and dirpath.is_dir():
        shutil.rmtree(dirpath)

    # create a fresh demo folder
    dirpath.mkdir()

    res = requests.get(URL_main_prefix+URL)    
    soup = bs(res.text, 'lxml')   
    #     repo_files = soup.find_all('a', class_="js-navigation-open")

    #gitstr = str(soup.find_all('p')[0])

    try:
        try:
            gitstr = str([s for s in soup.find_all('script') if "payload" in str(s)][0])
            gitstr = gitstr.split(">")[1].split("<")[0]
            repo_files = [d["path"].split(URL+"/")[1] for d in json.loads(gitstr)["payload"]["tree"]["items"]]
        except:
            gitstr = str([s for s in soup.find_all('script') if "payload" in str(s)][1])
            gitstr = gitstr.split(">")[1].split("<")[0]
            repo_files = [d["path"].split(URL+"/")[1] for d in json.loads(gitstr)["payload"]["tree"]["items"]]
        
        # correct for ampersand in file names
        # e.g., S&amp;C10vents.csv becomes S&C10vents.csv
        repo_files = [re.sub("&amp;", "&", f) for f in repo_files]
    except:
        raise Exception("The WORM Library is currently experiencing difficulty connecting to GitHub where demos are "
                "hosted. Please inform Grayson Boyer gmboyer@asu.edu")

    files = []
    for i in repo_files:
        if ('.csv' in i or '.ipynb' in i or '.3i' in i or '.6i' in i or '.cmp' in i or '.speciation' in i) and '.ipynb_checkpoints' not in i:
            files.append(i)

    for file in files:
        if '.speciation' not in file:
            # Download from URL and decode as UTF-8 text.
            with urlopen(URL_raw_prefix+URL+"/"+file) as webpage:
                content = webpage.read().decode()
    
            # Save to file.
            with open(demo_name+"/"+file, 'w') as output:
                output.write(content)
        else:
            urlretrieve(URL_raw_prefix+URL+"/"+file, demo_name+"/"+file)

    print(demo_name+" is ready.")


def get_worm_tour():
    demo_name = "Demo-0-WORM-Tour"
    URL = "WORM-Tour"
    get_WORM_demo(demo_name, URL)

def get_introduction_demo():
    demo_name = "Demo-1-Introduction"
    URL = "1-Introduction"
    get_WORM_demo(demo_name, URL)
    
def get_reaction_properties_demo():
    demo_name = "Demo-2-(1-2-3)-Reaction-Properties"
    URL = "2-Reaction-Properties"
    get_WORM_demo(demo_name, URL)
    
def get_univariant_curve_demo():
    demo_name = "Demo-2-4-Geothermometry-Univariant"
    URL = "2-Reaction-Properties/4-Univariant-Curves"
    get_WORM_demo(demo_name, URL)
    
def get_intro_aqueous_speciation_demo():
    demo_name = "Demo-3-1-Intro-Aqueous_Speciation"
    URL = "3-Aqueous-Speciation/1-Introduction-to-Aq-Speciation"
    get_WORM_demo(demo_name, URL)
    
def get_multi_aqueous_speciation_demo():
    demo_name = "Demo-3-2-Multi-Aqueous_Speciation"
    URL = "3-Aqueous-Speciation/2-Multi-Sample-Speciation"
    get_WORM_demo(demo_name, URL)
    
def get_charge_balance_demo():
    demo_name = "Demo-3-3-Charge-Balance"
    URL = "3-Aqueous-Speciation/3-Charge-Balancing"
    get_WORM_demo(demo_name, URL) 
    
def get_heterogeneous_equilibrium_demo():
    demo_name = "Demo-3-4-1-Heterogeneous-Equilibrium"
    URL = "3-Aqueous-Speciation/4-Custom-Database/1-Introduction"
    get_WORM_demo(demo_name, URL)

def get_heterogeneous_equilibrium_gas_demo():
    demo_name = "Demo-3-4-2-Gas-Equilibrium"
    URL = "3-Aqueous-Speciation/Heterogeneous-Equil-Dissolve-Gas"
    get_WORM_demo(demo_name, URL)

def get_alter_suppress_demo():
    demo_name = "Demo-3-5-Alter-Suppress"
    URL = "3-Aqueous-Speciation/5-Alter-and-Suppress"
    get_WORM_demo(demo_name, URL)
    
def get_EQ3_demo():
    demo_name = "Demo-3-6-1-EQ3"
    URL = "3-Aqueous-Speciation/6-Extras/speciate-3i-file"
    get_WORM_demo(demo_name, URL)

def get_EQ6_demo():
    demo_name = "Demo-3-6-2-EQ6"
    URL = "3-Aqueous-Speciation/6-Extras/speciate-6i-file"
    get_WORM_demo(demo_name, URL)

def get_custom_data0_demo():
    demo_name = "Demo-3-6-3-Custom-data0"
    URL = "3-Aqueous-Speciation/4-Custom-Database/2-Creating-data0-files"
    get_WORM_demo(demo_name, URL)
    
def get_intro_mass_transfer_demo():
    demo_name = "Demo-3-7-1-Intro-Mass-Transfer"
    URL = "3-Aqueous-Speciation/7-Mass-Transfer/1-Introduction"
    get_WORM_demo(demo_name, URL)

def get_mass_transfer_feature_demo():
    demo_name = "Demo-3-7-2-Mass-Transfer-Features"
    URL = "3-Aqueous-Speciation/7-Mass-Transfer/2-Feature-Demo"
    get_WORM_demo(demo_name, URL)

def get_mixing_demo():
    demo_name = "Demo-3-7-3-Mixing-Fluids"
    URL = "3-Aqueous-Speciation/7-Mass-Transfer/3-Fluid-Mixing"
    get_WORM_demo(demo_name, URL)

def get_speciation_datasets_demo():
    demo_name = "Demo-3-8-Dataset-Exploration"
    URL = "3-Aqueous-Speciation/6-Extras/speciation-datasets"
    get_WORM_demo(demo_name, URL)

def get_energy_supply_demo():
    demo_name = "Demo-3-9-Energy-Supplies"
    URL = "3-Aqueous-Speciation/Intro-to-Energy-Supplies"
    get_WORM_demo(demo_name, URL)

def get_intro_aqorg_demo():
    demo_name = "Demo-4-1-1-Intro-AqOrg"
    URL = "4-Thermodynamic-Property-Estimation"
    get_WORM_demo(demo_name, URL)

def get_aqorg_feature_demo():
    demo_name = "Demo-4-1-2-AqOrg-Features"
    URL = "4-Thermodynamic-Property-Estimation/Aq-Organics-Feature-Demo"
    get_WORM_demo(demo_name, URL)

def get_complicator_demo():
    demo_name = "Demo-4-2-1-WORM-Complicator"
    URL = "4-Thermodynamic-Property-Estimation/Complicator"
    get_WORM_demo(demo_name, URL)

def get_estimate_HKF_demo():
    demo_name = "Demo-4-3-Estimate-HKF-Parameters"
    URL = "4-Thermodynamic-Property-Estimation/Estimate-HKF-Parameters"
    get_WORM_demo(demo_name, URL)

def get_Weeks_2025_demo():
    demo_name = "Demo-5-Ammonia-Speciation-Weeks-et-al-2025"
    URL = "5-Community-WORM-Notebooks/Ammonia-Speciation-Weeks-et-al-2025"
    get_WORM_demo(demo_name, URL)

def get_Trinh_2026_demo():
    demo_name = "Demo-5-Europa-Methanogenesis-Trinh-et-al-2026"
    URL = "5-Community-WORM-Notebooks/Europa-Methanogenesis-Trinh-et-al-2026"
    get_WORM_demo(demo_name, URL)

def get_whats_in_water_demo():
    demo_name = "Demo-5-Whats-In-Your-Water-Weeks-Debes-2025"
    URL = "5-Community-WORM-Notebooks/Whats-In-Your-Water-Weeks-Debes-2025"
    get_WORM_demo(demo_name, URL)

def get_workshop_demo(workshop_name):
    demo_name = "Demo-Workshop-"+workshop_name
    URL = "WORKSHOP"
    get_WORM_demo(demo_name, URL)
    
def delete_all_demos():
    path = os.getcwd()
    pattern = os.path.join(path, "Demo-*")

    for item in glob(pattern):
        if not os.path.isdir(item):
            continue
        rmtree(item)