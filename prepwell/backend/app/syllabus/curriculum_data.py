"""Curated, in-code curriculum source of truth.

PrepWell stays local-first: this curriculum is curated from the standard published
NCERT framework (which the overwhelming majority of Indian boards follow closely),
NOT scraped at runtime. Every board in ``BOARDS`` maps to a *curriculum* key; if a
board has no specialised curriculum yet, the syllabus service falls back to ``ncert``.

To specialise a board, add its curriculum under ``CURRICULUM["<key>"]`` (or drop
override JSON files into ``data/syllabus/`` — see syllabus/service.py). Classes are
strings "1".."10"; subjects match config.SUBJECTS.
"""
from __future__ import annotations

from typing import Any

DEFAULT_BOARD = "cbse"
DEFAULT_CURRICULUM = "ncert"


# ---- Board registry (national + state boards) -------------------------------
# Each board maps to a curriculum key. Most state boards adopt the NCERT
# framework; ICSE is flagged with its own key to demonstrate per-board overrides
# (it falls back to NCERT content until an "icse" curriculum is authored).
BOARDS: list[dict[str, str]] = [
    {"code": "cbse", "name": "CBSE", "type": "national", "curriculum": "ncert"},
    {"code": "icse", "name": "ICSE / CISCE", "type": "national", "curriculum": "icse"},
    {"code": "nios", "name": "NIOS (Open Schooling)", "type": "national", "curriculum": "ncert"},
    {"code": "ap", "name": "Andhra Pradesh (BSEAP)", "type": "state", "curriculum": "ncert"},
    {"code": "assam", "name": "Assam (SEBA)", "type": "state", "curriculum": "ncert"},
    {"code": "bihar", "name": "Bihar (BSEB)", "type": "state", "curriculum": "ncert"},
    {"code": "cg", "name": "Chhattisgarh (CGBSE)", "type": "state", "curriculum": "ncert"},
    {"code": "delhi", "name": "Delhi (DBSE)", "type": "state", "curriculum": "ncert"},
    {"code": "goa", "name": "Goa (GBSHSE)", "type": "state", "curriculum": "ncert"},
    {"code": "gujarat", "name": "Gujarat (GSEB)", "type": "state", "curriculum": "ncert"},
    {"code": "haryana", "name": "Haryana (BSEH)", "type": "state", "curriculum": "ncert"},
    {"code": "hp", "name": "Himachal Pradesh (HPBOSE)", "type": "state", "curriculum": "ncert"},
    {"code": "jk", "name": "Jammu & Kashmir (JKBOSE)", "type": "state", "curriculum": "ncert"},
    {"code": "jharkhand", "name": "Jharkhand (JAC)", "type": "state", "curriculum": "ncert"},
    {"code": "karnataka", "name": "Karnataka (KSEEB)", "type": "state", "curriculum": "ncert"},
    {"code": "kerala", "name": "Kerala (KBPE)", "type": "state", "curriculum": "ncert"},
    {"code": "mp", "name": "Madhya Pradesh (MPBSE)", "type": "state", "curriculum": "ncert"},
    {"code": "maharashtra", "name": "Maharashtra (MSBSHSE)", "type": "state", "curriculum": "ncert"},
    {"code": "manipur", "name": "Manipur (BSEM)", "type": "state", "curriculum": "ncert"},
    {"code": "meghalaya", "name": "Meghalaya (MBOSE)", "type": "state", "curriculum": "ncert"},
    {"code": "mizoram", "name": "Mizoram (MBSE)", "type": "state", "curriculum": "ncert"},
    {"code": "nagaland", "name": "Nagaland (NBSE)", "type": "state", "curriculum": "ncert"},
    {"code": "odisha", "name": "Odisha (BSE Odisha)", "type": "state", "curriculum": "ncert"},
    {"code": "punjab", "name": "Punjab (PSEB)", "type": "state", "curriculum": "ncert"},
    {"code": "rajasthan", "name": "Rajasthan (RBSE)", "type": "state", "curriculum": "ncert"},
    {"code": "tn", "name": "Tamil Nadu (TNBSE)", "type": "state", "curriculum": "ncert"},
    {"code": "telangana", "name": "Telangana (TSBIE/BSE)", "type": "state", "curriculum": "ncert"},
    {"code": "tripura", "name": "Tripura (TBSE)", "type": "state", "curriculum": "ncert"},
    {"code": "up", "name": "Uttar Pradesh (UPMSP)", "type": "state", "curriculum": "ncert"},
    {"code": "uk", "name": "Uttarakhand (UBSE)", "type": "state", "curriculum": "ncert"},
    {"code": "wb", "name": "West Bengal (WBBSE)", "type": "state", "curriculum": "ncert"},
]


# ---- Compact builders -------------------------------------------------------
def _t(topic_id: str, title: str, skills: list[str], lo: int = 1, hi: int = 5) -> dict[str, Any]:
    return {"topic_id": topic_id, "title": title, "skills": skills, "difficulty_range": [lo, hi]}


def _ch(chapter_id: str, title: str, topics: list[dict[str, Any]]) -> dict[str, Any]:
    return {"chapter_id": chapter_id, "title": title, "topics": topics}


# =============================================================================
#  NCERT-aligned curriculum: classes 1-10, Maths / Science / English
# =============================================================================
_MATHS: dict[str, list[dict[str, Any]]] = {
    "1": [
        _ch("numbers", "Numbers", [
            _t("counting_1_20", "Counting up to 20", ["count objects", "number names", "before/after"], 1, 2),
            _t("compare_numbers", "Comparing Numbers", ["more/less", "biggest/smallest"], 1, 3),
        ]),
        _ch("operations", "Addition and Subtraction", [
            _t("addition_basic", "Addition up to 20", ["adding objects", "number line"], 1, 3),
            _t("subtraction_basic", "Subtraction up to 20", ["taking away", "counting back"], 1, 3),
        ]),
        _ch("shapes_measure", "Shapes and Measurement", [
            _t("shapes_around", "Shapes Around Us", ["circle", "square", "triangle"], 1, 2),
            _t("measure_compare", "Long/Short, Heavy/Light", ["compare length", "compare weight"], 1, 2),
        ]),
    ],
    "2": [
        _ch("numbers", "Numbers up to 100", [
            _t("place_value_tens", "Tens and Ones", ["place value", "expanded form"], 1, 3),
            _t("number_patterns", "Number Patterns", ["skip counting", "odd and even"], 1, 3),
        ]),
        _ch("operations", "Addition, Subtraction and Multiplication", [
            _t("add_sub_2digit", "2-digit Addition and Subtraction", ["carry", "borrow"], 2, 4),
            _t("multiplication_intro", "Introduction to Multiplication", ["repeated addition", "tables 2-5"], 2, 4),
        ]),
        _ch("measure_money", "Measurement, Money and Time", [
            _t("money_basic", "Money", ["coins and notes", "simple totals"], 1, 3),
            _t("time_basic", "Time", ["hours", "days of week"], 1, 3),
        ]),
    ],
    "3": [
        _ch("numbers", "Numbers up to 1000", [
            _t("place_value_hundreds", "Place Value to Hundreds", ["expanded form", "comparing"], 1, 3),
            _t("rounding_intro", "Rounding Numbers", ["nearest ten", "estimation"], 2, 4),
        ]),
        _ch("operations", "Multiplication and Division", [
            _t("multiplication_tables", "Multiplication Tables", ["tables up to 10", "word problems"], 2, 4),
            _t("division_intro", "Introduction to Division", ["equal sharing", "remainder idea"], 2, 4),
        ]),
        _ch("fractions_geo", "Fractions and Geometry", [
            _t("fractions_intro", "Introduction to Fractions", ["half", "quarter", "fraction of a whole"], 2, 4),
            _t("shapes_3d", "2D and 3D Shapes", ["sides and corners", "faces"], 1, 3),
        ]),
    ],
    "4": [
        _ch("numbers", "Large Numbers", [
            _t("numbers_to_10000", "Numbers up to 10,000", ["place value", "comparing", "rounding"], 2, 4),
            _t("factors_multiples_intro", "Factors and Multiples", ["multiples", "factors", "even/odd"], 2, 5),
        ]),
        _ch("operations", "Multiplication and Division", [
            _t("multiply_2digit", "Multiplying 2-digit Numbers", ["partial products", "estimation"], 2, 5),
            _t("division_facts", "Division", ["long division basics", "remainders"], 3, 5),
        ]),
        _ch("fractions_measure", "Fractions and Measurement", [
            _t("fractions_compare", "Comparing Fractions", ["equivalent fractions", "like denominators"], 2, 5),
            _t("perimeter_intro", "Perimeter", ["perimeter of rectangle", "units"], 2, 4),
        ]),
    ],
    "5": [
        _ch("fractions", "Fractions", [
            _t("understanding_fractions", "Understanding Fractions", ["numerator and denominator", "fraction of a whole", "fraction of a group"], 1, 3),
            _t("adding_fractions", "Adding Fractions", ["same denominator", "different denominator", "simplification"], 1, 5),
            _t("equivalent_fractions", "Equivalent Fractions", ["scaling up", "scaling down", "comparing fractions"], 2, 5),
        ]),
        _ch("decimals", "Decimals", [
            _t("reading_decimals", "Reading and Writing Decimals", ["tenths", "hundredths", "place value"], 1, 3),
            _t("adding_decimals", "Adding and Subtracting Decimals", ["aligning decimal points", "carrying", "borrowing"], 2, 4),
        ]),
        _ch("multiplication_division", "Multiplication and Division", [
            _t("multi_digit_multiplication", "Multi-digit Multiplication", ["partial products", "carrying", "estimation"], 2, 5),
            _t("long_division", "Long Division", ["divide", "remainder", "checking by multiplication"], 2, 5),
        ]),
        _ch("geometry", "Geometry and Shapes", [
            _t("angles", "Angles", ["acute", "right", "obtuse", "measuring with protractor"], 1, 4),
            _t("perimeter_area", "Perimeter and Area", ["perimeter of rectangle", "area of rectangle", "units"], 2, 5),
        ]),
    ],
    "6": [
        _ch("number_system", "Numbers and Integers", [
            _t("knowing_numbers", "Knowing Our Numbers", ["place value", "estimation", "Roman numerals"], 2, 4),
            _t("integers", "Integers", ["number line", "adding integers", "ordering"], 3, 5),
            _t("playing_with_numbers", "Playing with Numbers", ["factors", "multiples", "HCF and LCM"], 3, 5),
        ]),
        _ch("fractions_decimals", "Fractions and Decimals", [
            _t("fractions", "Fractions", ["proper/improper", "comparing", "operations"], 2, 5),
            _t("decimals", "Decimals", ["place value", "operations", "fraction-decimal link"], 2, 5),
        ]),
        _ch("algebra_geometry", "Algebra, Ratio and Geometry", [
            _t("algebra_intro", "Introduction to Algebra", ["variables", "simple expressions"], 3, 5),
            _t("ratio_proportion", "Ratio and Proportion", ["ratio", "unitary method"], 3, 5),
            _t("basic_geometry", "Basic Geometrical Ideas", ["lines", "angles", "polygons"], 2, 4),
        ]),
    ],
    "7": [
        _ch("number_system", "Numbers", [
            _t("integers", "Integers", ["operations", "properties", "word problems"], 3, 5),
            _t("fractions_decimals", "Fractions and Decimals", ["multiplication", "division"], 3, 5),
            _t("rational_numbers", "Rational Numbers", ["number line", "operations"], 3, 5),
        ]),
        _ch("algebra", "Algebra", [
            _t("simple_equations", "Simple Equations", ["forming equations", "solving"], 3, 5),
            _t("algebraic_expressions", "Algebraic Expressions", ["terms", "like terms", "adding"], 3, 5),
            _t("exponents_powers", "Exponents and Powers", ["laws of exponents", "standard form"], 3, 5),
        ]),
        _ch("geometry_mensuration", "Geometry and Mensuration", [
            _t("lines_angles", "Lines and Angles", ["complementary", "supplementary", "transversal"], 2, 5),
            _t("triangles", "The Triangle and its Properties", ["angle sum", "exterior angle"], 3, 5),
            _t("perimeter_area", "Perimeter and Area", ["area of triangle", "circle", "parallelogram"], 3, 5),
        ]),
        _ch("data", "Comparing Quantities and Data", [
            _t("comparing_quantities", "Comparing Quantities", ["percentage", "profit and loss", "simple interest"], 3, 5),
            _t("data_handling", "Data Handling", ["mean median mode", "bar graphs", "probability intro"], 2, 5),
        ]),
    ],
    "8": [
        _ch("number_system", "Numbers", [
            _t("rational_numbers", "Rational Numbers", ["properties", "operations", "representation"], 3, 5),
            _t("squares_roots", "Squares and Square Roots", ["perfect squares", "finding roots"], 3, 5),
            _t("cubes_roots", "Cubes and Cube Roots", ["perfect cubes", "cube roots"], 3, 5),
        ]),
        _ch("algebra", "Algebra", [
            _t("linear_equations", "Linear Equations in One Variable", ["solving", "word problems"], 3, 5),
            _t("algebraic_identities", "Algebraic Expressions and Identities", ["multiplication", "identities", "factorisation"], 3, 5),
            _t("exponents_powers", "Exponents and Powers", ["negative exponents", "standard form"], 3, 5),
        ]),
        _ch("geometry_mensuration", "Geometry and Mensuration", [
            _t("quadrilaterals", "Understanding Quadrilaterals", ["angle sum", "types", "properties"], 3, 5),
            _t("mensuration", "Mensuration", ["area of trapezium", "surface area", "volume"], 3, 5),
        ]),
        _ch("data_proportion", "Comparing Quantities and Data", [
            _t("comparing_quantities", "Comparing Quantities", ["percentage", "compound interest", "discount"], 3, 5),
            _t("direct_inverse", "Direct and Inverse Proportions", ["direct variation", "inverse variation"], 3, 5),
            _t("data_handling", "Data Handling", ["grouped data", "pie charts", "probability"], 3, 5),
        ]),
    ],
    "9": [
        _ch("number_algebra", "Number Systems and Algebra", [
            _t("number_systems", "Number Systems", ["rational/irrational", "real number line", "surds"], 3, 5),
            _t("polynomials", "Polynomials", ["degree", "factor theorem", "identities"], 3, 5),
            _t("linear_equations_two", "Linear Equations in Two Variables", ["solutions", "graphing"], 3, 5),
        ]),
        _ch("coordinate_geometry", "Coordinate Geometry", [
            _t("cartesian_plane", "Coordinate Geometry", ["quadrants", "plotting points"], 2, 4),
        ]),
        _ch("geometry", "Geometry", [
            _t("lines_angles", "Lines and Angles", ["angle pairs", "parallel lines"], 3, 5),
            _t("triangles", "Triangles", ["congruence", "inequalities"], 3, 5),
            _t("circles", "Circles", ["chords", "angle properties"], 3, 5),
        ]),
        _ch("mensuration_stats", "Mensuration and Statistics", [
            _t("surface_volume", "Surface Areas and Volumes", ["cylinder", "cone", "sphere"], 3, 5),
            _t("statistics", "Statistics", ["mean median mode", "frequency", "graphs"], 3, 5),
        ]),
    ],
    "10": [
        _ch("number_algebra", "Number Systems and Algebra", [
            _t("real_numbers", "Real Numbers", ["Euclid's lemma", "HCF/LCM", "irrationality proofs"], 3, 5),
            _t("polynomials", "Polynomials", ["zeroes", "relationship with coefficients"], 3, 5),
            _t("quadratic_equations", "Quadratic Equations", ["factorisation", "quadratic formula", "nature of roots"], 4, 5),
            _t("arithmetic_progressions", "Arithmetic Progressions", ["nth term", "sum of n terms"], 3, 5),
        ]),
        _ch("trigonometry", "Trigonometry", [
            _t("intro_trigonometry", "Introduction to Trigonometry", ["ratios", "identities", "values"], 4, 5),
            _t("applications_trig", "Heights and Distances", ["angle of elevation", "angle of depression"], 4, 5),
        ]),
        _ch("geometry_coordinate", "Geometry and Coordinate Geometry", [
            _t("triangles", "Triangles", ["similarity", "Pythagoras theorem"], 3, 5),
            _t("coordinate_geometry", "Coordinate Geometry", ["distance formula", "section formula"], 3, 5),
            _t("circles", "Circles", ["tangents", "properties"], 3, 5),
        ]),
        _ch("mensuration_stats", "Mensuration, Statistics and Probability", [
            _t("surface_volume", "Surface Areas and Volumes", ["combinations of solids", "frustum"], 3, 5),
            _t("statistics", "Statistics", ["mean of grouped data", "median", "mode", "ogive"], 3, 5),
            _t("probability", "Probability", ["theoretical probability", "sample space"], 3, 5),
        ]),
    ],
}

_SCIENCE: dict[str, list[dict[str, Any]]] = {
    "1": [
        _ch("my_body", "My Body and Senses", [
            _t("body_parts", "Parts of the Body", ["naming parts", "what they do"], 1, 2),
            _t("five_senses", "The Five Senses", ["see hear smell taste touch"], 1, 2),
        ]),
        _ch("living_world", "Plants and Animals", [
            _t("plants_around", "Plants Around Us", ["parts of a plant", "trees and flowers"], 1, 2),
            _t("animals_around", "Animals Around Us", ["pets", "wild animals", "sounds"], 1, 2),
        ]),
        _ch("needs", "Our Needs", [
            _t("food_water", "Food and Water", ["healthy food", "why we need water"], 1, 2),
        ]),
    ],
    "2": [
        _ch("living_nonliving", "Living and Non-living", [
            _t("living_things", "Living and Non-living Things", ["characteristics", "examples"], 1, 3),
        ]),
        _ch("plants_animals", "Plants and Animals", [
            _t("plants_uses", "Plants and Their Uses", ["food from plants", "parts we eat"], 1, 3),
            _t("animals_homes", "Animals and Their Homes", ["habitats", "young ones"], 1, 3),
        ]),
        _ch("environment", "Air, Water and Weather", [
            _t("air_water", "Air and Water Around Us", ["uses of air", "clean water"], 1, 3),
            _t("weather_seasons", "Weather and Seasons", ["seasons", "clothes we wear"], 1, 3),
        ]),
    ],
    "3": [
        _ch("plants", "The World of Plants", [
            _t("plant_parts", "Parts of a Plant", ["root stem leaf", "functions"], 2, 4),
        ]),
        _ch("animals", "The World of Animals", [
            _t("animal_groups", "Types of Animals", ["herbivore carnivore omnivore", "habitats"], 2, 4),
        ]),
        _ch("human_needs", "Human Body and Food", [
            _t("food_groups", "Food We Eat", ["balanced diet", "food groups"], 2, 4),
            _t("water_air", "Water and Air", ["sources", "importance"], 1, 3),
        ]),
    ],
    "4": [
        _ch("plants_animals", "Plants and Animals", [
            _t("plant_life", "Plant Life and Adaptation", ["photosynthesis idea", "adaptation"], 2, 4),
            _t("animal_adaptation", "Animals and Adaptation", ["adaptation to habitat", "food chains"], 2, 5),
        ]),
        _ch("human_body", "Human Body", [
            _t("teeth_digestion", "Teeth and Digestion", ["types of teeth", "digestion basics"], 2, 4),
        ]),
        _ch("matter_water", "Matter and Water", [
            _t("states_of_matter", "Solids, Liquids and Gases", ["states", "examples"], 2, 4),
            _t("water_cycle", "The Water Cycle", ["evaporation", "condensation", "rain"], 2, 5),
        ]),
    ],
    "5": [
        _ch("human_body", "The Human Body", [
            _t("digestion", "Digestive System", ["organs", "first organ of digestion", "absorption"], 2, 5),
            _t("skeleton", "Skeletal System", ["bones", "joints", "movement"], 1, 4),
        ]),
        _ch("plants", "Plants and Their Life", [
            _t("photosynthesis", "How Plants Make Food", ["photosynthesis", "leaf parts", "sunlight"], 2, 5),
            _t("reproduction_plants", "Reproduction in Plants", ["seeds", "germination", "dispersal"], 2, 5),
        ]),
        _ch("matter", "Matter and Materials", [
            _t("states_of_matter", "States of Matter", ["solid liquid gas", "changes of state"], 1, 4),
            _t("mixtures", "Mixtures and Separation", ["mixtures", "filtering", "evaporation"], 2, 5),
        ]),
        _ch("earth_space", "Earth and Space", [
            _t("solar_system", "The Solar System", ["planets", "sun", "moon phases"], 1, 4),
            _t("weather", "Weather and Climate", ["weather elements", "seasons"], 1, 4),
        ]),
    ],
    "6": [
        _ch("life", "Living World", [
            _t("food_components", "Components of Food", ["nutrients", "balanced diet", "deficiency"], 2, 5),
            _t("living_organisms_habitat", "Living Organisms and Habitat", ["habitat", "adaptation", "characteristics"], 2, 5),
            _t("body_movements", "Body Movements", ["joints", "muscles", "animal movement"], 2, 4),
        ]),
        _ch("materials", "Materials", [
            _t("sorting_materials", "Sorting Materials into Groups", ["properties", "soluble/insoluble"], 2, 4),
            _t("separation", "Separation of Substances", ["filtration", "sedimentation", "evaporation"], 2, 5),
        ]),
        _ch("physics", "Motion, Light and Electricity", [
            _t("motion_measurement", "Motion and Measurement", ["units", "types of motion"], 2, 5),
            _t("light_shadows", "Light, Shadows and Reflections", ["sources", "shadows", "mirrors"], 2, 4),
            _t("electricity_circuits", "Electricity and Circuits", ["simple circuit", "conductors"], 2, 5),
        ]),
    ],
    "7": [
        _ch("life", "Life Processes", [
            _t("nutrition_plants", "Nutrition in Plants", ["photosynthesis", "modes of nutrition"], 3, 5),
            _t("nutrition_animals", "Nutrition in Animals", ["digestive system", "ruminants"], 3, 5),
            _t("respiration", "Respiration in Organisms", ["breathing", "cellular respiration"], 3, 5),
        ]),
        _ch("matter", "Matter and Changes", [
            _t("acids_bases_salts", "Acids, Bases and Salts", ["indicators", "neutralisation"], 3, 5),
            _t("physical_chemical", "Physical and Chemical Changes", ["reversible", "rusting"], 3, 5),
            _t("heat", "Heat", ["temperature", "conduction convection radiation"], 3, 5),
        ]),
        _ch("physics", "Motion, Light and Electricity", [
            _t("motion_time", "Motion and Time", ["speed", "distance-time graph"], 3, 5),
            _t("electric_current", "Electric Current and its Effects", ["heating effect", "magnetic effect"], 3, 5),
            _t("light", "Light", ["reflection", "mirrors and lenses"], 3, 5),
        ]),
    ],
    "8": [
        _ch("life", "Living World", [
            _t("microorganisms", "Microorganisms: Friend and Foe", ["bacteria virus fungi", "diseases", "food preservation"], 3, 5),
            _t("cell_structure", "Cell Structure and Functions", ["cell parts", "plant vs animal cell"], 3, 5),
            _t("reproduction_animals", "Reproduction in Animals", ["sexual/asexual", "life cycle"], 3, 5),
        ]),
        _ch("matter", "Materials and Chemistry", [
            _t("coal_petroleum", "Coal and Petroleum", ["fossil fuels", "conservation"], 2, 4),
            _t("combustion_flame", "Combustion and Flame", ["types of combustion", "flame zones"], 3, 5),
        ]),
        _ch("physics", "Force, Sound and Light", [
            _t("force_pressure", "Force and Pressure", ["types of force", "pressure", "atmospheric pressure"], 3, 5),
            _t("friction", "Friction", ["factors", "advantages", "reducing friction"], 3, 5),
            _t("sound", "Sound", ["vibration", "frequency", "noise"], 3, 5),
        ]),
    ],
    "9": [
        _ch("matter", "Matter", [
            _t("matter_surroundings", "Matter in Our Surroundings", ["states", "evaporation", "latent heat"], 3, 5),
            _t("is_matter_pure", "Is Matter Around Us Pure", ["mixtures", "solutions", "separation"], 3, 5),
            _t("atoms_molecules", "Atoms and Molecules", ["laws", "mole concept", "formulae"], 4, 5),
        ]),
        _ch("biology", "Life Processes", [
            _t("cell_unit_of_life", "The Fundamental Unit of Life", ["cell organelles", "membrane"], 3, 5),
            _t("tissues", "Tissues", ["plant tissues", "animal tissues"], 3, 5),
        ]),
        _ch("physics", "Motion and Force", [
            _t("motion", "Motion", ["equations of motion", "graphs"], 3, 5),
            _t("force_laws", "Force and Laws of Motion", ["Newton's laws", "momentum"], 4, 5),
            _t("gravitation", "Gravitation", ["universal law", "weight", "buoyancy"], 4, 5),
        ]),
    ],
    "10": [
        _ch("chemistry", "Chemistry", [
            _t("chemical_reactions", "Chemical Reactions and Equations", ["balancing", "types of reactions"], 3, 5),
            _t("acids_bases_salts", "Acids, Bases and Salts", ["pH", "neutralisation", "salts"], 3, 5),
            _t("metals_nonmetals", "Metals and Non-metals", ["reactivity series", "corrosion"], 3, 5),
            _t("carbon_compounds", "Carbon and its Compounds", ["covalent bonds", "functional groups"], 4, 5),
        ]),
        _ch("biology", "Life Processes", [
            _t("life_processes", "Life Processes", ["nutrition", "respiration", "transportation", "excretion"], 3, 5),
            _t("control_coordination", "Control and Coordination", ["nervous system", "hormones"], 3, 5),
            _t("reproduction", "How do Organisms Reproduce", ["asexual", "sexual", "reproductive health"], 3, 5),
            _t("heredity_evolution", "Heredity and Evolution", ["Mendel's laws", "inheritance"], 4, 5),
        ]),
        _ch("physics", "Physics", [
            _t("light_reflection_refraction", "Light: Reflection and Refraction", ["mirrors", "lenses", "ray diagrams"], 4, 5),
            _t("human_eye", "The Human Eye and the Colourful World", ["defects of vision", "dispersion"], 3, 5),
            _t("electricity", "Electricity", ["Ohm's law", "resistance", "power"], 4, 5),
            _t("magnetic_effects", "Magnetic Effects of Electric Current", ["magnetic field", "electromagnetic induction"], 4, 5),
        ]),
    ],
}

_ENGLISH: dict[str, list[dict[str, Any]]] = {
    "1": [
        _ch("foundations", "Reading Foundations", [
            _t("phonics", "Phonics and Sounds", ["letter sounds", "blending"], 1, 2),
            _t("sight_words", "Simple Words", ["three-letter words", "reading aloud"], 1, 2),
        ]),
        _ch("grammar", "Words", [
            _t("naming_words", "Naming Words (Nouns)", ["names of people", "things", "places"], 1, 2),
            _t("action_words", "Action Words (Verbs)", ["doing words"], 1, 2),
        ]),
    ],
    "2": [
        _ch("grammar", "Grammar Basics", [
            _t("nouns", "Nouns", ["common nouns", "proper nouns"], 1, 3),
            _t("pronouns", "Pronouns", ["he she it they"], 1, 3),
            _t("articles", "Articles", ["a an the"], 1, 3),
        ]),
        _ch("reading_writing", "Reading and Writing", [
            _t("reading_stories", "Reading Short Stories", ["comprehension", "characters"], 1, 3),
            _t("sentence_making", "Making Sentences", ["word order", "full stop"], 1, 3),
        ]),
    ],
    "3": [
        _ch("grammar", "Grammar", [
            _t("nouns_gender", "Nouns and Gender", ["masculine/feminine", "singular/plural"], 2, 4),
            _t("verbs_tense", "Verbs and Simple Tense", ["present", "past"], 2, 4),
            _t("adjectives", "Adjectives", ["describing words"], 2, 4),
        ]),
        _ch("reading_writing", "Reading and Writing", [
            _t("comprehension", "Reading Comprehension", ["main idea", "details"], 2, 4),
            _t("paragraph_writing", "Paragraph Writing", ["topic sentence", "ideas"], 2, 5),
        ]),
    ],
    "4": [
        _ch("grammar", "Grammar", [
            _t("tenses", "Tenses", ["present", "past", "future"], 2, 5),
            _t("adverbs", "Adverbs", ["how when where"], 2, 4),
            _t("prepositions", "Prepositions", ["in on under between"], 2, 4),
        ]),
        _ch("vocab_writing", "Vocabulary and Writing", [
            _t("synonyms_antonyms", "Synonyms and Antonyms", ["word meanings", "opposites"], 2, 4),
            _t("informal_letter", "Informal Letter Writing", ["format", "friendly tone"], 3, 5),
        ]),
    ],
    "5": [
        _ch("grammar", "Grammar", [
            _t("parts_of_speech", "Parts of Speech", ["noun verb adjective adverb", "identify in sentence"], 2, 5),
            _t("tenses", "Tenses", ["simple present", "simple past", "simple future"], 2, 5),
            _t("subject_verb", "Subject-Verb Agreement", ["singular/plural", "matching verb"], 2, 5),
        ]),
        _ch("vocabulary", "Vocabulary", [
            _t("synonyms_antonyms", "Synonyms and Antonyms", ["word meanings", "opposites", "context"], 1, 4),
            _t("homophones", "Homophones and Spellings", ["sound-alike words", "correct spelling"], 2, 5),
        ]),
        _ch("reading", "Reading", [
            _t("comprehension", "Reading Comprehension", ["main idea", "inference", "vocabulary in context"], 2, 5),
        ]),
        _ch("writing", "Writing", [
            _t("paragraph_writing", "Paragraph Writing", ["topic sentence", "supporting ideas", "structure"], 2, 5),
            _t("letter_writing", "Letter Writing", ["informal letter", "format", "tone"], 3, 5),
        ]),
    ],
    "6": [
        _ch("grammar", "Grammar", [
            _t("nouns_pronouns", "Nouns and Pronouns", ["kinds of nouns", "types of pronouns"], 2, 5),
            _t("tenses", "Tenses", ["present continuous", "past forms"], 3, 5),
            _t("conjunctions", "Conjunctions and Prepositions", ["joining words", "place/time"], 2, 5),
        ]),
        _ch("reading_writing", "Reading and Writing", [
            _t("comprehension", "Reading Comprehension", ["main idea", "inference"], 3, 5),
            _t("story_writing", "Story and Paragraph Writing", ["sequence", "descriptive language"], 3, 5),
            _t("letter_writing", "Letter Writing", ["informal letter", "format"], 3, 5),
        ]),
    ],
    "7": [
        _ch("grammar", "Grammar", [
            _t("tenses", "Tenses", ["perfect tenses", "consistency"], 3, 5),
            _t("modals", "Modals", ["can could may must"], 3, 5),
            _t("active_passive_intro", "Active and Passive Voice (Intro)", ["voice change"], 4, 5),
        ]),
        _ch("reading_writing", "Reading and Writing", [
            _t("comprehension", "Reading Comprehension", ["unseen passage", "vocabulary"], 3, 5),
            _t("formal_letter", "Formal and Informal Letters", ["format", "register"], 3, 5),
            _t("essay_writing", "Essay and Story Writing", ["structure", "ideas"], 3, 5),
        ]),
    ],
    "8": [
        _ch("grammar", "Grammar", [
            _t("voice", "Active and Passive Voice", ["transformation", "rules"], 4, 5),
            _t("reported_speech", "Direct and Indirect Speech", ["reporting verbs", "tense change"], 4, 5),
            _t("conditionals", "Clauses and Conditionals", ["if clauses", "types"], 4, 5),
        ]),
        _ch("reading_writing", "Reading and Writing", [
            _t("comprehension", "Reading Comprehension", ["inference", "tone"], 3, 5),
            _t("notice_message", "Notice and Message Writing", ["format", "conciseness"], 3, 5),
            _t("essay_writing", "Essay Writing", ["argument", "structure"], 3, 5),
        ]),
    ],
    "9": [
        _ch("grammar", "Grammar", [
            _t("tenses_voice", "Tenses and Voice", ["mixed tenses", "passive"], 4, 5),
            _t("reported_speech", "Reported Speech", ["statements", "questions", "commands"], 4, 5),
            _t("determiners_clauses", "Determiners and Clauses", ["articles", "relative clauses"], 4, 5),
        ]),
        _ch("reading_writing", "Reading and Writing", [
            _t("comprehension", "Reading Comprehension", ["discursive passage", "factual passage"], 3, 5),
            _t("descriptive_writing", "Descriptive and Narrative Writing", ["imagery", "sequence"], 4, 5),
            _t("letter_diary", "Letter and Diary Writing", ["format", "voice"], 3, 5),
        ]),
    ],
    "10": [
        _ch("grammar", "Grammar", [
            _t("tenses_concord", "Tenses and Subject-Verb Concord", ["error correction", "gap filling"], 4, 5),
            _t("voice_speech", "Voice and Reported Speech", ["transformations", "editing"], 4, 5),
            _t("determiners_clauses", "Determiners and Clauses", ["usage", "sentence reordering"], 4, 5),
        ]),
        _ch("reading_writing", "Reading and Writing", [
            _t("comprehension", "Reading Comprehension", ["analytical reading", "inference"], 4, 5),
            _t("analytical_paragraph", "Analytical Paragraph Writing", ["data interpretation", "structure"], 4, 5),
            _t("formal_letter", "Formal Letter Writing", ["complaint", "enquiry", "format"], 3, 5),
        ]),
    ],
}

CURRICULUM: dict[str, dict[str, dict[str, list[dict[str, Any]]]]] = {
    "ncert": {
        "Maths": _MATHS,
        "Science": _SCIENCE,
        "English": _ENGLISH,
    },
    # Future per-board specialisations go here, e.g. "icse": {...}. Until then,
    # boards mapped to a missing curriculum fall back to "ncert".
}
