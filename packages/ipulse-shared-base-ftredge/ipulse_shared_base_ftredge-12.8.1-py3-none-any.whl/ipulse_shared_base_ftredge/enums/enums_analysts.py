"""
Analyst-related enums for AI prediction architecture.

This module defines all analyst identity, presentation, and execution enums
for the Analyst DNA v2 architecture.

AUTHOR: Russlan Ramdowar; russlan@ftredge.com
CREATED: 2025-12-28
"""

from .enums_pulse import AutoLower
from .enums_units import TimeUnit, TimeFrame


# =============================================================================
# CORE COGNITIVE DIMENSIONS (Identity)
# =============================================================================

class CognitiveStyle(AutoLower):
    """Primary and secondary cognitive styles - the mental model and investment philosophy.
    
    These represent fundamental analytical lenses and thinking frameworks.
    Display names and ordering will be controlled via database display_name fields.
    
    Organized by domain for conceptual clarity:
    - Economist/Finance styles
    - Power-seeking styles  
    - Detective/Journalistic styles
    - Scientific/Analytical styles
    - Mystics
    """
    # Economist/Finance Styles
    VALUE_PURIST = "value_purist"  # The Buffett - fundamentals, cash flow, intrinsic value
    ECONOMIST = "economist" # The Keynes - macro trends, cycles, behavioral finance
    MACRO_STRATEGIST = "macro_strategist"  # The Ray Dalio - top-down, rates, geopolitics, cycles
    GROWTH_HUNTER = "growth_hunter"  # The Cathie Wood, Peter Thiel - disruption, innovation, TAM
    TECHNICAL_QUANT = "technical_quant"  # The RoboTrader - data-driven, momentum, volatility
    CONTRARIAN = "contrarian"  # The Michael Burry - skeptical of consensus
    
    # Power-Seeking Styles
    MACHIAVELLIAN = "machiavellian"  # The Realpolitik - power dynamics, monopoly, lobbying
    EARTH_INVADER = "earth_invader"  # The Outsider - alien perspective, non-human logic patterns
    
    # Detective/Journalistic Styles
    FORENSIC_DETECTIVE = "forensic_detective"  # The Sherlock - accounting irregularities, hidden footnotes

     # Scientific/Analytical Styles
    SUPERINTELLIGENCE = "superintelligence"  # The Singularity - vast synthesis, non-obvious correlations
    PHYSICIST = "physicist"  # The Feynman - first principles, fundamental laws, deep modeling
    BIOLOGIST = "biologist"  # The Darwin - evolutionary patterns, adaptation, ecosystems
    CHEMIST = "chemist"  # The Curie - reaction dynamics, catalysts
    ENGINEER = "engineer"  # The Tesla, Elon Musk - systems thinking, optimization, efficiency

    # Mystics
    ASTROLOGIST = "astrologist"  # The Mystic - cosmic patterns, planetary cycles, fate

class PersonaVariant(AutoLower):
    """Intensity/moderation level of persona expression.
    
    Defines how strongly the cognitive style is applied.
    """
    STANDARD = "standard"  # Balanced, orthodox application of cognitive style
    EXTREME = "extreme"  # Maximum intensity, often contrarian or unconventional


class Mood(AutoLower):
    """Emotional/psychological flavor - can have multiple moods.
    
    Personas can combine moods (e.g., [AGGRESSIVE, GREEDY] or [FEARFUL, SAD]).
    """
    BALANCED = "balanced"  # Even-keeled, objective, measured temperament
    COLD = "cold"  # Detached, clinical, highly rational
    AGGRESSIVE = "aggressive"  # Bold, high-conviction, assertive expression
    FEARFUL = "fearful"  # Risk-averse, emphasizes caution and downside protection
    GREEDY = "greedy"  # Maximum upside seeking, opportunity capture focus
    SAD = "sad"  # Pessimistic outlook, melancholic framing, defensive positioning


class ExpertiseDomain(AutoLower):
    """Domain specialization for analyst expertise.
    
    Defines the markets/sectors the analyst is optimized for.
    """
    ALL_MARKETS = "all_markets"  # Generalist across all asset classes
    EQUITIES = "equities"  # All equity markets
    US_EQUITIES = "us_equities"  # US equity markets specifically
    CRYPTO = "crypto"  # Cryptocurrency markets
    COMMODITIES = "commodities"  # Commodity markets
    FIXED_INCOME = "fixed_income"  # Bonds and fixed income
    FX = "fx"  # Foreign exchange
    DERIVATIVES = "derivatives"  # Options, futures, swaps
    ALTERNATIVE = "alternative"  # Alternative investments (PE, VC, real estate)


# =============================================================================
# PRESENTATION DIMENSIONS (How They Communicate)
# =============================================================================

class CommunicationTone(AutoLower):
    """HOW the analyst communicates - the emotional/rhetorical stance.
    
    Defines delivery style and attitude in analysis presentation.
    """
    BALANCED = "balanced"  # Objective, measured, even-handed
    EXPRESSIVE = "expressive"  # Emotional, passionate, emphatic language
    SOCRATIC = "socratic"  # Question-driven, dialogic, challenges assumptions
    PROPHETIC = "prophetic"  # Grand vision, sweeping historical analogies
    GONZO = "gonzo"  # First-person, immersive, visceral, unfiltered
    INVESTIGATIVE = "investigative"  # Detective-like, evidence-building, methodical
    ROAST = "roast"  # Abrasive, brutally honest, mocking, sarcastic
    TELEGRAPHIC = "telegraphic"  # Terse, no-nonsense, BLUF attitude


class LexicalRegister(AutoLower):
    """Target audience sophistication level - vocabulary complexity.
    
    Controls how technical and specialized the language should be.
    """
    NOVICE_FRIENDLY = "novice_friendly"  # Explains jargon, analogies, educational tone
    INTERMEDIATE = "intermediate"  # Moderate terminology, balanced accessibility
    SME = "sme"  # Dense terminology, assumes domain expertise
    SLANG = "slang"  # Internet culture, meme references, Gen Z speak


# =============================================================================
# TASK SCOPE DIMENSIONS (What Timeframe)
# =============================================================================

class ThinkingHorizon(AutoLower):
    """Investment timeframe perspective - temporal scope of analysis.
    
    Defines the time horizon for investment analysis and predictions.
    
    Micro-Structure Horizons (High Frequency & Intraday):
    - HIGHFREQ_TRADE: Seconds/Minutes - Market microstructure, order flow, tick data
    - SCALP_TRADE: Minutes/Hours - Quick momentum bursts, breakout trading
    - INTRADAY_TRADE: Hours/Day - Session-based trading, closing before market close
    
    Swing & Trend Horizons (Days to Months):
    - SWING_TRADE: Days/Weeks - Capturing multi-day moves, technical patterns
    - POSITION_TRADE: Weeks/Months - Riding major trends, intermediate term
    
    Investment Horizons (Months to Decades):
    - TACTICAL_INVESTMENT: Months/Years - Medium-term allocation, business cycle investing
    - STRATEGIC_INVESTMENT: Years - Long-term capital appreciation, strategy execution
    - DYNASTY_BUILDING: Decades/Generations - Forever holding, compounding machines
    """
    HIGHFREQ_TRADE = "highfreq_trade"  # Seconds/Minutes: Market microstructure, order flow, tick data
    SCALP_TRADE = "scalp_trade"  # Minutes/Hours: Quick momentum bursts, breakout trading
    INTRADAY_TRADE = "intraday_trade"  # Hours/Day: Session-based trading, closing before market close
    SWING_TRADE = "swing_trade"  # Days/Weeks: Capturing multi-day moves, technical patterns
    POSITION_TRADE = "position_trade"  # Weeks/Months: Riding major trends, intermediate term
    TACTICAL_INVESTMENT = "tactical_investment"  # Months/Years: Medium-term allocation, business cycle investing (6m-3y)
    STRATEGIC_INVESTMENT = "strategic_investment"  # Years: Long-term capital appreciation, strategy execution (3y-7y)
    DYNASTY_BUILDING = "dynasty_building"  # Decades/Generations: Forever holding, compounding machines (7y-50y+)


class PredictionTaskType(AutoLower):
    """Type of prediction task being performed.
    
    Defines the analytical goal of the prediction pipeline.
    """
    FORECAST_CLOSE_PRICE_PCT_CHANGE = "forecast_close_price_pct_change"
    GENERATE_INVESTMENT_THESIS = "generate_investment_thesis"  # Qualitative buy/sell/hold reasoning
    CONDUCT_RISK_ASSESSMENT = "conduct_risk_assessment"  # Risk analysis and scoring


# =============================================================================
# EXECUTION CONFIGURATION DIMENSIONS (How They Work)
# =============================================================================

class AnalystMode(AutoLower):
    """Execution capability mode - composite human-friendly display label.
    
    Represents specific combinations of thinking_level, creativity_level,
    web_search, and rag_search capabilities.
    """
    # Pure Thinking Modes - no external data
    FAST_THINKER = "fast_thinker"  # thinking_level=FAST, no web, no RAG
    THINKER = "thinker"  # thinking_level=HIGH, no web, no RAG
    DEEP_THINKER = "deep_thinker"  # thinking_level=DEEP, no web, no RAG
    CREATIVE_THINKER = "creative_thinker"  # creativity_level=CREATIVE, thinking_level=HIGH
    
    # Thinking with Data - LLM + rich input data
    QUANT_THINKER = "quant_thinker"  # LLM reasoning + macro stats + quant predictions
    STATISTICAL_THINKER = "statistical_thinker"  # LLM reasoning + macro stats
    
    # Scholar Modes - RAG-enabled
    THINKING_SCHOLAR = "thinking_scholar"  # thinking_level=HIGH, rag_search=True, rag_mode=STANDARD
    DEEP_THINKING_SCHOLAR = "deep_thinking_scholar"  # thinking_level=DEEP, rag_search=True, rag_mode=PRECISE
    CREATIVE_SCHOLAR = "creative_scholar"  # creativity_level=CREATIVE, rag_search=True
    
    # Researcher Modes - Web-enabled
    THINKING_RESEARCHER = "thinking_researcher"  # thinking_level=HIGH, web_search=True, web_mode=STANDARD
    DEEP_RESEARCHER = "deep_researcher"  # thinking_level=DEEP, web_search=True, web_mode=DEEP
    CREATIVE_RESEARCHER = "creative_researcher"  # creativity_level=CREATIVE, web_search=True
    
    # Hybrid Modes - RAG + Web
    SCHOLAR_RESEARCHER = "scholar_researcher"  # Both rag_search=True and web_search=True, thinking_level=HIGH
    DEEP_SCHOLAR_RESEARCHER = "deep_scholar_researcher"  # Both enabled, thinking_level=DEEP, web_search_mode=DEEP
    CREATIVE_SCHOLAR_RESEARCHER = "creative_scholar_researcher"  # creativity_level=CREATIVE, both search types enabled
    
    # Specialized Analytical Modes - Non-LLM
    STATISTICIAN = "statistician"  # Classical statistical modeling (ARIMA, regression)
    QUANT = "quant"  # Deep learning models (neural networks, LSTM)


class AssignmentReason(AutoLower):
    """Reason for assigning an analyst to a subject.
    
    Context for why this specific analyst is covering this subject.
    """
    MANUAL_CURATION = "manual_curation"  # Explicitly assigned by human
    EXPERIMENTAL = "experimental"  # Testing new configurations
    AUTO_RECOMMEND = "auto_recommend"  # System recommended based on fit
    PILOT_TEST = "pilot_test"  # Testing new analyst performance
    PERFORMANCE_UPGRADE = "performance_upgrade"  # Upgrading from lower performing analyst


class ThinkingLevel(AutoLower):
    """Reasoning depth control - technical configuration.
    
    Controls the depth and thoroughness of the AI model's reasoning process.
    """
    FAST = "fast"  # Quick, efficient reasoning
    HIGH = "high"  # Deep, thorough reasoning (default)
    DEEP = "deep"  # Maximum reasoning depth (when available)


class CreativityLevel(AutoLower):
    """Model temperature/creativity control - technical configuration.
    
    Controls output variability and creative exploration.
    """
    DETERMINISTIC = "deterministic"  # Low temperature, highly consistent
    BALANCED = "balanced"  # Moderate creativity (default)
    CREATIVE = "creative"  # High temperature, exploratory

class DataStructureMode(AutoLower):
    """Data presentation format for AI consumption/production.
    
    Defines the structural paradigm of the data.
    """
    TABULAR = "tabular"  # Rigid arrays, positional encoding (for XGBoost/ARIMA)
    NARRATIVE_TEXT = "narrative_text"  # Human-readable text with templates (for LLMs)
    JSON = "json"  # Structured object data (for Hybrid/LLMs)


class AssemblyStyle(AutoLower):
    """Prompt assembly style for different model capabilities.
    
    Defines how the prompt components are stitched together.
    """
    STANDARD = "standard"  # Standard system + user prompt
    INSTRUCTION_FOCUSED = "instruction_focused"  # Enforced JSON schema output
    CONTENT_FOCUSED = "content_focused"  # Flexible narrative output
    MINIMAL = "minimal"  # Minimal context for high-speed models

class WebSearchMode(AutoLower):
    """Web search intensity - technical configuration.
    
    Defines web search depth when web_search is enabled.
    """
    STANDARD = "standard"  # Single query, top results (default)
    DEEP = "deep"  # Multi-step iterative research (premium cost)


class RagRetrievalMode(AutoLower):
    """RAG retrieval strategy - technical configuration.
    
    Defines retrieval precision when rag_search is enabled.
    """
    STANDARD = "standard"  # Balanced retrieval (default)
    PRECISE = "precise"  # High-precision retrieval, fewer but more relevant results


# =============================================================================
# COMPONENT TYPES (Scoping and Assembly)
# =============================================================================

class ScopingComponentType(AutoLower):
    """Types of reusable scoping context components.
    
    Defines the categories of instruction/context components used in prompt assembly.
    Uses lowercase as per architecture specification.
    Numbered codes: 10s series.
    """
    GENERAL_GUIDELINES = "general_guidelines"  # 10: Universal instructions
    COMMUNICATION_TONE_INSTRUCTIONS = "communication_tone_instructions"  # 20: Tone/attitude directives
    LEXICAL_REGISTER_INSTRUCTIONS = "lexical_register_instructions"  # 30: Audience-specific language
    SUBJECT_CONTEXT = "subject_context"  # 40: Subject-specific context
    TASK_INSTRUCTIONS = "task_instructions"  # 50: Task-specific instructions


class ContentStatus(AutoLower):
    """Content status for component templates.
    
    Indicates whether component content contains runtime placeholders.
    Numbered codes: 10s series.
    """
    STATIC = "static"  # 10: No placeholders, ready to use as-is
    WITH_PLACEHOLDERS = "with_placeholders"  # Contains {{TABLE.FIELD}} placeholders


class PersonaInjectionMethod(AutoLower):
    """Method for injecting persona instructions into model API calls.
    
    Only applicable to configurable models (LLMs). Null for traditional ML models.
    """
    SYSTEM_INSTRUCTION = "system_instruction"  # Via system instruction field
    USER_CONTENT = "user_content"  # Via user content/prompt
    HYBRID = "hybrid"  # Split across both fields


# =============================================================================
# ENUM HELPER FUNCTIONS
# =============================================================================

def get_horizon_constraints(thinking_horizon: ThinkingHorizon) -> dict:
    """Dynamically derive min/max horizon values from thinking_horizon enum.
    
    This function provides time constraint lookups for thinking horizons.
    Used throughout the analyst DNA architecture for:
    - Validating horizon values in xref table configurations
    - Filtering compatible analyst personas by thinking horizon
    - Enforcing time range constraints in prediction pipelines
    - Dynamic constraint resolution vs. hardcoded values in schemas
    
    Args:
        thinking_horizon: The thinking horizon enum value
        
    Returns:
        dict: Dictionary with min_val, min_timeunit, max_val, max_timeunit.
              Format:
              {
                  'min_val': int,
                  'min_timeunit': TimeUnit,
                  'max_val': int,
                  'max_timeunit': TimeUnit
              }
    
    Note:
        Each type's max val is always inclusive. min val is non inclusive.
        
        Current implementation supports all 8 horizons from micro-structure trading to multi-generational investing.
    """
    
    horizon_map = {
        ThinkingHorizon.HIGHFREQ_TRADE: {
            "min_val": 0, "min_timeunit": TimeUnit.SECOND,
            "max_val": 10, "max_timeunit": TimeUnit.SECOND
        },  # nanoseconds to 10 seconds (market microstructure)
        ThinkingHorizon.SCALP_TRADE: {
            "min_val": 10, "min_timeunit": TimeUnit.SECOND,
            "max_val": 5, "max_timeunit": TimeUnit.MINUTE
        },  # Minutes to 4 hours (intraday momentum)
        ThinkingHorizon.INTRADAY_TRADE: {
            "min_val": 5, "min_timeunit": TimeUnit.MINUTE,
            "max_val": 24, "max_timeunit": TimeUnit.HOUR
        },  # Hours to 1 day (session-based)
        ThinkingHorizon.SWING_TRADE: {
            "min_val": 1, "min_timeunit": TimeUnit.DAY,
            "max_val": 15, "max_timeunit": TimeUnit.DAY
        },  # Days to 3 weeks (multi-day moves)
        ThinkingHorizon.POSITION_TRADE: {
            "min_val": 15, "min_timeunit": TimeUnit.DAY,
            "max_val": 6, "max_timeunit": TimeUnit.MONTH
        },  # Weeks to 3 months (trend following)
        ThinkingHorizon.TACTICAL_INVESTMENT: {
            "min_val": 6, "min_timeunit": TimeUnit.MONTH,
            "max_val": 3, "max_timeunit": TimeUnit.YEAR
        },  # 6 months to 3 years (business cycle)
        ThinkingHorizon.STRATEGIC_INVESTMENT: {
            "min_val": 3, "min_timeunit": TimeUnit.YEAR,
            "max_val": 7, "max_timeunit": TimeUnit.YEAR
        },  # 3 years to 7 years (long-term capital appreciation)
        ThinkingHorizon.DYNASTY_BUILDING: {
            "min_val": 7, "min_timeunit": TimeUnit.YEAR,
            "max_val": 100, "max_timeunit": TimeUnit.YEAR
        },  # 7 years to 50+ years (generational wealth)
    }
    
    return horizon_map.get(thinking_horizon, {
        "min_val": 6, "min_timeunit": TimeUnit.MONTH,
        "max_val": 3, "max_timeunit": TimeUnit.YEAR
    })  # Default to TACTICAL

