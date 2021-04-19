settings_initialised = False
administrator = False
db_path = None
connection_string = None
conn = None
update_assets_menu = None
prioritise_menu = None
preferred_region_menu = None
preferred_region = None
fma_group_bys = []
prioritisation_on = None
ogr2ogr_path = None
db = None
dev = False
uat = False

expected_values = {
    "asset_class": ["Settlement", "Dispersed Population", "Critical Infrastructure", "Susceptible Habitat", "Economic Asset", "Other Asset"],
    "resilience": ["H", "M", "L"],
    "fma": ["SHS", "CIB", "LRR", "RAM"]}
    

domains = {
    "fma_type": ['SHS', 'CIB', 'LRR', 'RAM'], 
    "fuel_type": ['Tropical savanna', 'Pindan', 'Hummock grassland', 'Sandplain shrubland', 'Thicket', 'Mallee heath', 'Dry eucalypt forest', 'Wet eucalypt forest', 'Banksia woodland', 'Plantation', 'Acacia woodland', 'Semi arid woodland', 'Chenopod woodland']}
    
value_ranges = {
    "threshold_age": {"Min": -1, "Max": 150, "Step": 1},
    "target": {"Min": -1, "Max": 100, "Step": 1}}
    
asset_class_priorities = {
    "Settlement": 1,
    "Dispersed Population": 2, 
    "Critical Infrastructure": 2,
    "Susceptible Habitat": 2,
    "Economic Asset": 3,
    "Other Asset": 3}
    
regional_priority_grid = {
    1: {"H": 3, "M": 2, "L": 1},
    2: {"H": 4, "M": 3, "L": 2},
    3: {"H": 5, "M": 4, "L": 3}}
    
forest_regions = ['swan', 'south_west', 'warren']

    
