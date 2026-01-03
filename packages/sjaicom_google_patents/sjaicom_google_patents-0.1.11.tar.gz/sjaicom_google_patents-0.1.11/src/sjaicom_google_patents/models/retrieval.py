"""
Pydantic models for the IP Agent MCP service.
Defines the structure for RetrievalPlan (Request) and RetrievalResponse (Response).
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, ConfigDict

# --- Enums (Strict constraints for LLM) ---

class UserIntent(str, Enum):
    """Classifies the user's high-level goal."""
    PATENT_SEARCH = "patent_search"       # Simple search
    PATENT_MINING = "patent_mining"       # Mining/Idea validation
    LANDSCAPE_ANALYSIS = "landscape_analysis" # Competitor/Trend analysis
    LEGAL_RISK_CHECK = "legal_risk_check" # FTO/Infringement check
    DOCUMENT_RETRIEVAL = "document_retrieval" # Get paper/patent full text

class ResourceType(str, Enum):
    """The type of data source to query."""
    PATENT = "patent"
    PAPER = "paper"
    TRADEMARK = "trademark"

class ActionType(str, Enum):
    """The operation to perform on the resource."""
    SEARCH = "search"
    GET_DETAILS = "get_details"
    CHECK_STATUS = "check_status"

class Region(str, Enum):
    """Geographic scope for patent search.
    Standardized Country/Organization codes.
    """
    # Core Regions (Most frequently used)
    WO = "WO"       # WORLD INTELLECTUAL PROPERTY ORGANIZATION
    US = "US"       # UNITED STATES OF AMERICA
    EP = "EP"       # EUROPEAN PATENT OFFICE (EPO)
    JP = "JP"       # JAPAN
    KR = "KR"       # REPUBLIC OF KOREA
    CN = "CN"       # CHINA
    
    # Extended Regions (Alphabetical Order)
    AE = "AE"       # UNITED ARAB EMIRATES
    AG = "AG"       # ANTIGUA AND BARBUDA
    AL = "AL"       # ALBANIA
    AM = "AM"       # ARMENIA
    AO = "AO"       # ANGOLA
    AP = "AP"       # AFRICAN REGIONAL INTELLECTUAL PROPERTY ORGANIZATION (ARIPO)
    AR = "AR"       # ARGENTINA
    AT = "AT"       # AUSTRIA
    AU = "AU"       # AUSTRALIA
    AW = "AW"       # ARUBA
    AZ = "AZ"       # AZERBAIJAN
    BA = "BA"       # BOSNIA AND HERZEGOVINA
    BB = "BB"       # BARBADOS
    BD = "BD"       # BANGLADESH
    BE = "BE"       # BELGIUM
    BF = "BF"       # BURKINA FASO
    BG = "BG"       # BULGARIA
    BH = "BH"       # BAHRAIN
    BJ = "BJ"       # BENIN
    BN = "BN"       # BRUNEI DARUSSALAM
    BO = "BO"       # BOLIVIA
    BR = "BR"       # BRAZIL
    BW = "BW"       # BOTSWANA
    BX = "BX"       # BENELUX OFFICE FOR INTELLECTUAL PROPERTY (BOIP)
    BY = "BY"       # BELARUS
    BZ = "BZ"       # BELIZE
    CA = "CA"       # CANADA
    CF = "CF"       # CENTRAL AFRICAN REPUBLIC
    CG = "CG"       # CONGO
    CH = "CH"       # SWITZERLAND
    CI = "CI"       # CÔTE D'IVOIRE
    CL = "CL"       # CHILE
    CM = "CM"       # CAMEROON
    CO = "CO"       # COLOMBIA
    CR = "CR"       # COSTA RICA
    CS = "CS"       # CZECHOSLOVAKIA
    CU = "CU"       # CUBA
    CY = "CY"       # CYPRUS
    CZ = "CZ"       # CZECH REPUBLIC
    DD = "DD"       # GERMAN DEMOCRATIC REPUBLIC
    DE = "DE"       # GERMANY
    DJ = "DJ"       # DJIBOUTI
    DK = "DK"       # DENMARK
    DM = "DM"       # DOMINICA
    DO = "DO"       # DOMINICAN REPUBLIC
    DZ = "DZ"       # ALGERIA
    EA = "EA"       # EURASIAN PATENT ORGANIZATION (EAPO)
    EC = "EC"       # ECUADOR
    EE = "EE"       # ESTONIA
    EG = "EG"       # EGYPT
    EM = "EM"       # OFFICE FOR HARMONIZATION IN THE INTERNAL MARKET (OHIM)
    ES = "ES"       # SPAIN
    FI = "FI"       # FINLAND
    FR = "FR"       # FRANCE
    GA = "GA"       # GABON
    GB = "GB"       # UNITED KINGDOM
    GC = "GC"       # PATENT OFFICE OF THE GCC
    GD = "GD"       # GRENADA
    GE = "GE"       # GEORGIA
    GH = "GH"       # GHANA
    GM = "GM"       # GAMBIA
    GN = "GN"       # GUINEA
    GQ = "GQ"       # EQUATORIAL GUINEA
    GR = "GR"       # GREECE
    GT = "GT"       # GUATEMALA
    GW = "GW"       # GUINEA-BISSAU
    HK = "HK"       # HONG KONG SAR, CHINA
    HN = "HN"       # HONDURAS
    HR = "HR"       # CROATIA
    HU = "HU"       # HUNGARY
    IB = "IB"       # INTERNATIONAL BUREAU OF WIPO
    ID = "ID"       # INDONESIA
    IE = "IE"       # IRELAND
    IL = "IL"       # ISRAEL
    IN = "IN"       # INDIA
    IR = "IR"       # IRAN, ISLAMIC REPUBLIC OF
    IS = "IS"       # ICELAND
    IT = "IT"       # ITALY
    JO = "JO"       # JORDAN
    KE = "KE"       # KENYA
    KG = "KG"       # KYRGYZSTAN
    KH = "KH"       # CAMBODIA
    KM = "KM"       # COMOROS
    KN = "KN"       # SAINT KITTS AND NEVIS
    KP = "KP"       # DEMOCRATIC PEOPLE'S REPUBLIC OF KOREA
    KW = "KW"       # KUWAIT
    KZ = "KZ"       # KAZAKHSTAN
    LA = "LA"       # LAO PEOPLE'S DEMOCRATIC REPUBLIC
    LC = "LC"       # SAINT LUCIA
    LI = "LI"       # LIECHTENSTEIN
    LK = "LK"       # SRI LANKA
    LR = "LR"       # LIBERIA
    LS = "LS"       # LESOTHO
    LT = "LT"       # LITHUANIA
    LU = "LU"       # LUXEMBOURG
    LV = "LV"       # LATVIA
    LY = "LY"       # LIBYAN ARAB JAMAHIRIYA
    MA = "MA"       # MOROCCO
    MC = "MC"       # MONACO
    MD = "MD"       # REPUBLIC OF MOLDOVA
    ME = "ME"       # MONTENEGRO
    MG = "MG"       # MADAGASCAR
    MK = "MK"       # THE FORMER YUGOSLAV REPUBLIC OF MACEDONIA
    ML = "ML"       # MALI
    MN = "MN"       # MONGOLIA
    MO = "MO"       # MACAO
    MR = "MR"       # MAURITANIA
    MT = "MT"       # MALTA
    MW = "MW"       # MALAWI
    MX = "MX"       # MEXICO
    MY = "MY"       # MALAYSIA
    MZ = "MZ"       # MOZAMBIQUE
    NA = "NA"       # NAMIBIA
    NE = "NE"       # NIGER
    NG = "NG"       # NIGERIA
    NI = "NI"       # NICARAGUA
    NL = "NL"       # NETHERLANDS
    NO = "NO"       # NORWAY
    NZ = "NZ"       # NEW ZEALAND
    OA = "OA"       # OAPI
    OM = "OM"       # OMAN
    PA = "PA"       # PANAMA
    PE = "PE"       # PERU
    PG = "PG"       # PAPUA NEW GUINEA
    PH = "PH"       # PHILIPPINES
    PL = "PL"       # POLAND
    PT = "PT"       # PORTUGAL
    PY = "PY"       # PARAGUAY
    QA = "QA"       # QATAR
    RO = "RO"       # ROMANIA
    RS = "RS"       # SERBIA
    RU = "RU"       # RUSSIAN FEDERATION
    RW = "RW"       # RWANDA
    SA = "SA"       # SAUDI ARABIA
    SC = "SC"       # SEYCHELLES
    SD = "SD"       # SUDAN
    SE = "SE"       # SWEDEN
    SG = "SG"       # SINGAPORE
    SI = "SI"       # SLOVENIA
    SK = "SK"       # SLOVAKIA
    SL = "SL"       # SIERRA LEONE
    SM = "SM"       # SAN MARINO
    SN = "SN"       # SENEGAL
    ST = "ST"       # SAO TOME AND PRINCIPE
    SU = "SU"       # USSR (Historical)
    SV = "SV"       # EL SALVADOR
    SY = "SY"       # SYRIAN ARAB REPUBLIC
    SZ = "SZ"       # SWAZILAND
    TD = "TD"       # CHAD
    TG = "TG"       # TOGO
    TH = "TH"       # THAILAND
    TJ = "TJ"       # TAJIKISTAN
    TM = "TM"       # TURKMENISTAN
    TN = "TN"       # TUNISIA
    TR = "TR"       # TURKEY
    TT = "TT"       # TRINIDAD AND TOBAGO
    TW = "TW"       # TAIWAN
    TZ = "TZ"       # TANZANIA
    UA = "UA"       # UKRAINE
    UG = "UG"       # UGANDA
    UY = "UY"       # URUGUAY
    UZ = "UZ"       # UZBEKISTAN
    VC = "VC"       # SAINT VINCENT AND THE GRENADINES
    VE = "VE"       # VENEZUELA
    VN = "VN"       # VIET NAM
    YU = "YU"       # YUGOSLAVIA (Historical)
    ZA = "ZA"       # SOUTH AFRICA
    ZM = "ZM"       # ZAMBIA
    ZW = "ZW"       # ZIMBABWE

    GLOBAL = "Global" # Special flag for All Regions

# --- Nested Parameter Models ---

class SearchParams(BaseModel):
    """Parameters for 'search' action."""
    keywords: List[str] = Field(..., description="List of technical keywords. Example: ['5G', 'antenna']")
    regions: List[Region] = Field(default=[Region.CN], description="Target regions.")
    date_range: Optional[str] = Field(None, description="Time range, e.g., 'last_3_years' or '2020-2024'.")
    assignee: Optional[str] = Field(None, description="Company or person name.")
    limit: int = Field(default=10, le=100, description="Max results to return.")

class StrategyConfig(BaseModel):
    """Configuration for execution strategy."""
    allow_generalization: bool = Field(default=False, description="If true, MCP may relax criteria if no results found. DEFAULT: FALSE (Fail-Fast).")
    require_fulltext: bool = Field(default=False, description="If true, only return results with full text available.")

# --- Core Plan Structure (Request) ---

class RetrievalStep(BaseModel):
    """A single step in the retrieval plan.
    
    CRITICAL INSTRUCTION FOR LLM:
    - For Multi-Region Search (e.g., "China, US, Europe"): create ONE step and set `params['regions']` to `["CN", "US", "EP"]`. 
      DO NOT create separate steps for each region.
    - For Global Search: set `params['regions']` to `["Global"]` or list specific major regions in ONE step.
    - Do NOT split identical searches into multiple steps.
    """
    step: int = Field(..., description="Step sequence number, starting from 1.")
    resource_type: Union[ResourceType, str] = Field(..., description="Data source type. 'patent' is the main supported type.")
    action: Union[ActionType, str] = Field(..., description="Action to perform. 'search' is the main supported action.")
    params: Dict[str, Any] = Field(..., description="Dynamic parameters based on action. For 'search', use SearchParams structure.")
    strategy: Optional[StrategyConfig] = Field(default_factory=StrategyConfig, description="Execution strategy.")
    rationale: Optional[str] = Field(None, description="LLM's reasoning for this step.")

class RetrievalPlan(BaseModel):
    """
    The master plan generated by the LLM.
    This is the input argument for the 'execute_retrieval_plan' tool.
    """
    task_id: Optional[str] = Field(None, description="Unique task identifier. If None, MCP will generate one.")
    user_intent: UserIntent = Field(..., description="The classified intent of the user.")
    retrieval_plan: List[RetrievalStep] = Field(..., description="Ordered list of steps to execute.")
    
    model_config = ConfigDict(extra="ignore")

# --- Response Structure (Output) ---

class FrequencyItem(BaseModel):
    """Time-based frequency stats."""
    year_range: str
    percentage: float

class StatItem(BaseModel):
    """Statistical item for summary (Assignee, Inventor, CPC)."""
    key: str
    percentage: float
    frequency: List[FrequencyItem] = Field(default_factory=list)

class SearchSummary(BaseModel):
    """High-level statistical summary from SerpApi."""
    assignees: List[StatItem] = Field(default_factory=list, alias="assignee")
    inventors: List[StatItem] = Field(default_factory=list, alias="inventor")
    cpcs: List[StatItem] = Field(default_factory=list, alias="cpc")

class PatentImage(BaseModel):
    """Patent figure/image."""
    thumbnail: str
    full: str

class PatentData(BaseModel):
    """Standardized patent data structure."""
    id: str = Field(..., description="Patent ID, e.g., 'US20240012345A1'")
    title: str
    snippet: Optional[str] = Field(None, description="Snippet/Abstract with highlighted keywords")
    assignee: Optional[str] = None
    inventor: Optional[str] = None
    priority_date: Optional[str] = None
    filing_date: Optional[str] = None
    publication_date: Optional[str] = None
    publication_number: Optional[str] = None
    language: Optional[str] = None
    kind_code: Optional[str] = Field(None, description="Kind code, e.g., A1, B2")
    
    # Links & Media
    patent_link: Optional[str] = None
    serpapi_link: Optional[str] = Field(None, description="Link to SerpApi details for this patent")
    pdf_link: Optional[str] = None
    thumbnail: Optional[str] = None
    figures: List[PatentImage] = Field(default_factory=list)
    
    # Status
    region: str
    status: Optional[str] = Field(None, description="e.g., 'ACTIVE', 'EXPIRED', 'GRANT', 'APPLICATION'")
    legal_status: Optional[str] = Field(None, description="Unified legal status")
    country_status: Dict[str, str] = Field(default_factory=dict, description="Status in different countries")
    
    score: Optional[float] = None # Relevance score
    extension: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Extension field for additional data")

class MetaInfo(BaseModel):
    """Metadata about the execution."""
    total_found: int
    returned_count: int
    warnings: List[str] = Field(default_factory=list)
    sources_used: List[str] = Field(default_factory=list)
    suggestion: Optional[str] = Field(None, description="Guidance for the LLM on how to interact with the user next.")
    api_debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug info about API calls (URL, params, etc).")

class RetrievalResponse(BaseModel):
    """
    The final output returned to the LLM.
    """
    task_id: str
    status: str = Field(..., description="'success', 'partial_success', or 'failed'")
    summary: Optional[SearchSummary] = Field(None, description="Statistical summary of the search results")
    data: Dict[str, List[Any]] = Field(default_factory=dict, description="Results keyed by type, e.g., {'patents': [...], 'papers': []}")
    meta: MetaInfo

class PatentSearchRequest(BaseModel):
    """
    Direct request for patent search (SerpApi wrapper).
    """
    keywords: str = Field(..., description="Search query, e.g. '(VR) OR (Virtual Reality)'. Supports boolean operators.")
    country_codes: str = Field("CN,US,WO", description="Comma-separated country codes, e.g. 'CN,US,WO'. Default: 'CN,US,WO'")
    date_range: Optional[str] = Field(None, description="Date filter, e.g. 'priority:20220101' (after) or 'before:priority:20230101'.")
    limit: int = Field(10, description="Number of results to return (10-100). Default: 10")
    skip_cache: bool = Field(False, description="If true, bypass SerpApi cache. Default: false")

class PatentSearchResponse(BaseModel):
    """
    Standardized response for patent search.
    """
    total_results: int = Field(0, description="Total estimated results found")
    results: List[PatentData] = Field(default_factory=list)
    summary: Optional[SearchSummary] = None
    debug_info: Optional[Dict[str, Any]] = None

