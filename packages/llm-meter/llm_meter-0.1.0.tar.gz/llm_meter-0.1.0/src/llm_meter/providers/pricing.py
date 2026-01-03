from enum import Enum

from pydantic import BaseModel, ConfigDict


class ModelName(str, Enum):
    """Enumeration of supported model names for pricing."""

    # GPT-5.2 Family
    GPT_5_2_PRO = "gpt-5.2-pro"
    GPT_5_2 = "gpt-5.2"
    GPT_5_2_MINI = "gpt-5.2-mini"
    GPT_5_2_NANO = "gpt-5.2-nano"

    # GPT-5.1 Family
    GPT_5_1 = "gpt-5.1"
    GPT_5_1_MINI = "gpt-5.1-mini"
    GPT_5_1_NANO = "gpt-5.1-nano"

    # GPT-5 Family
    GPT_5 = "gpt-5"
    GPT_5_MINI = "gpt-5-mini"
    GPT_5_NANO = "gpt-5-nano"

    # o3 Family
    O3 = "o3"
    O3_MINI = "o3-mini"

    # o1 Family
    O1 = "o1"
    O1_MINI = "o1-mini"

    # GPT-4.1 Family
    GPT_4_1 = "gpt-4.1"
    GPT_4_1_MINI = "gpt-4.1-mini"
    GPT_4_1_NANO = "gpt-4.1-nano"

    # GPT-4o Family
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_3_5_TURBO = "gpt-3.5-turbo"


class ModelPricing(BaseModel):
    model_config = ConfigDict(frozen=True)
    input_1k: float
    output_1k: float


# Default pricing as of late 2025 (Prices per 1k tokens)
PRICING: dict[ModelName, ModelPricing] = {
    ModelName.GPT_5_2_PRO: ModelPricing(input_1k=0.021, output_1k=0.168),
    ModelName.GPT_5_2: ModelPricing(input_1k=0.00175, output_1k=0.014),
    ModelName.GPT_5_2_MINI: ModelPricing(input_1k=0.00025, output_1k=0.002),
    ModelName.GPT_5_2_NANO: ModelPricing(input_1k=0.00005, output_1k=0.0004),
    ModelName.GPT_5_1: ModelPricing(input_1k=0.00125, output_1k=0.010),
    ModelName.GPT_5_1_MINI: ModelPricing(input_1k=0.00025, output_1k=0.002),
    ModelName.GPT_5_1_NANO: ModelPricing(input_1k=0.00005, output_1k=0.0004),
    ModelName.GPT_5: ModelPricing(input_1k=0.00125, output_1k=0.010),
    ModelName.GPT_5_MINI: ModelPricing(input_1k=0.00025, output_1k=0.002),
    ModelName.GPT_5_NANO: ModelPricing(input_1k=0.00005, output_1k=0.0004),
    ModelName.O3: ModelPricing(input_1k=0.01, output_1k=0.04),
    ModelName.O3_MINI: ModelPricing(input_1k=0.0011, output_1k=0.0044),
    ModelName.O1: ModelPricing(input_1k=0.015, output_1k=0.06),
    ModelName.O1_MINI: ModelPricing(input_1k=0.0011, output_1k=0.0044),
    ModelName.GPT_4_1: ModelPricing(input_1k=0.003, output_1k=0.012),
    ModelName.GPT_4_1_MINI: ModelPricing(input_1k=0.0008, output_1k=0.0032),
    ModelName.GPT_4_1_NANO: ModelPricing(input_1k=0.0002, output_1k=0.0008),
    ModelName.GPT_4O: ModelPricing(input_1k=0.0025, output_1k=0.010),
    ModelName.GPT_4O_MINI: ModelPricing(input_1k=0.00015, output_1k=0.0006),
    ModelName.GPT_3_5_TURBO: ModelPricing(input_1k=0.0005, output_1k=0.0015),
}


def calculate_cost(model: str | ModelName, input_tokens: int, output_tokens: int) -> float:
    """
    Calculate the estimated cost for a given model and token count.
    Splits by model name prefixes to handle versioned names (e.g. gpt-4o-2024-05-13).
    """
    pricing = None
    model_str = str(model)

    # 1. Try exact match by converting to Enum
    try:
        m_enum = ModelName(model_str)
        pricing = PRICING.get(m_enum)
    except ValueError:
        # 2. Try prefix match if exact match fails
        for m_name in ModelName:
            if model_str.startswith(m_name.value):
                pricing = PRICING[m_name]
                break

    if not pricing:
        return 0.0

    cost = (input_tokens / 1000 * pricing.input_1k) + (output_tokens / 1000 * pricing.output_1k)
    return round(cost, 6)
