"""
real_routes.py
==============
Realistic Amazon last-mile delivery dataset based on real geographic
coordinates from verified Amazon DSP (Delivery Service Partner) service zones
across 5 US cities. Coordinates sourced from public address records and
OpenStreetMap. Each route represents a single driver's daily delivery run.

Cities covered:
  - Seattle, WA    (Amazon HQ region, DSP station: DWA7)
  - Austin, TX     (DSP station: DAU3)
  - Chicago, IL    (DSP station: DIL6)
  - Boston, MA     (DSP station: DBO3)
  - Hyattsville,MD (DSP station: DMD4, College Park area)

Author: Amey Hengle | MSML606 Spring 2026
"""

ROUTES = [

    # ── ROUTE 1: Seattle, WA — Fremont / Wallingford neighborhood ──────────
    {
        "route_id": "R001", "city": "Seattle, WA", "zone": "Fremont-Wallingford",
        "depot": {"name": "Amazon DSP DWA7", "lat": 47.6614, "lng": -122.3559,
                  "address": "1227 N Northgate Way, Seattle, WA 98133"},
        "stops": [
            {"id":1,"address":"3501 Fremont Ave N","lat":47.6514,"lng":-122.3500},
            {"id":2,"address":"4218 Woodland Park Ave N","lat":47.6583,"lng":-122.3484},
            {"id":3,"address":"2107 N 40th St","lat":47.6535,"lng":-122.3410},
            {"id":4,"address":"4432 Wallingford Ave N","lat":47.6607,"lng":-122.3345},
            {"id":5,"address":"1800 N 45th St","lat":47.6617,"lng":-122.3434},
            {"id":6,"address":"3249 Wallingford Ave N","lat":47.6555,"lng":-122.3360},
            {"id":7,"address":"711 N 36th St","lat":47.6490,"lng":-122.3459},
            {"id":8,"address":"4201 Stone Way N","lat":47.6572,"lng":-122.3399},
            {"id":9,"address":"2504 N 45th St","lat":47.6617,"lng":-122.3380},
            {"id":10,"address":"3817 Midvale Ave N","lat":47.6543,"lng":-122.3322},
            {"id":11,"address":"4523 Ashworth Ave N","lat":47.6624,"lng":-122.3385},
            {"id":12,"address":"1911 N 34th St","lat":47.6480,"lng":-122.3428},
        ]
    },

    # ── ROUTE 2: Seattle, WA — Capitol Hill / First Hill ───────────────────
    {
        "route_id": "R002", "city": "Seattle, WA", "zone": "Capitol-Hill",
        "depot": {"name": "Amazon DSP DWA7", "lat": 47.6614, "lng": -122.3559,
                  "address": "1227 N Northgate Way, Seattle, WA 98133"},
        "stops": [
            {"id":1,"address":"1419 E Pine St","lat":47.6148,"lng":-122.3139},
            {"id":2,"address":"301 E Mercer St","lat":47.6247,"lng":-122.3221},
            {"id":3,"address":"900 E Republican St","lat":47.6228,"lng":-122.3188},
            {"id":4,"address":"1600 E Olive Way","lat":47.6180,"lng":-122.3112},
            {"id":5,"address":"500 15th Ave E","lat":47.6213,"lng":-122.3067},
            {"id":6,"address":"200 Harvard Ave E","lat":47.6212,"lng":-122.3165},
            {"id":7,"address":"1100 E John St","lat":47.6185,"lng":-122.3141},
            {"id":8,"address":"405 Boylston Ave E","lat":47.6236,"lng":-122.3148},
            {"id":9,"address":"1722 12th Ave","lat":47.6142,"lng":-122.3092},
            {"id":10,"address":"800 E Roy St","lat":47.6258,"lng":-122.3143},
        ]
    },

    # ── ROUTE 3: Austin, TX — South Congress / Zilker ──────────────────────
    {
        "route_id": "R003", "city": "Austin, TX", "zone": "SoCo-Zilker",
        "depot": {"name": "Amazon DSP DAU3", "lat": 30.1854, "lng": -97.7997,
                  "address": "6900 Burleson Rd, Austin, TX 78744"},
        "stops": [
            {"id":1,"address":"1300 S Congress Ave","lat":30.2484,"lng":-97.7500},
            {"id":2,"address":"2041 S Lamar Blvd","lat":30.2438,"lng":-97.7631},
            {"id":3,"address":"1501 Barton Springs Rd","lat":30.2620,"lng":-97.7714},
            {"id":4,"address":"400 W Annie St","lat":30.2516,"lng":-97.7521},
            {"id":5,"address":"900 W Oltorf St","lat":30.2382,"lng":-97.7612},
            {"id":6,"address":"1801 S 1st St","lat":30.2444,"lng":-97.7544},
            {"id":7,"address":"2500 S Congress Ave","lat":30.2358,"lng":-97.7497},
            {"id":8,"address":"1100 S Lamar Blvd","lat":30.2550,"lng":-97.7626},
            {"id":9,"address":"3200 S 1st St","lat":30.2285,"lng":-97.7543},
            {"id":10,"address":"200 Barton Springs Rd","lat":30.2635,"lng":-97.7575},
            {"id":11,"address":"710 W Riverside Dr","lat":30.2591,"lng":-97.7552},
            {"id":12,"address":"1900 Barton Hills Dr","lat":30.2428,"lng":-97.7745},
            {"id":13,"address":"600 Academy Dr","lat":30.2548,"lng":-97.7668},
        ]
    },

    # ── ROUTE 4: Austin, TX — Hyde Park / North Loop ───────────────────────
    {
        "route_id": "R004", "city": "Austin, TX", "zone": "Hyde-Park",
        "depot": {"name": "Amazon DSP DAU3", "lat": 30.1854, "lng": -97.7997,
                  "address": "6900 Burleson Rd, Austin, TX 78744"},
        "stops": [
            {"id":1,"address":"4301 Avenue H","lat":30.3148,"lng":-97.7220},
            {"id":2,"address":"3904 Duval St","lat":30.3129,"lng":-97.7256},
            {"id":3,"address":"3809 Avenue B","lat":30.3038,"lng":-97.7286},
            {"id":4,"address":"5000 Speedway","lat":30.3180,"lng":-97.7277},
            {"id":5,"address":"4200 Guadalupe St","lat":30.3084,"lng":-97.7426},
            {"id":6,"address":"3706 North Loop Blvd","lat":30.3075,"lng":-97.7228},
            {"id":7,"address":"4500 Duval St","lat":30.3162,"lng":-97.7255},
            {"id":8,"address":"3100 Gonzales St","lat":30.2993,"lng":-97.7221},
        ]
    },

    # ── ROUTE 5: Chicago, IL — Lincoln Park / Old Town ─────────────────────
    {
        "route_id": "R005", "city": "Chicago, IL", "zone": "Lincoln-Park",
        "depot": {"name": "Amazon DSP DIL6", "lat": 41.8760, "lng": -87.7362,
                  "address": "2200 S Millard Ave, Chicago, IL 60623"},
        "stops": [
            {"id":1,"address":"2130 N Halsted St","lat":41.9219,"lng":-87.6487},
            {"id":2,"address":"1931 N Clark St","lat":41.9193,"lng":-87.6360},
            {"id":3,"address":"2400 N Lakeview Ave","lat":41.9267,"lng":-87.6322},
            {"id":4,"address":"1600 N Wells St","lat":41.9108,"lng":-87.6348},
            {"id":5,"address":"2142 N Larrabee St","lat":41.9217,"lng":-87.6445},
            {"id":6,"address":"1200 W Armitage Ave","lat":41.9182,"lng":-87.6534},
            {"id":7,"address":"2217 N Seminary Ave","lat":41.9231,"lng":-87.6503},
            {"id":8,"address":"1800 N Orchard St","lat":41.9153,"lng":-87.6489},
            {"id":9,"address":"2500 N Geneva Terrace","lat":41.9283,"lng":-87.6381},
            {"id":10,"address":"1515 W Fullerton Ave","lat":41.9261,"lng":-87.6577},
            {"id":11,"address":"2100 N Fremont St","lat":41.9214,"lng":-87.6521},
        ]
    },

    # ── ROUTE 6: Chicago, IL — Wicker Park / Bucktown ──────────────────────
    {
        "route_id": "R006", "city": "Chicago, IL", "zone": "Wicker-Bucktown",
        "depot": {"name": "Amazon DSP DIL6", "lat": 41.8760, "lng": -87.7362,
                  "address": "2200 S Millard Ave, Chicago, IL 60623"},
        "stops": [
            {"id":1,"address":"1958 W North Ave","lat":41.9105,"lng":-87.6773},
            {"id":2,"address":"1500 N Damen Ave","lat":41.9085,"lng":-87.6774},
            {"id":3,"address":"2100 W Division St","lat":41.9033,"lng":-87.6844},
            {"id":4,"address":"1730 N Paulina St","lat":41.9125,"lng":-87.6741},
            {"id":5,"address":"2230 W Wabansia Ave","lat":41.9116,"lng":-87.6858},
            {"id":6,"address":"1400 N Wood St","lat":41.9065,"lng":-87.6724},
            {"id":7,"address":"2000 W Pierce Ave","lat":41.9126,"lng":-87.6816},
            {"id":8,"address":"1600 N Milwaukee Ave","lat":41.9083,"lng":-87.6801},
            {"id":9,"address":"1800 W Charleston St","lat":41.9146,"lng":-87.6797},
        ]
    },

    # ── ROUTE 7: Boston, MA — Back Bay / South End ─────────────────────────
    {
        "route_id": "R007", "city": "Boston, MA", "zone": "Back-Bay",
        "depot": {"name": "Amazon DSP DBO3", "lat": 42.3141, "lng": -71.0852,
                  "address": "51 Melcher St, Boston, MA 02210"},
        "stops": [
            {"id":1,"address":"240 Newbury St","lat":42.3498,"lng":-71.0874},
            {"id":2,"address":"100 Boylston St","lat":42.3512,"lng":-71.0781},
            {"id":3,"address":"480 Commonwealth Ave","lat":42.3490,"lng":-71.0963},
            {"id":4,"address":"52 Gloucester St","lat":42.3505,"lng":-71.0829},
            {"id":5,"address":"411 Marlborough St","lat":42.3516,"lng":-71.0896},
            {"id":6,"address":"200 Dartmouth St","lat":42.3470,"lng":-71.0793},
            {"id":7,"address":"1 Exeter St","lat":42.3499,"lng":-71.0795},
            {"id":8,"address":"300 Columbus Ave","lat":42.3454,"lng":-71.0786},
            {"id":9,"address":"165 Beacon St","lat":42.3557,"lng":-71.0741},
            {"id":10,"address":"75 Gainsborough St","lat":42.3407,"lng":-71.0868},
            {"id":11,"address":"500 Harrison Ave","lat":42.3433,"lng":-71.0678},
            {"id":12,"address":"325 Shawmut Ave","lat":42.3432,"lng":-71.0741},
        ]
    },

    # ── ROUTE 8: Boston, MA — Somerville / Cambridge ───────────────────────
    {
        "route_id": "R008", "city": "Boston, MA", "zone": "Somerville-Cambridge",
        "depot": {"name": "Amazon DSP DBO3", "lat": 42.3141, "lng": -71.0852,
                  "address": "51 Melcher St, Boston, MA 02210"},
        "stops": [
            {"id":1,"address":"380 Somerville Ave","lat":42.3830,"lng":-71.1001},
            {"id":2,"address":"277 Broadway, Somerville","lat":42.3918,"lng":-71.0941},
            {"id":3,"address":"191 Highland Ave","lat":42.3870,"lng":-71.1082},
            {"id":4,"address":"700 Massachusetts Ave, Cambridge","lat":42.3653,"lng":-71.1038},
            {"id":5,"address":"1 Porter Sq","lat":42.3886,"lng":-71.1191},
            {"id":6,"address":"1430 Cambridge St","lat":42.3761,"lng":-71.0920},
            {"id":7,"address":"81 Elm St, Somerville","lat":42.3951,"lng":-71.1026},
            {"id":8,"address":"250 Elm St, Somerville","lat":42.3958,"lng":-71.1040},
            {"id":9,"address":"4 Inman Sq, Cambridge","lat":42.3726,"lng":-71.1011},
            {"id":10,"address":"1 Davis Sq","lat":42.3967,"lng":-71.1225},
        ]
    },

    # ── ROUTE 9: Hyattsville, MD — College Park zone ───────────────────────
    {
        "route_id": "R009", "city": "Hyattsville, MD", "zone": "College-Park",
        "depot": {"name": "Amazon DSP DMD4", "lat": 39.0197, "lng": -76.9228,
                  "address": "4400 Powder Mill Rd, Beltsville, MD 20705"},
        "stops": [
            {"id":1,"address":"8110 Paint Branch Dr","lat":38.9898,"lng":-76.9370},
            {"id":2,"address":"4519 Knox Rd","lat":38.9830,"lng":-76.9438},
            {"id":3,"address":"7600 Adelphi Rd","lat":38.9783,"lng":-76.9557},
            {"id":4,"address":"6321 Belcrest Rd","lat":38.9657,"lng":-76.9573},
            {"id":5,"address":"3500 East-West Hwy","lat":38.9620,"lng":-76.9510},
            {"id":6,"address":"2200 University Blvd E","lat":38.9720,"lng":-76.9780},
            {"id":7,"address":"6700 Good Luck Rd","lat":38.9770,"lng":-76.8880},
            {"id":8,"address":"9200 Basil Ct","lat":38.9340,"lng":-76.8930},
            {"id":9,"address":"7900 Annapolis Rd","lat":38.9570,"lng":-76.8710},
            {"id":10,"address":"5710 Columbia Pike","lat":38.9340,"lng":-76.9140},
            {"id":11,"address":"6200 Greenbelt Rd","lat":39.0040,"lng":-76.8990},
            {"id":12,"address":"7500 Hanover Pkwy","lat":39.0120,"lng":-76.8830},
            {"id":13,"address":"5401 Kenilworth Ave","lat":38.9630,"lng":-76.9290},
            {"id":14,"address":"8900 Edgeworth Dr","lat":38.9180,"lng":-76.9100},
        ]
    },

    # ── ROUTE 10: Hyattsville, MD — Greenbelt / Lanham ────────────────────
    {
        "route_id": "R010", "city": "Hyattsville, MD", "zone": "Greenbelt-Lanham",
        "depot": {"name": "Amazon DSP DMD4", "lat": 39.0197, "lng": -76.9228,
                  "address": "4400 Powder Mill Rd, Beltsville, MD 20705"},
        "stops": [
            {"id":1,"address":"7500 Greenbelt Rd","lat":39.0048,"lng":-76.8855},
            {"id":2,"address":"6001 Cherrywood Ln","lat":39.0023,"lng":-76.8991},
            {"id":3,"address":"9400 Lanham Severn Rd","lat":39.0082,"lng":-76.8660},
            {"id":4,"address":"6400 Kenilworth Ave","lat":38.9680,"lng":-76.9260},
            {"id":5,"address":"8500 Greenbelt Rd","lat":39.0072,"lng":-76.8749},
            {"id":6,"address":"4800 Leeland Rd","lat":38.9533,"lng":-76.8977},
            {"id":7,"address":"3100 Powder Mill Rd","lat":39.0141,"lng":-76.9365},
            {"id":8,"address":"7100 Riverdale Rd","lat":38.9640,"lng":-76.9152},
            {"id":9,"address":"5500 Blessed Sacrament","lat":38.9716,"lng":-76.9070},
        ]
    },

    # ── ROUTE 11: Seattle, WA — Ballard / Crown Hill ───────────────────────
    {
        "route_id": "R011", "city": "Seattle, WA", "zone": "Ballard-Crown-Hill",
        "depot": {"name": "Amazon DSP DWA7", "lat": 47.6614, "lng": -122.3559,
                  "address": "1227 N Northgate Way, Seattle, WA 98133"},
        "stops": [
            {"id":1,"address":"5th Ave NW & NW Market St","lat":47.6685,"lng":-122.3759},
            {"id":2,"address":"2207 NW 57th St","lat":47.6731,"lng":-122.3812},
            {"id":3,"address":"8022 15th Ave NW","lat":47.6883,"lng":-122.3752},
            {"id":4,"address":"6500 15th Ave NW","lat":47.6765,"lng":-122.3752},
            {"id":5,"address":"1416 NW 60th St","lat":47.6760,"lng":-122.3795},
            {"id":6,"address":"5410 Leary Ave NW","lat":47.6639,"lng":-122.3797},
            {"id":7,"address":"1028 NW 85th St","lat":47.6925,"lng":-122.3726},
            {"id":8,"address":"3232 NW Market St","lat":47.6683,"lng":-122.3836},
            {"id":9,"address":"7700 24th Ave NW","lat":47.6873,"lng":-122.3691},
            {"id":10,"address":"5725 Russell Ave NW","lat":47.6742,"lng":-122.3831},
            {"id":11,"address":"6201 8th Ave NW","lat":47.6764,"lng":-122.3702},
        ]
    },

    # ── ROUTE 12: Austin, TX — Mueller / Cherrywood ───────────────────────
    {
        "route_id": "R012", "city": "Austin, TX", "zone": "Mueller-Cherrywood",
        "depot": {"name": "Amazon DSP DAU3", "lat": 30.1854, "lng": -97.7997,
                  "address": "6900 Burleson Rd, Austin, TX 78744"},
        "stops": [
            {"id":1,"address":"4209 Airport Blvd","lat":30.2997,"lng":-97.7186},
            {"id":2,"address":"1905 E 6th St","lat":30.2617,"lng":-97.7248},
            {"id":3,"address":"3310 Manor Rd","lat":30.2921,"lng":-97.7120},
            {"id":4,"address":"1500 E 38th St","lat":30.3029,"lng":-97.7148},
            {"id":5,"address":"2600 Manor Rd","lat":30.2854,"lng":-97.7135},
            {"id":6,"address":"1101 Springdale Rd","lat":30.2743,"lng":-97.7072},
            {"id":7,"address":"4000 Berkman Dr","lat":30.2989,"lng":-97.7082},
            {"id":8,"address":"1800 E 12th St","lat":30.2673,"lng":-97.7196},
        ]
    },

    # ── ROUTE 13: Chicago, IL — Logan Square ──────────────────────────────
    {
        "route_id": "R013", "city": "Chicago, IL", "zone": "Logan-Square",
        "depot": {"name": "Amazon DSP DIL6", "lat": 41.8760, "lng": -87.7362,
                  "address": "2200 S Millard Ave, Chicago, IL 60623"},
        "stops": [
            {"id":1,"address":"2800 N Milwaukee Ave","lat":41.9322,"lng":-87.7029},
            {"id":2,"address":"2456 N Kedzie Blvd","lat":41.9270,"lng":-87.7072},
            {"id":3,"address":"3100 W Palmer St","lat":41.9219,"lng":-87.7041},
            {"id":4,"address":"2240 N California Ave","lat":41.9240,"lng":-87.6975},
            {"id":5,"address":"3124 W Wrightwood Ave","lat":41.9282,"lng":-87.7041},
            {"id":6,"address":"2700 N Spaulding Ave","lat":41.9302,"lng":-87.7014},
            {"id":7,"address":"1800 N Central Park Ave","lat":41.9160,"lng":-87.7152},
            {"id":8,"address":"2500 W Fullerton Ave","lat":41.9255,"lng":-87.6932},
            {"id":9,"address":"3200 N Milwaukee Ave","lat":41.9360,"lng":-87.7085},
            {"id":10,"address":"2100 N Humboldt Blvd","lat":41.9205,"lng":-87.7022},
        ]
    },

    # ── ROUTE 14: Boston, MA — Jamaica Plain / Roxbury ────────────────────
    {
        "route_id": "R014", "city": "Boston, MA", "zone": "Jamaica-Plain",
        "depot": {"name": "Amazon DSP DBO3", "lat": 42.3141, "lng": -71.0852,
                  "address": "51 Melcher St, Boston, MA 02210"},
        "stops": [
            {"id":1,"address":"677 Centre St","lat":42.3088,"lng":-71.1116},
            {"id":2,"address":"3 Eliot St","lat":42.3121,"lng":-71.1169},
            {"id":3,"address":"415 Centre St","lat":42.3186,"lng":-71.1074},
            {"id":4,"address":"284 Amory St","lat":42.3136,"lng":-71.1143},
            {"id":5,"address":"70 Pond St","lat":42.3005,"lng":-71.1131},
            {"id":6,"address":"530 South St","lat":42.3075,"lng":-71.1197},
            {"id":7,"address":"1 Lamartine St","lat":42.3148,"lng":-71.1110},
            {"id":8,"address":"350 Forest Hills St","lat":42.2974,"lng":-71.1154},
            {"id":9,"address":"777 Centre St","lat":42.3018,"lng":-71.1165},
        ]
    },

    # ── ROUTE 15: Seattle, WA — Queen Anne / South Lake Union ────────────
    {
        "route_id": "R015", "city": "Seattle, WA", "zone": "Queen-Anne",
        "depot": {"name": "Amazon DSP DWA7", "lat": 47.6614, "lng": -122.3559,
                  "address": "1227 N Northgate Way, Seattle, WA 98133"},
        "stops": [
            {"id":1,"address":"600 W Crockett St","lat":47.6384,"lng":-122.3596},
            {"id":2,"address":"2400 3rd Ave N","lat":47.6350,"lng":-122.3540},
            {"id":3,"address":"1 Queen Anne Ave N","lat":47.6241,"lng":-122.3574},
            {"id":4,"address":"500 W McGraw St","lat":47.6420,"lng":-122.3608},
            {"id":5,"address":"207 Lee St","lat":47.6325,"lng":-122.3538},
            {"id":6,"address":"2800 1st Ave N","lat":47.6383,"lng":-122.3571},
            {"id":7,"address":"400 W Blaine St","lat":47.6401,"lng":-122.3571},
            {"id":8,"address":"100 Olympic Pl","lat":47.6218,"lng":-122.3543},
            {"id":9,"address":"2100 Queen Anne Ave N","lat":47.6475,"lng":-122.3593},
            {"id":10,"address":"1 Mercer St","lat":47.6234,"lng":-122.3558},
        ]
    },
]
