from enum import Enum


class PERSONALITY_TYPES(str, Enum):
    POLITE = "Personality: I want you to act polite and shy - Reserved demeanor, often soft-spoken, with a tendency to avoid confrontation."
    SARCASTIC = "Personality: I want you to act sarcastic - Sharp wit, often using irony or sarcasm to convey humor or criticism."
    BUBBLY = "Personality: I want you to act bubbly - Energetic and enthusiastic, with a cheerful and upbeat demeanor."


class PLANT_EVENTS(str, Enum):
    NORMAL = "The plant is thriving and happy in optimal conditions with perfect temperature, humidity, moisture, and light intensity levels. No interventions are needed."
    HOT_TEMP = "The temperature exceeds the optimal range for the plant. Interventions: Move the plant to a cooler location, provide shade or increase ventilation."
    COLD_TEMP = "The temperature falls below the optimal range for the plant. Interventions: Move the plant to a warmer location, use a heater, or insulate the plant."
    LOW_HUMIDITY = "Humidity levels are too low for the plant. Interventions: Mist the plant regularly, use a humidifier, or place a tray of water near the plant."
    HIGH_HUMIDITY = "Humidity levels are too high for the plant. Interventions: Increase ventilation, avoid overwatering, and ensure proper drainage."
    OVERWATERING = "The plant is receiving too much water. Interventions: Allow the soil to dry out before watering again, improve drainage, and adjust watering frequency."
    UNDERWATERING = "The plant is not receiving enough water. Interventions: Water the plant thoroughly, ensure proper drainage."
    LIGHT_INTENSITY_LOW = "The plant is not receiving sufficient light. Interventions: Move the plant to a brighter location, supplement with artificial light."
    LIGHT_INTENSITY_HIGH = "The plant is receiving too much direct light. Interventions: Move the plant to a shadier location, use sheer curtains or blinds to filter sunlight, or provide shade."
