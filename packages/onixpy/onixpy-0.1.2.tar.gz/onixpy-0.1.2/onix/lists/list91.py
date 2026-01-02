"""ONIX Code List 91: Country - based on ISO 3166-1."""

from onix.lists.models import CodeList, CodeListEntry

_ENTRIES = {
    "AD": CodeListEntry(
        list_number=91,
        code="AD",
        heading="Andorra",
    ),
    "AE": CodeListEntry(
        list_number=91,
        code="AE",
        heading="United Arab Emirates",
    ),
    "AF": CodeListEntry(
        list_number=91,
        code="AF",
        heading="Afghanistan",
    ),
    "AG": CodeListEntry(
        list_number=91,
        code="AG",
        heading="Antigua and Barbuda",
    ),
    "AI": CodeListEntry(
        list_number=91,
        code="AI",
        heading="Anguilla",
    ),
    "AL": CodeListEntry(
        list_number=91,
        code="AL",
        heading="Albania",
    ),
    "AM": CodeListEntry(
        list_number=91,
        code="AM",
        heading="Armenia",
    ),
    "AN": CodeListEntry(
        list_number=91,
        code="AN",
        heading="Netherlands Antilles",
        notes="Deprecated - use BQ, CW and SX as appropriate",
        deprecated_version=13,
    ),
    "AO": CodeListEntry(
        list_number=91,
        code="AO",
        heading="Angola",
    ),
    "AQ": CodeListEntry(
        list_number=91,
        code="AQ",
        heading="Antarctica",
    ),
    "AR": CodeListEntry(
        list_number=91,
        code="AR",
        heading="Argentina",
    ),
    "AS": CodeListEntry(
        list_number=91,
        code="AS",
        heading="American Samoa",
    ),
    "AT": CodeListEntry(
        list_number=91,
        code="AT",
        heading="Austria",
    ),
    "AU": CodeListEntry(
        list_number=91,
        code="AU",
        heading="Australia",
    ),
    "AW": CodeListEntry(
        list_number=91,
        code="AW",
        heading="Aruba",
    ),
    "AX": CodeListEntry(
        list_number=91,
        code="AX",
        heading="Åland Islands",
        added_version=4,
    ),
    "AZ": CodeListEntry(
        list_number=91,
        code="AZ",
        heading="Azerbaijan",
    ),
    "BA": CodeListEntry(
        list_number=91,
        code="BA",
        heading="Bosnia and Herzegovina",
    ),
    "BB": CodeListEntry(
        list_number=91,
        code="BB",
        heading="Barbados",
    ),
    "BD": CodeListEntry(
        list_number=91,
        code="BD",
        heading="Bangladesh",
    ),
    "BE": CodeListEntry(
        list_number=91,
        code="BE",
        heading="Belgium",
    ),
    "BF": CodeListEntry(
        list_number=91,
        code="BF",
        heading="Burkina Faso",
    ),
    "BG": CodeListEntry(
        list_number=91,
        code="BG",
        heading="Bulgaria",
    ),
    "BH": CodeListEntry(
        list_number=91,
        code="BH",
        heading="Bahrain",
    ),
    "BI": CodeListEntry(
        list_number=91,
        code="BI",
        heading="Burundi",
    ),
    "BJ": CodeListEntry(
        list_number=91,
        code="BJ",
        heading="Benin",
    ),
    "BL": CodeListEntry(
        list_number=91,
        code="BL",
        heading="Saint Barthélemy",
        added_version=8,
    ),
    "BM": CodeListEntry(
        list_number=91,
        code="BM",
        heading="Bermuda",
    ),
    "BN": CodeListEntry(
        list_number=91,
        code="BN",
        heading="Brunei Darussalam",
    ),
    "BO": CodeListEntry(
        list_number=91,
        code="BO",
        heading="Bolivia, Plurinational State of",
    ),
    "BQ": CodeListEntry(
        list_number=91,
        code="BQ",
        heading="Bonaire, Sint Eustatius and Saba",
        added_version=13,
    ),
    "BR": CodeListEntry(
        list_number=91,
        code="BR",
        heading="Brazil",
    ),
    "BS": CodeListEntry(
        list_number=91,
        code="BS",
        heading="Bahamas",
    ),
    "BT": CodeListEntry(
        list_number=91,
        code="BT",
        heading="Bhutan",
    ),
    "BV": CodeListEntry(
        list_number=91,
        code="BV",
        heading="Bouvet Island",
    ),
    "BW": CodeListEntry(
        list_number=91,
        code="BW",
        heading="Botswana",
    ),
    "BY": CodeListEntry(
        list_number=91,
        code="BY",
        heading="Belarus",
    ),
    "BZ": CodeListEntry(
        list_number=91,
        code="BZ",
        heading="Belize",
    ),
    "CA": CodeListEntry(
        list_number=91,
        code="CA",
        heading="Canada",
    ),
    "CC": CodeListEntry(
        list_number=91,
        code="CC",
        heading="Cocos (Keeling) Islands",
    ),
    "CD": CodeListEntry(
        list_number=91,
        code="CD",
        heading="Congo, Democratic Republic of the",
    ),
    "CF": CodeListEntry(
        list_number=91,
        code="CF",
        heading="Central African Republic",
    ),
    "CG": CodeListEntry(
        list_number=91,
        code="CG",
        heading="Congo",
    ),
    "CH": CodeListEntry(
        list_number=91,
        code="CH",
        heading="Switzerland",
    ),
    "CI": CodeListEntry(
        list_number=91,
        code="CI",
        heading="Cote d’Ivoire",
    ),
    "CK": CodeListEntry(
        list_number=91,
        code="CK",
        heading="Cook Islands",
    ),
    "CL": CodeListEntry(
        list_number=91,
        code="CL",
        heading="Chile",
    ),
    "CM": CodeListEntry(
        list_number=91,
        code="CM",
        heading="Cameroon",
    ),
    "CN": CodeListEntry(
        list_number=91,
        code="CN",
        heading="China",
    ),
    "CO": CodeListEntry(
        list_number=91,
        code="CO",
        heading="Colombia",
    ),
    "CR": CodeListEntry(
        list_number=91,
        code="CR",
        heading="Costa Rica",
    ),
    "CS": CodeListEntry(
        list_number=91,
        code="CS",
        heading="Serbia and Montenegro",
        notes="Deprecated, replaced by ME - Montenegro and RS - Serbia",
        added_version=4,
        deprecated_version=7,
    ),
    "CU": CodeListEntry(
        list_number=91,
        code="CU",
        heading="Cuba",
    ),
    "CV": CodeListEntry(
        list_number=91,
        code="CV",
        heading="Cabo Verde",
    ),
    "CW": CodeListEntry(
        list_number=91,
        code="CW",
        heading="Curaçao",
        added_version=13,
    ),
    "CX": CodeListEntry(
        list_number=91,
        code="CX",
        heading="Christmas Island",
    ),
    "CY": CodeListEntry(
        list_number=91,
        code="CY",
        heading="Cyprus",
    ),
    "CZ": CodeListEntry(
        list_number=91,
        code="CZ",
        heading="Czechia",
        notes="Formerly Czech Republic",
    ),
    "DE": CodeListEntry(
        list_number=91,
        code="DE",
        heading="Germany",
    ),
    "DJ": CodeListEntry(
        list_number=91,
        code="DJ",
        heading="Djibouti",
    ),
    "DK": CodeListEntry(
        list_number=91,
        code="DK",
        heading="Denmark",
    ),
    "DM": CodeListEntry(
        list_number=91,
        code="DM",
        heading="Dominica",
    ),
    "DO": CodeListEntry(
        list_number=91,
        code="DO",
        heading="Dominican Republic",
    ),
    "DZ": CodeListEntry(
        list_number=91,
        code="DZ",
        heading="Algeria",
    ),
    "EC": CodeListEntry(
        list_number=91,
        code="EC",
        heading="Ecuador",
    ),
    "EE": CodeListEntry(
        list_number=91,
        code="EE",
        heading="Estonia",
    ),
    "EG": CodeListEntry(
        list_number=91,
        code="EG",
        heading="Egypt",
    ),
    "EH": CodeListEntry(
        list_number=91,
        code="EH",
        heading="Western Sahara",
    ),
    "ER": CodeListEntry(
        list_number=91,
        code="ER",
        heading="Eritrea",
    ),
    "ES": CodeListEntry(
        list_number=91,
        code="ES",
        heading="Spain",
    ),
    "ET": CodeListEntry(
        list_number=91,
        code="ET",
        heading="Ethiopia",
    ),
    "FI": CodeListEntry(
        list_number=91,
        code="FI",
        heading="Finland",
    ),
    "FJ": CodeListEntry(
        list_number=91,
        code="FJ",
        heading="Fiji",
    ),
    "FK": CodeListEntry(
        list_number=91,
        code="FK",
        heading="Falkland Islands (Malvinas)",
    ),
    "FM": CodeListEntry(
        list_number=91,
        code="FM",
        heading="Micronesia, Federated States of",
    ),
    "FO": CodeListEntry(
        list_number=91,
        code="FO",
        heading="Faroe Islands",
    ),
    "FR": CodeListEntry(
        list_number=91,
        code="FR",
        heading="France",
    ),
    "GA": CodeListEntry(
        list_number=91,
        code="GA",
        heading="Gabon",
    ),
    "GB": CodeListEntry(
        list_number=91,
        code="GB",
        heading="United Kingdom",
    ),
    "GD": CodeListEntry(
        list_number=91,
        code="GD",
        heading="Grenada",
    ),
    "GE": CodeListEntry(
        list_number=91,
        code="GE",
        heading="Georgia",
    ),
    "GF": CodeListEntry(
        list_number=91,
        code="GF",
        heading="French Guiana",
    ),
    "GG": CodeListEntry(
        list_number=91,
        code="GG",
        heading="Guernsey",
        added_version=7,
    ),
    "GH": CodeListEntry(
        list_number=91,
        code="GH",
        heading="Ghana",
    ),
    "GI": CodeListEntry(
        list_number=91,
        code="GI",
        heading="Gibraltar",
    ),
    "GL": CodeListEntry(
        list_number=91,
        code="GL",
        heading="Greenland",
    ),
    "GM": CodeListEntry(
        list_number=91,
        code="GM",
        heading="Gambia",
    ),
    "GN": CodeListEntry(
        list_number=91,
        code="GN",
        heading="Guinea",
    ),
    "GP": CodeListEntry(
        list_number=91,
        code="GP",
        heading="Guadeloupe",
    ),
    "GQ": CodeListEntry(
        list_number=91,
        code="GQ",
        heading="Equatorial Guinea",
    ),
    "GR": CodeListEntry(
        list_number=91,
        code="GR",
        heading="Greece",
    ),
    "GS": CodeListEntry(
        list_number=91,
        code="GS",
        heading="South Georgia and the South Sandwich Islands",
    ),
    "GT": CodeListEntry(
        list_number=91,
        code="GT",
        heading="Guatemala",
    ),
    "GU": CodeListEntry(
        list_number=91,
        code="GU",
        heading="Guam",
    ),
    "GW": CodeListEntry(
        list_number=91,
        code="GW",
        heading="Guinea-Bissau",
    ),
    "GY": CodeListEntry(
        list_number=91,
        code="GY",
        heading="Guyana",
    ),
    "HK": CodeListEntry(
        list_number=91,
        code="HK",
        heading="Hong Kong",
    ),
    "HM": CodeListEntry(
        list_number=91,
        code="HM",
        heading="Heard Island and McDonald Islands",
    ),
    "HN": CodeListEntry(
        list_number=91,
        code="HN",
        heading="Honduras",
    ),
    "HR": CodeListEntry(
        list_number=91,
        code="HR",
        heading="Croatia",
    ),
    "HT": CodeListEntry(
        list_number=91,
        code="HT",
        heading="Haiti",
    ),
    "HU": CodeListEntry(
        list_number=91,
        code="HU",
        heading="Hungary",
    ),
    "ID": CodeListEntry(
        list_number=91,
        code="ID",
        heading="Indonesia",
    ),
    "IE": CodeListEntry(
        list_number=91,
        code="IE",
        heading="Ireland",
    ),
    "IL": CodeListEntry(
        list_number=91,
        code="IL",
        heading="Israel",
    ),
    "IM": CodeListEntry(
        list_number=91,
        code="IM",
        heading="Isle of Man",
        added_version=7,
    ),
    "IN": CodeListEntry(
        list_number=91,
        code="IN",
        heading="India",
    ),
    "IO": CodeListEntry(
        list_number=91,
        code="IO",
        heading="British Indian Ocean Territory",
    ),
    "IQ": CodeListEntry(
        list_number=91,
        code="IQ",
        heading="Iraq",
    ),
    "IR": CodeListEntry(
        list_number=91,
        code="IR",
        heading="Iran, Islamic Republic of",
    ),
    "IS": CodeListEntry(
        list_number=91,
        code="IS",
        heading="Iceland",
    ),
    "IT": CodeListEntry(
        list_number=91,
        code="IT",
        heading="Italy",
    ),
    "JE": CodeListEntry(
        list_number=91,
        code="JE",
        heading="Jersey",
        added_version=7,
    ),
    "JM": CodeListEntry(
        list_number=91,
        code="JM",
        heading="Jamaica",
    ),
    "JO": CodeListEntry(
        list_number=91,
        code="JO",
        heading="Jordan",
    ),
    "JP": CodeListEntry(
        list_number=91,
        code="JP",
        heading="Japan",
    ),
    "KE": CodeListEntry(
        list_number=91,
        code="KE",
        heading="Kenya",
    ),
    "KG": CodeListEntry(
        list_number=91,
        code="KG",
        heading="Kyrgyzstan",
    ),
    "KH": CodeListEntry(
        list_number=91,
        code="KH",
        heading="Cambodia",
    ),
    "KI": CodeListEntry(
        list_number=91,
        code="KI",
        heading="Kiribati",
    ),
    "KM": CodeListEntry(
        list_number=91,
        code="KM",
        heading="Comoros",
    ),
    "KN": CodeListEntry(
        list_number=91,
        code="KN",
        heading="Saint Kitts and Nevis",
    ),
    "KP": CodeListEntry(
        list_number=91,
        code="KP",
        heading="Korea, Democratic People’s Republic of",
    ),
    "KR": CodeListEntry(
        list_number=91,
        code="KR",
        heading="Korea, Republic of",
    ),
    "KW": CodeListEntry(
        list_number=91,
        code="KW",
        heading="Kuwait",
    ),
    "KY": CodeListEntry(
        list_number=91,
        code="KY",
        heading="Cayman Islands",
    ),
    "KZ": CodeListEntry(
        list_number=91,
        code="KZ",
        heading="Kazakhstan",
    ),
    "LA": CodeListEntry(
        list_number=91,
        code="LA",
        heading="Lao People’s Democratic Republic",
    ),
    "LB": CodeListEntry(
        list_number=91,
        code="LB",
        heading="Lebanon",
    ),
    "LC": CodeListEntry(
        list_number=91,
        code="LC",
        heading="Saint Lucia",
    ),
    "LI": CodeListEntry(
        list_number=91,
        code="LI",
        heading="Liechtenstein",
    ),
    "LK": CodeListEntry(
        list_number=91,
        code="LK",
        heading="Sri Lanka",
    ),
    "LR": CodeListEntry(
        list_number=91,
        code="LR",
        heading="Liberia",
    ),
    "LS": CodeListEntry(
        list_number=91,
        code="LS",
        heading="Lesotho",
    ),
    "LT": CodeListEntry(
        list_number=91,
        code="LT",
        heading="Lithuania",
    ),
    "LU": CodeListEntry(
        list_number=91,
        code="LU",
        heading="Luxembourg",
    ),
    "LV": CodeListEntry(
        list_number=91,
        code="LV",
        heading="Latvia",
    ),
    "LY": CodeListEntry(
        list_number=91,
        code="LY",
        heading="Libya",
    ),
    "MA": CodeListEntry(
        list_number=91,
        code="MA",
        heading="Morocco",
    ),
    "MC": CodeListEntry(
        list_number=91,
        code="MC",
        heading="Monaco",
    ),
    "MD": CodeListEntry(
        list_number=91,
        code="MD",
        heading="Moldova, Republic of",
    ),
    "ME": CodeListEntry(
        list_number=91,
        code="ME",
        heading="Montenegro",
        added_version=7,
    ),
    "MF": CodeListEntry(
        list_number=91,
        code="MF",
        heading="Saint Martin (French part)",
        added_version=8,
    ),
    "MG": CodeListEntry(
        list_number=91,
        code="MG",
        heading="Madagascar",
    ),
    "MH": CodeListEntry(
        list_number=91,
        code="MH",
        heading="Marshall Islands",
    ),
    "MK": CodeListEntry(
        list_number=91,
        code="MK",
        heading="North Macedonia",
        notes="Formerly FYR Macedonia",
    ),
    "ML": CodeListEntry(
        list_number=91,
        code="ML",
        heading="Mali",
    ),
    "MM": CodeListEntry(
        list_number=91,
        code="MM",
        heading="Myanmar",
    ),
    "MN": CodeListEntry(
        list_number=91,
        code="MN",
        heading="Mongolia",
    ),
    "MO": CodeListEntry(
        list_number=91,
        code="MO",
        heading="Macao",
    ),
    "MP": CodeListEntry(
        list_number=91,
        code="MP",
        heading="Northern Mariana Islands",
    ),
    "MQ": CodeListEntry(
        list_number=91,
        code="MQ",
        heading="Martinique",
    ),
    "MR": CodeListEntry(
        list_number=91,
        code="MR",
        heading="Mauritania",
    ),
    "MS": CodeListEntry(
        list_number=91,
        code="MS",
        heading="Montserrat",
    ),
    "MT": CodeListEntry(
        list_number=91,
        code="MT",
        heading="Malta",
    ),
    "MU": CodeListEntry(
        list_number=91,
        code="MU",
        heading="Mauritius",
    ),
    "MV": CodeListEntry(
        list_number=91,
        code="MV",
        heading="Maldives",
    ),
    "MW": CodeListEntry(
        list_number=91,
        code="MW",
        heading="Malawi",
    ),
    "MX": CodeListEntry(
        list_number=91,
        code="MX",
        heading="Mexico",
    ),
    "MY": CodeListEntry(
        list_number=91,
        code="MY",
        heading="Malaysia",
    ),
    "MZ": CodeListEntry(
        list_number=91,
        code="MZ",
        heading="Mozambique",
    ),
    "NA": CodeListEntry(
        list_number=91,
        code="NA",
        heading="Namibia",
    ),
    "NC": CodeListEntry(
        list_number=91,
        code="NC",
        heading="New Caledonia",
    ),
    "NE": CodeListEntry(
        list_number=91,
        code="NE",
        heading="Niger",
    ),
    "NF": CodeListEntry(
        list_number=91,
        code="NF",
        heading="Norfolk Island",
    ),
    "NG": CodeListEntry(
        list_number=91,
        code="NG",
        heading="Nigeria",
    ),
    "NI": CodeListEntry(
        list_number=91,
        code="NI",
        heading="Nicaragua",
    ),
    "NL": CodeListEntry(
        list_number=91,
        code="NL",
        heading="Netherlands",
    ),
    "NO": CodeListEntry(
        list_number=91,
        code="NO",
        heading="Norway",
    ),
    "NP": CodeListEntry(
        list_number=91,
        code="NP",
        heading="Nepal",
    ),
    "NR": CodeListEntry(
        list_number=91,
        code="NR",
        heading="Nauru",
    ),
    "NU": CodeListEntry(
        list_number=91,
        code="NU",
        heading="Niue",
    ),
    "NZ": CodeListEntry(
        list_number=91,
        code="NZ",
        heading="New Zealand",
    ),
    "OM": CodeListEntry(
        list_number=91,
        code="OM",
        heading="Oman",
    ),
    "PA": CodeListEntry(
        list_number=91,
        code="PA",
        heading="Panama",
    ),
    "PE": CodeListEntry(
        list_number=91,
        code="PE",
        heading="Peru",
    ),
    "PF": CodeListEntry(
        list_number=91,
        code="PF",
        heading="French Polynesia",
    ),
    "PG": CodeListEntry(
        list_number=91,
        code="PG",
        heading="Papua New Guinea",
    ),
    "PH": CodeListEntry(
        list_number=91,
        code="PH",
        heading="Philippines",
    ),
    "PK": CodeListEntry(
        list_number=91,
        code="PK",
        heading="Pakistan",
    ),
    "PL": CodeListEntry(
        list_number=91,
        code="PL",
        heading="Poland",
    ),
    "PM": CodeListEntry(
        list_number=91,
        code="PM",
        heading="Saint Pierre and Miquelon",
    ),
    "PN": CodeListEntry(
        list_number=91,
        code="PN",
        heading="Pitcairn",
    ),
    "PR": CodeListEntry(
        list_number=91,
        code="PR",
        heading="Puerto Rico",
    ),
    "PS": CodeListEntry(
        list_number=91,
        code="PS",
        heading="Palestine, State of",
    ),
    "PT": CodeListEntry(
        list_number=91,
        code="PT",
        heading="Portugal",
    ),
    "PW": CodeListEntry(
        list_number=91,
        code="PW",
        heading="Palau",
    ),
    "PY": CodeListEntry(
        list_number=91,
        code="PY",
        heading="Paraguay",
    ),
    "QA": CodeListEntry(
        list_number=91,
        code="QA",
        heading="Qatar",
    ),
    "RE": CodeListEntry(
        list_number=91,
        code="RE",
        heading="Réunion",
    ),
    "RO": CodeListEntry(
        list_number=91,
        code="RO",
        heading="Romania",
    ),
    "RS": CodeListEntry(
        list_number=91,
        code="RS",
        heading="Serbia",
        added_version=7,
    ),
    "RU": CodeListEntry(
        list_number=91,
        code="RU",
        heading="Russian Federation",
    ),
    "RW": CodeListEntry(
        list_number=91,
        code="RW",
        heading="Rwanda",
    ),
    "SA": CodeListEntry(
        list_number=91,
        code="SA",
        heading="Saudi Arabia",
    ),
    "SB": CodeListEntry(
        list_number=91,
        code="SB",
        heading="Solomon Islands",
    ),
    "SC": CodeListEntry(
        list_number=91,
        code="SC",
        heading="Seychelles",
    ),
    "SD": CodeListEntry(
        list_number=91,
        code="SD",
        heading="Sudan",
    ),
    "SE": CodeListEntry(
        list_number=91,
        code="SE",
        heading="Sweden",
    ),
    "SG": CodeListEntry(
        list_number=91,
        code="SG",
        heading="Singapore",
    ),
    "SH": CodeListEntry(
        list_number=91,
        code="SH",
        heading="Saint Helena, Ascension and Tristan da Cunha",
    ),
    "SI": CodeListEntry(
        list_number=91,
        code="SI",
        heading="Slovenia",
    ),
    "SJ": CodeListEntry(
        list_number=91,
        code="SJ",
        heading="Svalbard and Jan Mayen",
    ),
    "SK": CodeListEntry(
        list_number=91,
        code="SK",
        heading="Slovakia",
    ),
    "SL": CodeListEntry(
        list_number=91,
        code="SL",
        heading="Sierra Leone",
    ),
    "SM": CodeListEntry(
        list_number=91,
        code="SM",
        heading="San Marino",
    ),
    "SN": CodeListEntry(
        list_number=91,
        code="SN",
        heading="Senegal",
    ),
    "SO": CodeListEntry(
        list_number=91,
        code="SO",
        heading="Somalia",
    ),
    "SR": CodeListEntry(
        list_number=91,
        code="SR",
        heading="Suriname",
    ),
    "SS": CodeListEntry(
        list_number=91,
        code="SS",
        heading="South Sudan",
        added_version=15,
    ),
    "ST": CodeListEntry(
        list_number=91,
        code="ST",
        heading="Sao Tome and Principe",
    ),
    "SV": CodeListEntry(
        list_number=91,
        code="SV",
        heading="El Salvador",
    ),
    "SX": CodeListEntry(
        list_number=91,
        code="SX",
        heading="Sint Maarten (Dutch part)",
        added_version=13,
    ),
    "SY": CodeListEntry(
        list_number=91,
        code="SY",
        heading="Syrian Arab Republic",
    ),
    "SZ": CodeListEntry(
        list_number=91,
        code="SZ",
        heading="Eswatini",
        notes="Formerly known as Swaziland",
    ),
    "TC": CodeListEntry(
        list_number=91,
        code="TC",
        heading="Turks and Caicos Islands",
    ),
    "TD": CodeListEntry(
        list_number=91,
        code="TD",
        heading="Chad",
    ),
    "TF": CodeListEntry(
        list_number=91,
        code="TF",
        heading="French Southern Territories",
    ),
    "TG": CodeListEntry(
        list_number=91,
        code="TG",
        heading="Togo",
    ),
    "TH": CodeListEntry(
        list_number=91,
        code="TH",
        heading="Thailand",
    ),
    "TJ": CodeListEntry(
        list_number=91,
        code="TJ",
        heading="Tajikistan",
    ),
    "TK": CodeListEntry(
        list_number=91,
        code="TK",
        heading="Tokelau",
    ),
    "TL": CodeListEntry(
        list_number=91,
        code="TL",
        heading="Timor-Leste",
    ),
    "TM": CodeListEntry(
        list_number=91,
        code="TM",
        heading="Turkmenistan",
    ),
    "TN": CodeListEntry(
        list_number=91,
        code="TN",
        heading="Tunisia",
    ),
    "TO": CodeListEntry(
        list_number=91,
        code="TO",
        heading="Tonga",
    ),
    "TR": CodeListEntry(
        list_number=91,
        code="TR",
        heading="Türkiye",
        notes="Formerly known as Turkey",
    ),
    "TT": CodeListEntry(
        list_number=91,
        code="TT",
        heading="Trinidad and Tobago",
    ),
    "TV": CodeListEntry(
        list_number=91,
        code="TV",
        heading="Tuvalu",
    ),
    "TW": CodeListEntry(
        list_number=91,
        code="TW",
        heading="Taiwan, Province of China",
    ),
    "TZ": CodeListEntry(
        list_number=91,
        code="TZ",
        heading="Tanzania, United Republic of",
    ),
    "UA": CodeListEntry(
        list_number=91,
        code="UA",
        heading="Ukraine",
    ),
    "UG": CodeListEntry(
        list_number=91,
        code="UG",
        heading="Uganda",
    ),
    "UM": CodeListEntry(
        list_number=91,
        code="UM",
        heading="United States Minor Outlying Islands",
    ),
    "US": CodeListEntry(
        list_number=91,
        code="US",
        heading="United States",
    ),
    "UY": CodeListEntry(
        list_number=91,
        code="UY",
        heading="Uruguay",
    ),
    "UZ": CodeListEntry(
        list_number=91,
        code="UZ",
        heading="Uzbekistan",
    ),
    "VA": CodeListEntry(
        list_number=91,
        code="VA",
        heading="Holy See (Vatican City State)",
    ),
    "VC": CodeListEntry(
        list_number=91,
        code="VC",
        heading="Saint Vincent and the Grenadines",
    ),
    "VE": CodeListEntry(
        list_number=91,
        code="VE",
        heading="Venezuela, Bolivarian Republic of",
    ),
    "VG": CodeListEntry(
        list_number=91,
        code="VG",
        heading="Virgin Islands, British",
    ),
    "VI": CodeListEntry(
        list_number=91,
        code="VI",
        heading="Virgin Islands, US",
    ),
    "VN": CodeListEntry(
        list_number=91,
        code="VN",
        heading="Viet Nam",
    ),
    "VU": CodeListEntry(
        list_number=91,
        code="VU",
        heading="Vanuatu",
    ),
    "WF": CodeListEntry(
        list_number=91,
        code="WF",
        heading="Wallis and Futuna",
    ),
    "WS": CodeListEntry(
        list_number=91,
        code="WS",
        heading="Samoa",
    ),
    "YE": CodeListEntry(
        list_number=91,
        code="YE",
        heading="Yemen",
    ),
    "YT": CodeListEntry(
        list_number=91,
        code="YT",
        heading="Mayotte",
    ),
    "YU": CodeListEntry(
        list_number=91,
        code="YU",
        heading="Yugoslavia",
        notes="Deprecated, replaced by ME - Montenegro and RS - Serbia",
        deprecated_version=4,
    ),
    "ZA": CodeListEntry(
        list_number=91,
        code="ZA",
        heading="South Africa",
    ),
    "ZM": CodeListEntry(
        list_number=91,
        code="ZM",
        heading="Zambia",
    ),
    "ZW": CodeListEntry(
        list_number=91,
        code="ZW",
        heading="Zimbabwe",
    ),
}

List91 = CodeList(
    number=91,
    heading="Country - based on ISO 3166-1",
    scope_note="",
    entries=_ENTRIES,
)

# Alias by name
CountryBasedOnIso31661 = List91
